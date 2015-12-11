from os import environ
import re

from fabric.api import local, runs_once, shell_env


ALL_ARGS = frozenset(['BOT_API_KEY', 'CI_COMMIT_ID', 'REFRESH_TOKEN'])
# These are the same for prod and staging.
COMMON_ARGS = frozenset(['BOT_API_KEY', 'CI_COMMIT_ID', 'REFRESH_TOKEN'])
# These are different for prod and staging. Staging is prepended with "STAGING_"
APPLICATION_ARGS = ALL_ARGS.difference(COMMON_ARGS)

# Backend uses everything except REFRESH_TOKEN, and CI_COMMIT_ID.
BACKEND_ARGS = ALL_ARGS.difference(['CI_COMMIT_ID', 'REFRESH_TOKEN'])


app_config = {
    'MODULES': 'app.yaml',
    'CONFIGS': 'index.yaml queue.yaml cron.yaml',
    'CONFIG': 'secrets.py'
}


def _overwrite(file_obj, text):
    file_obj.seek(0)
    file_obj.write(text)
    file_obj.truncate()


@runs_once
def install_backend_dependencies():
    local('pip install --upgrade --no-deps --requirement requirements_xlib.txt -t xlib')
    local('rm -rf xlib/*.egg-info xlib/*.dist-info xlib/VERSION xlib/*.pth')


@runs_once
def install_test_dependencies():
    local('pip install --upgrade --quiet --requirement requirements.txt')


def lint():
    install_test_dependencies()
    local('flake8 .')


def test():
    lint()
    local('python -m multitest discover -v -t . -s test')


def coverage():
    install_test_dependencies()
    local('coverage run -m multitest discover -t . -s test 2> /dev/null')
    local('coverage combine')
    local('coverage report -m')


def debug(runtime='local'):
    """Starts up debug server. Run with `debug:docker` to run with docker"""
    install_test_dependencies()
    with shell_env(GAE_LOCAL_VM_RUNTIME='1'):
        local('''
        dev_appserver.py --host 0.0.0.0 --log_level debug {MODULES}'''.format(**app_config))


if environ.get('CI'):
    def secrets():
        """Validates and sets backend secrets"""
        with open(app_config['CONFIG'], 'r+') as backend_config:
            text = backend_config.read()
            for arg in BACKEND_ARGS:
                if arg not in text:
                    raise Exception('{} not found in {}'.format(arg, app_config['CONFIG']))
                text = re.sub(r'{0} = \'.*\''.format(arg),
                              '{0} = \'{1}\''.format(arg, app_config[arg]),
                              text)
            _overwrite(backend_config, text)
        local('flake8 {CONFIG} --max-line-length=1000'.format(**app_config))

    def production():
        """Configures deploy for production"""
        app_config['APPLICATION'] = 'your-app'  # TODO better app detection
        for arg in ALL_ARGS:
            app_config[arg] = environ[arg]

    def staging():
        """Configures deploy for staging"""
        app_config['APPLICATION'] = 'your-app-staging'  # TODO better app detection
        app_config['MODULES'] = 'app.yaml discovery.yaml platform.yaml sender.yaml video.yaml'
        for arg in COMMON_ARGS:
            app_config[arg] = environ[arg]
        for arg in APPLICATION_ARGS:
            app_config[arg] = environ['STAGING_{}'.format(arg)]
        # minimize instance count for staging
        for module in app_config['MODULES'].split(' '):
            with open(module, 'r+') as module_file:
                text = module_file.read()
                text = re.sub(r'min_idle_instances: .*', 'min_idle_instances: 0', text)
                text = re.sub(r'max_idle_instances: .*', 'max_idle_instances: 1', text)
                text = re.sub(r'min_num_instances: .*', 'min_num_instances: 1', text)
                _overwrite(module_file, text)

    def validate_env():
        """Validates required files and environment variables"""
        production()
        staging()
        secrets()

    def deploy_application():
        """Deploys application with given config"""
        if 'APPLICATION' not in app_config:
            raise Exception('Deploy environment not specified. Use `fab staging deploy` or `fab production deploy`.')
        secrets()
        for module in app_config['MODULES'].split(' '):
            with open(module, 'r+') as module_file:
                text = module_file.read()
                text = re.sub(r'application: .*', 'application: {}'.format(app_config['APPLICATION']), text)
                _overwrite(module_file, text)

        local('appcfg.py update {} --oauth2_refresh_token={}'
              .format(app_config['MODULES'], app_config['REFRESH_TOKEN']))

    def deploy_staging():
        """Alias for `fab staging deploy_application`"""
        staging()
        deploy_application()

    def deploy():
        """Alias for `fab production deploy_application`"""
        production()
        deploy_application()
