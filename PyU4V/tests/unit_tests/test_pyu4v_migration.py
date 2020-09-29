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
"""test_pyu4v_migration.py."""

import testtools

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants


class PyU4VMigrationTest(testtools.TestCase):
    """Test migration."""

    def setUp(self):
        """Setup."""
        super(PyU4VMigrationTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.common = self.conn.common
            self.migration = self.conn.migration

    def tearDown(self):
        """tearDown."""
        super(PyU4VMigrationTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_migration_info(self):
        """Test get_migration_info."""
        migration_info = self.migration.get_migration_info()
        self.assertEqual(self.data.migration_info, migration_info)

    def test_create_migration_environment(self):
        """Test create_migration_environment."""
        with mock.patch.object(
                self.migration, 'create_resource') as mock_create:
            self.migration.create_migration_environment(
                target_array_id=self.data.remote_array)
            self.assertEqual(1, mock_create.call_count)

    def test_delete_migration_environment(self):
        """Test delete_migration_environment."""
        with mock.patch.object(
                self.migration, 'delete_resource') as mock_delete:
            self.migration.delete_migration_environment(
                self.data.remote_array)
            mock_delete.assert_called_once_with(
                category=constants.MIGRATION,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.conn.array_id,
                resource_type=constants.ENVIRONMENT,
                resource_type_id=self.data.remote_array)

    def test_get_array_migration_capabilities(self):
        """Test get_array_migration_capabilities."""
        capabilities = self.migration.get_array_migration_capabilities()
        capabilities_ref = (
            self.data.migration_capabilities['storageArrayCapability'][0])
        self.assertEqual(capabilities_ref, capabilities)

    def test_get_environment_list(self):
        """Test get_environment_list."""
        environment_list = self.migration.get_environment_list()
        env_list_ref = self.data.migration_environment_list['arrayId']
        self.assertEqual(env_list_ref, environment_list)

    def test_get_environment(self):
        """Test get_environment."""
        env_name = self.data.migration_environment_list['arrayId'][0]
        environment_details = self.migration.get_environment(env_name)
        env_details_ref = self.data.migration_environment_details
        self.assertEqual(env_details_ref, environment_details)

    def test_get_storage_group_list(self):
        """Test get_storage_group_list."""
        storage_group_list = self.migration.get_storage_group_list()
        sg_list_ref = self.data.sg_list_migration['name']
        self.assertEqual(sg_list_ref, storage_group_list)

    def test_get_storage_group_list_migration_only_groups(self):
        """Test get_storage_group_list."""
        storage_group_list = self.migration.get_storage_group_list(
            include_migrations=True)
        sg_list_ref = self.data.sg_list_migration['migratingName']
        self.assertEqual(sg_list_ref, storage_group_list)

    def test_get_storage_groups(self):
        """Test get_storage_groups."""
        storage_group_list = self.migration.get_storage_groups()
        sg_info_ref = self.data.sg_list_migration
        self.assertEqual(sg_info_ref, storage_group_list)
        self.assertIsInstance(sg_info_ref, dict)

    def test_get_storage_group(self):
        """Test get_storage_group."""
        sg_name_ref = self.data.sg_list_migration['name'][0]
        storage_group = self.migration.get_storage_group(sg_name_ref)
        self.assertEqual(self.data.sg_details_migration[0], storage_group)

    def test_create_storage_group_migration(self):
        """Test create_storage_group_migration."""
        with mock.patch.object(
                self.migration, 'create_resource') as mock_create:
            self.migration.create_storage_group_migration(
                self.data.storagegroup_name, self.data.remote_array)
            self.assertEqual(1, mock_create.call_count)

    def test_modify_storage_group_migration(self):
        """Test modify_storage_group_migration."""
        with mock.patch.object(self.migration, 'modify_resource') as mock_mod:
            self.migration.modify_storage_group_migration(
                self.data.storagegroup_name, 'Recover')
            mock_mod.assert_called_once()

    def test_delete_storage_group_migration(self):
        """Test delete_storage_group_migration."""
        with mock.patch.object(
                self.migration, 'delete_resource') as mock_delete:
            self.migration.delete_storage_group_migration(
                self.data.storagegroup_name)
            mock_delete.assert_called_once_with(
                category=constants.MIGRATION,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.conn.array_id,
                resource_type=constants.STORAGEGROUP,
                resource_type_id=self.data.storagegroup_name)

    def test_create_storage_group_migration_params(self):
        """Test create_storage_group_migration."""
        with mock.patch.object(
                self.migration, 'create_resource') as mock_create:
            ref_params = dict()
            ref_params['otherArrayId'] = self.data.remote_array
            ref_params['srpId'] = self.data.srp
            ref_params['portGroupId'] = self.data.port_group_name_f
            ref_params['noCompression'] = True
            ref_params['preCopy'] = True
            ref_params['validate'] = True

            self.migration.create_storage_group_migration(
                storage_group_name=self.data.storagegroup_name,
                target_array_id=self.data.remote_array, srp_id=self.data.srp,
                port_group_id=self.data.port_group_name_f, no_compression=True,
                pre_copy=True, validate=True)
            mock_create.assert_called_once_with(
                category=constants.MIGRATION,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.conn.array_id,
                resource_type=constants.STORAGEGROUP,
                resource_type_id=self.data.storagegroup_name,
                payload=ref_params)

    def test_modify_storage_group_migration_params(self):
        """Test modify_storage_group_migration."""
        with mock.patch.object(self.migration, 'modify_resource') as mock_mod:
            ref_options = dict()
            ref_options['action'] = 'LINK'
            ref_options['option'] = 'dummy_option'
            ref_options['executionOption'] = constants.ASYNCHRONOUS

            self.migration.modify_storage_group_migration(
                storage_group_name=self.data.storagegroup_name,
                action='LINK', options={'option': 'dummy_option'}, _async=True)
            mock_mod.assert_called_once_with(
                category=constants.MIGRATION,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.conn.array_id,
                resource_type=constants.STORAGEGROUP,
                resource_type_id=self.data.storagegroup_name,
                payload=ref_options)
