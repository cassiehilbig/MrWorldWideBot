from functools import wraps

from errors import INVALID_PARAMETER
from lib import logging


def require_params(*params):
    def wrap(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            missing_params = [param for param in params if param not in self.params]
            if len(missing_params) > 0:
                message = 'Missing params: {}'.format(', '.join(missing_params))
                # Only respond with an error if this isn't an App Engine task. Tasks will attempt to retry in the event
                # they fail, but this failure is not recoverable, so respond successfully after logging.
                if 'X-AppEngine-TaskName' not in self.request.headers:
                    logging.info(message)
                    self.respond_error(400, INVALID_PARAMETER, message)
                else:
                    logging.error(message)
                return

            return fn(self, *args, **kwargs)

        return wrapper

    return wrap


def log_error_after_task_failures(threshold):
    """
    Log at the error level when an app engine task has retried at least 'threshold' times.
    This decorator should only be applied to webapp2.RequestHandler HTTP methods (get(), post(), etc..).
    """

    def wrap(func):
        def wrapper(self, *args, **kwargs):
            result = None
            exception = False

            try:
                result = func(self, *args, **kwargs)
            except Exception:
                exception = True

            # A task can fail with an exception or an error status.
            if exception or not (200 <= self.response.status_int <= 299):
                failure_count = int(self.request.headers.get('X-AppEngine-TaskExecutionCount', 0)) + 1

                if failure_count >= threshold:
                    logging.error('Task has failed {} time(s)'.format(failure_count))

            if exception:
                raise

            return result

        return wrapper

    return wrap
