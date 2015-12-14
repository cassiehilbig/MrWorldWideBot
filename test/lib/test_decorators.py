import mock

from test.test_base import TestBase
from lib.decorators import require_params, log_error_after_task_failures
from app import app


REQUIRED_PARAMS = ('aparam', 'bparam', 'cparam')


@app.route('/test/require_params', methods=['POST'])
@require_params(*REQUIRED_PARAMS)
def params_required():
    return ''


@app.route('/test/log_error_success', methods=['POST'])
@log_error_after_task_failures(2)
def log_error_after_failures_success():
    return ''


@app.route('/test/log_error_failure', methods=['POST'])
@log_error_after_task_failures(2)
def log_error_after_failures_500():
    return '', 500


@app.route('/test/log_error_exception', methods=['POST'])
@log_error_after_task_failures(2)
def log_error_after_failures_exception():
    raise Exception('opps')


class DecoratorsTest(TestBase):
    def setUp(self):
        super(self.__class__, self).setUp()

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_below_threshold_success(self, logging):
        self.api_call('post', '/test/log_error_success', headers={'X-AppEngine-TaskExecutionCount': '0'}, status=200)
        self.assertEqual(logging.call_count, 0)

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_at_threshold_success(self, logging):
        self.api_call('post', '/test/log_error_success', headers={'X-AppEngine-TaskExecutionCount': '1'}, status=200)
        self.assertEqual(logging.call_count, 0)

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_over_threshold_success(self, logging):
        self.api_call('post', '/test/log_error_success', headers={'X-AppEngine-TaskExecutionCount': '2'}, status=200)
        self.assertEqual(logging.call_count, 0)

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_below_threshold_failure(self, logging):
        self.api_call('post', '/test/log_error_failure', headers={'X-AppEngine-TaskExecutionCount': '0'}, status=500)
        self.assertEqual(logging.call_count, 0)

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_at_threshold_failure(self, logging):
        self.api_call('post', '/test/log_error_failure', headers={'X-AppEngine-TaskExecutionCount': '1'}, status=500)
        self.assertEqual(logging.call_count, 1)
        self.assertEqual(logging.call_args_list[0][0][0], 'Task has failed 2 time(s)')

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_above_threshold_failure(self, logging):
        self.api_call('post', '/test/log_error_failure', headers={'X-AppEngine-TaskExecutionCount': '3'}, status=500)
        self.assertEqual(logging.call_count, 1)
        self.assertEqual(logging.call_args_list[0][0][0], 'Task has failed 4 time(s)')

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_below_threshold_exception(self, logging):
        self.api_call('post', '/test/log_error_exception', headers={'X-AppEngine-TaskExecutionCount': '0'}, status=500)
        self.assertEqual(logging.call_count, 1)

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_at_threshold_exception(self, logging):
        self.api_call('post', '/test/log_error_exception', headers={'X-AppEngine-TaskExecutionCount': '1'}, status=500)
        self.assertEqual(logging.call_count, 2)
        self.assertEqual(logging.call_args_list[0][0][0], 'Task has failed 2 time(s)')

    @mock.patch('lib.logging.error')
    def test_log_error_after_task_failures_threshold_above_threshold_exception(self, logging):
        self.api_call('post', '/test/log_error_exception', headers={'X-AppEngine-TaskExecutionCount': '3'}, status=500)
        self.assertEqual(logging.call_count, 2)
        self.assertEqual(logging.call_args_list[0][0][0], 'Task has failed 4 time(s)')

    def test_require_params_success(self):
        body = {param: 'Some value' for param in REQUIRED_PARAMS}
        self.api_call('post', '/test/require_params', data=body, status=200)

    def test_require_params_failure_missing_all(self):
        j = self.api_call('post', '/test/require_params', status=400).json

        self.assertEqual(j, {
            'message': 'Missing params: {}'.format(', '.join(REQUIRED_PARAMS))
        })

    def test_require_params_failure_missing_one(self):
        for param in REQUIRED_PARAMS:
            sent_params = [p for p in REQUIRED_PARAMS if p is not param]
            body = {param: 'Some value' for param in sent_params}
            j = self.api_call('post', '/test/require_params', data=body, status=400).json
            self.assertEqual(j, {
                'message': 'Missing params: {}'.format(param)
            })

    def test_require_params_success_is_task(self):
        headers = {'X-AppEngine-TaskName': 'some-task'}
        body = {param: 'Some value' for param in REQUIRED_PARAMS}
        self.api_call('post', '/test/require_params', data=body, headers=headers, status=200)

    def test_require_params_failure_is_task_missing_all(self):
        headers = {'X-AppEngine-TaskName': 'some-task'}
        self.api_call('post', '/test/require_params', headers=headers, status=200)

    def test_require_params_failures_missing_one(self):
        headers = {'X-AppEngine-TaskName': 'some-task'}
        for param in REQUIRED_PARAMS:
            sent_params = [p for p in REQUIRED_PARAMS if p is not param]
            body = {param: 'Some value' for param in sent_params}
            self.api_call('post', '/test/require_params', data=body, headers=headers, status=200)
