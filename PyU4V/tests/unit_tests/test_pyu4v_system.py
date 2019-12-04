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
"""test_pyu4v_system.py."""

import mock
import testtools

from unittest.mock import MagicMock

from PyU4V import common
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants

ARRAY_ID = constants.ARRAY_ID
ARRAY_NUM = constants.ARRAY_NUM
HEALTH = constants.HEALTH
HEALTH_CHECK = constants.HEALTH_CHECK
SG_ID = constants.SG_ID
SG_NUM = constants.SG_NUM
SYMMETRIX = constants.SYMMETRIX
SYSTEM = constants.SYSTEM
TAG = constants.TAG
TAG_NAME = constants.TAG_NAME


class PyU4VSystemTest(testtools.TestCase):
    """Test System."""

    def setUp(self):
        """Setup."""
        super(PyU4VSystemTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.common = self.conn.common
            self.system = self.conn.system

    def test_get_system_health(self):
        """Test get_system_health."""
        health_check_result = self.system.get_system_health()
        self.assertEqual(self.data.array_health, health_check_result)

    def test_list_system_health_check(self):
        """Test list_system_health_checks."""
        health_check_list = self.system.list_system_health_check()
        self.assertEqual(self.data.array_health_check_list, health_check_list)

    def test_get_health_check_details(self):
        """Test get_health_check_details."""
        health_check = self.system.get_health_check_details(health_check_id=1)
        self.assertEqual(self.data.health_check_response, health_check)

    def test_perform_health_check(self):
        """Test perform_health_check."""
        run_test = self.system.perform_health_check()
        self.assertEqual(run_test, self.data.perform_health_check_response)

    def test_delete_health_check(self):
        """Test delete_health_check."""
        common.CommonFunctions.delete_resource = MagicMock(
            side_effect=self.common.delete_resource)
        self.system.delete_health_check(health_check_id=1)
        common.CommonFunctions.delete_resource.assert_called_once_with(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=self.conn.array_id, resource_type=HEALTH,
            resource_type_id=HEALTH_CHECK, object_type=1)

    def test_get_disk_id_list(self):
        """Test get_disk_id_list."""
        disk_list = self.system.get_disk_id_list(failed=True)
        self.assertEqual(self.data.disk_list, disk_list)

    def test_get_disk_details(self):
        """Test get_disk_details."""
        disk_info = self.system.get_disk_details(disk_id='1')
        self.assertEqual(self.data.disk_info, disk_info)

    def test_get_tags(self):
        """Test get_tags."""
        common.CommonFunctions.get_resource = MagicMock(
            side_effect=self.common.get_resource)

        tag_list = self.system.get_tags(
            array_id=self.conn.array_id, tag_name='UNIT-TEST',
            storage_group_id='TEST-SG', num_of_storage_groups=1,
            num_of_arrays=3)

        common.CommonFunctions.get_resource.assert_called_once_with(
            category=SYSTEM, resource_level=TAG, params={
                ARRAY_ID: self.conn.array_id, TAG_NAME: 'UNIT-TEST',
                SG_ID: 'TEST-SG', SG_NUM: '1', ARRAY_NUM: '3'})
        self.assertEqual(self.data.tag_list, tag_list)

    def test_get_tagged_objects(self):
        """Test get_tagged_objects."""
        tagged_objects = self.system.get_tagged_objects(tag_name='UNIT-TEST')
        self.assertEqual(self.data.tagged_objects, tagged_objects)
