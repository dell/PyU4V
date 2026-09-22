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
"""test_pyu4v_ci_storage_groups.py."""
import testtools

from unittest import mock
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn


class PyU4VPerformanceEnhancedTest(testtools.TestCase):

    def setUp(self):
        """SetUp."""
        super(PyU4VPerformanceEnhancedTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.performace_enhanced = self.conn.performance_enhanced
            self.common = univmax_conn.CommonFunctions

    def tearDown(self):
        """tearDown."""
        super(PyU4VPerformanceEnhancedTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_performance_categories_list(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_performance_categories_list()
        mock_get.assert_called()

    def test_get_all_performance_metrics_for_system(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_all_performance_metrics_for_system()
        mock_get.assert_called()

    def test_get_category_metrics(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_category_metrics(category='Array')
        mock_get.assert_called()

    def test_get_category_metrics_all_metrics_true(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_category_metrics(
                category='Array', all_metrics=True)
        expected_uri = (
            f'/v1/systems/{self.data.array}/performance-categories/Array'
            '?metric_type=All')
        mock_get.assert_called_once_with(
            target_uri=expected_uri, resource_type=None)

    def test_get_category_metrics_all_metrics_with_existing_filters(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_category_metrics(
                category='Array', filters=['time_range eq 1'],
                all_metrics=True)
        expected_uri = (
            f'/v1/systems/{self.data.array}/performance-categories/Array'
            '?filter=time_range eq 1&metric_type=All')
        mock_get.assert_called_once_with(
            target_uri=expected_uri, resource_type=None)

    def test_get_category_metrics_all_metrics_false(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_category_metrics(
                category='Array', all_metrics=False)
        call_args = mock_get.call_args
        target_uri = call_args[1].get(
            'target_uri', call_args[0][0] if call_args[0] else '')
        self.assertNotIn('metric_type', target_uri)

    def test_get_realtime_categories_list(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_realtime_categories_list()
        mock_get.assert_called()

    def test_get_realtime_category_metrics(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_realtime_category_metrics(
                category='Array')
        mock_get.assert_called()

    def test_get_realtime_category_metrics_all_metrics_true(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_realtime_category_metrics(
                category='Array', all_metrics=True)
        expected_uri = (
            f'/v1/systems/{self.data.array}/realtime-categories/Array'
            '?metric_type=All')
        mock_get.assert_called_once_with(
            target_uri=expected_uri, resource_type=None)

    def test_get_realtime_category_metrics_with_filters(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_realtime_category_metrics(
                category='Array', filters=['time_range eq 5'],
                all_metrics=True)
        expected_uri = (
            f'/v1/systems/{self.data.array}/realtime-categories/Array'
            '?filter=time_range eq 5&metric_type=All')
        mock_get.assert_called_once_with(
            target_uri=expected_uri, resource_type=None)

    def test_get_realtime_category_metrics_all_metrics_false(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.performace_enhanced.get_realtime_category_metrics(
                category='FEDirector', all_metrics=False)
        call_args = mock_get.call_args
        target_uri = call_args[1].get(
            'target_uri', call_args[0][0] if call_args[0] else '')
        self.assertNotIn('metric_type', target_uri)
