from unittest import TestCase
from datetime import datetime

from lib.datetime_utils import datetime_to_utc_timestamp_millis


class DatetimeUtilsTest(TestCase):
    def test_birthday(self):
        dt = datetime(1987, 6, 26)
        self.assertEqual(datetime_to_utc_timestamp_millis(dt), 551664000000)

    def test_leap_year(self):
        dt = datetime(2004, 2, 29)
        self.assertEqual(datetime_to_utc_timestamp_millis(dt), 1078012800000)

    def test_future_with_millis(self):
        dt = datetime(2020, 5, 30, 1, 2, 34, 567000)
        self.assertEqual(datetime_to_utc_timestamp_millis(dt), 1590800554567)
