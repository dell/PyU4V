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
"""test_pyu4v_ci_snapshot.py."""
import testtools
import time

from PyU4V.tests.ci_tests import base


class CITestSnapshot(base.TestBaseTestCase, testtools.TestCase):
    """Test Snapshot Functions via conn.snapshot module."""

    def setUp(self):
        """SetUp."""
        super(CITestSnapshot, self).setUp()
        self.snapshot = self.conn.snapshot
        self.srdf = self.conn.srdf
        self.replication = self.conn.replication
        self.provisioning = self.conn.provisioning
        self.system = self.conn.system
        self.is_v4 = self.common.is_array_v4(self.conn.array_id)

    # -------------------------------------------------------------------------
    # General replication methods (remain in replication.py)
    # -------------------------------------------------------------------------

    def test_get_array_replication_capabilities(self):
        """Test get_array_replication_capabilities."""
        rep_info = self.replication.get_array_replication_capabilities(
            array_id=self.conn.array_id)
        self.assertEqual(9, len(rep_info.keys()))
        assert 'symmetrixId' in rep_info
        assert 'snapVxCapable' in rep_info
        assert 'rdfCapable' in rep_info
        assert 'witness_capable' in rep_info
        assert 'virtual_witness_capable' in rep_info
        assert 'snapshot_policy_capable' in rep_info
        assert 'metro_dr_capable' in rep_info
        assert 'vasa_async_remote_rep_capable' in rep_info
        assert 'metro_capable' in rep_info

    def test_get_replication_info(self):
        """Test get_replication_info."""
        array_id = self.conn.array_id
        rep_info = self.replication.get_replication_info()
        self.assertEqual(array_id, rep_info.get('symmetrixId'))
        assert 'storageGroupCount' in rep_info
        assert 'replicationCacheUsage' in rep_info

    def test_get_replication_enabled_storage_groups(self):
        """Test get_replication_enabled_storage_groups."""
        self.create_sg_snapshot()
        snap_list = self.replication.get_replication_enabled_storage_groups(
            has_snapshots=True, has_srdf=False)
        self.assertIsInstance(snap_list, list)

    def test_get_storage_group_replication_details(self):
        """Test get_storage_group_replication_details."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        rep_info = self.replication.get_storage_group_replication_details(
            storage_group_id=sg_name)
        self.assertEqual(1, rep_info.get('numSnapVXSnapshots'))

    def test_is_volume_in_replication_session(self):
        """Test is_volume_in_replication_session."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        volume = snapshot_info.get('source_volume')
        vol_name = volume[0].get('name')
        snapxv_src = False
        i = 0
        while not snapxv_src:
            time.sleep(1)
            i += 1
            snapxv_tgt, snapxv_src, rdf_group = (
                self.replication.is_volume_in_replication_session(
                    device_id=vol_name))
            if i > 10:
                break
        self.assertTrue(i <= 10)
        self.assertEqual(snapxv_src, True)

    # -------------------------------------------------------------------------
    # SnapshotFunctions methods (conn.snapshot)
    # -------------------------------------------------------------------------

    def test_is_snapvx_licensed(self):
        """Test is_snapvx_licensed."""
        licensed = self.snapshot.is_snapvx_licensed()
        self.assertIs(True, licensed)

    def test_get_storage_group_snapshot_list(self):
        """Test get_storage_group_snapshot_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        sg_snap_list = self.snapshot.get_storage_group_snapshot_list(
            storage_group_id=sg_name)
        self.assertEqual(snapshot_info.get('name'), sg_snap_list[0])

    def test_get_storage_group_no_snapshot(self):
        """Test get_storage_group_snapshot_list returns empty for SG with no snapshot."""
        storage_group_name = self.generate_name('sg')
        volume_name = self.generate_name()
        self.provisioning.create_storage_group(
            self.SRP, storage_group_name, self.SLO,
            vol_name=volume_name)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self.assertFalse(self.snapshot.get_storage_group_snapshot_list(
            storage_group_name))

    def test_create_storage_group_snapshot(self):
        """Test create_storage_group_snapshot by generation."""
        if self.is_v4:
            self.skipTest('Create storage group snapshot by generation does '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        self.snapshot.create_storage_group_snapshot(
            sg_name, 'ci_snap', ttl=1, hours=True)
        snapshot_info = self.snapshot.get_storage_group_snapshot_list(sg_name)
        snapshot_details = (
            self.snapshot.get_storage_group_snapshot_generation_list(
                sg_name, snap_name='ci_snap'))
        self.snapshot.delete_storage_group_snapshot(
            sg_name, snap_name='ci_snap', gen=(snapshot_details[0]))
        self.assertIn('ci_snap', snapshot_info)

    def test_create_storage_group_snapshot_by_snap_id(self):
        """Test create_storage_group_snapshot by snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        ss_name = self.generate_name(object_type='ss')
        self.snapshot.create_storage_group_snapshot(
            sg_name, ss_name, ttl=1, hours=True)
        snapshot_info = self.snapshot.get_storage_group_snapshot_list(sg_name)
        snapshot_details = (
            self.snapshot.get_storage_group_snapshot_snap_id_list(
                sg_name, ss_name))
        self.snapshot.delete_storage_group_snapshot_by_snap_id(
            sg_name, ss_name, snapshot_details[0])
        self.assertIn(ss_name, snapshot_info)

    def test_get_storage_group_snapshot_snap_id_list(self):
        """Test get_storage_group_snapshot_snap_id_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        snap_id_list = (
            self.snapshot.get_storage_group_snapshot_snap_id_list(
                sg_name, snap_name))
        self.assertEqual([snap_id], snap_id_list)

    def test_get_snapshot_generation_details(self):
        """Test get_snapshot_generation_details."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_gen_details = self.snapshot.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(['Established'], snap_gen_details.get('state'))

    def test_get_snapshot_snap_id_details(self):
        """Test get_snapshot_snap_id_details."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        snap_details = self.snapshot.get_snapshot_snap_id_details(
            sg_name, snap_name, snap_id)
        self.assertEqual(['Established'], snap_details.get('state'))

    def test_modify_storage_group_snapshot_rename(self):
        """Test modify_storage_group_snapshot rename."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does  '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        snapshot_details = (
            self.snapshot.get_storage_group_snapshot_generation_list(
                sg_name, snap_name=old_name))
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name=old_name, new_name='newname',
            gen_num=snapshot_details[0])
        snap_list = self.snapshot.get_storage_group_snapshot_list(
            storage_group_id=sg_name)
        # change name back so clean up will work automatically
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name='newname', new_name=old_name,
            gen_num=snapshot_details[0])
        self.assertEqual('newname', snap_list[0])

    def test_modify_storage_group_snap_rename_by_snap_id(self):
        """Test modify_storage_group_snapshot_by_snap_id rename."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        new_name = self.generate_name(object_type='ss')
        snapshot_details = (
            self.snapshot.get_storage_group_snapshot_snap_id_list(
                sg_name, old_name))
        snap_id = snapshot_details[0]
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, None, old_name, snap_id, new_name=new_name)
        snap_list = self.snapshot.get_storage_group_snapshot_list(sg_name)
        # change name back so clean up will work automatically
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, None, new_name, snap_id, new_name=old_name)
        self.assertEqual(new_name, snap_list[0])

    def test_modify_storage_group_snapshot_link(self):
        """Test modify_storage_group_snapshot link."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot link by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertEqual(True, snap_details.get('isLinked'))
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storage_group_snap_relink(self):
        """Test modify_storage_group_snapshot relink."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot relink by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(snap_details.get('isLinked'))
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, relink=True)
        relink_snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(relink_snap_details.get('isLinked'))
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storage_group_snap_link_by_snap_id(self):
        """Test modify_storage_group_snapshot_by_snap_id link."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, link=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(snap_details.get('linked'))
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.provisioning.delete_storage_group(target_sg)

    def test_modify_storage_group_snap_relink_by_snap_id(self):
        """Test modify_storage_group_snapshot_by_snap_id relink."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, link=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(snap_details.get('linked'))
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, relink=True)
        relink_snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(relink_snap_details.get('linked'))
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.provisioning.delete_storage_group(target_sg)

    def test_modify_storage_group_snapshot_unlink(self):
        """Test modify_storage_group_snapshot unlink."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot unlink by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        linked_snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(linked_snap_details.get('isLinked'))
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.assertFalse(snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storage_group_snapshot_unlink_by_snap_id(self):
        """Test modify_storage_group_snapshot_by_snap_id unlink."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, link=True)
        linked_snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(linked_snap_details.get('linked'))
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.assertFalse(snap_details.get('linked'))
        self.provisioning.delete_storage_group(target_sg)

    def test_modify_storage_group_snapshot_restore(self):
        """Test modify_storage_group_snapshot restore."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot restore by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name=snap_name, gen_num=0, restore=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_restored=True)
        self.assertTrue('Restored' in snap_details.get('state'))

    def test_modify_storage_group_snap_restore_by_snap_id(self):
        """Test modify_storage_group_snapshot_by_snap_id restore."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, None, snap_name, snap_id, restore=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_restored=True)
        self.assertTrue('Restored' in snap_details.get('state'))

    def test_restore_snapshot(self):
        """Test restore_snapshot."""
        if self.is_v4:
            self.skipTest('Restore snapshot by generation does '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        self.snapshot.restore_snapshot(sg_id=sg_name,
                                       snap_name=snap_name, gen_num=0)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_restored=True)
        self.assertTrue('Restored' in snap_details.get('state'))

    def test_restore_snapshot_by_snap_id(self):
        """Test restore_snapshot_by_snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.snapshot.restore_snapshot_by_snap_id(sg_name, snap_name, snap_id)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_restored=True)
        self.assertTrue('Restored' in snap_details.get('state'))

    def test_rename_snapshot(self):
        """Test rename_snapshot."""
        if self.is_v4:
            self.skipTest('Rename snapshot by generation does '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        self.snapshot.rename_snapshot(
            sg_id=sg_name, snap_name=old_name, new_name='newname', gen_num=0)
        snap_list = self.snapshot.get_storage_group_snapshot_list(
            storage_group_id=sg_name)
        self.assertEqual('newname', snap_list[0])
        # change name back so clean up will work automatically
        self.snapshot.rename_snapshot(
            sg_id=sg_name, snap_name='newname', new_name=old_name, gen_num=0)

    def test_rename_snapshot_by_snap_id(self):
        """Test rename_snapshot_by_snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        new_name = self.generate_name(object_type='ss')
        self.snapshot.rename_snapshot_by_snap_id(
            sg_name, old_name, new_name, snap_id)
        snap_list = self.snapshot.get_storage_group_snapshot_list(sg_name)
        self.assertEqual(new_name, snap_list[0])
        # change name back so clean up will work automatically
        self.snapshot.rename_snapshot_by_snap_id(
            sg_name, new_name, old_name, snap_id)

    def test_link_gen_snapshot(self):
        """Test link_gen_snapshot."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.snapshot.link_gen_snapshot(
            sg_id=sg_name, link_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(snap_details.get('isLinked'))
        self.snapshot.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.assertFalse(snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_link_snapshot_by_snap_id(self):
        """Test link_snapshot_by_snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.assertIsNotNone(snap_id)
        self.snapshot.link_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(snap_details.get('linked'))
        self.snapshot.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.assertFalse(snap_details.get('linked'))
        self.provisioning.delete_storage_group(target_sg)

    def test_unlink_gen_snapshot(self):
        """Test unlink_gen_snapshot."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.snapshot.link_gen_snapshot(
            sg_id=sg_name, link_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(snap_details.get('isLinked'))
        self.snapshot.unlink_gen_snapshot(
            sg_id=sg_name, unlink_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.assertFalse(snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_unlink_snapshot_by_snap_id(self):
        """Test unlink_snapshot_by_snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.snapshot.link_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id)
        linked_snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(linked_snap_details.get('linked'))
        self.snapshot.unlink_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.assertFalse(snap_details.get('linked'))
        self.provisioning.delete_storage_group(target_sg)

    def test_find_expired_snapvx_snapshots(self):
        """Test find_expired_snapvx_snapshots."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        expired_snap_list = self.snapshot.find_expired_snapvx_snapshots()
        self.assertIsInstance(expired_snap_list, list)

    def test_find_expired_snapvx_snapshots_by_snap_id(self):
        """Test find_expired_snapvx_snapshots_by_snap_ids."""
        expired_snap_list = (
            self.snapshot.find_expired_snapvx_snapshots_by_snap_ids())
        self.assertIsInstance(expired_snap_list, list)

    def test_bulk_terminate_snapshots(self):
        """Test bulk_terminate_snapshots."""
        sg_name = self.create_empty_storage_group()
        self.provisioning.create_volume_from_storage_group_return_id(
            'bulk_terminate_test', sg_name, '1')
        self.snapshot.create_storage_group_snapshot(
            sg_name, sg_name, ttl=1, hours=True)
        self.snapshot.create_storage_group_snapshot(
            sg_name, sg_name, ttl=1, hours=True)
        self.snapshot.create_storage_group_snapshot(
            sg_name, sg_name, ttl=1, hours=True)
        self.snapshot.bulk_terminate_snapshots(
            storage_group_id=sg_name, snap_name=sg_name,
            terminate_all_snapshots=True, force=True)
        snapshot_info = self.snapshot.get_storage_group_snapshot_list(sg_name)
        self.assertEquals(0, len(snapshot_info))

    # -------------------------------------------------------------------------
    # Private polling helpers
    # -------------------------------------------------------------------------

    def _test_get_ss_gen_detail(
            self, sg_name, snap_name, gen_num, check_linked=False,
            check_unlinked=False, check_restored=False):
        time.sleep(1)
        snap_details = self.snapshot.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=gen_num)
        i = 0
        if check_unlinked:
            while snap_details.get('isLinked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to unlink" % i)
                snap_details = (
                    self.snapshot.get_snapshot_generation_details(
                        sg_id=sg_name, snap_name=snap_name, gen_num=gen_num))
                if i > 10:
                    break
        elif check_linked:
            while not snap_details.get('isLinked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to link" % i)
                snap_details = (
                    self.snapshot.get_snapshot_generation_details(
                        sg_id=sg_name, snap_name=snap_name, gen_num=gen_num))
                if i > 10:
                    break
        elif check_restored:
            while 'Restored' not in snap_details.get('state'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to restore" % i)
                snap_details = (
                    self.snapshot.get_snapshot_generation_details(
                        sg_id=sg_name, snap_name=snap_name, gen_num=gen_num))
                if i > 10:
                    break
        else:
            print("WARNING - no check set so polling can not occur.")
        return snap_details

    def _test_get_ss_snapid_detail(
            self, sg_name, snap_name, snap_id, check_linked=False,
            check_unlinked=False, check_restored=False):
        time.sleep(1)
        snap_details = self.snapshot.get_snapshot_snap_id_details(
            sg_name, snap_name, snap_id)
        i = 0
        if check_unlinked:
            while snap_details.get('linked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to unlink" % i)
                snap_details = self.snapshot.get_snapshot_snap_id_details(
                    sg_name, snap_name, snap_id)
                if i > 10:
                    break
        elif check_linked:
            while not snap_details.get('linked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to link" % i)
                snap_details = self.snapshot.get_snapshot_snap_id_details(
                    sg_name, snap_name, snap_id)
                if i > 10:
                    break
        elif check_restored:
            while 'Restored' not in snap_details.get('state'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to restore" % i)
                snap_details = self.snapshot.get_snapshot_snap_id_details(
                    sg_name, snap_name, snap_id)
                if i > 10:
                    break
        return snap_details
