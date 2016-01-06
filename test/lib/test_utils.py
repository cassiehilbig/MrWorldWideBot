import json

from test.test_base import TestBase
from lib.utils import partition, error_response


class UtilsTest(TestBase):
    def test_partition_empty_list(self):
        self.assertListEqual(partition([], 5), [])

    def test_partition_list_length_not_divisible_by_size(self):
        self.assertListEqual(partition([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])

    def test_partition_list_length_divisble_by_size(self):
        self.assertListEqual(partition([1, 2, 3, 4, 5, 6], 2), [[1, 2], [3, 4], [5, 6]])

    def test_error_response_with_message(self):
        self.assertEqual(error_response(123, 'msg'), (json.dumps({'message': 'msg'}), 123))

    def test_error_response_no_message(self):
        self.assertEqual(error_response(123), (json.dumps({'message': None}), 123))
