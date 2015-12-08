import json

from google.appengine.api import taskqueue

from config import Config
from lib.base_handler import BaseHandler
from lib.decorators import require_params, log_error_after_task_failures
from lib.kik_bot import send_messages
from lib.botsworth_state_machine import state_machine
from lib.utils import generate_signature, partition
from model import BotUser
from secrets import BOTSWORTH_API_KEY
from app import app
from flask import request


@app.route('/receive', methods=['POST'])
def receive():
    if request.headers.get('X-Kik-Signature') != generate_signature(BOTSWORTH_API_KEY, request.get_data()):
        return 'API signature incorrect', 403

    try:
        data = json.loads(request.get_data())

        if 'messages' not in data:
            raise ValueError
    except ValueError:
        return 'Invalid request body', 400

    tasks = []
    for message in data['messages']:
        tasks.append(taskqueue.Task(
            url='/tasks/incoming',
            payload=json.dumps({'message': message})))

    for batch in partition(tasks, Config.MAX_TASKQUEUE_BATCH_SIZE):
        taskqueue.Queue('incoming').add(batch)

    return '', 200


@app.route('/tasks/incoming', methods=['POST'])
def incoming():
    return 'yolo'
