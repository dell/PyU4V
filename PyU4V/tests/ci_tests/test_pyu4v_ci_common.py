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
"""test_pyu4v_ci_common.py."""

import re
import testtools

from unittest.mock import MagicMock

from PyU4V import common
from PyU4V.tests.ci_tests import base
from PyU4V.utils import constants

UNISPHERE_VERSION = constants.UNISPHERE_VERSION


class CITestCommon(base.TestBaseTestCase, testtools.TestCase):
    """Test Common."""

    def setUp(self):
        """setUp."""
        super(CITestCommon, self).setUp()
        self.common = self.conn.common
        self.provision = self.conn.provisioning

    def test_common_for_create_volume(self):
        """Test methods used by create volume operation.

        Test wait_for_job_complete is called
        Test get_job_by_id is called
        Test _is_job_finished is called
        Test check_status_code_success is called
        Test wait_for_job is called
        Test _build_uri is called
        Test get_request is called
        Test _build_uri_get_version is called
        Test get_resource is NOT called
        """
        common.CommonFunctions.wait_for_job_complete = MagicMock(
            side_effect=self.common.wait_for_job_complete)
        common.CommonFunctions.get_job_by_id = MagicMock(
            side_effect=self.common.get_job_by_id)
        common.CommonFunctions._is_job_finished = MagicMock(
            side_effect=self.common._is_job_finished)
        common.CommonFunctions.check_status_code_success = MagicMock(
            side_effect=self.common.check_status_code_success)
        common.CommonFunctions.wait_for_job = MagicMock(
            side_effect=self.common.wait_for_job)
        common.CommonFunctions._build_uri = MagicMock(
            side_effect=self.common._build_uri)
        common.CommonFunctions.get_request = MagicMock(
            side_effect=self.common.get_request)
        common.CommonFunctions._build_uri_get_version = MagicMock(
            side_effect=self.common._build_uri_get_version)
        common.CommonFunctions.get_resource = MagicMock(
            side_effect=self.common.get_resource)

        self.create_volume()

        common.CommonFunctions.wait_for_job_complete.assert_called()
        common.CommonFunctions.get_job_by_id.assert_called()
        common.CommonFunctions._is_job_finished.assert_called()
        common.CommonFunctions.check_status_code_success.assert_called()
        common.CommonFunctions.wait_for_job.assert_called()
        common.CommonFunctions._build_uri.assert_called()
        common.CommonFunctions.get_request.assert_called()
        common.CommonFunctions._build_uri_get_version.assert_called()
        common.CommonFunctions.get_resource.assert_called()

    def test_common_for_modify_host(self):
        """"Test methods used by create host operation.

        Test create_resource is called
        Test modify_resource is called
        """
        self.conn.provisioning.create_resource = MagicMock(
            side_effect=self.common.create_resource)
        self.conn.provisioning.modify_resource = MagicMock(
            side_effect=self.common.modify_resource)
        self.modify_host()
        self.conn.provisioning.create_resource.assert_called()
        self.conn.provisioning.modify_resource.assert_called()

    def test_get_uni_version(self):
        """Test get_uni_version."""
        version, major_version = self.common.get_uni_version()
        major = (UNISPHERE_VERSION[0] + UNISPHERE_VERSION[1] + '.'
                 + UNISPHERE_VERSION[2])
        self.assertTrue(re.match(r'^T|X|V' + major + r'\S+$', version))
        self.assertEqual(UNISPHERE_VERSION, major_version)

    def test_get_array_list(self):
        """Test get_array_list."""
        array_list = self.common.get_array_list()
        self.assertIsInstance(array_list, list)
        self.assertIn(self.conn.array_id, array_list)

    def test_get_v3_or_newer_array_list(self):
        """Test get_v3_or_newer_array_list."""
        array_list = self.common.get_v3_or_newer_array_list()
        self.assertIsInstance(array_list, list)
        self.assertIn(self.conn.array_id, array_list)

    def test_get_array(self):
        """Test get_array."""
        array = self.common.get_array(self.conn.array_id)
        self.assertEqual(self.conn.array_id, array['symmetrixId'])

    def test_get_iterator_results(self):
        """Test get_iterator_results."""
        if self.conn.performance.is_array_diagnostic_performance_registered():
            start_time, end_time = (
                self.conn.performance.extract_timestamp_keys(
                    category='Array'))
            result = self.conn.performance.get_array_stats(
                metrics='PercentReads', start_time=start_time,
                end_time=end_time)
            self.assertTrue(result)
            self.assertIsInstance(result, dict)
            if result and len(result.get('result')) <= 1000:
                self.skipTest(
                    'Skipping test_get_iterator_results because there is not '
                    'enough performance data collected. It takes just under '
                    'four days to build up enough data to return more than '
                    '1000 performance results. There are currently only {cnt} '
                    'performance intervals available'.format(
                        cnt=len(result.get('result'))))
            else:
                self.assertTrue(len(result.get('result')) > 1000)
        else:
            self.skipTest('Skipping test_get_iterator_results because array '
                          'is not registered for performance metrics which '
                          'are required for this test.')

    def test_is_array_v4(self):
        """Test get_array."""
        if self.common.is_array_v4(self.conn.array_id):
            self.assertTrue(self.common.is_array_v4(self.conn.array_id))
