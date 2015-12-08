import json

from google.appengine.api import taskqueue

from config import Config
from lib.utils import generate_signature, partition
from lib.decorators import require_params
from secrets import BOT_API_KEY
from app import app
from flask import request


@app.route('/receive', methods=['POST'])
def receive():
    if request.headers.get('X-Kik-Signature') != generate_signature(BOT_API_KEY, request.get_data()):
        return 'API signature incorrect', 403

    if not isinstance(request.params.get('messages'), list):
        return 'Invalid request body', 400

    tasks = []
    for message in request.params['messages']:
        tasks.append(taskqueue.Task(
            url='/tasks/incoming',
            payload=json.dumps({'message': message})))

    for batch in partition(tasks, Config.MAX_TASKQUEUE_BATCH_SIZE):
        taskqueue.Queue('incoming').add(batch)

    return '', 200


@app.route('/tasks/incoming', methods=['POST'])
@require_params('message')
def incoming():
    return 'yolo'
