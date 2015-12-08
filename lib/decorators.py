from functools import wraps

from lib import logging
from flask import request


def require_params(*params):
    def wrap(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            missing_params = [param for param in params if param not in request.params]
            if len(missing_params) > 0:
                message = 'Missing params: {}'.format(', '.join(missing_params))
                # Only respond with an error if this isn't an App Engine task. Tasks will attempt to retry in the event
                # they fail, but this failure is not recoverable, so respond successfully after logging.
                if 'X-AppEngine-TaskName' not in request.headers:
                    logging.info(message)
                    return 'Invalid parameter', 400
                else:
                    return ''

            return fn(self, *args, **kwargs)

        return wrapper

    return wrap


def log_error_after_task_failures(threshold):
    """
    Log at the error level when an app engine task has retried at least 'threshold' times.
    This decorator should only be applied to webapp2.RequestHandler HTTP methods (get(), post(), etc..).
    """

    def wrap(func):
        def wrapper(*args, **kwargs):
            result = None
            exception = False

            try:
                result, status_code = func(*args, **kwargs)
            except Exception:
                exception = True

            # A task can fail with an exception or an error status.
            if exception or not (200 <= status_code <= 299):
                failure_count = int(request.headers.get('X-AppEngine-TaskExecutionCount', 0)) + 1

                if failure_count >= threshold:
                    logging.error('Task has failed {} time(s)'.format(failure_count))

            if exception:
                raise

            return result

        return wrapper

    return wrap
