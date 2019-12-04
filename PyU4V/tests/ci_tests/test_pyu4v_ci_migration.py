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
"""test_pyu4v_ci_migration.py."""
import testtools

from PyU4V.tests.ci_tests import base
from PyU4V.utils import exception


class CITestMigration(base.TestBaseTestCase, testtools.TestCase):
    """Test Migration."""

    def setUp(self):
        """setUp."""
        super(CITestMigration, self).setUp()
        self.migration = self.conn.migration

    def test_get_migration_info(self):
        """Test get_migration_info."""
        migration_info = self.migration.get_migration_info()
        self.assertEqual(4, len(migration_info.keys()))
        self.assertEqual(self.conn.array_id, migration_info.get('arrayId'))
        self.assertTrue(migration_info.get('local'))
        assert 'migrationSessionCount' in migration_info
        assert 'storageGroupCount' in migration_info

    def test_get_array_migration_capabilities(self):
        """Test get_array_migration_capabilities."""
        array_capabilities = self.migration.get_array_migration_capabilities()
        self.assertTrue(array_capabilities)
        self.assertEqual(6, len(array_capabilities.keys()))
        self.assertEqual(self.conn.array_id, array_capabilities.get('arrayId'))
        assert 'srdfsTarget' in array_capabilities
        assert 'srdfsSource' in array_capabilities
        assert 'dmTarget' in array_capabilities
        assert 'dmSource' in array_capabilities
        assert 'compression' in array_capabilities

    def test_get_environment_list(self):
        """Test get_environment_list."""
        env_migration_list = self.migration.get_environment_list()
        self.assertIsInstance(env_migration_list, list)

    def test_get_environment(self):
        """Test get_environment."""
        do_cleanup = False
        env_migration_list = self.migration.get_environment_list()
        if not env_migration_list:
            self.create_ci_migration_environment()
            env_migration_list = self.migration.get_environment_list()
            do_cleanup = True
        if env_migration_list:
            tgt_array = env_migration_list[0]
            env_details = self.migration.get_environment(tgt_array)
            self.assertTrue(env_details)
            self.assertEqual(4, len(env_details.keys()))
            self.assertEqual(self.conn.array_id,
                             env_details.get('symmetrixId'))
            self.assertEqual(tgt_array, env_details.get('otherSymmetrixId'))
            assert 'invalid' in env_details
            assert 'state' in env_details
            if do_cleanup:
                self.migration.delete_migration_environment(tgt_array)
        else:
            self.skipTest(reason='It is not possible to create an environment')

    def test_get_environment_exception(self):
        """Test get_environment exception."""
        self.assertRaises(exception.ResourceNotFoundException,
                          self.migration.get_environment, 'no_array_id')

    def test_get_storage_group_list(self):
        """Test get_storage_group_list."""
        migrating_storage_groups = self.migration.get_storage_group_list()
        self.assertIsInstance(migrating_storage_groups, list)

    def test_get_storage_group_migrating_list(self):
        """Test get_storage_group_list."""
        migrating_storage_groups = self.migration.get_storage_group_list(
            include_migrations=True)
        self.assertIsInstance(migrating_storage_groups, list)

    def test_get_storage_group_list_all(self):
        """Test get_storage_groups."""
        storage_group_info = self.migration.get_storage_groups()
        self.assertIsInstance(storage_group_info, dict)
        assert 'name' in storage_group_info.keys()
        assert 'migratingName' in storage_group_info.keys()

    def test_create_delete_migration_environment(self):
        """Test create_migration_environment & delete_migration_environment."""
        migration_env = self.create_ci_migration_environment()
        tgt_array = migration_env.get('arrayId')
        assert tgt_array in self.migration.get_environment_list()
        self.migration.delete_migration_environment(tgt_array)
        assert tgt_array not in self.migration.get_environment_list()
