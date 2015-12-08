from datetime import date, timedelta, datetime
import json

from freezegun import freeze_time

from google.appengine.api import urlfetch

from const import MetricsEvent
from metrics.mixpanel_api import Mixpanel
import mock
from secrets import MIXPANEL_API_KEY, MIXPANEL_API_SECRET
from test.test_base import TestBase


class MixpanelApiTest(TestBase):
    def setUp(self):
        super(self.__class__, self).setUp()
        self.mixpanel = Mixpanel(MIXPANEL_API_KEY, MIXPANEL_API_SECRET)

    @freeze_time(datetime(year=2015, month=1, day=20))
    @mock.patch('google.appengine.api.urlfetch.fetch')
    def test_request(self, fetch):
        from_date = (date.today() - timedelta(days=14)).isoformat()
        to_date = date.today().isoformat()

        fetch.return_value.content = json.dumps({
            'legend_size': 1,
            'data': {
                'series': ['2015-06-03', ],
                'values': {'Sent Welcome Reply': {'2015-06-03': 0}}
            }
        })

        self.mixpanel.request(["segmentation"], {
            'event': MetricsEvent.OUT_SIGNUP_RESPONSE,
            'from_date': from_date,
            'to_date': to_date,
            'unit': 'day',
            'where': 'properties["bot-id"]=="%s"' % 'botsworth'
        })

        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(fetch.call_args[1]['deadline'], 60)
        self.assertEqual(fetch.call_args[1]['method'], urlfetch.GET)
        self.assertEqual(
            fetch.call_args[1]['url'],
            'http://mixpanel.com/api/2.0/segmentation/'
            '?format=json'
            '&from_date=2015-01-06'
            '&expire=1421712600'
            '&sig=dd1804adfb7684e945d6909f19b1a07a'
            '&to_date=2015-01-20'
            '&api_key='
            '&where=properties%5B%22bot-id%22%5D%3D%3D%22botsworth%22'
            '&event=Sent+Welcome+Reply&unit=day'
        )
