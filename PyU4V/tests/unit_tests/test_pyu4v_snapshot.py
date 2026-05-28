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
"""test_pyu4v_snapshot.py."""

import testtools

from unittest import mock

from PyU4V import common
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn


class PyU4VSnapshotTest(testtools.TestCase):
    """Test snapshot module."""

    def setUp(self):
        """Setup."""
        super(PyU4VSnapshotTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.snapshot = self.conn.snapshot

    def tearDown(self):
        """tearDown."""
        super(PyU4VSnapshotTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_snapshot_module_accessible(self):
        """Test that snapshot module is accessible via conn.snapshot."""
        self.assertIsNotNone(self.snapshot)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'name': ['snap1', 'snap2']})
    def test_get_storage_group_snapshot_list(self, mck_get):
        """Test get_storage_group_snapshot_list."""
        snap_list = self.snapshot.get_storage_group_snapshot_list('test_sg')
        self.assertEqual(['snap1', 'snap2'], snap_list)

    @mock.patch.object(common.CommonFunctions, 'create_resource',
                       return_value={'snapshotName': 'test_snap'})
    def test_create_storage_group_snapshot(self, mck_create):
        """Test create_storage_group_snapshot."""
        result = self.snapshot.create_storage_group_snapshot(
            'test_sg', 'test_snap')
        self.assertEqual({'snapshotName': 'test_snap'}, result)

    @mock.patch.object(common.CommonFunctions, 'create_resource',
                       return_value={'snapshotName': 'test_snap'})
    def test_create_storage_group_snapshot_with_ttl(self, mck_create):
        """Test create_storage_group_snapshot with TTL."""
        result = self.snapshot.create_storage_group_snapshot(
            'test_sg', 'test_snap', ttl='1', hours=True)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'generations': [0, 1, 2]})
    def test_get_storage_group_snapshot_generation_list(self, mck_get):
        """Test get_storage_group_snapshot_generation_list."""
        gen_list = self.snapshot.get_storage_group_snapshot_generation_list(
            'test_sg', 'snap1')
        self.assertEqual([0, 1, 2], gen_list)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'snapids': [100, 101, 102]})
    def test_get_storage_group_snapshot_snap_id_list(self, mck_get):
        """Test get_storage_group_snapshot_snap_id_list."""
        snap_ids = self.snapshot.get_storage_group_snapshot_snap_id_list(
            'test_sg', 'snap1')
        self.assertEqual([100, 101, 102], snap_ids)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'generation': 0, 'state': 'Established'})
    def test_get_snapshot_generation_details(self, mck_get):
        """Test get_snapshot_generation_details."""
        details = self.snapshot.get_snapshot_generation_details(
            'test_sg', 'snap1', 0)
        self.assertEqual(0, details['generation'])

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'snapid': 100, 'state': 'Established'})
    def test_get_snapshot_snap_id_details(self, mck_get):
        """Test get_snapshot_snap_id_details."""
        details = self.snapshot.get_snapshot_snap_id_details(
            'test_sg', 'snap1', 100)
        self.assertEqual(100, details['snapid'])

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_modify_storage_group_snapshot(self, mck_modify):
        """Test modify_storage_group_snapshot."""
        result = self.snapshot.modify_storage_group_snapshot(
            'src_sg', 'tgt_sg', 'snap1', link=True)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_modify_storage_group_snapshot_by_snap_id(self, mck_modify):
        """Test modify_storage_group_snapshot_by_snap_id."""
        result = self.snapshot.modify_storage_group_snapshot_by_snap_id(
            'src_sg', 'tgt_sg', 'snap1', 100, link=True)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_restore_snapshot(self, mck_modify):
        """Test restore_snapshot."""
        result = self.snapshot.restore_snapshot('test_sg', 'snap1')
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_restore_snapshot_by_snap_id(self, mck_modify):
        """Test restore_snapshot_by_snap_id."""
        result = self.snapshot.restore_snapshot_by_snap_id(
            'test_sg', 'snap1', 100)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_rename_snapshot(self, mck_modify):
        """Test rename_snapshot."""
        result = self.snapshot.rename_snapshot(
            'test_sg', 'snap1', 'snap1_renamed')
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'delete_resource')
    def test_delete_storage_group_snapshot(self, mck_delete):
        """Test delete_storage_group_snapshot."""
        self.snapshot.delete_storage_group_snapshot('test_sg', 'snap1')
        mck_delete.assert_called_once()

    @mock.patch.object(common.CommonFunctions, 'delete_resource')
    def test_delete_storage_group_snapshot_by_snap_id(self, mck_delete):
        """Test delete_storage_group_snapshot_by_snap_id."""
        self.snapshot.delete_storage_group_snapshot_by_snap_id(
            'test_sg', 'snap1', 100)
        mck_delete.assert_called_once()

    @mock.patch.object(common.CommonFunctions, 'delete_resource')
    def test_bulk_terminate_snapshots(self, mck_delete):
        """Test bulk_terminate_snapshots."""
        self.snapshot.bulk_terminate_snapshots(
            'test_sg', 'snap1', terminate_all_snapshots=True)
        mck_delete.assert_called_once()

    def test_delegation_from_replication(self):
        """Test that replication module delegates to snapshot module."""
        replication = self.conn.replication
        with mock.patch.object(
                common.CommonFunctions, 'get_request',
                return_value={'name': ['snap1']}):
            result = replication.get_storage_group_snapshot_list('test_sg')
            self.assertEqual(['snap1'], result)
