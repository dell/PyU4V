# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
from typing import Any

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)


class EnhancedPerformanceFunctions:
    """Enhanced Functions for retrieving latest diagnostic level
    performance Metrics."""

    def __init__(self, array_id: str, rest_client: Any) -> None:
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id
        self.enhanced_api_version = constants.ENHANCED_API_VERSION

    @staticmethod
    def _build_filter_query(filters: list[str] | None) -> str:
        """Join filter clauses without interpreting their expressions.

        Commas separate clauses; semicolons within membership expressions
        are preserved. Unisphere validates operators and values.

        :param filters: list of filter expressions -- list
        :returns: filter query string or empty string -- str
        """
        if filters:
            return '?filter=' + ','.join(filters)
        return ''

    def _build_metrics_query(self, filters: list[str] | None,
                             all_metrics: bool) -> str:
        """Build category metric query parameters.

        :param filters: list of filter expressions -- list
        :param all_metrics: include all available metrics -- bool
        :returns: category metric query string or empty string -- str
        """
        query = self._build_filter_query(filters)
        if all_metrics:
            query += ('&' if query else '?') + 'metric_type=All'
        return query

    def _perf_uri(self, array_id: str, category: str | None = None) -> str:
        """Construct the performance-categories URI.

        :param array_id: 12 Digit Serial Number of Array -- str
        :param category: optional performance category name -- str
        :returns: URI path -- str
        """
        base = (f"/{self.enhanced_api_version}/systems"
                f"/{array_id}/performance-categories")
        if category:
            return f"{base}/{category}"
        return base

    def _realtime_uri(self, array_id: str, category: str | None = None) -> str:
        """Construct the realtime-categories URI.

        :param array_id: 12 Digit Serial Number of Array -- str
        :param category: optional real-time category name -- str
        :returns: URI path -- str
        """
        base = (f"/{self.enhanced_api_version}/systems"
                f"/{array_id}/realtime-categories")
        if category:
            return f"{base}/{category}"
        return base

    def get_performance_categories_list(
            self, array_id: str | None = None) -> dict[str, Any]:
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
            target_uri=self._perf_uri(array_id),
            resource_type=None)
        if response:
            category_list = response['performance_categories']
        else:
            category_list = []
        return category_list

    def get_all_performance_metrics_for_system(self, array_id=None,
                                               filters=None):
        """Get latest data for all KPI metrics.

        :param array_id: 12 Digit Serial Number of Array -- int
        :param filters: users can filter on the time_range and component id,
                        these can be combined in single query,
                        e.g. filters=['time_range eq 1','id ilike Oracle',
                        'data_format eq Maximum']
                        valid values for time range are 1,2,4,8,12,
                        24 in hours, you can also specify data_format to
                        return Average or Maximum values, note for max
                        values to be retuned you must be registered for
                        realtime statistics. Membership examples:
                        filters=['id in (SG1;SG2)'] includes listed IDs;
                        filters=['id notin (SG1;SG2)'] excludes listed IDs.
                        Each expression must be a string in the list.
                        The same filters are sent to every category -- list
        :returns: data for all available categories for the specified PowerMax
                 Array diagnostic level metrics only, 5 min interval -- dict
        """
        array_id = array_id if array_id else self.array_id
        category_list = self.get_performance_categories_list(
            array_id=array_id)
        full_metric_collection = []
        # Build the optional filter part – empty string when no filters.
        filter_part = self._build_filter_query(filters)
        for category in category_list:
            response = self.common.get_request(
                target_uri=(self._perf_uri(array_id, category['id'])
                            + filter_part),
                resource_type=None)
            if response is not None:
                full_metric_collection.append(response)
        return full_metric_collection

    def get_category_metrics(self, category: str, array_id=None, filters=None,
                             all_metrics=False):
        """Get latest data for KPI metrics for specified performance
        category.

        :param category: performance category name -- str
        :param array_id: 12 Digit Serial Number of Array -- int
        :param filters: users can filter on the time_range and component id,
                        these can be combined in single query,
                        e.g. filters=['time_range eq 1','id ilike Oracle',
                        'data_format eq Maximum']
                        valid values for time range are 1,2,4,8,12,
                        24 in hours, you can also specify data_format to
                        return Average or Maximum values, note for max
                        values to be retuned you must be registered for
                        realtime statistics. Membership examples:
                        filters=['id in (SG1;SG2;SG3)'] includes listed IDs;
                        filters=['id notin (SG1;SG2)'] excludes listed IDs.
                        Values are semicolon-separated inside parentheses.
                        Each expression must be a string in the list;
                        separate clauses are joined with commas.  Note for
                        in notin filters the id is a list of storage groups
                          -- list
        :param all_metrics: when True adds the 'metric_type=All' query
                            parameter to return all available metrics instead
                            of KPI metrics only, default is False -- bool
        :returns: full list of all KPI metrics for latest diagnostic
                 timestamp for the specified array and performance category --
                 dict
        """
        array_id = array_id if array_id else self.array_id
        query_part = self._build_metrics_query(filters, all_metrics)
        response = self.common.get_request(
            target_uri=(self._perf_uri(array_id, category)
                        + query_part),
            resource_type=None)
        return response

    def get_realtime_categories_list(self, array_id=None):
        """Get a list of real-time performance categories.

        :param array_id: 12 Digit Serial Number of Array -- str
        :returns: a list of real-time categories available for querying --
                 list
        """
        array_id = array_id if array_id else self.array_id
        response = self.common.get_request(
            target_uri=self._realtime_uri(array_id),
            resource_type=None)
        if response:
            category_list = response.get('realtime_categories', [])
        else:
            category_list = []
        return category_list

    def get_realtime_category_metrics(self, category, array_id=None,
                                      filters=None, all_metrics=False):
        """Get real-time performance data for a specified category.

        Metrics are collected at a 5-second interval. By default only
        the last available 5-second interval is returned.

        Supported categories: Array, BEDirector, BEPort,
        ExternalDirector, FEDirector, FEPort, RDFDirector, RDFPort,
        StorageGroups.

        :param category: real-time category name -- str
        :param array_id: 12 Digit Serial Number of Array -- str
        :param filters: users can filter on time_range and component id,
                        these can be combined in a single query,
                        e.g. filters=['time_range eq 5', 'id eq OR-1C']
                        valid values for time_range are 1, 5, 10, 15, 30,
                        60 in minutes. Expressions are passed unchanged to
                        Unisphere, which determines supported operators.
                        See get_category_metrics for membership syntax;
                        support must be checked for the real-time endpoint
                        on the installed Unisphere version -- list
        :param all_metrics: when True adds the 'metric_type=All' query
                            parameter to return all available metrics instead
                            of KPI metrics only, default is False -- bool
        :returns: real-time performance data for the specified category --
                 dict
        """
        array_id = array_id if array_id else self.array_id
        query_part = self._build_metrics_query(filters, all_metrics)
        response = self.common.get_request(
            target_uri=(self._realtime_uri(array_id, category)
                        + query_part),
            resource_type=None)
        return response
