from google.appengine.api import urlfetch_stub
from google.appengine.api.apiproxy_stub import APIProxyStub
from google.appengine.api.memcache.memcache_stub import MemcacheServiceStub as _MemcacheServiceStub
from google.appengine.ext.testbed import Testbed as _Testbed, MEMCACHE_SERVICE_NAME, URLFETCH_SERVICE_NAME, \
    GCS_URLMATCHERS_TO_FETCH_FUNCTIONS


class Testbed(_Testbed):
    def init_memcache_stub(self, enable=True):
        """Enable the memcache stub.

        Args:
          enable: True, if the fake service should be enabled, False if real service should be disabled.
        """
        if not enable:
            self._disable_stub(MEMCACHE_SERVICE_NAME)
            return

        stub = MemcacheServiceStub()
        self._register_stub(MEMCACHE_SERVICE_NAME, stub)

    def init_urlfetch_stub(self, enable=True, stub=True):
        """Enable the urlfetch stub.

        The urlfetch service stub uses the urllib module to make
        requests. Because on appserver urllib also relies the urlfetch
        infrastructure, using this stub will have no effect.

        Args:
          enable: True, if the fake service should be enabled, False if real service should be disabled.
          stub: True, if the fake service should be stubbed.
        """

        if not enable:
            self._disable_stub(URLFETCH_SERVICE_NAME)
            return

        if stub:
            stub = URLFetchServiceMock()
        else:
            urlmatchers_to_fetch_functions = []
            urlmatchers_to_fetch_functions.extend(GCS_URLMATCHERS_TO_FETCH_FUNCTIONS)
            stub = urlfetch_stub.URLFetchServiceStub(urlmatchers_to_fetch_functions=urlmatchers_to_fetch_functions)

        self._register_stub(URLFETCH_SERVICE_NAME, stub)


class MemcacheServiceStub(_MemcacheServiceStub):
    def set_gettime(self, func):
        self._gettime = func


class URLFetchServiceMock(APIProxyStub):
    def __init__(self, service_name='urlfetch'):
        super(URLFetchServiceMock, self).__init__(service_name)
        self._status = None
        self._headers = None
        self._content = None
        self._routes = {}
        self._on_request = None

    def set_request_callback(self, callback):
        self._on_request = callback

    def set_response(self, status, headers, content):
        self._status = status
        self._headers = headers
        self._content = content

    def route_response(self, method, url, status, headers, content):
        self._routes[(method, url)] = {
            'status': status,
            'headers': headers,
            'content': content,
        }

    def _Dynamic_Fetch(self, request, response):
        if self._on_request is not None:
            self._on_request(request)
        request_method = {
            request.GET: 'GET',
            request.POST: 'POST',
            request.PUT: 'PUT',
            request.PATCH: 'PATCH',
            request.DELETE: 'DELETE',
        }[request.method()]
        for method, path in self._routes:
            if request.url().startswith(path) and method.upper() == request_method:
                data = self._routes[(method, path)]
                break
        else:
            data = {
                'status': self._status,
                'headers': self._headers,
                'content': self._content,
            }
        if data['status'] is None:
            raise Exception(
                'urlfetch response not setup for %s %s, call set_urlfetch_response' % (request_method, request.url()))

        response.set_finalurl(request.url)
        response.set_contentwastruncated(False)
        response.set_statuscode(data['status'])
        response.set_content(data['content'])
        for header, value in data['headers'].items():
            new_header = response.add_header()
            new_header.set_key(header)
            new_header.set_value(value)
        self.request = request
        self.response = response
