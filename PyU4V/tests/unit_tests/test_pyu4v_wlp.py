# Copyright (c) 2019 Dell Inc. or its subsidiaries.
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
"""test_pyu4v_wlp.py."""

import mock
import testtools

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn


class PyU4VUnivmaxWLPTest(testtools.TestCase):
    """Test Unisphere connection."""

    def setUp(self):
        """Setup."""
        super(PyU4VUnivmaxWLPTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.wlp = self.conn.wlp

    def tearDown(self):
        """tearDown."""
        super(PyU4VUnivmaxWLPTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_wlp_info_success(self):
        """Test get_wlp_information success."""
        with mock.patch.object(
                self.wlp.common, 'get_resource',
                return_value=self.data.wlp_info) as mck_wlp_info:
            wlp_info = self.wlp.get_wlp_information(self.data.array)
            self.assertEqual(self.data.wlp_info, wlp_info)
            mck_wlp_info.assert_called_once_with(
                category='wlp', resource_level='symmetrix',
                resource_level_id=self.data.array)

    def test_get_wlp_info_fail(self):
        """Test get_wlp_information fail."""
        with mock.patch.object(self.wlp.common, 'get_resource',
                               return_value=None):
            wlp_info = self.wlp.get_wlp_information(self.data.array)
            self.assertFalse(wlp_info)
            self.assertIsInstance(wlp_info, dict)

    def test_get_headroom_success(self):
        """Test get_headroom success."""
        with mock.patch.object(
                self.wlp.common, 'get_resource',
                return_value=self.data.headroom_array) as mck_head:
            headroom = self.wlp.get_headroom(
                self.data.array, self.data.workload, 'SRP_TEST', 'Gold')
            self.assertEqual(self.data.headroom_array['gbHeadroom'], headroom)
            params = {'srp': 'SRP_TEST', 'slo': 'Gold',
                      'workloadtype': self.data.workload}
            mck_head.assert_called_once_with(
                category='wlp', resource_level='symmetrix',
                resource_level_id=self.data.array, resource_type='headroom',
                params=params)

    def test_get_headroom_fail(self):
        """Test get_headroom fail."""
        with mock.patch.object(self.wlp.common, 'get_resource',
                               return_value=None):
            headroom = self.wlp.get_headroom(self.data.array,
                                             self.data.workload)
            self.assertFalse(headroom)
            self.assertIsInstance(headroom, list)
