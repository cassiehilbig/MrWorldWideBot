from app import app

from flask import request
from mixpanel import Consumer

from lib.decorators import require_params


@app.route('/tasks/mixpanel', methods=['POST'])
@require_params('endpoint', 'data')
def send_mixpanel():
    consumer = Consumer()
    consumer.send(request.args['endpoint'], request.args['data'])
    return '', 200
