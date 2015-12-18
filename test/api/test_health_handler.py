from test.test_base import TestBase


class HealthHandlerTest(TestBase):

    def test_success(self):
        self.api_call('get', '/health/', status=200)
