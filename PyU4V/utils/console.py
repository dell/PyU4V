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
"""console.py"""

import logging

from PyU4V.utils import decorators

LOG = logging.getLogger(__name__)


@decorators.deprecation_notice('utils', 9.1, 10.0)
def choose_from_list(query_category, query_list):
    """Choose an item from a list.

    DEPRECATION NOTICE: utils.console.choose_from_list() will be deprecated
    in PyU4V version 10.0. For further information please consult PyU4V 9.1
    release notes.

    :param query_category: query category e.g. snapshot -- str
    :param query_list: query selection options -- list
    :returns: user selection -- str
    """
    print('Choose the {cat} you want from the below list:'.format(
        cat=query_category))
    for counter, value in enumerate(query_list):
        print('{counter}: {value}'.format(counter=counter, value=value))
    selection = input('Choice: ')
    return query_list[int(selection)]
