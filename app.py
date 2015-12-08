from importlib import import_module
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'xlib'))

from flask import Flask

app = Flask(__name__)

module = os.environ.get('CURRENT_MODULE_ID', 'default')

path = ('{}/api/{}'.format(os.path.dirname(os.path.realpath(__file__)), module))
routes = []

for file_name in os.listdir(path):
    if not file_name.startswith('.') and file_name.endswith('.py') and file_name != '__init__.py':
        api_name = file_name[:-3]
        import_module('api.{}.{}'.format(module, api_name))

__all__ = ['app']
