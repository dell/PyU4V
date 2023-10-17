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
from PyU4V.utils import decorators

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

    @decorators.deprecation_notice(
        'get_wlp_information', 10.1, 10.3)
    def get_wlp_information(self, array_id):
        """Get the latest timestamp from WLP for processing New Workloads.

        :param array_id: array id -- str
        :returns: wlp details -- dict
        """
        response = self.common.get_resource(
            category=WLP, resource_level=SYMMETRIX,
            resource_level_id=array_id)
        return response if response else dict()

    @decorators.deprecation_notice(
        'get_headroom', 10.1, 10.3)
    def get_headroom(self, array_id, workload=None, srp=None, slo=None):
        """Get the Remaining Headroom Capacity.

        Get the headroom capacity for a given srp/ slo/ workload combination.

        :param array_id: array id -- str
        :param workload: the workload type -- str
        :param srp: storage resource pool id -- str
        :param slo: service level id -- str
        :returns: headroom details -- dict
        """
        params = dict()
        if srp:
            params[SRP] = srp
        if slo:
            params[SLO] = slo
        if workload:
            params[WORKLOADTYPE] = workload

        response = self.common.get_resource(
            category=WLP,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=HEADROOM, params=params)
        return response.get(GB_HEADROOM, list()) if response else list()

    @decorators.deprecation_notice(
        'get_capabilities', 10.1, 10.3)
    def get_capabilities(self, array_id=None):
        """Generate WLP capability list for each WLP authorized array.

        :param array_id: array id -- str
        :returns: array WLP capabilities -- list
        """
        return_response = list()
        response = self.common.get_resource(
            category=WLP, resource_level='capabilities',
            resource_type=SYMMETRIX)
        if array_id:
            for wlp_info in response.get('symmetrixCapability'):
                if wlp_info.get('symmetrixId') == array_id:
                    return_response = [wlp_info]
                    break
        else:
            return_response = response.get('symmetrixCapability', list())

        return return_response
