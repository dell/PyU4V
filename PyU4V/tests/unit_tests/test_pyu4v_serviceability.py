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
"""test_pyu4v_serviceability.py."""

import testtools

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants
from PyU4V import common

ARRAY_ID = constants.ARRAY_ID


class PyU4VServiceabilityTest(testtools.TestCase):
    """Test Serviceability."""

    def setUp(self):
        """Setup."""
        super(PyU4VServiceabilityTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.common = self.conn.common
            self.serviceability = self.conn.serviceability

    def test_get_local_system(self):
        """Test get_local_system."""
        result = self.serviceability.get_local_system()
        self.assertEqual(self.data.serviceability_symmetrix, result)

    def test_get_ntp_settings(self):
        """Test get_symmetrix_ntp_server."""
        result = self.serviceability.get_ntp_settings()
        self.assertEqual(self.data.ntp_server, result)

    def test_modify_ntp_settings(self):
        """Test modify_ntp_server."""
        modify_ntp_server_result = self.serviceability.modify_ntp_settings(
            ntp_server='10.10.10.10')
        self.assertEqual(self.data.ntp_server, modify_ntp_server_result)

    @mock.patch.object(
        common.CommonFunctions, 'download_file',
        return_value=pf.FakeResponse(200, dict(),
                                     content=b'test_binary_data'))
    def test_download_grab_files(self, mck_dl):
        """Test get_symmetrix."""
        response = self.serviceability.download_grab_files(
            dir_path=".", file_name="test", timeout=10)
        self.assertTrue(response['success'])

    def test_get_ip_configuration(self):
        """Test get_ip_configuration."""
        ip_configuration_result = self.serviceability.get_ip_configuration()
        self.assertEqual(self.data.ip_configuration, ip_configuration_result)

    def test_update_ip_configuration(self):
        """Test update_ip_configuration."""
        update_ip_conf_result = self.serviceability.update_ip_configuration(
            action='UpdateIPV4',
            natone_ip_address='10.10.10.10',
            natone_netmask='10.10.10.10',
            natone_gateway='10.10.10.10',
            nattwo_ip_address='10.10.10.10',
            nattwo_netmask='10.10.10.10',
            nattwo_gateway='10.10.10.10'
        )
        self.assertTrue(update_ip_conf_result)

    def test_update_ipv6_configuration(self):
        """Test update_ip_configuration."""
        update_ip_conf_result = self.serviceability.update_ip_configuration(
            action='UpdateIPV6',
            natone_ip_address='fe80::1445:a902:2421:828e%20',
            natone_netmask='fe80::1445:a902:2421:828e%20',
            natone_gateway='fe80::1445:a902:2421:828e%20',
            nattwo_ip_address='fe80::1445:a902:2421:828e%20',
            nattwo_netmask='fe80::1445:a902:2421:828e%20',
            nattwo_gateway='1fe80::1445:a902:2421:828e%20'
        )
        self.assertTrue(update_ip_conf_result)

    def test_get_application(self):
        """Test get_application."""
        get_application_result = self.serviceability.get_application()
        self.assertEqual(self.data.applications, get_application_result)

    def test_modify_unisphere_service_access(self):
        """Test modify_unisphere_application."""
        result = self.serviceability.modify_unisphere_service_access(
            action='AllowServerAccess')
        self.assertEqual(self.data.unisphere_application, result)

    def test_restart_unisphere_application(self):
        """Test restart_unisphere_application."""
        restart_result = self.serviceability.restart_unisphere_application()
        self.assertTrue(restart_result)

    def test_get_unisphere_application_details(self):
        result = self.serviceability.get_unisphere_application_details()
        self.assertTrue(result)

    def test_get_unisphere_configuration(self):
        result = self.serviceability.get_unisphere_configuration()
        self.assertTrue(result)

    def test_get_symavoid_settings(self):
        response = self.serviceability.get_symavoid_settings()
        self.assertTrue(response)

    def test_update_symavoid_settings(self):
        """Test update_symavoid_settings."""
        result = self.serviceability.update_symavoid_settings(
            action='RemoveFromSymmavoid', symm_list='[000123456789]'
        )
        add = self.serviceability.update_symavoid_settings(
            action='AddToSymmavoid', symm_list='[000123456789]'
        )
        self.assertTrue(result)
        self.assertTrue(add)

    def test_get_solutions_enabler_application(self):
        """Test get_solutions_enabler_application."""
        result = self.serviceability.get_solutions_enabler_application()
        self.assertEqual(self.data.solutions_enabler_application, result)

    def test_modify_solutions_enabler_configuration(self):
        """test updating settings in modify_solutions_enabler_configuration."""
        result = self.serviceability.modify_solutions_enabler_configuration(
            allow_symforce=True, use_access_id='Client'
        )
        self.assertTrue(result)

    def test_modify_nethosts(self):
        result = self.serviceability.modify_nethosts(
            action='add', host_name='10.60.156.63', user='rawstorage')
        remove = self.serviceability.modify_nethosts(
            action='remove', host_name='10.60.156.63', user='rawstorage')
        self.assertTrue(result)
        self.assertTrue(remove)

    def test_get_solutions_enabler_configuration(self):
        """Test get_solutions_enabler_configuration"""
        result = self.serviceability.get_solutions_enabler_configuration()
        self.assertEqual(self.data.solutions_enabler_configuration, result)

    def test_replace_self_signed_certificate(self):
        """Test replace_self_signed_certificate"""
        result = self.serviceability.replace_self_signed_certificate(
            node_name='Semgmt0')
        self.assertEqual(self.data.self_signed_cert_response, result)

    def test_import_custom_certificate(self):
        """Test import custom certificate"""
        with mock.patch.object(
                self.serviceability,
                'import_custom_certificate') as mock_upload:
            node_name = 'Unisphere'
            keyfile = __file__
            certfile = __file__
            trustfile = __file__

            self.serviceability.import_custom_certificate(
                node_name=node_name,
                keyfile=keyfile,
                certfile=certfile,
                trustfile=trustfile
            )

            mock_upload.assert_called_with(
                node_name=node_name,
                keyfile=keyfile,
                certfile=certfile,
                trustfile=trustfile
            )
