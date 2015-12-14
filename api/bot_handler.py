import json

from google.appengine.api import taskqueue
from flask import request

from config import Config
from lib import logging
from lib.utils import generate_signature, partition, error_response
from lib.decorators import require_params
from lib.bot_state_machine import state_machine
from kik.api import send_messages
from model import BotUser
from app import app


@app.route('/receive', methods=['POST'])
def receive():
    if request.headers.get('X-Kik-Signature') != generate_signature(Config.BOT_API_KEY, request.get_data()):
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
    message = request.args['message']

    logging.debug('Processing message: {}'.format(message))

    user = BotUser.get_or_create(message['from'])
    outgoing_messages = state_machine.handle_message(user, message)

    user.put()

    send_messages(outgoing_messages, bot_name=Config.BOT_USERNAME, bot_api_key=Config.BOT_API_KEY)

    return '', 200
