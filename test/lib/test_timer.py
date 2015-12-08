from freezegun import freeze_time

from test.test_base import TestBase
from lib.timer import Timer


class TimerTest(TestBase):

    def test_timer_manual(self):
        timer = Timer()

        with freeze_time('2012-01-14 03:21:34.100'):
            timer.start()

        with freeze_time('2012-01-14 03:21:34.255'):
            timer.stop()

        self.assertEqual(timer.interval, 155)

    def test_timer_automatic(self):
        timer = Timer()

        with freeze_time('2012-01-14 03:21:34.100'):
            timer.__enter__()

        with freeze_time('2012-01-14 03:21:34.255'):
            timer.__exit__()

        self.assertEqual(timer.interval, 155)
