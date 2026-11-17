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
"""test_pyu4v_ci_srdf.py."""
import testtools
import time

from PyU4V.tests.ci_tests import base


class CITestSRDF(base.TestBaseTestCase, testtools.TestCase):
    """Test SRDF Functions via conn.srdf module."""

    def setUp(self):
        """SetUp."""
        super(CITestSRDF, self).setUp()
        self.srdf = self.conn.srdf
        self.replication = self.conn.replication
        self.provisioning = self.conn.provisioning
        self.system = self.conn.system
        self.is_v4 = self.common.is_array_v4(self.conn.array_id)

    # -------------------------------------------------------------------------
    # RDF group and volume queries
    # -------------------------------------------------------------------------

    def test_get_rdf_group(self):
        """Test get_rdf_group."""
        rdf_group = self.srdf.get_rdf_group_list()
        if not rdf_group:
            self.skipTest('test_get_rdf_group - Unable to get an RDF group.')
        rdf_number = rdf_group[0].get('rdfgNumber')
        rdfg_details = self.srdf.get_rdf_group(rdf_number=rdf_number)
        self.assertIn('remoteSymmetrix', rdfg_details)

    def test_get_rdf_group_list(self):
        """Test get_rdf_group_list."""
        rdf_number = self.srdf.get_rdf_group_list()
        self.assertIsInstance(rdf_number, list)

    def test_get_rdf_group_list_with_parms(self):
        """Test get_rdf_group_list with filter parameters."""
        rdf_number = self.srdf.get_rdf_group_list(
            group_type='Dynamic', remote_symmetrix_id=self.conn.remote_array,
            volume_count=0, rdf_mode='Synchronous')
        self.assertIsInstance(rdf_number, list)

    def test_get_rdf_group_volume(self):
        """Test get_rdf_group_volume."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        rdf_vol_details = self.srdf.get_rdf_group_volume(
            rdf_number=srdf_group_number, device_id=device_id)
        self.assertIn('localRdfGroupNumber', rdf_vol_details)
        self.assertEqual(srdf_group_number,
                         rdf_vol_details.get('localRdfGroupNumber'))

    def test_get_rdf_group_number(self):
        """Test get_rdf_group_number via label lookup."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        label = self.srdf.get_rdf_group(srdf_group_number).get('label')
        number = self.srdf.get_rdf_group_number(label)
        self.assertEqual(srdf_group_number, number)

    def test_get_rdf_group_volume_list(self):
        """Test get_rdf_group_volume_list."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        rdf_volume_list = self.srdf.get_rdf_group_volume_list(
            srdf_group_number)
        self.assertIsInstance(rdf_volume_list, list)

    def test_are_volumes_rdf_paired(self):
        """Test are_volumes_rdf_paired."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        pair_state = self.srdf.are_volumes_rdf_paired(
            remote_array=self.conn.remote_array, device_id=local_volume,
            target_device=remote_volume, rdf_group=srdf_group_number)
        self.assertIn('Synchronized', pair_state)

    # -------------------------------------------------------------------------
    # Storage group SRDF operations
    # -------------------------------------------------------------------------

    def test_get_storage_group_srdf_group_list(self):
        """Test get_storage_group_srdf_group_list."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdfg_list = self.srdf.get_storage_group_srdf_group_list(sg_name)
        self.assertIsInstance(sg_rdfg_list, list)

    def test_get_storage_group_srdf_details(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdf_details = self.srdf.get_storage_group_srdf_details(
            sg_name, srdf_group_number)
        self.assertIsInstance(sg_rdf_details, dict)

    def test_create_storage_group_srdf_pairings(self):
        """Test create_storage_group_srdf_pairings."""
        self.check_for_remote_array()
        sg_name = self.generate_name(object_type='sg')
        vol_name = self.generate_name(object_type='v')
        self.conn.provisioning.create_storage_group(
            self.SRP, sg_name, self.SLO, None, False, 1, 1, 'GB', False, False,
            vol_name)
        self.srdf.create_storage_group_srdf_pairings(
            storage_group_id=sg_name, remote_sid=self.conn.remote_array,
            srdf_mode='Synchronous', establish=True)
        srdf_group_number = (
            self.srdf.get_storage_group_srdf_group_list(sg_name))[0]
        self.addCleanup(self.cleanup_rdfg, sg_name, srdf_group_number)

    # Split Functions Below will have status of Failed over as Source Volume
    # is not masked to a host

    def test_modify_storage_group_srdf(self):
        """Test modify_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.srdf.modify_storage_group_srdf(sg_name, 'split', srdf_group_number)
        status = self.srdf.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_suspend_storage_group_srdf(self):
        """Test suspend_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.srdf.suspend_storage_group_srdf(sg_name, srdf_group_number)
        status = self.srdf.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Suspended', status)

    def test_establish_storage_group_srdf(self):
        """Test establish_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.srdf.suspend_storage_group_srdf(sg_name, srdf_group_number)
        self.srdf.establish_storage_group_srdf(sg_name, srdf_group_number)
        time.sleep(3)
        status = self.srdf.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_failover_storage_group_srdf(self):
        """Test failover_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.srdf.failover_storage_group_srdf(sg_name, srdf_group_number)
        status = self.srdf.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_failback_storage_group_srdf(self):
        """Test failback_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.srdf.failover_storage_group_srdf(sg_name, srdf_group_number)
        self.srdf.failback_storage_group_srdf(sg_name, srdf_group_number)
        status = self.srdf.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_create_storage_group_from_rdfg(self):
        """Test create_storage_group_from_rdfg."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        storage_group_name = self.generate_name('sg')
        self.srdf.create_storage_group_from_rdfg(
            storage_group_name=storage_group_name,
            srdf_group_number=srdf_group_number, rdf_type='RDF1')
        sg_rdfg_list = self.srdf.get_storage_group_srdf_group_list(
            storage_group_id=storage_group_name)
        self.assertIn(srdf_group_number, sg_rdfg_list)
        self.provisioning.delete_storage_group(
            storage_group_id=storage_group_name)

    def test_modify_storage_group_srdf_set_consistency_enable(self):
        """Test modify_storage_group_srdf to enable consistency."""
        if not self._run_consistency_enable_check():
            self.skipTest(
                'Skip test_modify_storage_group_srdf_set_consistency_enable '
                'This fix is in V9.2.1.7')
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.srdf.modify_storage_group_srdf(
            storage_group_id=sg_name, action='setmode',
            srdf_group_number=srdf_group_number,
            options={'setMode': {'mode': 'Asynchronous'}})
        status = self.srdf.modify_storage_group_srdf(
            storage_group_id=sg_name, srdf_group_number=srdf_group_number,
            action="EnableConsistency")
        self.assertEqual('Enabled', status.get('consistency_protection'))
        disable_status = self.srdf.modify_storage_group_srdf(
            storage_group_id=sg_name, srdf_group_number=srdf_group_number,
            action="DisableConsistency")
        self.assertEqual(
            'Disabled', disable_status.get('consistency_protection'))

    # -------------------------------------------------------------------------
    # RDF directors and ports
    # -------------------------------------------------------------------------

    def test_get_rdf_director_list(self):
        """Test get_rdf_director_list."""
        rdf_director_list = self.srdf.get_rdf_director_list()
        self.assertIsInstance(rdf_director_list, list)

    def test_get_rdf_director_detail(self):
        """Test get_rdf_director_detail."""
        rdf_director_list = self.srdf.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_details = self.srdf.get_rdf_director_detail(
                director_id=rdf_director_list[0])
            self.assertIsInstance(rdf_director_details, dict)
            self.assertIn('directorId', rdf_director_details)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_get_rdf_director_port_list(self):
        """Test get_rdf_director_port_list."""
        rdf_director_list = self.srdf.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_ports = self.srdf.get_rdf_director_port_list(
                director_id=rdf_director_list[0])
            self.assertIsInstance(rdf_director_ports, list)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_get_rdf_director_port_details(self):
        """Test get_rdf_director_port_details."""
        rdf_director_list = self.srdf.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_ports = self.srdf.get_rdf_director_port_list(
                director_id=rdf_director_list[0],
                filters={'rdf_capable': 'true'})
            rdf_port_detail = self.srdf.get_rdf_director_port_details(
                director_id=rdf_director_list[0],
                port_id=rdf_director_ports[0])
            self.assertIn('wwn', rdf_port_detail)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_get_rdf_port_remote_connections(self):
        """Test get_rdf_port_remote_connections."""
        local_array = self.conn.array_id
        local_port_list, remote_port_list = self.get_online_rdf_ports()
        if not remote_port_list:
            self.skipTest('Skipping test_get_rdf_port_remote_connections - '
                          'No remote port list.')
        self.conn.set_array_id(local_array)
        dir_id = local_port_list[0].split(':')[0]
        port_no = local_port_list[0].split(':')[1]
        connections = self.srdf.get_rdf_port_remote_connections(
            director_id=dir_id, port_id=port_no)
        self.assertIn('remotePort', connections)

    # -------------------------------------------------------------------------
    # RDF group create / modify / delete
    # -------------------------------------------------------------------------

    def test_create_and_delete_rdf_group(self):
        """Test create_rdf_group and delete_rdf_group."""
        local_array = self.conn.array_id
        local_port_list, remote_port_list = self.get_online_rdf_ports()
        if not remote_port_list:
            self.skipTest('Skipping test_create_and_delete_rdf_group - '
                          'No remote port list.')
        self.conn.set_array_id(local_array)
        rdf_group = self.get_next_free_srdf_group()
        self.srdf.create_rdf_group(
            local_director_port_list=local_port_list,
            remote_array_id=self.conn.remote_array,
            remote_director_port_list=remote_port_list,
            array_id=local_array, local_rdfg_number=rdf_group,
            remote_rdfg_number=rdf_group, label='pyu4v_' + str(rdf_group))
        rdf_group_list = self.srdf.get_rdf_group_list()
        rdfg_list = [group['rdfgNumber'] for group in rdf_group_list]
        self.assertIn(rdf_group, rdfg_list)
        self.srdf.delete_rdf_group(srdf_group_number=rdf_group)
        rdf_group_list = self.srdf.get_rdf_group_list()
        rdfg_list = [group['rdfgNumber'] for group in rdf_group_list]
        self.assertNotIn(rdf_group, rdfg_list)

    def test_modify_rdf_group_add_remove_port(self):
        """Test adding and removing a port from an RDF group."""
        srdf_group, local_port_list, remote_port_list = self.setup_srdf_group()
        if not remote_port_list:
            self.skipTest('Skipping test_modify_rdf_group_add_remove_port - '
                          'no remote port list')
        port_list = [local_port_list[0]]
        self.srdf.modify_rdf_group(
            action='remove_ports', srdf_group_number=srdf_group,
            port_list=port_list)
        modified_port_list = self.srdf.get_rdf_group(
            rdf_number=srdf_group)['localPorts']
        self.assertNotIn(local_port_list[0], modified_port_list)
        self.srdf.modify_rdf_group(
            action='add_ports', port_list=port_list,
            srdf_group_number=srdf_group)
        modified_port_list = self.srdf.get_rdf_group(
            rdf_number=srdf_group)['localPorts']
        self.assertIn(local_port_list[0], modified_port_list)
        self.srdf.delete_rdf_group(srdf_group_number=srdf_group)

    def test_modify_rdf_group_change_label(self):
        """Test modify_rdf_group to change group label."""
        srdf_group, local_port_list, remote_port_list = self.setup_srdf_group()
        if not remote_port_list:
            self.skipTest('Skipping test_modify_rdf_group_change_label - '
                          'no remote port list.')
        srdf_group_label = self.generate_name('label')
        self.srdf.modify_rdf_group(
            action='set_label', label=srdf_group_label,
            srdf_group_number=srdf_group)
        rdfg_detail = self.srdf.get_rdf_group(srdf_group)
        self.assertIn('PyU4V-', rdfg_detail['label'])
        self.srdf.delete_rdf_group(srdf_group_number=srdf_group)

    # -------------------------------------------------------------------------
    # Private helper
    # -------------------------------------------------------------------------

    def _run_consistency_enable_check(self):
        """Check whether the array ucode supports consistency enable."""
        version, major = self.conn.common.get_uni_version()
        if major == '92':
            version_list = version.split('.')
            if version_list[2] == '1':
                if int(version_list[3]) < 7:
                    return False
        return True
