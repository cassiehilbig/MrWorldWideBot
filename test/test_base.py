from __future__ import absolute_import
from unittest import TestCase
import os

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import ndb
from google.appengine.ext.testbed import TASKQUEUE_SERVICE_NAME, URLFETCH_SERVICE_NAME, MEMCACHE_SERVICE_NAME
from webtest import TestApp

import app
from test.testbed import Testbed

apps = {
    'default': app.create('default')
}


class TestBase(TestCase):
    MODULE = 'default'
    MOCK_URL_FETCH = True
    ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))

    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1.0)
        self.app = apps[self.MODULE]
        self.testapp = TestApp(self.app)
        self.testbed = Testbed()
        self.testbed.activate()
        self.testbed.init_app_identity_stub()
        self.testbed.init_taskqueue_stub(root_path=self.ROOT_PATH)
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub(root_path=self.ROOT_PATH, consistency_policy=self.policy)
        self.testbed.init_user_stub()
        self.testbed.init_images_stub()
        self.testbed.init_logservice_stub()
        self.testbed.init_channel_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_urlfetch_stub(stub=self.MOCK_URL_FETCH)

        ndb.get_context().set_cache_policy(lambda key: False)
        self._orig_server_software = os.environ.get("SERVER_SOFTWARE", None)

    def tearDown(self):
        os.environ['SERVER_SOFTWARE'] = self._orig_server_software
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
            self.testapp.post(task.url, params=task.payload, headers=task.headers)

    def api_call(self, method, resource, data=None, status=200, headers={}, upload_files=None, https=True,
                 cookies=None):
        method = method.lower()
        is_json = False

        if type(data) in (dict, list) and (method in ['post', 'put', 'patch']):
            is_json = True

            # TODO: data as query param for other requests

        if cookies:
            for cookie in cookies:
                self.testapp.set_cookie(cookie['name'], cookie['value'])

        if is_json:
            func = getattr(self.testapp, method.lower() + '_json')
        else:
            func = getattr(self.testapp, method.lower())

        extra_environ = {
            'wsgi.url_scheme': 'https' if https else 'http'
        }

        kwargs = {
            'status': status,
            'headers': headers,
            'extra_environ': extra_environ
        }

        if data:
            kwargs['params'] = data

        if upload_files:
            kwargs['upload_files'] = upload_files

        response = func(resource, **kwargs)
        # Reset saved cookies
        self.testapp.reset()
        return response

    def set_urlfetch_response(self, status=200, headers={}, content=''):
        self.testbed.get_stub(URLFETCH_SERVICE_NAME).set_response(status, headers, content)

    def set_urlfetch_request_callback(self, callback):
        self.testbed.get_stub(URLFETCH_SERVICE_NAME).set_request_callback(callback)

    def route_urlfetch_response(self, method, url, status=200, headers={}, content=''):
        self.testbed.get_stub(URLFETCH_SERVICE_NAME).route_response(method, url, status, headers, content)

    def set_memcache_gettime(self, func):
        self.testbed.get_stub(MEMCACHE_SERVICE_NAME).set_gettime(func)
        # Please forgive me, future coders, for the hackiness
        # The memcache stub stores the gettime function on EVERY cache items, so we have to reset them all
        for namespace, cachedict in self.testbed.get_stub(MEMCACHE_SERVICE_NAME)._the_cache.iteritems():
            for key, entry in cachedict.iteritems():
                entry._gettime = func
