from importlib import import_module
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'xlib'))

from flask import Flask, request

app = Flask(__name__)


@app.before_request
def parse_data():
    if request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
        try:
            request.args = json.loads(request.get_data())
        except ValueError:
            pass


module = os.environ.get('CURRENT_MODULE_ID', 'default')

path = ('{}/api/{}'.format(os.path.dirname(os.path.realpath(__file__)), module))
routes = []

for file_name in os.listdir(path):
    if not file_name.startswith('.') and file_name.endswith('.py') and file_name != '__init__.py':
        api_name = file_name[:-3]
        import_module('api.{}.{}'.format(module, api_name))

__all__ = ['app']
