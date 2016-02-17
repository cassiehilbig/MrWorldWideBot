import json

from flask import request
from google.appengine.api import taskqueue
from kik.api import send_messages
from kik.messages import MessageType

from app import app
from config import Config
from lib import logging
from lib.bot_state_machine import state_machine
from lib.decorators import require_params
from lib.utils import generate_signature, partition, error_response


# Message types that should be processed. If you choose to respond to other message types, you will
# need to add them here
ALLOWED_MESSAGE_TYPES = [MessageType.TEXT, MessageType.PICTURE, MessageType.VIDEO, MessageType.LINK,
                         MessageType.STICKER, MessageType.SCAN_DATA]


@app.route('/receive', methods=['POST'])
def receive():
    if request.headers.get('X-Kik-Signature') != generate_signature(Config.BOT_API_KEY, request.get_data()):
        return error_response(403, 'API signature incorrect')

    if not isinstance(request.args.get('messages'), list):
        return error_response(400, 'Invalid request body')

    tasks = []
    for message in request.args['messages']:
        if 'type' in message and message['type'] in ALLOWED_MESSAGE_TYPES:
            tasks.append(taskqueue.Task(
                url='/tasks/incoming',
                payload=json.dumps({'message': message})))
        else:
            logging.info('Ignoring non-whitelisted message of type {}'.format(message['type']))

    for batch in partition(tasks, Config.MAX_TASKQUEUE_BATCH_SIZE):
        taskqueue.Queue('incoming').add(batch)

    return '', 200


@app.route('/tasks/incoming', methods=['POST'])
@require_params('message')
def incoming():
    message = request.args['message']

    logging.debug('Processing message: {}'.format(message))

    outgoing_messages = state_machine.handle_message(message['from'], message)

    if len(outgoing_messages) > 0:
        send_messages(outgoing_messages, bot_name=Config.BOT_USERNAME, bot_api_key=Config.BOT_API_KEY)

    return '', 200
