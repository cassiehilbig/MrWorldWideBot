import mock

from test.test_base import TestBase


class MetricsHandlerTest(TestBase):

    @mock.patch('api.metrics_handler.Consumer.send')
    def test_send(self, send):
        self.api_call('post', '/tasks/mixpanel', data={
            'endpoint': 'foobar.com',
            'data': {'test': 'something'}
        }, status=200)

        send.assert_called_once_with('foobar.com', {'test': 'something'})
