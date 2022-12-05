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
"""test_pyu4v_clone.py."""

import testtools

from unittest import mock

from PyU4V import common
from PyU4V import clone
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import exception


class PyU4VcloneTest(testtools.TestCase):
    """Test clone functions."""

    def setUp(self):
        """Setup."""
        super(PyU4VcloneTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.provisioning = self.conn.provisioning
            self.clone = self.conn.clone
            self.common = univmax_conn.CommonFunctions

    def tearDown(self):
        """tearDown."""
        super(PyU4VcloneTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.clone_target_sg_list)
    def test_get_clone_target_storage_group_list(self, patch_get):
        """test_get_clone_target_storage_group_list. """
        target_sg_list = self.clone.get_clone_target_storage_group_list(
            storage_group_id="PYU4V")
        self.assertEqual(
            pcd.CommonData.clone_target_sg_list.get(
                "clone_target_sg_names"), target_sg_list)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.clone_pairs_list)
    def test_get_clone_pairs_list(self, patch_get):
        """test_get_clone_pairs_list. """
        clone_pairs_list = self.clone.get_clone_pairs_list(
            storage_group_id="PYU4V_SG")
        self.assertEqual(
            pcd.CommonData.clone_pairs_list, clone_pairs_list)
    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.clone_target_get)
    def test_get_clone_storage_group_pair_details(self, patch_get):
        clone_pair_details = self.clone.get_clone_storage_group_pair_details(
            storage_group_id="PyU4V_SG", target_storage_group_id="PYU4v_TGT_SG"
        )
        self.assertEqual(pcd.CommonData.clone_target_get, clone_pair_details)

    def test_create_clone(self):
        with mock.patch.object(
                self.common, 'create_resource') as mock_create:
            self.clone.create_clone(
                storage_group_id="PyU4V_SG",
                target_storage_group_id="PyU4V_TGT_SG")
            mock_create.assert_called_once()

    def test_terminate_clone(self):
        with mock.patch.object(
                self.common, 'delete_resource') as mock_delete:
            self.clone.terminate_clone(storage_group_id="PyU4V_SG",
                                   target_storage_group_id="PYU4V_SG_SG")
            mock_delete.assert_called_once()

    def test_establish_clone(self):
        with mock.patch.object(
                self.common, 'modify_resource') as mock_modify:
            self.clone.establish_clone(
                storage_group_id="PyU4V_SG",
                target_storage_group_id="PyU4V_TGT_SG", _async=True)
            mock_modify.assert_called_once()
    def test_restore_clone(self):
        with mock.patch.object(
                self.common, 'modify_resource') as mock_modify:
            self.clone.restore_clone(
                storage_group_id="PyU4V_SG",
                target_storage_group_id="PyU4V_TGT_SG", _async=True)

            mock_modify.assert_called_with(
                target_uri=(
                    '/100/replication/symmetrix/000197800123/storagegroup/'
                    'PyU4V_SG/clone/storagegroup/PyU4V_TGT_SG'),
                resource_type=None, payload={
                    'action': 'Restore',
                    'restore': {'force': False, 'star': False},
                    'executionOption': 'ASYNCHRONOUS'})

    def test_split_clone(self):
        with mock.patch.object(
                self.common, 'modify_resource') as mock_modify:
            self.clone.split_clone(
                storage_group_id="PyU4V_SG",
                target_storage_group_id="PyU4V_TGT_SG", _async=True)
            mock_modify.assert_called_with(
                target_uri=(
                    '/100/replication/symmetrix/000197800123/storagegroup/'
                    'PyU4V_SG/clone/storagegroup/PyU4V_TGT_SG'),
                resource_type=None,
                payload={'action': 'Split',
                         'split': {'force':
                                       False, 'star': False,
                                   'skip': False},
                         'executionOption': 'ASYNCHRONOUS'})
