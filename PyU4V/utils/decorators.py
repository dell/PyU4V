# Copyright (c) 2020 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""decorators.py"""

import logging
import time

from functools import wraps

LOG = logging.getLogger('PyU4V.action_required')


def deprecation_notice(func_class, start_version, end_version):
    """Notify the user of function deprecation in a future version.

    :param func_class: the class name for deprecated function -- str
    :param start_version: the start Unisphere version -- float
    :param end_version: the end Unisphere version -- float
    :returns: decorated function -- decorator
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            LOG.warning(
                '{func_class}.{func} will be deprecated in version {end}. For '
                'further information please consult PyU4V {start} release '
                'notes.'.format(
                    func_class=func_class, func=func.__name__, end=end_version,
                    start=start_version))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def refactoring_notice(func_class, path, start_version, end_version):
    """Notify the user of function refactoring elsewhere in PyU4V.

    :param func_class: the class name for deprecated function -- str
    :param path: path to the new function -- str
    :param start_version: the start Unisphere version -- float
    :param end_version: the end Unisphere version -- float
    :returns: decorated function -- decorator
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            LOG.warning(
                '{func_class}.{func} will be deprecated in version {end} in '
                'favour of function {path}. For further information please '
                'consult PyU4V {start} release notes.'.format(
                    func_class=func_class, func=func.__name__, end=end_version,
                    path=path, start=start_version))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def retry(exceptions, total_attempts=3, delay=3, backoff=2):
    """Decorator for retrying function calls.

    :param exceptions: expected exceptions to retry on -- class or tuple
    :param total_attempts: times to run function before failure. -- int
    :param delay: initial delay between retries in seconds. -- int
    :param backoff: delay multiplier between each attempt -- int
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            _tries = total_attempts
            _delay = delay
            while _tries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = ('{f_name} failed due to exception {e}, Retrying '
                           'in {delay} seconds.'
                           ''.format(f_name=f.__name__, e=e, delay=_delay))
                    LOG.warning(msg)
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry
