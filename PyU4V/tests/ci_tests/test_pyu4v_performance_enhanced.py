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
"""test_pyu4v_ci_storage_groups.py."""
import testtools

from PyU4V.tests.ci_tests import base


class CITestPerformanceEnhanced(base.TestBaseTestCase, testtools.TestCase):

    def setUp(self):
        """SetUp."""
        super(CITestPerformanceEnhanced, self).setUp()
        self.performance_enhanced = self.conn.performance_enhanced

    def test_get_performance_categories_list(self):
        categories = (
            self.performance_enhanced.get_performance_categories_list())
        self.assertIn('metrics', categories[0])
        self.assertIn('id', categories[0])

    def test_get_all_performance_metrics_for_system(self):
        metrics = (
            self.performance_enhanced.get_all_performance_metrics_for_system())
        self.assertIn('id', metrics[0])
        self.assertIn('metric_instances', metrics[0])

    def test_get_category_metrics(self):
        category_metrics = self.performance_enhanced.get_category_metrics(
            category='Array')
        self.assertIn('HostIOs', category_metrics['metric_instances'][0][
            'metrics'][0])

    def test_get_category_metrics_with_filters(self):
        category_metrics = self.performance_enhanced.get_category_metrics(
            category='Array', filters=["time_range eq 1"])
        self.assertIn('HostIOs', category_metrics['metric_instances'][0][
            'metrics'][0])
        self.assertGreater(len(category_metrics['metric_instances'][0][
            'metrics']), 1)
