import json

from test.test_base import TestBase
from config import Config
import lib.metrics


class MetricsTest(TestBase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.old_mixpanel_token = Config.MIXPANEL_TOKEN
        lib.metrics._mp = None

    def tearDown(self):
        super(self.__class__, self).tearDown()
        Config.MIXPANEL_TOKEN = self.old_mixpanel_token

    def test_track(self):
        Config.MIXPANEL_TOKEN = 'test'

        lib.metrics.track('testuser', 'A Test Event', {'foo': 'bar'})

        tasks = self.get_tasks('mixpanel')
        data = tasks[0].payload
        decoded = json.loads(json.loads(data)['data'])
        self.assertEqual(decoded['event'], 'A Test Event')
        self.assertEqual(decoded['properties']['distinct_id'], 'testuser')
        self.assertEqual(decoded['properties']['token'], 'test')
        self.assertEqual(decoded['properties']['foo'], 'bar')
