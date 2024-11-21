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
"""test_pyu4v_metro_dr.py."""

import testtools

from unittest import mock

from PyU4V import common
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import exception


class PyU4VMetroDRTest(testtools.TestCase):
    """Test MetroDR."""

    def setUp(self):
        """Setup."""
        super(PyU4VMetroDRTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.provisioning = self.conn.provisioning
            self.replication = self.conn.replication
            self.metro_dr = self.conn.metro_dr

    def test_get_metrodr_environment_list(self):
        """Test get_metrodr_environment_list."""
        environment_list = self.metro_dr.get_metrodr_environment_list()
        self.assertIsInstance(environment_list, list)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.metro_dr_detail)
    def test_get_metrodr_environment_details(self, mck_get):
        """Test get_metrodr_environment_details."""
        env_detail = self.metro_dr.get_metrodr_environment_details(
            environment_name='PyU4V_Metro')
        self.assertEqual(pcd.CommonData.metro_dr_detail, env_detail)

    def test_create_metrodr_environment(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'create_resource') as mock_create:
            self.metro_dr.create_metrodr_environment(
                storage_group_name="PyU4V", environment_name='PyU4V',
                metro_r1_array_id='000197800123',
                metro_r2_array_id='000197800124',
                dr_array_id='000197800125', dr_replication_mode='Asynchronous')
            mock_create.assert_called_once()

    def test_create_metrodr_environment_adaptive(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'create_resource') as mock_create:
            self.metro_dr.create_metrodr_environment(
                storage_group_name="PyU4V", environment_name='PyU4V',
                metro_r1_array_id='000197800123',
                metro_r2_array_id='000197800124',
                dr_array_id='000197800125',
                dr_replication_mode='AdaptiveCopyDisk')
            mock_create.assert_called_once()

    def test_create_metrodr_environment_bad_input(self):
        """Test create_metrodr_environment."""
        self.assertRaises(
            exception.InvalidInputException,
            self.metro_dr.create_metrodr_environment,
            storage_group_name="PyU4V", environment_name='PyU4V',
            metro_r1_array_id='000197800123', metro_r2_array_id='000197800124',
            dr_array_id='000197800125', dr_replication_mode='BAD')

    def test_delete_metrodr_environment(self):
        """Test delete_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'delete_resource') as mock_delete:
            self.metro_dr.delete_metrodr_environment(
                environment_name='PyU4V')
            self.metro_dr.delete_metrodr_environment(
                environment_name='PyU4V', metro_r1_array_id='000123456789')
            mock_delete.assert_called()

    def test_convert_to_metrodr_environment(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'create_resource') as mock_create:
            self.metro_dr.convert_to_metrodr_environment(
                storage_group_name="PyU4V", environment_name='PyU4V',
                metro_r1_array_id='000197800123', metro_r2_dr_rdfg=45)
            self.metro_dr.convert_to_metrodr_environment(
                storage_group_name="PyU4V", environment_name='PyU4V',
                metro_r2_dr_rdfg=45)
            mock_create.assert_called()

    def test_modify_metrodr_environment_failover(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'modify_resource') as mock_put:
            self.metro_dr.modify_metrodr_environment(
                action='failover', environment_name='PyU4V')
            mock_put.assert_called_once()

    def test_modify_metrodr_environment_failback(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'modify_resource') as mock_put:
            self.metro_dr.modify_metrodr_environment(
                action='failback', environment_name='PyU4V', metro=True,
                keep_r2=True)
            mock_put.assert_called_once()

    def test_modify_metrodr_environment_bad_action(self):
        """Test create_metrodr_environment."""
        self.assertRaises(
            exception.VolumeBackendAPIException,
            self.metro_dr.modify_metrodr_environment,
            action='Invalid_Action', environment_name='PyU4V')

    def test_modify_metrodr_environment_suspend(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'modify_resource') as mock_put:
            self.metro_dr.modify_metrodr_environment(
                action='suspend', environment_name='PyU4V', metro=True,
                keep_r2=True)
            mock_put.assert_called_once()

    def test_modify_metrodr_environment_establish(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'modify_resource') as mock_put:
            self.metro_dr.modify_metrodr_environment(
                action='establish', environment_name='PyU4V', metro=True,
                _async=True)
            mock_put.assert_called_once()

    def test_modify_metrodr_environment_set_mode(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'modify_resource') as mock_put:
            self.metro_dr.modify_metrodr_environment(
                action='SetMode', environment_name='PyU4V',
                dr_replication_mode='AdaptiveCopyDisk')
            mock_put.assert_called_once()

    def test_modify_metrodr_environment_restore_both(self):
        """Test create_metrodr_environment."""
        self.assertRaises(
            exception.InvalidInputException,
            self.metro_dr.modify_metrodr_environment, action='restore',
            environment_name='PyU4V', metro=True, dr=True)

    def test_modify_metrodr_environment_recover(self):
        """Test create_metrodr_environment."""
        with mock.patch.object(
                self.metro_dr, 'modify_resource') as mock_put:
            self.metro_dr.modify_metrodr_environment(
                action='recover', environment_name='PyU4V')
            mock_put.assert_called_once()
