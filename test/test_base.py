from __future__ import absolute_import
from unittest import TestCase
import os
import json

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import ndb
from google.appengine.ext.testbed import TASKQUEUE_SERVICE_NAME, MEMCACHE_SERVICE_NAME

from test.testbed import Testbed

os.environ['BOT_USERNAME'] = 'test_bot'
os.environ['BOT_API_KEY'] = 'test_key'

from app import app


class TestBase(TestCase):
    MODULE = 'default'
    MOCK_URL_FETCH = True
    ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))

    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1.0)

        self.app = app.test_client()
        self.app.testing = True

        # self.testapp = TestApp(self.app)
        self.testbed = Testbed()
        self.testbed.activate()
        self.testbed.init_app_identity_stub()
        self.testbed.init_taskqueue_stub(root_path=self.ROOT_PATH)
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub(root_path=self.ROOT_PATH, consistency_policy=self.policy)
        self.testbed.init_user_stub()
        self.testbed.init_logservice_stub()
        self.testbed.init_channel_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_urlfetch_stub(stub=self.MOCK_URL_FETCH)

        ndb.get_context().set_cache_policy(lambda key: False)
        self._orig_server_software = os.environ.get("SERVER_SOFTWARE", None)

    def tearDown(self):
        self.testbed.deactivate()
        self.set_current_user(None)

    def set_current_user(self, email, user_id=None, is_admin=False):
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def get_tasks(self, queue=None):
        return self.testbed.get_stub(TASKQUEUE_SERVICE_NAME).get_filtered_tasks(queue_names=queue)

    def execute_tasks(self, queue='default'):
        tasks = self.get_tasks(queue)
        retries = []
        self.testbed.get_stub(TASKQUEUE_SERVICE_NAME).FlushQueue(queue)
        for task in tasks:
            del task.headers['Content-Length']
            try:
                self.testapp.post(task.url, params=task.payload, headers=task.headers)
            except:
                retries.append(task)

        for task in retries:
            self.app.post(task.url, data=task.payload, headers=task.headers)

    def api_call(self, method, resource, data=None, status=200, headers={}, upload_files=None, https=True,
                 cookies=None):
        if type(data) in (dict, list) and (method in ['post', 'put', 'patch']):
            data = json.dumps(data)

        func = getattr(self.app, method.lower())
        result = func(resource, data=data, headers=headers)

        self.assertEqual(result.status_code, status)

        try:
            result.json = json.loads(result.data)
        except ValueError:
            pass

        return result

    def set_memcache_gettime(self, func):
        self.testbed.get_stub(MEMCACHE_SERVICE_NAME).set_gettime(func)
        # Please forgive me, future coders, for the hackiness
        # The memcache stub stores the gettime function on EVERY cache items, so we have to reset them all
        for namespace, cachedict in self.testbed.get_stub(MEMCACHE_SERVICE_NAME)._the_cache.iteritems():
            for key, entry in cachedict.iteritems():
                entry._gettime = func
