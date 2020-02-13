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
"""test_pyu4v_ci_replication.py.py."""
import testtools
import time

from PyU4V.tests.ci_tests import base


class CITestReplication(base.TestBaseTestCase, testtools.TestCase):
    """Test Replication Functions."""

    def setUp(self):
        """SetUp."""
        super(CITestReplication, self).setUp()
        self.replication = self.conn.replication
        self.provisioning = self.conn.provisioning
        self.system = self.conn.system

    def test_get_array_replication_capabilities(self):
        """Test get_array_replication_capabilities."""
        rep_info = self.conn.replication.get_array_replication_capabilities()
        self.assertEqual(5, len(rep_info.keys()))
        assert 'symmetrixId' in rep_info
        assert 'snapVxCapable' in rep_info
        assert 'rdfCapable' in rep_info
        assert 'witness_capable' in rep_info
        assert 'virtual_witness_capable' in rep_info

    def test_is_snapvx_licensed(self):
        """Test is_snapvx_licensed."""
        licensed = self.replication.is_snapvx_licensed()
        self.assertIs(True, licensed)

    def test_get_storage_group_rep(self):
        """Test get_storage_group_rep."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        rep_info = self.replication.get_storage_group_rep(
            storage_group_name=sg_name)
        self.assertEqual(1, rep_info.get('numSnapVXSnapshots'))

    def create_storagegroup_snap(self):
        """Test get_storagegroup_snapshot_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        self.replication.create_storagegroup_snap(sg_name, 'ci_snap', ttl=1,
                                                  hours=True)
        snapshot_info = self.replication.get_storagegroup_snapshot_list(
            sg_name)
        self.assertIn('ci_snap', snapshot_info)
        self.replication.delete_storagegroup_snapshot(sg_name,
                                                      snap_name='ci_snap',
                                                      gen_num=0)

    def test_get_storage_group_replication_details(self):
        """Test get_storage_group_replication_details."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        rep_info = self.replication.get_storage_group_replication_details(
            storage_group_id=sg_name)
        self.assertEqual(1, rep_info.get('numSnapVXSnapshots'))

    def test_get_storage_group_rep_list(self):
        """Test get_storage_group_rep_list."""
        self.create_sg_snapshot()
        snap_list = self.replication.get_storage_group_rep_list(
            has_snapshots=True, has_srdf=False)
        self.assertIsInstance(snap_list, list)

    def test_get_replication_enabled_storage_groups(self):
        """Test get_replication_enabled_storage_groups."""
        self.create_sg_snapshot()
        snap_list = self.replication.get_replication_enabled_storage_groups(
            has_snapshots=True, has_srdf=True)
        self.assertIsInstance(snap_list, list)

    def test_get_storagegroup_snapshot_list(self):
        """Test get_storagegroup_snapshot_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        sg_snap_list = self.replication.get_storagegroup_snapshot_list(
            storagegroup_id=sg_name)
        self.assertEqual(snapshot_info.get('name'), sg_snap_list[0])

    def test_get_storage_group_snapshot_list(self):
        """Test get_storage_group_snapshot_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        sg_snap_list = self.replication.get_storage_group_snapshot_list(
            storage_group_id=sg_name)
        self.assertEqual(snapshot_info.get('name'), sg_snap_list[0])

    def test_modify_storagegroup_snap_rename(self):
        """Test modify_storage_group_snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name=old_name, new_name='newname', gen_num=0)
        snap_list = self.replication.get_storagegroup_snapshot_list(
            storagegroup_id=sg_name)
        self.assertEqual('newname', snap_list[0])
        # change name back so clean up will work automatically
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name='newname', new_name=old_name, gen_num=0)

    def test_get_replication_info(self):
        """Test get_replication_info."""
        array_id = self.conn.array_id
        rep_info = self.replication.get_replication_info()
        self.assertEqual(array_id, rep_info.get('symmetrixId'))
        assert 'storageGroupCount' in rep_info
        assert 'replicationCacheUsage' in rep_info

    def test_modify_storagegroup_snap_link(self):
        """Test to cover link snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(True, snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storagegroup_snap_unlink(self):
        """Test to cover unlink snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        linked_snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(True, linked_snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(False, snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storagegroup_snap_restore(self):
        """Test to cover restore snapshot."""
        self.skipTest("Skipping test_modify_storagegroup_snap_restore "
                      "due to OPT 564297")
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name=snap_name, gen_num=0, restore=True)
        snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        restored = False
        if 'Restored' in snap_details.get('state'):
            restored = True
        self.assertEqual(True, restored)

    def test_restore_snapshot(self):
        """Test to cover restore snapshot."""
        self.skipTest("Skipping test_restore_snapshot due to OPT 564297")
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        self.replication.restore_snapshot(sg_id=sg_name,
                                          snap_name=snap_name, gen_num=0)
        snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        restored = False
        if 'Restored' in snap_details.get('state'):
            restored = True
        self.assertEqual(True, restored)

    def test_rename_snapshot(self):
        """Test to cover rename snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        self.replication.rename_snapshot(
            sg_id=sg_name, snap_name=old_name, new_name='newname', gen_num=0)
        snap_list = self.replication.get_storagegroup_snapshot_list(
            storagegroup_id=sg_name)
        self.assertEqual('newname', snap_list[0])
        # change name back so clean up will work automatically
        self.replication.rename_snapshot(
            sg_id=sg_name, snap_name='newname', new_name=old_name,
            gen_num=0)

    def test_link_gen_snapshot(self):
        """Test to cover link snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.link_gen_snapshot(
            sg_id=sg_name, link_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(True, snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_unlink_gen_snapshot(self):
        """Test to cover unlink snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.link_gen_snapshot(
            sg_id=sg_name, link_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        linked_snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(True, linked_snap_details.get('isLinked'))
        self.replication.unlink_gen_snapshot(
            sg_id=sg_name, unlink_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(False, snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_is_vol_in_rep_session(self):
        """Test is_vol_in_rep_session."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        volume = snapshot_info.get('sourceVolume')
        vol_name = volume[0].get('name')
        snapxv_tgt, snapxv_src, rdf_group = (
            self.replication.is_vol_in_rep_session(device_id=vol_name))
        self.assertEqual(snapxv_src, True)

    def test_is_volume_in_replication_session(self):
        """Test is_volume_in_replication_session."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        volume = snapshot_info.get('sourceVolume')
        vol_name = volume[0].get('name')
        snapxv_tgt, snapxv_src, rdf_group = (
            self.replication.is_volume_in_replication_session(
                device_id=vol_name))
        self.assertEqual(snapxv_src, True)

    def test_get_snapshot_generation_details(self):
        """Test get_snapshot_generation_details."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_gen_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(['Established'], snap_gen_details.get('state'))

    def test_get_storage_group_snapshot_generation_list(self):
        """Test get_storagegroup_snapshot_generation_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        gen_list = (
            self.replication.get_storagegroup_snapshot_generation_list(
                storagegroup_id=sg_name, snap_name=snap_name))
        self.assertEqual([0], gen_list)

    def test_get_rdf_group(self):
        """Test get_rdf_group."""
        rdf_number = self.replication.get_rdf_group_list()[0].get('rdfgNumber')
        rdfg_details = self.replication.get_rdf_group(rdf_number=rdf_number)
        self.assertIn('remoteSymmetrix', rdfg_details)

    def test_get_rdf_group_list(self):
        """Test get_migration_info."""
        rdf_number = self.replication.get_rdf_group_list()
        self.assertIsInstance(rdf_number, list)

    def test_get_rdf_group_volume(self):
        """Test get_rdf_group_volume."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        rdf_vol_details = self.replication.get_rdf_group_volume(
            rdf_number=srdf_group_number, device_id=device_id)
        self.assertIn('localRdfGroupNumber', rdf_vol_details)
        self.assertEqual(srdf_group_number,
                         rdf_vol_details.get('localRdfGroupNumber'))

    def test_get_rdf_group_number(self):
        """Test get_rdf_group."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        label = self.replication.get_rdf_group(srdf_group_number).get('label')
        number = self.replication.get_rdf_group_number(label)
        self.assertEqual(srdf_group_number, number)

    def test_get_rdf_group_volume_list(self):
        """Test get_rdf_group_volume_list."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        rdf_volume_list = self.replication.get_rdf_group_volume_list(
            srdf_group_number)
        self.assertIsInstance(rdf_volume_list, list)

    def test_are_vols_rdf_paired(self):
        """Test are_vols_rdf_paired."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        pair_state = self.replication.are_vols_rdf_paired(
            remote_array=self.conn.remote_array, device_id=local_volume,
            target_device=remote_volume, rdf_group=srdf_group_number)
        self.assertIn('Synchronized', pair_state)

    def test_find_expired_snapvx_snapshots(self):
        """Test find_expired_snapvx_snapshots."""
        expired_snap_list = self.replication.find_expired_snapvx_snapshots()
        self.assertIsInstance(expired_snap_list, list)

    def test_are_volumes_rdf_paired(self):
        """Test are_volumes_rdf_paired."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        pair_state = self.replication.are_volumes_rdf_paired(
            remote_array=self.conn.remote_array, device_id=local_volume,
            target_device=remote_volume, rdf_group=srdf_group_number)
        self.assertIn('Synchronized', pair_state)

    def test_get_storagegroup_srdfg_list(self):
        """Test get_storagegroup_srdfg_list."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdfg_list = self.replication.get_storagegroup_srdfg_list(sg_name)
        self.assertIsInstance(sg_rdfg_list, list)

    def test_get_storage_group_srdf_group_list(self):
        """Test get_storage_group_srdf_group_list."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdfg_list = self.replication.get_storage_group_srdf_group_list(
            sg_name)
        self.assertIsInstance(sg_rdfg_list, list)

    def test_get_storagegroup_srdf_details(self):
        """Test get_storagegroup_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdf_details = self.replication.get_storagegroup_srdf_details(
            sg_name, srdf_group_number)
        self.assertIsInstance(sg_rdf_details, dict)

    def test_get_storage_group_srdf_details(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdf_details = self.replication.get_storage_group_srdf_details(
            sg_name, srdf_group_number)
        self.assertIsInstance(sg_rdf_details, dict)

    def test_create_storagegroup_srdf_pairings(self):
        """Test create_storagegroup_srdf_pairings."""
        self.check_for_remote_array()
        sg_name = self.generate_name(object_type='sg')
        self.conn.provisioning.create_storage_group(
            self.SRP, sg_name, self.SLO, None, False, 1, 1, 'GB', False, False,
            'CI_TEST_VOL')
        self.replication.create_storagegroup_srdf_pairings(
            storagegroup_id=sg_name, remote_sid=self.conn.remote_array,
            srdfmode='Synchronous', establish=True)
        srdf_group_number = (
            self.conn.replication.get_storage_group_srdf_group_list(
                sg_name))[0]
        self.addCleanup(self.cleanup_rdfg, sg_name, srdf_group_number)

    # Split Functions Below will have status of Failed over as Source Volume
    # is not masked to a host
    def test_modify_storagegroup_srdf(self):
        """Test modify_storagegroup_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.modify_storagegroup_srdf(
            sg_name, 'split', srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_modify_storage_group_srdf(self):
        """Test modify_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.modify_storage_group_srdf(
            sg_name, 'split', srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_suspend_storagegroup_srdf(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.suspend_storagegroup_srdf(
            sg_name, srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Suspended', status)

    def test_suspend_storage_group_srdf(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.suspend_storage_group_srdf(
            sg_name, srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Suspended', status)

    def test_establish_storagegroup_srdf(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.suspend_storage_group_srdf(sg_name, srdf_group_number)
        self.replication.establish_storagegroup_srdf(
            sg_name, srdf_group_number)
        time.sleep(3)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_establish_storage_group_srdf(self):
        """Test establish_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.suspend_storage_group_srdf(sg_name, srdf_group_number)
        self.replication.establish_storage_group_srdf(
            sg_name, srdf_group_number)
        time.sleep(3)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_failover_storagegroup_srdf(self):
        """Test failover_storagegroup_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.failover_storagegroup_srdf(sg_name, srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_failover_storage_group_srdf(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.failover_storage_group_srdf(sg_name,
                                                     srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_failback_storagegroup_srdf(self):
        """Test failback_storagegroup_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.failover_storage_group_srdf(
            sg_name, srdf_group_number)
        self.replication.failback_storagegroup_srdf(sg_name, srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_failback_storage_group_srdf(self):
        """Test failback_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.failover_storage_group_srdf(
            sg_name, srdf_group_number)
        self.replication.failback_storage_group_srdf(
            sg_name, srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_get_rdf_director_list(self):
        """Test get rdf director list."""
        rdf_director_list = self.replication.get_rdf_director_list()
        self.assertIsInstance(rdf_director_list, list)

    def test_get_rdf_director_detail(self):
        """Test get_rdf_director_detail."""
        rdf_director_list = self.replication.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_details = self.replication.get_rdf_director_detail(
                director_id=rdf_director_list[0])
            self.assertIsInstance(rdf_director_details, dict)
            self.assertIn('directorId', rdf_director_details)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_get_rdf_director_port_list(self):
        """Test get_rdf_direector_list."""
        rdf_director_list = self.replication.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_ports = self.replication.get_rdf_director_port_list(
                director_id=rdf_director_list[0])
            self.assertIsInstance(rdf_director_ports, list)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_get_rdf_director_port_details(self):
        """Test get_rdf_director_port_details."""
        rdf_director_list = self.replication.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_ports = self.replication.get_rdf_director_port_list(
                director_id=rdf_director_list[0])
            rdf_port_detail = self.replication.get_rdf_director_port_details(
                director_id=rdf_director_list[0],
                port_id=rdf_director_ports[0])
            self.assertIn('wwn', rdf_port_detail)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_create_and_delete_rdf_group(self):
        """Test create_rdf_group and delete_rdf_group."""
        local_array = self.conn.array_id
        local_port_list, remote_port_list = self.get_online_rdf_ports()
        self.conn.set_array_id(local_array)
        rdf_group = self.get_next_free_srdf_group()
        self.replication.create_rdf_group(
            local_director_port_list=local_port_list,
            remote_array_id=self.conn.remote_array,
            remote_director_port_list=remote_port_list,
            array_id=local_array, local_rdfg_number=rdf_group,
            remote_rdfg_number=rdf_group, label='pyu4v_' + str(rdf_group))
        rdf_group_list = self.replication.get_rdf_group_list()
        rdfg_list = []
        for group in rdf_group_list:
            rdfg_list.append(group['rdfgNumber'])
        self.assertIn(rdf_group, rdfg_list)
        self.replication.delete_rdf_group(srdf_group_number=rdf_group)
        rdf_group_list = self.replication.get_rdf_group_list()
        rdfg_list = []
        for group in rdf_group_list:
            rdfg_list.append(group['rdfgNumber'])
        self.assertNotIn(rdf_group, rdfg_list)

    def test_get_rdf_port_remote_connections(self):
        """Test get_rdf_port_remote_connections."""
        local_array = self.conn.array_id
        local_port_list, remote_port_list = self.get_online_rdf_ports()
        self.conn.set_array_id(local_array)
        dir_id = local_port_list[0].split(':')[0]
        port_no = local_port_list[0].split(':')[1]
        connections = self.replication.get_rdf_port_remote_connections(
            director_id=dir_id, port_id=port_no)
        self.assertIn('remotePort', connections)

    def test_modify_rdf_group_add_remove_port(self):
        """test adding and removing of port from RDF group."""
        srdf_group, local_port_list, remote_port_list = self.setup_srdf_group()
        port_list = []
        port_list.append(local_port_list[0])
        self.replication.modify_rdf_group(
            action='remove_ports', srdf_group_number=srdf_group,
            port_list=port_list)
        modifed_port_list = self.replication.get_rdf_group(
            rdf_number=srdf_group)['localPorts']
        self.assertNotIn(local_port_list[0], modifed_port_list)
        self.replication.modify_rdf_group(
            action='add_ports', port_list=port_list,
            srdf_group_number=srdf_group)
        modifed_port_list = self.replication.get_rdf_group(
            rdf_number=srdf_group)['localPorts']
        self.assertIn(local_port_list[0], modifed_port_list)
        self.replication.delete_rdf_group(srdf_group_number=srdf_group)

    def test_modify_rdf_group_change_label(self):
        """Test modify_rdf_group_change_label."""
        srdf_group, local_port_list, remote_port_list = self.setup_srdf_group()
        self.replication.modify_rdf_group(
            action='set_label', label='pyu4v_chg',
            srdf_group_number=srdf_group)
        rdfg_detail = self.replication.get_rdf_group(srdf_group)
        self.assertIn('pyu4v_chg', rdfg_detail['label'])
        self.replication.delete_rdf_group(srdf_group_number=srdf_group)

    def test_create_storage_group_from_rdfg(self):
        """Test create_storage_group_from_rdfg."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        self.replication.create_storage_group_from_rdfg(
            storage_group_name='ci_new_srdf_delete',
            srdf_group_number=srdf_group_number, rdf_type='RDF1')
        sg_rdfg_list = self.replication.get_storage_group_srdf_group_list(
            storage_group_id='ci_new_srdf_delete')
        self.assertIn(srdf_group_number, sg_rdfg_list)
        self.provisioning.delete_storage_group(
            storage_group_id='ci_new_srdf_delete')
