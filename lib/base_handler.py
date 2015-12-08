import json

from google.appengine.api.datastore_errors import BadValueError
from google.appengine.api.validation import ValidationError
import webapp2

from const import TTL
from errors import INTERNAL_ERROR, INVALID_PARAMETER
from lib import logging
from model import BaseModel


class BaseHandler(webapp2.RequestHandler):
    def initialize(self, *args, **kwargs):
        super(BaseHandler, self).initialize(*args, **kwargs)
        if not self.content_type_valid(self.request):
            self.abort(415)

        try:
            self.body_params = json.loads(self.request.body)
        except:
            self.body_params = {}

        self.params = {}
        self.params.update(self.request.params)

        if isinstance(self.body_params, dict):
            self.params.update(self.body_params)

    def handle_exception(self, exception, debug):
        if isinstance(exception, BadValueError) or isinstance(exception, ValidationError):
            self.respond_error(400, INVALID_PARAMETER)
        else:
            logging.exception(exception)
            self.respond_error(500, INTERNAL_ERROR)

    def cache_header(self, max_age=0, public=True):
        if max_age:
            cache_string = 'public' if public else 'private'
            self.response.headers['Cache-Control'] = '%s, max-age=%s' % (cache_string, max_age)
        else:
            self.response.headers['Cache-Control'] = 'no-cache'

    def security_headers(self):
        self.response.headers['Strict-Transport-Security'] = 'max-age=%s' % TTL.YEAR
        self.response.headers['X-Frame-Options'] = 'DENY'

    def respond(self, data, content_type='application/json', max_age=0, public=True, headers={}):
        self.security_headers()
        self.cache_header(max_age=max_age, public=public)

        for header, value in headers.items():
            if header == 'Content-Type':
                content_type = value
            else:
                self.response.headers[header] = value

        if content_type == 'application/json':
            if isinstance(data, BaseModel):
                data = data.to_dict()
            elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], BaseModel):
                data = [e.to_dict() for e in data]
            data = json.dumps(data, separators=(',', ':'))

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(data)

    def respond_error(self, code, error, message='', data={}, max_age=0, headers={}):
        self.response.set_status(code)
        self.respond({'error': error, 'message': message, 'data': data}, max_age=max_age, headers=headers)

    @staticmethod
    def content_type_valid(req):
        content_type = req.headers.get('Content-Type')
        if req.method == 'POST' and content_type == 'application/x-www-form-urlencoded':
            return False
        return True
