import base64
import json

from test.test_base import TestBase

import secrets
from metrics.metrics import sampling_id, should_sample, Metrics


class MetricsTest(TestBase):
    def setUp(self):
        super(MetricsTest, self).setUp()
        self.old_mixpanel_token = secrets.MIXPANEL_TOKEN

    def tearDown(self):
        super(MetricsTest, self).tearDown()
        secrets.MIXPANEL_TOKEN = self.old_mixpanel_token

    def test_sampling_id(self):
        self.assertEqual(sampling_id('craig'), 0xdbe4108e)
        self.assertEqual(sampling_id('mamacken'), 0x52da4ced)

    def test_should_sample(self):
        # lowest order 4 bytes of SHA-1 of 'craig' = 0xdbe4108e
        self.assertFalse(should_sample('craig', sampling_rate=0.50))

        # lowest order 4 bytes of SHA-1 of 'mamacken' = 0x52da4ced
        self.assertTrue(should_sample('mamacken', sampling_rate=0.50))

    def test_simple_track(self):
        secrets.MIXPANEL_TOKEN = 'test'
        m = Metrics()

        r = m.track('test_event', {'user': 'dr.nick', 'my': 'metric'})
        data = r[0].request.payload()[4:]
        data = base64.b64decode(data)

        decoded = json.loads(data)[0]
        self.assertEqual(decoded['event'], 'test_event')
        self.assertEqual(decoded['properties']['user'], 'dr.nick')
        self.assertEqual(decoded['properties']['token'], 'test')
        self.assertEqual(decoded['properties']['my'], 'metric')
        self.assertNotIn('bot-id', decoded['properties'])
