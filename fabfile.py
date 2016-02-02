import json
from os import environ
import re

from fabric.api import hide, local, runs_once
from fabric.colors import magenta

PROJECT_ID_NAME = 'GOOGLE_PROJECT_ID'
REFRESH_TOKEN_NAME = 'GOOGLE_REFRESH_TOKEN'

ALL_CONFIGS = frozenset(['BOT_USERNAME', 'BOT_API_KEY'])


@runs_once
def install_xlib(reinstall=False):
    if reinstall:
        local('rm -rf xlib/*')
    local('printf \'%s\n%s\n\' \'[install]\' \'prefix=\' > ~/.pydistutils.cfg')
    local('pip install --upgrade --no-deps --requirement requirements.xlib.txt -t xlib')
    local('rm ~/.pydistutils.cfg')
    local('rm -rf xlib/*.egg-info xlib/*.dist-info xlib/VERSION xlib/*.pth')


@runs_once
def install():
    local('pip install --upgrade --quiet --requirement requirements.txt')


def lint():
    install()
    local('flake8 .')


def test():
    install()
    install_xlib()
    lint()
    local('python -m multitest discover -v -t . -s test')


def coverage():
    install()
    install_xlib()
    local('coverage run -m multitest discover -t . -s test 2> /dev/null')
    local('coverage combine')
    local('coverage report -m')


def prepare_env(project=None):
    config = {}
    for arg in ALL_CONFIGS:
        config[arg] = environ[arg]
    with open('app.yaml', 'r+') as app_file:
        text = app_file.read()
        if project is not None:
            text = re.sub('application:.*', 'application: {}'.format(project), text)
        for arg in ALL_CONFIGS:
            if arg not in text:
                raise Exception('{} not found in app.yaml file'.format(arg))
            text = re.sub(r'{0}: .*'.format(arg), '{0}: \'{1}\''.format(arg, config[arg]), text)
        app_file.seek(0)
        app_file.write(text)
        app_file.truncate()


def debug():
    """Starts up debug server"""
    install()
    install_xlib()
    prepare_env()
    local('dev_appserver.py --host 0.0.0.0 --log_level debug .')


def deploy():
    """Deploys application"""
    install()
    install_xlib(reinstall=True)
    prepare_env(environ[PROJECT_ID_NAME])
    try:
        refresh_token = environ[REFRESH_TOKEN_NAME]
    except KeyError:
        with hide('running'):
            print magenta('{} was not found in the environment'.format(REFRESH_TOKEN_NAME))
            local('appcfg.py list_versions .', capture=True)
            with open('{}/.appcfg_oauth2_tokens'.format(environ['HOME'])) as token_file:
                token_text = token_file.read()
            refresh_token = json.loads(token_text)['refresh_token']
            print magenta('Your refresh token is: {}'.format(refresh_token))
            print magenta('Please have it in the environment using: '.format(refresh_token))
            print magenta('export {}={}'.format(REFRESH_TOKEN_NAME, refresh_token))
    local('appcfg.py update . --oauth2_refresh_token {}'.format(refresh_token))
