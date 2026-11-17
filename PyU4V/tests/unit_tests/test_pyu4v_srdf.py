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
"""test_pyu4v_srdf.py."""

import testtools

from unittest import mock

from PyU4V import common
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import exception


class PyU4VSRDFTest(testtools.TestCase):
    """Test SRDF module."""

    def setUp(self):
        """Setup."""
        super(PyU4VSRDFTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.srdf = self.conn.srdf

    def tearDown(self):
        """tearDown."""
        super(PyU4VSRDFTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_srdf_module_accessible(self):
        """Test that srdf module is accessible via conn.srdf."""
        self.assertIsNotNone(self.srdf)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'rdfgNumber': 1, 'label': 'test_rdfg'})
    def test_get_rdf_group(self, mck_get):
        """Test get_rdf_group."""
        result = self.srdf.get_rdf_group(1)
        self.assertEqual(1, result['rdfgNumber'])

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'rdfGroupID': [1, 2, 3]})
    def test_get_rdf_group_list(self, mck_get):
        """Test get_rdf_group_list."""
        result = self.srdf.get_rdf_group_list()
        self.assertEqual([1, 2, 3], result)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'name': ['00001', '00002']})
    def test_get_rdf_group_volume_list(self, mck_get):
        """Test get_rdf_group_volume_list."""
        result = self.srdf.get_rdf_group_volume_list(1)
        self.assertEqual(['00001', '00002'], result)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'localVolumeName': '00001',
                                     'remoteVolumeName': '00002',
                                     'remoteSymmetrixId': '000297900111',
                                     'localVolumeState': 'Ready',
                                     'rdfpairState': 'Synchronized'})
    def test_are_volumes_rdf_paired(self, mck_get):
        """Test are_volumes_rdf_paired."""
        paired, state, rdf_state = self.srdf.are_volumes_rdf_paired(
            '000297900111', '00001', '00002', 1)
        self.assertTrue(paired)
        self.assertEqual('Ready', state)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'rdfgs': [1, 2]})
    def test_get_storage_group_srdf_group_list(self, mck_get):
        """Test get_storage_group_srdf_group_list."""
        result = self.srdf.get_storage_group_srdf_group_list('test_sg')
        self.assertEqual([1, 2], result)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'rdfGroupNumber': 1})
    def test_get_storage_group_srdf_details(self, mck_get):
        """Test get_storage_group_srdf_details."""
        result = self.srdf.get_storage_group_srdf_details('test_sg', 1)
        self.assertEqual(1, result['rdfGroupNumber'])

    @mock.patch.object(common.CommonFunctions, 'create_resource',
                       return_value={'success': True})
    def test_create_storage_group_srdf_pairings(self, mck_create):
        """Test create_storage_group_srdf_pairings."""
        result = self.srdf.create_storage_group_srdf_pairings(
            'test_sg', '000297900111', 'Synchronous', establish=True)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_modify_storage_group_srdf(self, mck_modify):
        """Test modify_storage_group_srdf."""
        result = self.srdf.modify_storage_group_srdf(
            'test_sg', 'Establish', 1)
        self.assertIsNotNone(result)

    def test_modify_storage_group_srdf_invalid_action(self):
        """Test modify_storage_group_srdf with invalid action."""
        self.assertRaises(
            exception.VolumeBackendAPIException,
            self.srdf.modify_storage_group_srdf,
            'test_sg', 'InvalidAction', 1)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_suspend_storage_group_srdf(self, mck_modify):
        """Test suspend_storage_group_srdf."""
        result = self.srdf.suspend_storage_group_srdf('test_sg', 1)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_establish_storage_group_srdf(self, mck_modify):
        """Test establish_storage_group_srdf."""
        result = self.srdf.establish_storage_group_srdf('test_sg', 1)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_failover_storage_group_srdf(self, mck_modify):
        """Test failover_storage_group_srdf."""
        result = self.srdf.failover_storage_group_srdf('test_sg', 1)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'modify_resource',
                       return_value={'success': True})
    def test_failback_storage_group_srdf(self, mck_modify):
        """Test failback_storage_group_srdf."""
        result = self.srdf.failback_storage_group_srdf('test_sg', 1)
        self.assertIsNotNone(result)

    @mock.patch.object(common.CommonFunctions, 'delete_resource')
    def test_delete_storage_group_srdf(self, mck_delete):
        """Test delete_storage_group_srdf."""
        self.srdf.delete_storage_group_srdf('test_sg', 1)
        mck_delete.assert_called_once()

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'directorId': ['RF-1F', 'RF-2F']})
    def test_get_rdf_director_list(self, mck_get):
        """Test get_rdf_director_list."""
        result = self.srdf.get_rdf_director_list()
        self.assertEqual(['RF-1F', 'RF-2F'], result)

    @mock.patch.object(common.CommonFunctions, 'delete_resource')
    def test_delete_rdf_group(self, mck_delete):
        """Test delete_rdf_group."""
        self.srdf.delete_rdf_group(1)
        mck_delete.assert_called_once()

    def test_delegation_from_replication(self):
        """Test that replication module delegates to srdf module."""
        replication = self.conn.replication
        with mock.patch.object(
                common.CommonFunctions, 'get_request',
                return_value={'rdfGroupID': [1, 2]}):
            result = replication.get_rdf_group_list()
            self.assertEqual([1, 2], result)
