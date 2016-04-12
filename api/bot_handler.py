import json

from google.appengine.api import taskqueue

from app import app, kik
from config import Config
from flask import request
from kik.messages import messages_from_json, TextMessage, PictureMessage, VideoMessage, LinkMessage, \
    StartChattingMessage, StickerMessage, ScanDataMessage
from lib import logging
from lib.bot_state_machine import state_machine
from lib.decorators import require_params
from lib.utils import partition, error_response

# Message types that should be processed. If you choose to respond to other message types, you will
# need to add them here
ALLOWED_MESSAGE_TYPES = [TextMessage, PictureMessage, VideoMessage, LinkMessage, StartChattingMessage,
                         StickerMessage, ScanDataMessage]


@app.route('/incoming', methods=['POST'])
def receive():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return error_response(403, 'API signature incorrect')

    if not isinstance(request.args.get('messages'), list):
        return error_response(400, 'Invalid request body')

    tasks = []
    for message in request.args['messages']:
        tasks.append(taskqueue.Task(
            url='/tasks/incoming',
            payload=json.dumps({'message': message})))

    for batch in partition(tasks, Config.MAX_TASKQUEUE_BATCH_SIZE):
        taskqueue.Queue('incoming').add(batch)

    return '', 200


@app.route('/tasks/incoming', methods=['POST'])
@require_params('message')
def incoming():
    message = messages_from_json([request.args['message']])[0]

    if not any(isinstance(message, allowed_type) for allowed_type in ALLOWED_MESSAGE_TYPES):
        logging.debug('Ignoring non allowed message of type {}'.format(message.type))
        return '', 200

    if message.mention and message.mention != Config.BOT_USERNAME:
        logging.debug('Dropping message mentioning another bot. Message is mentioning {}'.format(message.mention))
        return '', 200

    outgoing_messages = state_machine.handle_message(message.from_user, message)

    logging.debug('Processing message: {}'.format(message))

    if len(outgoing_messages) > 0:
        kik.send_messages(outgoing_messages)

    return '', 200
