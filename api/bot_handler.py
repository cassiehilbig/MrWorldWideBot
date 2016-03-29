import json

from flask import request
from google.appengine.api import taskqueue
from kik.messages import messages_from_json, TextMessage, PictureMessage, VideoMessage, LinkMessage, \
    StartChattingMessage, StickerMessage, ScanDataMessage

from app import app
from config import Config
from lib import logging
from lib.__init__ import get_kik_api
from lib.decorators import require_params
from lib.utils import partition, error_response

from lib.state_machine import StateMachine
# Message types that should be processed. If you choose to respond to other message types, you will
# need to add them here
ALLOWED_MESSAGE_TYPES = [TextMessage, PictureMessage, VideoMessage, LinkMessage, StartChattingMessage,
                         StickerMessage, ScanDataMessage]


@app.route('/incoming', methods=['POST'])
def receive():
    if not get_kik_api().utils.verify_signature(request.headers.get('X-Kik-Signature'), request.data):
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


    outgoing_messages = state_machine.handle_message(message['from'], message)

    if len(outgoing_messages) > 0:
        send_messages(outgoing_messages, bot_name=Config.BOT_USERNAME, bot_api_key=Config.BOT_API_KEY)

    logging.debug('Processing message: {}'.format(message))

    if isinstance(message, TextMessage):
        get_kik_api().message.send([TextMessage(to=message.from_user, chat_id=message.chat_id, body=message.body)])
    else:
        get_kik_api().message.send([TextMessage(to=message.from_user, chat_id=message.chat_id, body='I\'m just an example bot')])

    return '', 200
