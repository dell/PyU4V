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
"""workload_planner.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)

# Resource constants
# Resource constants
SYMMETRIX = constants.SYMMETRIX
WLP = constants.WLP
HEADROOM = constants.HEADROOM
GB_HEADROOM = constants.GB_HEADROOM
SRP = constants.SRP
SLO = constants.SLO
WORKLOADTYPE = constants.WORKLOADTYPE


class WLPFunctions(object):

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id

# Workload Planner functions depreciated in this release , please use the
# common functions to make custom API calls to WLP functions.
