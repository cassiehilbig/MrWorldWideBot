import json

from test.test_base import TestBase
from lib.admin_requests_mixin import AdminRequestsMixin, AdminFetchError, CreateBotError, UsernameAvailableCheckError,\
    UpdateDisplayNameError, UpdateProfilePictureError
from lib.utils import server_url


class AdminRequestsMixinTest(TestBase):
    def test_get_admin(self):
        self.route_urlfetch_response(
            'get',
            '{}/api/v1/botsworth/admin?username=eagerod'.format(server_url()),
            status=200,
            content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = AdminRequestsMixin()
        response = mixin._get_admin('eagerod')
        self.assertEqual(response, {})

    def test_get_admin_failure(self):
        self.route_urlfetch_response(
            'get',
            '{}/api/v1/botsworth/admin?username=eagerod'.format(server_url()),
            status=404,
            content='{}'
        )

        mixin = AdminRequestsMixin()
        self.assertRaises(AdminFetchError, mixin._get_admin, 'eagerod')

    def test_create_bot_error(self):
        self.route_urlfetch_response(
            'post',
            '{}/api/v1/botsworth/bot/create'.format(server_url()),
            status=400,
            content='{}'
        )

        mixin = AdminRequestsMixin()
        self.assertRaises(CreateBotError, mixin._create_bot, 'eagerod', 'somebot', 'somebot')

    def test_create_bot_success(self):
        self.route_urlfetch_response(
            'post',
            '{}/api/v1/botsworth/bot/create'.format(server_url()),
            status=200,
            content='{"foo": "bar"}'
        )

        mixin = AdminRequestsMixin()
        self.assertEqual(mixin._create_bot('eagerod', 'somebot', 'somebot'), {'foo': 'bar'})

    def test_check_available_error(self):
        self.route_urlfetch_response(
            'get',
            '{}/api/v1/botsworth/username_available?username={}'.format(server_url(), 'somebot'),
            status=400,
            content='{}'
        )

        mixin = AdminRequestsMixin()
        self.assertRaises(UsernameAvailableCheckError, mixin._check_username_available, 'somebot')

    def test_check_available_success_unavailable(self):
        self.route_urlfetch_response(
            'get',
            '{}/api/v1/botsworth/username_available?username={}'.format(server_url(), 'somebot'),
            status=200,
            content='{"available": false}'
        )

        mixin = AdminRequestsMixin()
        self.assertEqual(mixin._check_username_available('somebot'), {"available": False})

    def test_check_available_success_available(self):
        self.route_urlfetch_response(
            'get',
            '{}/api/v1/botsworth/username_available?username={}'.format(server_url(), 'somebot'),
            status=200,
            content='{"available": true}'
        )

        mixin = AdminRequestsMixin()
        self.assertEqual(mixin._check_username_available('somebot'), {"available": True})

    def test_update_display_name(self):
        self.route_urlfetch_response(
            'put',
            '{}/api/v1/botsworth/bot/abot_id/display_name'.format(server_url()),
            status=200,
            content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = AdminRequestsMixin()
        response = mixin._update_bot_display_name('eagerod', 'abot_id', 'Bots-o-rama')
        self.assertEqual(response, {})

    def test_update_display_name_failure(self):
        self.route_urlfetch_response(
            'put',
            '{}/api/v1/botsworth/bot/abot_id/display_name'.format(server_url()),
            status=401,
            content='{}'
        )

        mixin = AdminRequestsMixin()
        self.assertRaises(UpdateDisplayNameError, mixin._update_bot_display_name, 'eagerod', 'abot_id', 'Bots-o-rama')

    def test_update_profile_pic(self):
        self.route_urlfetch_response(
            'put',
            '{}/api/v1/botsworth/bot/abot_id/profile_pic'.format(server_url()),
            status=200,
            content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = AdminRequestsMixin()
        response = mixin._update_bot_profile_picture('eagerod', 'abot_id', 'picolo')
        self.assertEqual(response, {})

        self.assertEqual(json.loads(self.request.payload()), {
            'username': 'eagerod',
            'profile_picture': 'picolo'
        })

    def test_update_profile_pic_failure(self):
        self.route_urlfetch_response(
            'put',
            '{}/api/v1/botsworth/bot/abot_id/profile_pic'.format(server_url()),
            status=401,
            content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = AdminRequestsMixin()
        self.assertRaises(UpdateProfilePictureError, mixin._update_bot_profile_picture, 'eagerod', 'abot_id', 'picolo')

        self.assertEqual(json.loads(self.request.payload()), {
            'username': 'eagerod',
            'profile_picture': 'picolo'
        })
