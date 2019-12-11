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

"""
OpenStack test_migrate.py.

Test file for migrate.py and migrate_utils.py
"""
import platform

from . import pyu4v_common_data as pcd  # noqa: H304
from . import pyu4v_fakes as pf  # noqa: H304
from PyU4V import provisioning
from PyU4V import rest_requests
from PyU4V.tools.openstack import migrate_utils
from PyU4V import univmax_conn
from PyU4V.utils import exception

import mock
import testtools


class TestMigrate(testtools.TestCase):
    """Test cases for migrate script."""

    def setUp(self):
        """Set up the test class."""
        super(TestMigrate, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            conn = univmax_conn.U4VConn()
        self.utils = migrate_utils.MigrateUtils(conn)

    def test_get_masking_view_component_dict_old(self):
        """Test for get_masking_view_component_dict, SMIS case."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_1)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('No_SLO', component_dict['no_slo'])
        self.assertEqual('MV', component_dict['postfix'])

    def test_get_masking_view_component_dict_slo_old(self):
        """Test for get_masking_view_component_dict, SMIS case with SLO."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_2)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('Diamond', component_dict['slo'])
        self.assertEqual('NONE', component_dict['workload'])
        self.assertEqual('MV', component_dict['postfix'])

    def test_get_masking_view_component_dict_slo_workload_old(self):
        """Test for get_masking_view_component_dict.

        SMIS, SLO and workload.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_3)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('Diamond', component_dict['slo'])
        self.assertEqual('DSS', component_dict['workload'])
        self.assertEqual('MV', component_dict['postfix'])

    def test_get_masking_view_component_dict_slo_old_2(self):
        """Test for get_masking_view_component_dict.

        SMIS, SLO, test 2.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_4)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('Silver', component_dict['slo'])
        self.assertEqual('NONE', component_dict['workload'])
        self.assertEqual('MV', component_dict['postfix'])

    def test_get_masking_view_component_dict_compression_disabled_old(self):
        """Test for get_masking_view_component_dict.

        SMIS and compression disabled.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_5)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('Bronze', component_dict['slo'])
        self.assertEqual('OLTP', component_dict['workload'])
        self.assertEqual('-CD', component_dict['CD'])

    def test_get_masking_view_component_dict_replication_enabled_old(self):
        """Test for get_masking_view_component_dict.

         SMIS and compression enabled.
         """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_6)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('Diamond', component_dict['slo'])
        self.assertEqual('OLTP', component_dict['workload'])
        self.assertEqual('-RE', component_dict['RE'])

    def test_get_masking_view_component_dict_host_with_dashes_no_slo_old(
            self):
        """Test for get_masking_view_component_dict.

        SMIS and host with dashes.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_7)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('host-with-dashes', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('No_SLO', component_dict['no_slo'])
        self.assertEqual('MV', component_dict['postfix'])

    def test_get_masking_view_component_dict_host_with_dashes_old(self):
        """Test for get_masking_view_component_dict.

        SMIS and host with dashes.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_8)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('host-with-dashes', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('Diamond', component_dict['slo'])
        self.assertEqual('NONE', component_dict['workload'])
        self.assertEqual('MV', component_dict['postfix'])

    def test_get_masking_view_component_dict_new(self):
        """Test for get_masking_view_component_dict REST."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_1, 'test')
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('myportgroup', component_dict['portgroup'])
        self.assertEqual('MV', component_dict['postfix'])

    def test_get_masking_view_component_dict_mismatch(self):
        """Test for get_masking_view_component_dict REST mismatch."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_1)
        self.assertIsNone(component_dict)

    def test_get_masking_view_component_dict_portgroup_dashes_new(self):
        """Test for get_masking_view_component_dict.

        REST and portgroup with dashes.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_2, 'test')
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('portgroup-with-dashes', component_dict['portgroup'])

    def test_get_masking_view_component_dict_portgroup_dashes_mismatch(self):
        """Test for get_masking_view_component_dict.

        Port group with dashes mismatch.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_2)
        self.assertIsNone(component_dict)

    def test_get_masking_view_component_dict_host_dashes_new(self):
        """Test for get_masking_view_component_dict.

        REST and host with dashes.
        """
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_3, 'test')
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('host-with-dash', component_dict['host'])
        self.assertEqual('I', component_dict['protocol'])
        self.assertEqual('myportgroup', component_dict['portgroup'])

    def test_get_masking_view_component_dict_host_dashes_mismatch(self):
        """Test for get_masking_view_component_dict."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_3)
        self.assertIsNone(component_dict)

    def test_get_storage_group_component_dict_no_slo_new(self):
        """Test for get_storage_group_component_dict.

        REST and no SLO.
        """
        component_dict = self.utils.get_storage_group_component_dict(
            self.data.rest_sg_1)
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('No_SLO', component_dict['no_slo'])
        self.assertEqual('os-iscsi-pg', component_dict['portgroup'])
        self.assertIsNone(component_dict['sloworkload'])
        self.assertIsNone(component_dict['srp'])

    def test_get_storage_group_component_dict_slo_workload_2(self):
        """Test for get_storage_group_component_dict.

        SLO, workload and test 2.
        """
        component_dict = self.utils.get_storage_group_component_dict(
            self.data.rest_sg_4)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('SRP_1', component_dict['srp'])
        self.assertEqual('os-iscsi-pg', component_dict['portgroup'])
        self.assertEqual('DiamodOLTP', component_dict['sloworkload'])
        self.assertIsNone(component_dict['no_slo'])

    def test_get_storage_group_component_dict_compression_disabled(self):
        """Test for get_storage_group_component_dict.

        Compression disabled.
        """
        component_dict = self.utils.get_storage_group_component_dict(
            self.data.rest_sg_2)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('SRP_1', component_dict['srp'])
        self.assertEqual('os-iscsi-pg', component_dict['portgroup'])
        self.assertEqual('DiamodNONE', component_dict['sloworkload'])
        self.assertEqual('-CD', component_dict['after_pg'])
        self.assertIsNone(component_dict['no_slo'])

    def test_get_storage_group_component_dict_replication_enabled(self):
        """Test for get_storage_group_component_dict.

        Replication enabled.
        """
        component_dict = self.utils.get_storage_group_component_dict(
            self.data.rest_sg_4)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('SRP_1', component_dict['srp'])
        self.assertEqual('os-iscsi-pg', component_dict['portgroup'])
        self.assertEqual('DiamodOLTP', component_dict['sloworkload'])
        self.assertEqual('-RE', component_dict['after_pg'])
        self.assertIsNone(component_dict['no_slo'])

    def test_get_storage_group_component_dict_slo_no_workload(self):
        """Test for get_storage_group_component_dict.

        SLO and no workload.
        """
        component_dict = self.utils.get_storage_group_component_dict(
            self.data.rest_sg_3)
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('SRP_1', component_dict['srp'])
        self.assertEqual('os-iscsi-pg', component_dict['portgroup'])
        self.assertEqual('DiamodNONE', component_dict['sloworkload'])
        self.assertIsNone(component_dict['no_slo'])

    def test_get_storage_group_component_dict_dashes(self):
        """Test for get_storage_group_component_dict, dashes."""
        component_dict = self.utils.get_storage_group_component_dict(
            self.data.rest_sg_5)
        self.assertEqual('host-with-dashes', component_dict['host'])
        self.assertEqual('OS', component_dict['prefix'])
        self.assertEqual('SRP_1', component_dict['srp'])
        self.assertEqual('DiamodOLTP', component_dict['sloworkload'])
        self.assertEqual('myportgroup', component_dict['portgroup'])
        self.assertEqual('-RE', component_dict['after_pg'])

    def test_check_input_yes(self):
        """Test for check_input, yes"""
        self.assertTrue(self.utils.check_input('Y', 'Y'))
        self.assertTrue(self.utils.check_input('y', 'Y'))
        self.assertTrue(self.utils.check_input('YES', 'Y'))
        self.assertTrue(self.utils.check_input('yes', 'Y'))
        self.assertTrue(self.utils.check_input('Yes', 'Y'))
        self.assertTrue(self.utils.check_input('yeS', 'Y'))
        self.assertFalse(self.utils.check_input('ye', 'Y'))
        self.assertFalse(self.utils.check_input('oui', 'Y'))

    def test_check_input_no(self):
        """Test for check_input, no."""
        self.assertTrue(self.utils.check_input('N', 'N'))
        self.assertTrue(self.utils.check_input('n', 'N'))
        self.assertTrue(self.utils.check_input('NO', 'N'))
        self.assertTrue(self.utils.check_input('no', 'N'))
        self.assertTrue(self.utils.check_input('No', 'N'))
        self.assertTrue(self.utils.check_input('nO', 'N'))
        self.assertFalse(self.utils.check_input('non', 'N'))

    def test_check_input_exit(self):
        """Test for check_input, exit"""
        self.assertTrue(self.utils.check_input('X', 'X'))
        self.assertTrue(self.utils.check_input('x', 'X'))
        self.assertTrue(self.utils.check_input('Exit', 'X'))
        self.assertTrue(self.utils.check_input('eXiT', 'X'))
        self.assertTrue(self.utils.check_input('EXIT', 'X'))
        self.assertFalse(self.utils.check_input('quit', 'X'))

    def test_validate_masking_view_true(self):
        """Test for validate_masking_view."""
        self.assertTrue(self.utils.validate_masking_view(
            self.data.rest_mv_1, 'revert'))

    def test_validate_masking_view_false(self):
        """Test for validate_masking_view, false."""
        self.assertFalse(self.utils.validate_masking_view(
            self.data.rest_mv_1))

    def test_smart_print(self):
        """Test for smart_print."""
        print_str = "%s supports smart_print."
        self.utils.smart_print(print_str, migrate_utils.DEBUG,
                               platform.python_version())

    def test_smart_print_multiple_args(self):
        """Test for smart_print, multiple args."""
        arg_1 = 'Hello'
        arg_2 = 'everyone!'
        print_str = "%s %s %s supports multiple args in smart_print."
        self.utils.smart_print(
            print_str, migrate_utils.DEBUG,
            arg_1, arg_2, platform.python_version())

    def test_smart_print_multiple_args_exception(self):
        """Test for smart_print, multiple args exception."""
        arg_1 = 'Woops!'
        print_str = "%s %s %s problem in smart_print."
        self.assertRaises(TypeError,
                          self.utils.smart_print, print_str, arg_1,
                          platform.python_version())
        arg_2 = 'woops!'
        print_str = "%s problem in smart_print."
        self.assertRaises(TypeError,
                          self.utils.smart_print, print_str,
                          migrate_utils.DEBUG, arg_1,
                          arg_2, platform.python_version())

    def test_verify_protocol(self):
        """Test for verify_protocol."""
        self.assertTrue(self.utils.verify_protocol('I'))
        self.assertFalse(self.utils.verify_protocol('i'))
        self.assertFalse(self.utils.verify_protocol('I-'))
        self.assertFalse(self.utils.verify_protocol('random'))
        self.assertTrue(self.utils.verify_protocol('F'))
        self.assertFalse(self.utils.verify_protocol('f'))
        self.assertFalse(self.utils.verify_protocol('F-'))

    def test_get_object_components(self):
        """Test for get_object_components."""
        regex_str = '^(?P<prefix>OS)-(?P<host>.+?)((?P<srp>SRP.+?)-' \
                    '(?P<slo>.+?)-(?P<workload>.+?)|(?P<no_slo>No_SLO))-' \
                    '(?P<protocol>I|F)(?P<CD>-CD|s*)(?P<RE>-RE|s*)-' \
                    '(?P<postfix>MV)$'
        input_str = 'OS-myhost-SRP_1-Silver-NONE-I-MV'
        object_dict = self.utils.get_object_components(
            regex_str, input_str)

        self.assertEqual('OS', object_dict['prefix'])
        self.assertEqual('myhost-', object_dict['host'])
        self.assertEqual('SRP_1', object_dict['srp'])
        self.assertEqual('I', object_dict['protocol'])
        self.assertEqual('Silver', object_dict['slo'])
        self.assertEqual('NONE', object_dict['workload'])
        self.assertEqual('MV', object_dict['postfix'])

    def test_get_object_components_invalid(self):
        """Test for get_object_components, invalid."""
        regex_str = (r'^(?P<prefix>OS)-(?P<host>.+?)((?P<srp>SRP.+?)-'
                     r'(?P<slo>.+?)-(?P<workload>.+?)|(?P<no_slo>No_SLO))-'
                     r'(?P<protocol>I|F)(?P<CD>-CD|s*)(?P<RE>-RE|s*)-'
                     r'(?P<postfix>MV)$')
        input_str = 'random-masking-view'
        self.assertIsNone(self.utils.get_object_components(
            regex_str, input_str))

    def test_get_object_components_and_correct_host(self):
        """Test for get_object_components_and_correct_host."""
        regex_str = (r'^(?P<prefix>OS)-(?P<host>.+?)((?P<srp>SRP.+?)-'
                     r'(?P<slo>.+?)-(?P<workload>.+?)|(?P<no_slo>No_SLO))-'
                     r'(?P<protocol>I|F)(?P<CD>-CD|s*)(?P<RE>-RE|s*)-'
                     r'(?P<postfix>MV)$')
        input_str = 'OS-myhost-SRP_1-Silver-NONE-I-MV'
        object_dict = self.utils.get_object_components_and_correct_host(
            regex_str, input_str)
        self.assertEqual('myhost', object_dict['host'])

    def test_get_object_components_and_correct_host_invalid(self):
        """Test for get_object_components_and_correct_host, invalid."""
        regex_str = (r'^(?P<prefix>OS)-(?P<host>.+?)((?P<srp>SRP.+?)-'
                     r'(?P<slo>.+?)-(?P<workload>.+?)|(?P<no_slo>No_SLO))-'
                     r'(?P<protocol>I|F)(?P<CD>-CD|s*)(?P<RE>-RE|s*)-'
                     r'(?P<postfix>MV)$')
        input_str = 'random-masking-view'
        self.assertIsNone(self.utils.get_object_components_and_correct_host(
            regex_str, input_str))

    def test_check_mv_for_migration(self):
        """Test for check_mv_for_migration."""
        self.assertTrue(self.utils.check_masking_view_for_migration(
            self.data.smis_mv_2))
        self.assertTrue(self.utils.check_masking_view_for_migration(
            self.data.rest_mv_1, 'test'))
        self.assertFalse(self.utils.check_masking_view_for_migration(
            self.data.smis_mv_2, 'test'))
        self.assertFalse(self.utils.check_masking_view_for_migration(
            self.data.rest_mv_1))

    def test_compile_new_element_names(self):
        """Test for compile_new_element_names."""
        element_dict = self.utils.compile_new_element_names(
            self.data.smis_mv_3, self.data.m_portgroup,
            self.data.m_host_name, self.data.smis_sg_3)
        self.assertEqual(
            'OS-myhost-I-myportgroup-SG', element_dict['new_sg_parent_name'])
        self.assertEqual('Diamond', element_dict['service_level'])
        self.assertEqual('myhost', element_dict['initiator_group'])
        self.assertEqual(
            'OS-myhost-I-myportgroup-MV', element_dict['new_mv_name'])
        self.assertEqual('myportgroup', element_dict['port_group'])
        self.assertEqual(
            'OS-myhost-SRP_1-DiamondDSS-myportgroup',
            element_dict['new_sg_name'])
        self.assertEqual('DSS', element_dict['workload'])
        self.assertEqual('SRP_1', element_dict['srp'])

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       return_value=pcd.CommonData.m_storagegroup)
    def test_compile_new_element_names_revert(self, mock_sg):
        """Test for compile_new_element_names, revert case."""
        element_dict = self.utils.compile_new_element_names(
            self.data.rest_mv_1, self.data.m_portgroup,
            self.data.m_host_name, self.data.rest_sg_3, 'revert')
        self.assertEqual('myhost', element_dict['initiator_group'])
        self.assertEqual('OS-myhost-SRP_1-Diamond-OLTP-I-MV',
                         element_dict['new_mv_name'])
        self.assertEqual('OS-myhost-SRP_1-Diamond-OLTP-I-SG',
                         element_dict['new_sg_name'])
        self.assertEqual('myportgroup', element_dict['port_group'])
        self.assertEqual('Diamond', element_dict['service_level'])
        self.assertEqual('OLTP', element_dict['workload'])
        self.assertEqual('SRP_1', element_dict['srp'])

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_storage_group',
                       side_effect=exception.ResourceNotFoundException(
                           'exception'))
    def test_compile_new_element_names_revert_no_storage_group(self, mock_sg):
        """Test for compile_new_element_names, no storage group."""
        element_dict = self.utils.compile_new_element_names(
            self.data.rest_mv_1, self.data.portgroup,
            self.data.m_host_name, self.data.rest_sg_3, 'revert')
        self.assertEqual({}, element_dict)

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       return_value={
                           'portGroupId': pcd.CommonData.m_portgroup,
                           'hostId': pcd.CommonData.m_initiatorgroup,
                           'storageGroupId': pcd.CommonData.m_sg_name,
                       })
    def test_get_elements_from_masking_view(
            self, mock_details):
        """Test for get_elements_from_masking_view."""
        masking_view_components = self.utils.get_elements_from_masking_view(
            self.data.smis_mv_1)
        self.assertEqual(
            self.data.m_sg_name, masking_view_components['storagegroup'])
        self.assertEqual(
            self.data.m_portgroup, masking_view_components['portgroup'])
        self.assertEqual(
            self.data.m_initiatorgroup,
            masking_view_components['initiatorgroup'])

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       side_effect=exception.ResourceNotFoundException(
                           'exception'))
    def test_get_elements_from_masking_view_exception(
            self, mock_details):
        """Test for get_elements_from_masking_view, exception."""
        self.assertRaises(exception.ResourceNotFoundException,
                          self.utils.get_elements_from_masking_view,
                          self.data.smis_mv_1)

    def test_print_component_dict(self):
        """Test for print_component_dict."""
        component_dict = (
            self.utils.print_component_dict(self.data.smis_mv_1))
        self.assertEqual('MV', component_dict['postfix'])
        self.assertEqual('No_SLO', component_dict['no_slo'])

    def test_print_component_dict_revert(self):
        """Test for print_component_dict, revert."""
        component_dict = (
            self.utils.print_component_dict(self.data.rest_mv_2, revert=True))
        self.assertEqual('myhost', component_dict['host'])
        self.assertEqual('portgroup-with-dashes', component_dict['portgroup'])
        self.assertEqual('I', component_dict['protocol'])

    def test_print_component_dict_mismatch(self):
        """Test for print_component_dict, mismatch."""
        component_dict = (
            self.utils.print_component_dict(self.data.smis_mv_2, revert=True))
        self.assertIsNone(component_dict)

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       return_value=pcd.CommonData.m_storagegroup)
    def test_get_element_dict_revert(self, mock_sg):
        """Test for get_element_dict_revert."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_1, revert=True)

        element_dict = self.utils.get_element_dict_revert(
            component_dict, self.data.rest_sg_4, '-RE', "",
            self.data.m_portgroup, self.data.m_host_name)
        self.assertEqual('myhost', element_dict['initiator_group'])
        self.assertEqual('myportgroup', element_dict['port_group'])
        self.assertEqual('OS-myhost-SRP_1-Diamond-OLTP-I-RE-SG',
                         element_dict['new_sg_name'])
        self.assertEqual('OS-myhost-SRP_1-Diamond-OLTP-I-RE-MV',
                         element_dict['new_mv_name'])
        self.assertEqual('Diamond', element_dict['service_level'])
        self.assertEqual('OLTP', element_dict['workload'])

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       return_value={'slo': 'Diamond'})
    def test_get_element_dict_revert_no_workload(self, mock_sg):
        """Test for get_element_dict_revert, no workload."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.rest_mv_1, revert=True)

        element_dict = self.utils.get_element_dict_revert(
            component_dict, self.data.rest_sg_2, '-CD', "",
            self.data.m_portgroup, self.data.m_host_name)
        self.assertEqual('myhost', element_dict['initiator_group'])
        self.assertEqual('myportgroup', element_dict['port_group'])
        self.assertEqual('OS-myhost-SRP_1-Diamond-NONE-I-CD-SG',
                         element_dict['new_sg_name'])
        self.assertEqual('OS-myhost-SRP_1-Diamond-NONE-I-CD-MV',
                         element_dict['new_mv_name'])
        self.assertEqual('Diamond', element_dict['service_level'])

    def test_get_element_dict(self):
        """Test for get_element_dict."""
        component_dict = self.utils.get_masking_view_component_dict(
            self.data.smis_mv_4)

        element_dict = self.utils.get_element_dict(
            component_dict, '-CD', "",
            self.data.m_portgroup, self.data.m_host_name)
        self.assertEqual('myhost', element_dict['initiator_group'])
        self.assertEqual('myportgroup', element_dict['port_group'])
        self.assertEqual('OS-myhost-SRP_1-SilverNONE-myportgroup-CD',
                         element_dict['new_sg_name'])
        self.assertEqual('OS-myhost-I-myportgroup-MV',
                         element_dict['new_mv_name'])
        self.assertEqual('Silver', element_dict['service_level'])

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'is_child_storage_group_in_parent_storage_group',
                       return_value=True)
    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       return_value=pcd.CommonData.m_storagegroup)
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       return_value=pcd.CommonData.m_maskingview)
    def test_validate_existing_masking_view(
            self, mock_mv, mock_sg, mock_child):
        """Test for validate_existing_masking_view."""
        new_masking_view_details = self.utils.get_masking_view(
            self.data.smis_mv_1)
        element_dict = self.utils.compile_new_element_names(
            self.data.smis_mv_1, self.data.m_portgroup,
            self.data.m_initiatorgroup,
            self.data.smis_sg_1)
        self.assertTrue(self.utils.validate_existing_masking_view(
            new_masking_view_details, self.data.m_portgroup,
            self.data.m_host_name, element_dict))

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       return_value={
                           'portGroupId': pcd.CommonData.m_portgroup,
                           'hostId': pcd.CommonData.m_host_name,
                           'storageGroupId': "random_sg",
                           'maskingViewId': pcd.CommonData.rest_mv_1})
    def test_validate_existing_masking_view_false(
            self, mock_mv):
        """Test for validate_existing_masking_view, false."""
        new_masking_view_details = self.utils.get_masking_view(
            self.data.smis_mv_1)
        element_dict = self.utils.compile_new_element_names(
            self.data.smis_mv_1, self.data.m_portgroup,
            self.data.m_initiatorgroup,
            self.data.smis_sg_1)
        self.assertFalse(self.utils.validate_existing_masking_view(
            new_masking_view_details, self.data.m_portgroup,
            self.data.m_host_name, element_dict))

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       return_value=pcd.CommonData.m_storagegroup)
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       return_value={
                           'portGroupId': pcd.CommonData.m_portgroup,
                           'hostId': pcd.CommonData.m_host_name,
                           'storageGroupId': pcd.CommonData.smis_sg_8,
                           'maskingViewId': pcd.CommonData.smis_mv_1})
    def test_validate_existing_masking_view_revert_true(
            self, mock_mv, mock_sg):
        """Test for validate_existing_masking_view, revert true"""
        new_masking_view_details = self.utils.get_masking_view(
            self.data.rest_mv_1)
        self.assertTrue(self.utils.validate_existing_masking_view(
            new_masking_view_details, self.data.m_portgroup,
            self.data.m_host_name, self.data.element_dict_revert, revert=True))

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       return_value={
                           'portGroupId': pcd.CommonData.m_portgroup,
                           'hostId': pcd.CommonData.m_host_name,
                           'storageGroupId': "random_sg",
                           'maskingViewId': pcd.CommonData.rest_mv_1})
    def test_validate_existing_masking_view_revert_false(
            self, mock_mv):
        """Test for validate_existing_masking_view, revert false."""
        new_masking_view_details = self.utils.get_masking_view(
            self.data.rest_mv_1)
        self.assertFalse(self.utils.validate_existing_masking_view(
            new_masking_view_details, self.data.portgroup,
            self.data.m_host_name, self.data.element_dict_revert, revert=True))

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_storage_group',
                       return_value=pcd.CommonData.m_storagegroup)
    def test_get_storage_group(self, mock_sg):
        """Test for get_storage_group."""
        storage_group = self.utils.get_storage_group(
            self.data.smis_sg_1)
        self.assertEqual('Diamond', storage_group['slo'])
        self.assertEqual('OLTP', storage_group['workload'])

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_storage_group',
                       side_effect=exception.ResourceNotFoundException(
                           'exception'))
    def test_get_storage_group_none(self, mock_sg):
        """Test for get_storage_group, none."""
        self.assertIsNone(self.utils.get_storage_group(
            self.data.smis_sg_1))

    @mock.patch.object(
        provisioning.ProvisioningFunctions,
        'create_volume_from_storage_group_return_id',
        return_value='00001')
    @mock.patch.object(
        provisioning.ProvisioningFunctions, 'create_storage_group')
    @mock.patch.object(
        provisioning.ProvisioningFunctions,
        'add_child_storage_group_to_parent_group')
    def test_create_child_storage_group_and_add_to_parent(
            self, mock_add, mock_create, mock_vol):
        """Test for create_child_storage_group_and_add_to_parent."""
        element_dict = self.utils.compile_new_element_names(
            self.data.smis_mv_1, self.data.m_portgroup,
            self.data.m_initiatorgroup,
            self.data.smis_sg_1)
        self.utils.create_child_storage_group_and_add_to_parent(
            element_dict)
        mock_add.assert_called_once()
        mock_add.reset_mock()

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'create_child_storage_group_and_add_to_parent')
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_storage_group',
                       side_effect=exception.ResourceNotFoundException(
                           'exception'))
    @mock.patch.object(
        provisioning.ProvisioningFunctions, 'create_empty_storage_group')
    def test_get_or_create_cascaded_storage_group(
            self, mock_empty, mock_sg, mock_create):
        """Test for get_or_create_cascaded_storage_group."""
        element_dict = self.utils.compile_new_element_names(
            self.data.smis_mv_2, self.data.m_portgroup,
            self.data.m_initiatorgroup,
            self.data.smis_sg_2)
        self.utils.get_or_create_cascaded_storage_group(element_dict)
        mock_empty.assert_called_once()
        mock_empty.reset_mock()

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'create_masking_view_existing_components')
    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_or_create_cascaded_storage_group')
    def test_get_or_create_elements(self, mock_sg, mock_mv):
        """Test for get_or_create_elements."""
        element_dict = self.utils.compile_new_element_names(
            self.data.smis_mv_2, self.data.m_portgroup,
            self.data.m_initiatorgroup,
            self.data.smis_sg_2)
        self.utils.get_or_create_elements(element_dict)
        mock_mv.assert_called_once()
        mock_mv.reset_mock()

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_or_create_cascaded_storage_group',
                       return_value=None)
    def test_get_or_create_elements_except(self, mock_sg):
        """Test for get_or_create_elements, exception."""
        element_dict = self.utils.compile_new_element_names(
            self.data.smis_mv_2, self.data.m_portgroup,
            self.data.m_initiatorgroup,
            self.data.smis_sg_2)
        self.assertRaises(exception.ResourceNotFoundException,
                          self.utils.get_or_create_elements, element_dict)

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'create_masking_view_existing_components')
    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       side_effect=[None, pcd.CommonData.m_storagegroup])
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'create_non_empty_storage_group')
    def test_get_or_create_elements_revert(
            self, mock_create_sg, mock_sg, mock_cc):
        """Test for get_or_create_elements, revert."""
        self.utils.get_or_create_elements(
            self.data.element_dict_revert, revert=True)
        mock_create_sg.assert_called_once()
        mock_create_sg.reset_mock()

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       return_value=pcd.CommonData.m_maskingview)
    def test_get_masking_view(self, mock_sg):
        """Test for get_masking_view."""
        masking_view = self.utils.get_masking_view(
            self.data.smis_sg_1)
        self.assertEqual('OS-myhost-I-myportgroup-MV',
                         masking_view['maskingViewId'])
        self.assertEqual('myportgroup', masking_view['portGroupId'])
        self.assertEqual('OS-myhost-I-myportgroup-SG',
                         masking_view['storageGroupId'])

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       side_effect=exception.ResourceNotFoundException(
                           'exception'))
    def test_get_masking_view_none(self, mock_sg):
        """Test for get_masking_view."""
        self.assertIsNone(self.utils.get_masking_view(
            self.data.smis_mv_1))

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       return_value=pcd.CommonData.mv_components)
    def test_get_or_create_masking_view(self, mock_mv):
        """Test for get_or_create_masking_view."""
        masking_view_details = self.utils.get_or_create_masking_view(
            self.data.element_dict, self.data.m_portgroup,
            self.data.m_host_name)
        self.assertEqual('myhost', masking_view_details['hostId'])
        self.assertEqual('OS-myhost-No_SLO-os-iscsi-pg',
                         masking_view_details['storageGroupId'])
        self.assertEqual('myportgroup', masking_view_details['portGroupId'])
        self.assertEqual('OS-myhost-I-myportgroup-MV',
                         masking_view_details['maskingViewId'])

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       return_value=pcd.CommonData.m_storagegroup)
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'create_masking_view_existing_components')
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view',
                       side_effect=[None, pcd.CommonData.mv_components])
    def test_get_or_create_masking_view_none(
            self, mock_mv, mock_create, mock_sg):
        """Test for get_or_create_masking_view, none."""
        masking_view_details = self.utils.get_or_create_masking_view(
            self.data.element_dict, self.data.m_portgroup,
            self.data.m_host_name)
        self.assertEqual('myhost', masking_view_details['hostId'])
        self.assertEqual('OS-myhost-No_SLO-os-iscsi-pg',
                         masking_view_details['storageGroupId'])
        self.assertEqual('myportgroup', masking_view_details['portGroupId'])
        self.assertEqual('OS-myhost-I-myportgroup-MV',
                         masking_view_details['maskingViewId'])

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'move_volumes_between_storage_groups',
                       return_value={
                           'storageGroupId': pcd.CommonData.smis_sg_1})
    def test_move_volumes_from_source_to_target(self, mock_mv):
        """Test for move_vols_from_source_to_target."""
        source_sg = self.utils.move_volumes_from_source_to_target(
            self.data.device_list, self.data.smis_sg_2,
            self.data.rest_sg_3, False)
        self.assertEqual(self.data.smis_sg_1, source_sg['storageGroupId'])

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'create_volume_from_storage_group_return_id')
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'move_volumes_between_storage_groups',
                       return_value={
                           'storageGroupId': pcd.CommonData.smis_sg_1})
    def test_move_volumes_from_source_to_target_new_vol(
            self, mock_mv, mock_create_vol):
        """Test for move_vols_from_source_to_target, new volume."""
        self.utils.move_volumes_from_source_to_target(
            self.data.device_list, self.data.smis_sg_2,
            self.data.rest_sg_3, True)
        mock_create_vol.assert_called_once()
        mock_create_vol.reset_mock()

    def test_validate_list_true(self):
        """Test for validate_list, true."""
        subset_list = ['0064F', '0088E', '00890']
        self.assertTrue(
            self.utils.validate_list(self.data.device_list, subset_list))

    def test_validate_list_false(self):
        """Test for validate_list, false."""
        subset_list = ['00000']
        self.assertFalse(
            self.utils.validate_list(self.data.device_list, subset_list))

    def test_choose_subset_volumes(self):
        """Test for choose_subset_volumes."""
        user_input = "'0064F', '0088E', '00890'"
        with mock.patch.object(migrate_utils.MigrateUtils,
                               'input', return_value=user_input):
            device_list, create_vol = self.utils.choose_subset_volumes(
                self.data.smis_sg_1, self.data.device_list)
        self.assertIn('0064F', device_list)
        self.assertIn('0088E', device_list)
        self.assertIn('00890', device_list)

    def test_choose_subset_volumes_no_quotes(self):
        """Test for choose_subset_volumes, no quotes."""
        user_input = "0064F, 0088E, 00890"
        with mock.patch.object(migrate_utils.MigrateUtils,
                               'input', return_value=user_input):
            device_list, create_vol = self.utils.choose_subset_volumes(
                self.data.smis_sg_1, self.data.device_list)
        self.assertIn('0064F', device_list)
        self.assertIn('0088E', device_list)
        self.assertIn('00890', device_list)

    def test_choose_subset_volumes_no_quotes_or_spaces(self):
        """Test for choose_subset_volumes, no quotes or spaces."""
        user_input = "0064F,0088E,00890"
        with mock.patch.object(migrate_utils.MigrateUtils,
                               'input', return_value=user_input):
            device_list, create_vol = self.utils.choose_subset_volumes(
                self.data.smis_sg_1, self.data.device_list)
        self.assertIn('0064F', device_list)
        self.assertIn('0088E', device_list)
        self.assertIn('00890', device_list)

    def test_choose_subset_volumes_spaces(self):
        """Test for choose_subset_volumes, spaces."""
        user_input = "0064F 0088E 00890"
        with mock.patch.object(migrate_utils.MigrateUtils,
                               'input', return_value=user_input):
            device_list, create_vol = self.utils.choose_subset_volumes(
                self.data.smis_sg_1, self.data.device_list)
        self.assertFalse(device_list)

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'input', return_value='Y')
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_volumes_from_storage_group',
                       return_value=pcd.CommonData.device_list)
    def test_get_volume_list_full(self, mock_vols, mock_yes):
        """Test for get_volume_list, full."""
        volume_list, create_vol = (
            self.utils.get_volume_list(self.data.smis_sg_1))
        self.assertEqual(self.data.device_list, volume_list)
        self.assertTrue(create_vol)

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'choose_subset_volumes',
                       return_value=(['00890'], False))
    @mock.patch.object(migrate_utils.MigrateUtils,
                       'input', return_value='N')
    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_volumes_from_storage_group',
                       return_value=pcd.CommonData.device_list)
    def test_get_volume_list_subset(self, mock_vols, mock_no, mock_subset):
        """Test for get_volume_list, subset."""
        volume_list, create_vol = (
            self.utils.get_volume_list(self.data.smis_sg_1))
        mock_subset.assert_called_once()
        mock_subset.reset_mock()

        self.assertEqual(['00890'], volume_list)
        self.assertFalse(create_vol)

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       return_value=pcd.CommonData.m_storagegroup)
    @mock.patch.object(migrate_utils.MigrateUtils,
                       'input', return_value='Y')
    def test_choose_sg(self, mock_yes, mock_sg):
        """Test for choose_sg."""
        element_dict, child_storage_group = self.utils.choose_storage_group(
            self.data.rest_mv_1,
            [self.data.rest_sg_6, self.data.rest_sg_3],
            self.data.m_portgroup, self.data.m_initiatorgroup, True)
        self.assertEqual(
            'OS-myhost-SRP_1-Diamond-OLTP-I-CD-MV',
            element_dict['new_mv_name'])
        self.assertEqual(
            'OS-myhost-SRP_1-Diamond-OLTP-I-CD-SG',
            element_dict['new_sg_name'])
        self.assertEqual('SRP_1', element_dict['srp'])
        self.assertEqual('Diamond', element_dict['service_level'])
        self.assertEqual('OLTP', element_dict['workload'])
        self.assertEqual('myportgroup', element_dict['port_group'])
        self.assertEqual('myinitiatorgroup', element_dict['initiator_group'])

        self.assertEqual(
            'OS-myhost-SRP_1-DiamodOLTP-myportgroup-CD', child_storage_group)

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       side_effect=[pcd.CommonData.source_sg_details,
                                    pcd.CommonData.m_storagegroup])
    def test_set_qos_target_no_host_io(self, mock_sg):
        """Test for set_qosm no host IO."""
        with mock.patch.object(provisioning.ProvisioningFunctions,
                               'modify_storage_group') as mock_modify:
            self.utils.set_qos(
                self.data.smis_sg_2, self.data.rest_sg_3)
            mock_modify.assert_called_once()

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       side_effect=[pcd.CommonData.source_sg_details,
                                    pcd.CommonData.source_sg_details])
    def test_set_qos_target_qos_same_as_source(self, mock_sg):
        """Test for set_qos, same as source."""
        with mock.patch.object(provisioning.ProvisioningFunctions,
                               'modify_storage_group') as mock_modify:
            self.utils.set_qos(
                self.data.smis_sg_2, self.data.rest_sg_3)
            mock_modify.assert_not_called()

    @mock.patch.object(migrate_utils.MigrateUtils,
                       'get_storage_group',
                       side_effect=[pcd.CommonData.source_sg_details,
                                    pcd.CommonData.target_sg_details])
    def test_set_qos_target_different_host_io(self, mock_sg):
        """Test for set_qos, different host IO."""
        with mock.patch.object(provisioning.ProvisioningFunctions,
                               'modify_storage_group') as mock_modify:
            self.utils.set_qos(
                self.data.smis_sg_2, self.data.rest_sg_3)
            mock_modify.assert_called_once()

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'is_child_storage_group_in_parent_storage_group',
                       return_value=False)
    @mock.patch.object(migrate_utils.MigrateUtils,
                       '_add_child_to_parent')
    def test_existing_child_storage_group_check(self, mock_add, mock_check):
        """Test for _existing_child_storage_group_check."""
        self.utils._existing_child_storage_group_check(
            self.data.element_dict['new_sg_name'],
            self.data.element_dict['new_sg_parent_name'])
        mock_add.assert_called_once()
