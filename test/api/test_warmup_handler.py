from test.test_base import TestBase


class WarmupHandlerTest(TestBase):

    def test_success(self):
        self.api_call('get', '/_ah/warmup', status=200)
