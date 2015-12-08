import mock
import json

from lib.utils import server_url, partition, error_response
from test.test_base import TestBase


class UtilsTest(TestBase):
    def test_server_url_none(self):
        self.assertEqual(server_url(), 'http://localhost:8080')

    @mock.patch('lib.utils.is_debug', return_value=False)
    def test_server_url_production(self, is_debug):
        self.assertEqual(server_url(), 'https://bot-dashboard.appspot.com')

    def test_partition_empty_list(self):
        self.assertListEqual(partition([], 5), [])

    def test_partition_list_length_not_divisible_by_size(self):
        self.assertListEqual(partition([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])

    def test_partition_list_length_divisble_by_size(self):
        self.assertListEqual(partition([1, 2, 3, 4, 5, 6], 2), [[1, 2], [3, 4], [5, 6]])

    def test_error_response_with_message(self):
        self.assertEqual(error_response(123, 'code', 'msg'), (json.dumps({'error': 'code', 'message': 'msg'}), 123))

    def test_error_response_no_message(self):
        self.assertEqual(error_response(123, 'code'), (json.dumps({'error': 'code', 'message': None}), 123))
