# Copyright (c) 2023 Dell Inc. or its subsidiaries.
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
"""performance_enhanced.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)


class EnhancedPerformanceFunctions(object):
    """Enhanced Functions for retrieving latest diagnostic level
    performance Metrics."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.array_id = array_id
        self.enhanced_api_version = constants.ENHANCED_API_VERSION

    def get_performance_categories_list(self, array_id=None):
        """Get a list of performance categories and metrics that will be
        returned for each category.

        :param array_id: 12 Digit Serial Number of Array -- int
        :returns: a list of categories available for querying, returned list
                 has dictionary of category represented by 'id' key and
                 'metrics' key detailing what will be returned for the given
                 array represented by 'system' key -- list
        """
        array_id = array_id if array_id else self.array_id
        response = self.common.get_request(
            target_uri=f"/{self.enhanced_api_version}/systems"
                       f"/{array_id}/performance-categories",
            resource_type=None)
        if response:
            category_list = response['performance_categories']
        else:
            category_list = []
        return category_list

    def get_all_performance_metrics_for_system(self, array_id=None):
        """Get latest data for all KPI metrics.

        :param array_id: 12 Digit Serial Number of Array -- int
        :returns: data for all available categories for the specified PowerMax
                 Array diagnostic level metrics only, 5 min interval -- dict
        """
        array_id = array_id if array_id else self.array_id
        category_list = self.get_performance_categories_list(array_id=array_id)
        full_metric_collection = []
        for category in category_list:
            response = self.common.get_request(
                target_uri=f"/{self.enhanced_api_version}/systems"
                           f"/{array_id}/performance-categories/"
                           f"{category['id']}",
                resource_type=None)
            if response is not None:
                full_metric_collection.append(response)
        return full_metric_collection

    def get_category_metrics(self, category, array_id=None):
        """Get latest data for KPI metrics for specificied performance
        category.

        :param array_id: 12 Digit Serial Number of Array -- int
        :returns: full list of all KPI metrics for latest diagnostic
                 timestamp for the specified array and performance category --
                 dict
        """
        array_id = array_id if array_id else self.array_id
        response = self.common.get_request(
            target_uri=f"/{self.enhanced_api_version}/systems"
                       f"/{array_id}/performance-categories/"
                       f"{category}",
            resource_type=None)
        return response
