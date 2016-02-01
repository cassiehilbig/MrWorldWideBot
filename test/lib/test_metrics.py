import json

from test.test_base import TestBase
from model.bot_user import BotUser
from config import Config


class MetricsTest(TestBase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.old_mixpanel_token = Config.MIXPANEL_TOKEN

    def tearDown(self):
        super(self.__class__, self).tearDown()
        Config.MIXPANEL_TOKEN = self.old_mixpanel_token

    def test_track_with_state(self):
        Config.MIXPANEL_TOKEN = 'test'

        from lib.metrics import track  # Have to import after the token is set

        user = BotUser(id='testuser', states=['first-state', 'second-state'])

        track(user, 'A Test Event', {'foo': 'bar'})

        tasks = self.get_tasks('mixpanel')
        data = tasks[0].payload
        decoded = json.loads(json.loads(data)['data'])
        self.assertEqual(decoded['event'], 'A Test Event')
        self.assertEqual(decoded['properties']['distinct_id'], 'testuser')
        self.assertEqual(decoded['properties']['token'], 'test')
        self.assertEqual(decoded['properties']['state'], 'second-state')
        self.assertEqual(decoded['properties']['foo'], 'bar')

    def test_track_without_state(self):
        Config.MIXPANEL_TOKEN = 'test'

        from lib.metrics import track  # Have to import after the token is set

        user = BotUser(id='testuser')

        track(user, 'A Test Event', {'foo': 'bar'})

        tasks = self.get_tasks('mixpanel')
        data = tasks[0].payload
        decoded = json.loads(json.loads(data)['data'])
        self.assertEqual(decoded['event'], 'A Test Event')
        self.assertEqual(decoded['properties']['distinct_id'], 'testuser')
        self.assertEqual(decoded['properties']['token'], 'test')
        self.assertEqual(decoded['properties']['foo'], 'bar')
        self.assertNotIn('state', decoded['properties']['foo'])
