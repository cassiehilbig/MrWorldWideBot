import json
from os import environ
import re

from fabric.api import hide, local, runs_once

REFRESH_TOKEN_NAME = 'GOOGLE_REFRESH_TOKEN'

ALL_ARGS = frozenset(['BOT_USERNAME', 'BOT_API_KEY'])


@runs_once
def install_xlib():
    local('pip install --upgrade --no-deps --requirement requirements_xlib.txt -t xlib')
    local('rm -rf xlib/*.egg-info xlib/*.dist-info xlib/VERSION xlib/*.pth')


@runs_once
def install():
    local('pip install --upgrade --quiet --requirement requirements.txt')


def lint():
    install()
    local('flake8 .')


def test():
    install()
    lint()
    local('python -m multitest discover -v -t . -s test')


def coverage():
    install()
    local('coverage run -m multitest discover -t . -s test 2> /dev/null')
    local('coverage combine')
    local('coverage report -m')


def debug():
    """Starts up debug server. Run with `debug:docker` to run with docker"""
    install()
    local('dev_appserver.py --host 0.0.0.0 --log_level debug app.yaml')


def deploy():
    """Deploys application"""
    config = {}
    for arg in ALL_ARGS:
        config[arg] = environ[arg]
    with open('config.py', 'r+') as config_file:
        text = config_file.read()
        for arg in ALL_ARGS:
            if arg not in text:
                raise Exception('{} not found in config file'.format(arg))
            print arg, config[arg], text
            text = re.sub(r'{0} = .*'.format(arg), '{0} = \'{1}\''.format(arg, config[arg]), text)
        config_file.seek(0)
        config_file.write(text)
        config_file.truncate()
    lint()
    try:
        refresh_token = environ[REFRESH_TOKEN_NAME]
    except KeyError:
        with hide('running'):
            local('echo {} was not found in the environment'.format(REFRESH_TOKEN_NAME))
            local('echo Retrieving refresh token')
            local('appcfg.py list_versions .', capture=True)
            with open('{}/.appcfg_oauth2_tokens'.format(environ['HOME'])) as token_file:
                token_text = token_file.read()
            refresh_token = json.loads(token_text)['refresh_token']
            local('echo Your refresh token is: {}.')
            local('echo Please have it in the environment using: '.format(refresh_token))
            local('echo export {}={}'.format(REFRESH_TOKEN_NAME, refresh_token))
    local('appcfg.py update . --oauth2_refresh_token {}'.format(refresh_token))
    local('appcfg.py update_queues . --oauth2_refresh_token {}'.format(refresh_token))
    local('appcfg.py update_indexes . --oauth2_refresh_token {}'.format(refresh_token))
    local('appcfg.py update_cron . --oauth2_refresh_token {}'.format(refresh_token))
