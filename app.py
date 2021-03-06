import json
import sys
from importlib import import_module
from os import listdir, path

sys.path.insert(0, path.join(path.dirname(__file__), '.'))
sys.path.insert(0, path.join(path.dirname(__file__), 'xlib'))

from config import Config
from flask import Flask, request
from kik import KikApi, Configuration


app = Flask(__name__)
kik = KikApi(Config.BOT_USERNAME, Config.BOT_API_KEY)
config = Configuration(webhook='https://ea997cf2.ngrok.io/incoming', features={})
kik.set_configuration(config)


@app.before_request
def parse_data():
    if request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
        try:
            request.args = json.loads(request.get_data())
        except ValueError:
            pass


for file_name in listdir('{}/api'.format(path.dirname(path.realpath(__file__)))):
    if not file_name.startswith('.') and file_name.endswith('.py') and file_name != '__init__.py':
        import_module('api.{}'.format(file_name[:-3]))


__all__ = ['app']
