import os
import sys
from distutils.spawn import find_executable

TEST_ROOT = os.path.dirname(os.path.realpath(__file__))
os.environ['SERVER_SOFTWARE'] = 'Development'
os.environ['BOT_USERNAME'] = 'test_bot'
os.environ['BOT_API_KEY'] = 'test_key'

bin_path = os.path.dirname(os.path.realpath(find_executable('dev_appserver.py')))
sdk_path = os.path.realpath(os.path.join(bin_path, '..', 'platform', 'google_appengine'))

if not sdk_path:
    raise Exception('AppEngine SDK not found')

sys.path = [sdk_path, bin_path] + sys.path
import dev_appserver
dev_appserver.fix_sys_path()
