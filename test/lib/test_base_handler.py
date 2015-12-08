from google.appengine.api.validation import ValidationError

from test.test_base import TestBase
from const import TTL
from errors import INTERNAL_ERROR, INVALID_PARAMETER
from lib.base_handler import BaseHandler


class TestHandler(BaseHandler):
    def get(self):
        self.respond({})

    def post(self):
        self.respond({})

    def put(self):
        self.respond({})

    def patch(self):
        self.respond({})


class TestRespondHeadersHandler(BaseHandler):
    def get(self):
        self.respond('^&$%', headers={'Content-Type': 'application/x-supertext', 'X-Kik-Header': '1001'})


class TestErrorHandler(BaseHandler):
    def get(self):
        raise Exception('opps')

    def post(self):
        raise ValidationError('On no!')


class TestBaseHandler(TestBase):
    def setUp(self):
        super(self.__class__, self).setUp()
        for route in [
            (r'/test_base_handler', TestHandler),
            (r'/test_base_handler/error', TestErrorHandler),
            (r'/test_base_handler/headers', TestRespondHeadersHandler)
        ]:
            self.testapp.app.router.add(route)

    def test_no_error_params_list(self):
        self.api_call('post', '/test_base_handler', data=[], status=200)

    def test_respond_headers(self):
        response = self.api_call('get', '/test_base_handler/headers')
        self.assertEqual(response.headers['Content-Type'], 'application/x-supertext')
        self.assertEqual(response.headers['X-Kik-Header'], '1001')
        self.assertEqual(response.headers['Strict-Transport-Security'], 'max-age=%s' % TTL.YEAR)
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')

    def test_error_500(self):
        response = self.api_call('get', '/test_base_handler/error', status=500).json
        self.assertEqual(response['error'], INTERNAL_ERROR)
        self.assertEqual(response['message'], '')
        self.assertEqual(response['data'], {})

    def test_error_400(self):
        response = self.api_call('post', '/test_base_handler/error', status=400).json
        self.assertEqual(response['error'], INVALID_PARAMETER)
        self.assertEqual(response['message'], '')
        self.assertEqual(response['data'], {})

    def test_validate_content_type(self):
        tests = [
            {'method': 'POST', 'content_type': 'application/x-www-form-urlencoded', 'status': 415},
            {'method': 'GET', 'content_type': 'application/x-www-form-urlencoded', 'status': 200},
            {'method': 'POST', 'content_type': 'application/json', 'status': 200},
            {'method': 'PUT', 'content_type': 'application/x-www-form-urlencoded', 'status': 200},
            {'method': 'PATCH', 'content_type': 'application/x-www-form-urlencoded', 'status': 200}
        ]
        for test in tests:
            self.api_call(test['method'],
                          '/test_base_handler',
                          status=test['status'],
                          headers={'Content-Type': test['content_type']})
