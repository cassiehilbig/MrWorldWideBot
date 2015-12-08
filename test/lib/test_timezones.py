from test.test_base import TestBase
from lib import timezones
from lib.datetime_utils import datetime_to_utc_timestamp
from datetime import datetime


class TimezonesTest(TestBase):
    """The unix timestamps below were calculated by a quick node JS application that I wrote using moment.js,
    which was the least insane reference point I could find to work off of.

    This test ensures that the datetimes around the DST boundaries match the values from moment.js for the
    eastern timezone.
    """

    def _run_test(self, dt, ts):
        self.assertEqual(datetime_to_utc_timestamp(dt), ts)

    # Tests for DST start boundary
    # DST for 2014 starts at 02:00 EST on March 9, 2014

    def test_one_hour_before_dst_start(self):
        self._run_test(datetime(2014, 3, 9, 1, tzinfo=timezones.Eastern), 1394344800)

    def test_dst_start(self):
        self._run_test(datetime(2014, 3, 9, 2, tzinfo=timezones.Eastern), 1394348400)

    def test_half_hour_after_dst_start(self):
        self._run_test(datetime(2014, 3, 9, 2, 30, tzinfo=timezones.Eastern), 1394350200)

    def test_one_hour_after_dst_start(self):
        self._run_test(datetime(2014, 3, 9, 3, tzinfo=timezones.Eastern), 1394348400)

    def test_two_hours_after_dst_start(self):
        self._run_test(datetime(2014, 3, 9, 4, tzinfo=timezones.Eastern), 1394352000)

    # Tests for DST end boundary
    # DST for 2014 ends at 01:00 EST (02:00 EDT) November 2, 2014

    def test_two_hours_before_dst_end(self):
        self._run_test(datetime(2014, 11, 2, 0, tzinfo=timezones.Eastern), 1414900800)

    def test_one_and_a_half_hours_before_dst_end(self):
        self._run_test(datetime(2014, 11, 2, 0, 30, tzinfo=timezones.Eastern), 1414902600)

    def test_one_hour_before_dst_end(self):
        self._run_test(datetime(2014, 11, 2, 1, tzinfo=timezones.Eastern), 1414904400)

    def test_dst_end(self):
        self._run_test(datetime(2014, 11, 2, 2, tzinfo=timezones.Eastern), 1414911600)

    def test_half_hour_after_dst_end(self):
        self._run_test(datetime(2014, 11, 2, 2, 30, tzinfo=timezones.Eastern), 1414913400)

    def test_one_hour_after_dst_end(self):
        self._run_test(datetime(2014, 11, 2, 3, tzinfo=timezones.Eastern), 1414915200)
