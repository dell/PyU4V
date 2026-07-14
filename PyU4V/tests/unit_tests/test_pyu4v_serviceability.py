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
"""test_pyu4v_serviceability.py."""

import testtools

from pathlib import Path
from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants
from PyU4V.utils import exception
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

    def test_get_symavoid_settings_honors_array_override(self):
        """An explicit array ID is used without changing connection state."""
        original_array = self.serviceability.array_id
        with mock.patch.object(
                self.serviceability.common, 'get_request',
                return_value={}) as mock_get:
            self.serviceability.get_symavoid_settings(
                array_id='000123456789')

        mock_get.assert_called_once_with(
            target_uri=f"/{self.serviceability.common.UNI_VERSION}/"
                       f"serviceability/symmetrix/000123456789/"
                       f"application/unisphere/system",
            resource_type=None)
        self.assertEqual(original_array, self.serviceability.array_id)

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
        """Mixed-case valid actions retain their exact REST payloads."""
        responses = [{'action': 'add'}, {'action': 'remove'}]
        with mock.patch.object(
                self.serviceability.common, 'modify_resource',
                side_effect=responses) as mock_modify:
            add_result = self.serviceability.modify_nethosts(
                action='AdD', host_name='10.60.156.63', user='rawstorage')
            remove_result = self.serviceability.modify_nethosts(
                action='ReMoVe', host_name='10.60.156.63', user='rawstorage')

        target_uri = (
            f"/{self.serviceability.common.UNI_VERSION}/serviceability/"
            f"symmetrix/{self.data.array}/application/solutions_enabler")
        self.assertEqual(
            [mock.call(
                target_uri=target_uri, resource_type=None,
                payload={
                    'action': 'AddNethost',
                    'add_nethost': {
                        'node_name': '10.60.156.63',
                        'user': 'rawstorage'}}),
             mock.call(
                 target_uri=target_uri, resource_type=None,
                 payload={
                     'action': 'DeleteNethost',
                     'delete_nethost': {
                         'node_name': '10.60.156.63',
                         'user': 'rawstorage'}})],
            mock_modify.call_args_list)
        self.assertEqual(responses[0], add_result)
        self.assertEqual(responses[1], remove_result)

    def test_modify_nethosts_rejects_invalid_actions(self):
        """Invalid actions raise an SDK exception before any REST call."""
        with mock.patch.object(
                self.serviceability.common,
                'modify_resource') as mock_modify:
            for invalid_action in ('change', None, 123):
                with self.subTest(action=invalid_action):
                    with self.assertRaises(
                            exception.InvalidInputException) as raised:
                        self.serviceability.modify_nethosts(
                            action=invalid_action, host_name='host', user='user')
                    self.assertIn(
                        str(invalid_action), str(raised.exception))

        mock_modify.assert_not_called()

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
        """Certificate handles remain open for upload and close afterward."""
        expected_response = self.data.import_certs_response

        def validate_upload(**kwargs):
            form_data = kwargs['form_data']
            self.assertEqual(
                ['node_name', 'keyfile', 'trustfile', 'certfile'],
                list(form_data))
            self.assertEqual('Semgmt0', form_data['node_name'])
            for field_name in ('keyfile', 'trustfile', 'certfile'):
                self.assertFalse(form_data[field_name].closed)
            return expected_response

        with mock.patch.object(
                self.serviceability.common, 'upload_file',
                side_effect=validate_upload) as mock_upload:
            result = self.serviceability.import_custom_certificate(
                array_id='000123456789', node_name='Semgmt0',
                keyfile=__file__, certfile=__file__, trustfile=__file__)

        self.assertEqual(expected_response, result)
        mock_upload.assert_called_once()
        upload_args = mock_upload.call_args.kwargs
        self.assertEqual(
            f"/{self.serviceability.common.UNI_VERSION}/serviceability/"
            f"symmetrix/000123456789/application/solutions_enabler/"
            f"custom_certificate/import",
            upload_args['target_uri'])
        for field_name in ('keyfile', 'trustfile', 'certfile'):
            self.assertTrue(upload_args['form_data'][field_name].closed)

    def test_import_custom_certificate_closes_files_on_upload_error(self):
        """Upload exceptions propagate unchanged after handles are closed."""
        upload_error = exception.VolumeBackendAPIException(data='failure')
        with mock.patch.object(
                self.serviceability.common, 'upload_file',
                side_effect=upload_error) as mock_upload:
            with self.assertRaises(
                    exception.VolumeBackendAPIException) as raised:
                self.serviceability.import_custom_certificate(
                    node_name='Semgmt0', keyfile=__file__,
                    certfile=__file__, trustfile=__file__)

        self.assertIs(upload_error, raised.exception)
        form_data = mock_upload.call_args.kwargs['form_data']
        for field_name in ('keyfile', 'trustfile', 'certfile'):
            self.assertTrue(form_data[field_name].closed)

    def test_import_custom_certificate_rejects_each_invalid_path(self):
        """Every certificate input reports its own invalid path."""
        valid_path = __file__
        for field_name in ('keyfile', 'trustfile', 'certfile'):
            missing_path = Path(self.conf_dir) / f'missing-{field_name}.pem'
            file_args = {
                'keyfile': valid_path,
                'trustfile': valid_path,
                'certfile': valid_path}
            file_args[field_name] = missing_path

            with self.subTest(field=field_name):
                with mock.patch.object(
                        self.serviceability.common,
                        'upload_file') as mock_upload:
                    with self.assertRaises(
                            exception.InvalidInputException) as raised:
                        self.serviceability.import_custom_certificate(
                            node_name='Semgmt0', **file_args)

                self.assertIn(str(missing_path), str(raised.exception))
                mock_upload.assert_not_called()
