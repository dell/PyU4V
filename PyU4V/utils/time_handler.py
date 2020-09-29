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
"""time_handler.py"""

import logging
import time

from PyU4V.utils import exception

ONE_YEAR = 365 * 24 * 2600

LOG = logging.getLogger(__name__)


def format_time_input(time_in, return_seconds=False,
                      return_milliseconds=False):
    """Format timestamp as seconds/milliseconds for use in REST requests.

    :param time_in: timestamp -- int/float
    :param return_seconds: return time in seconds -- bool
    :param return_milliseconds: return time in milliseconds -- bool
    :returns: timestamp -- int
    """
    # Validate input params
    if not isinstance(time_in, (int, float)):
        msg = ('Invalid input: {i}, input must be of type int or float, input '
               'is {f}.'.format(i=time_in, f=type(time_in)))
        LOG.error(msg)
        raise exception.InvalidInputException(msg)
    if not any([return_seconds, return_milliseconds]) or (
            all([return_seconds, return_milliseconds])):
        msg = ('Invalid input param selection, one of return_seconds or '
               'return_milliseconds must be True.')
        LOG.error(msg)
        raise exception.InvalidInputException(msg)

    # Determine if the time_in is in format seconds or milliseconds since
    # epoch. We can deduce that it is milliseconds if the time input is greater
    # than the current time in seconds since epoch. There are edge cases,
    # especially if date was derived from a string representation without
    # timezone info, or the clocks are being changed. This is mitigated by
    # applying an offset of one year to the calculation. Millisecond times are
    # an order of magnitude greater so this is safe.
    time_sec, time_milli = False, False
    if time_in > time.time() + ONE_YEAR:
        time_milli = True
    else:
        time_sec = True

    if time_sec and return_milliseconds:
        return int(time_in) * 1000
    elif time_milli and return_seconds:
        return int(time_in) // 1000
    else:
        return int(time_in)
