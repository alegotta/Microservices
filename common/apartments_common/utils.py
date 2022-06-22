import logging
from functools import partial, wraps
from flask import request


# Credits to https://github.com/pallets/flask/issues/1359#issuecomment-477773987
def evaluate_params(response, *params):
    params_dict = {}

    for param in params:
        key = param
        expected_type = str
        default_value = None
        if type(param) is tuple:
            key = param[0]
            expected_type = param[1]
            if len(param) == 3:
                default_value = param[2]

        value = response.args.get(key, default_value)

        if value is None:
            raise ValueError(f"Missing parameter {key}")

        try:
            params_dict[key] = expected_type(value)
        except Exception:
            raise ValueError(f"Wrong format for {key}")

    return params_dict


class HealthCheckFilter(logging.Filter):
    """Filter for logging output"""

    def __init__(self, path, name=''):
        """Class constructor.
        We pass 'path' argument to instance  which is
        used by to filter logging for Flask routes.
        """
        self.path = path
        super().__init__(name)

    def filter(self, record):
        """Main filter function.
        We add a space after path here to ensure subpaths
        are not unintentionally excluded from logging"""
        return f"{self.path} " not in record.getMessage()


def disable_logging(func=None, *args, **kwargs):
    """Disable log messages for werkzeug log handler
    for a specific Flask routes.

    :param (function) func: wrapped function
    :param (list) args: decorator arguments
    :param (dict) kwargs: decorator keyword arguments
    :return (function) wrapped function
    """
    _logger = 'werkzeug'
    if not func:
        return partial(disable_logging, *args, **kwargs)

    @wraps(func)
    def wrapper(*args, **kwargs):
        path = request.environ['PATH_INFO']
        log = logging.getLogger(_logger)
        log.addFilter(HealthCheckFilter(path))
        return func(*args, **kwargs)
    return wrapper
