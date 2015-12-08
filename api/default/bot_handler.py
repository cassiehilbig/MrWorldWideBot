import json

from google.appengine.api import taskqueue
from flask import request

from config import Config
from lib.utils import generate_signature, partition, error_response
from lib.decorators import require_params
from secrets import BOT_API_KEY
from app import app
from errors import INVALID_PARAMETER, UNAUTHORIZED


@app.route('/receive', methods=['POST'])
def receive():
    if request.headers.get('X-Kik-Signature') != generate_signature(BOT_API_KEY, request.get_data()):
        return error_response(403, UNAUTHORIZED, 'API signature incorrect')

    if not isinstance(request.args.get('messages'), list):
        return error_response(400, INVALID_PARAMETER, 'Invalid request body')

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
    return 'yolo', 200
