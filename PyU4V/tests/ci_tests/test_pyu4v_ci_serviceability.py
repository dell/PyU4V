# Copyright (c) 2023 Dell Inc. or its subsidiaries.
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
"""test_pyu4v_ci_serviceability.py."""

import testtools

from pathlib import Path

from PyU4V.tests.ci_tests import base
from PyU4V.utils import constants
from PyU4V.utils import exception

NTP_SERVER = constants.NTP_SERVER
SYMMETRIX_ID = constants.SYMMETRIX_ID
SUCCESS = constants.SUCCESS
SERVICEABILITY_RECORD_PATH = constants.SERVICEABILITY_RECORD_PATH
NATONE_IP_ADDRESS_IPV4 = constants.NATONE_IP_ADDRESS_IPV4
NATONE_NETMASK_IPV4 = constants.NATONE_NETMASK_IPV4
NATONE_GATEWAY_IPV4 = constants.NATONE_GATEWAY_IPV4
NATTWO_IP_ADDRESS_IPV4 = constants.NATTWO_IP_ADDRESS_IPV4
NATTWO_NETMASK_IPV4 = constants.NATTWO_NETMASK_IPV4
NATTWO_GATEWAY_IPV4 = constants.NATTWO_GATEWAY_IPV4
NATONE_IP_ADDRESS_IPV6 = constants.NATONE_IP_ADDRESS_IPV6
NATONE_PREFIX_IPV6 = constants.NATONE_PREFIX_IPV6
NATONE_GATEWAY_IPV6 = constants.NATONE_GATEWAY_IPV6
NATTWO_IP_ADDRESS_IPV6 = constants.NATTWO_IP_ADDRESS_IPV6
NATTWO_PREFIX_IPV6 = constants.NATTWO_PREFIX_IPV6
NATTWO_GATEWAY_IPV6 = constants.NATTWO_GATEWAY_IPV6
APPLICATIONS = constants.APPLICATIONS
UNISPHERE = constants.UNISPHERE
SOLUTIONS_ENABLER = constants.SOLUTIONS_ENABLER
STATUS = constants.STATUS
GUEST_NAME = constants.GUEST_NAME
NODE_NAME = constants.NODE_NAME
VERSION = constants.VERSION
ACCESS_ID = constants.ACCESS_ID
SERVER_ACCESS = constants.SERVER_ACCESS
SE_BASE_CONFIGURATION = constants.SE_BASE_CONFIGURATION
SE_SERVICE_CONFIGURATION = constants.SE_SERVICE_CONFIGURATION
SYMM_LIST = constants.SYMM_LIST
SYMM_AVOID_LIST = constants.SYMM_AVOID_LIST
VASA_APPLICATIONS = constants.VASA_APPLICATIONS
RUNNING_STATUS = constants.RUNNING_STATUS
VP_LOG_FILE_SIZE_MB = constants.VP_LOG_FILE_SIZE_MB
VP_LOG_LEVEL = constants.VP_LOG_LEVEL
VP_NUM_OF_FILES_TO_BE_RETAINED = constants.VP_NUM_OF_FILES_TO_BE_RETAINED
VP_MAX_CONNECTION_PER_SESSION = constants.VP_MAX_CONNECTION_PER_SESSION
RETAIN_VP_CERT = constants.RETAIN_VP_CERT
SYMAPI_DEBUG_LOG = constants.SYMAPI_DEBUG_LOG
SE_APPLICATIONS = constants.SE_APPLICATIONS
SE_NETHOST = constants.SE_NETHOST
NODE_DISPLAYNAME = constants.NODE_DISPLAYNAME


class CITestServiceability(base.TestBaseTestCase, testtools.TestCase):
    """Test Serviceability."""

    def setUp(self):
        """setUp."""
        super(CITestServiceability, self).setUp()
        self.common = self.conn.common
        self.serviceability = self.conn.serviceability
        self.skipTest('These Tests are disruptive and should be validated '
                      'manually.')

    def test_get_local_system(self):
        """Test get_local_system."""
        serviceability_symmetrix = self.serviceability.get_local_system()
        self.assertTrue(serviceability_symmetrix)
        self.assertIsInstance(serviceability_symmetrix, dict)
        self.assertIn(SYMMETRIX_ID, serviceability_symmetrix.keys())

    def test_get_ntp_settings(self):
        """Test get_symmetrix_ntp_server."""
        ntp_server = self.serviceability.get_ntp_settings()
        self.assertTrue(ntp_server)
        self.assertIsInstance(ntp_server, dict)
        self.assertIn(NTP_SERVER, ntp_server.keys())

    def test_modify_ntp_settings(self):
        """Test Set a new NTP server information.
        Test will set current IP so as not to change configuration settings."""
        ntp_server = self.serviceability.get_ntp_settings()
        current_ntp_server = ntp_server[NTP_SERVER]
        try:
            self.serviceability.modify_ntp_settings(
                ntp_server=current_ntp_server)
        except exception.VolumeBackendAPIException as error:
            self.assertIn('A problem occurred modifying the symmetrix '
                          'resource: This input already exists.', error.msg)

    def test_download_grab_files(self):
        """Test download_grab_files write to file."""
        temp_dir_path = Path(self.create_temp_directory())
        response = self.serviceability.download_grab_files(
            dir_path=str(temp_dir_path), timeout=1000)
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertTrue(response.get(SUCCESS))
        self.assertIn(SERVICEABILITY_RECORD_PATH, response.keys())
        self.assertIn(str(temp_dir_path),
                      str(response.get(SERVICEABILITY_RECORD_PATH)))

    def test_get_ip_configuration(self):
        """Test get_ip_configuration."""
        ip_configuration = self.serviceability.get_ip_configuration()
        self.assertTrue(ip_configuration)
        self.assertIsInstance(ip_configuration, dict)
        self.assertTrue(len(ip_configuration) == 12)
        self.assertIn(NATONE_IP_ADDRESS_IPV4, ip_configuration.keys())
        self.assertIn(NATONE_NETMASK_IPV4, ip_configuration.keys())
        self.assertIn(NATONE_GATEWAY_IPV4, ip_configuration.keys())
        self.assertIn(NATTWO_IP_ADDRESS_IPV4, ip_configuration.keys())
        self.assertIn(NATTWO_NETMASK_IPV4, ip_configuration.keys())
        self.assertIn(NATTWO_GATEWAY_IPV4, ip_configuration.keys())

        self.assertIn(NATONE_IP_ADDRESS_IPV6, ip_configuration.keys())
        self.assertIn(NATONE_PREFIX_IPV6, ip_configuration.keys())
        self.assertIn(NATONE_GATEWAY_IPV6, ip_configuration.keys())
        self.assertIn(NATTWO_IP_ADDRESS_IPV6, ip_configuration.keys())
        self.assertIn(NATTWO_PREFIX_IPV6, ip_configuration.keys())
        self.assertIn(NATTWO_GATEWAY_IPV6, ip_configuration.keys())

    def test_update_ip_configuration(self):
        """Test update_ip_configuration. Test by setting existing inputs
        and expecting failure as this call will change the U4P IP."""
        ip_configuration = self.serviceability.get_ip_configuration()
        try:
            self.serviceability.update_ip_configuration(
                action='UpdateIPV4',
                natone_ip_address=ip_configuration['natone_ip_address_ipv4'],
                natone_netmask=ip_configuration['natone_netmask_ipv4'],
                natone_gateway=ip_configuration['natone_gateway_ipv4'],
                nattwo_ip_address=ip_configuration['nattwo_ip_address_ipv4'],
                nattwo_netmask=ip_configuration['nattwo_netmask_ipv4'],
                nattwo_gateway=ip_configuration['nattwo_gateway_ipv4'])
        except exception.VolumeBackendAPIException as error:
            self.assertIn('A problem occurred modifying the storage '
                          'group resource: This input already exists',
                          error.msg)

    def test_get_application(self):
        """Test get_application."""
        applications = self.serviceability.get_application()
        self.assertTrue(applications)
        self.assertIsInstance(applications, dict)
        self.assertIn(APPLICATIONS, applications.keys())
        applications_dict = {}
        for application in applications['applications']:
            key = application['application_id']
            applications_dict[key] = application
        self.assertIn(UNISPHERE, applications_dict.keys())
        self.assertIn(SOLUTIONS_ENABLER, applications_dict.keys())

    def test_get_unisphere_application_details(self):
        """Test get_unisphere_application."""
        unisphere_application = (
            self.serviceability.get_unisphere_application_details())
        self.assertTrue(unisphere_application)
        self.assertIsInstance(unisphere_application, dict)
        self.assertIn(STATUS, unisphere_application.keys())
        self.assertIn(GUEST_NAME, unisphere_application.keys())
        self.assertIn(NODE_NAME, unisphere_application.keys())
        self.assertIn(VERSION, unisphere_application.keys())
        self.assertIn(ACCESS_ID, unisphere_application.keys())
        self.assertIn(SERVER_ACCESS, unisphere_application.keys())

    def test_modify_unisphere_application(self):
        """Test modify_unisphere_application."""
        unisphere_app = self.serviceability.modify_unisphere_service_access(
            action='AllowServerAccess')
        self.assertTrue(unisphere_app)
        self.assertIsInstance(unisphere_app, dict)
        self.assertIn(STATUS, unisphere_app.keys())
        self.assertIn(GUEST_NAME, unisphere_app.keys())
        self.assertIn(NODE_NAME, unisphere_app.keys())
        self.assertIn(VERSION, unisphere_app.keys())
        self.assertIn(ACCESS_ID, unisphere_app.keys())
        self.assertIn(SERVER_ACCESS, unisphere_app.keys())

    def test_restart_unisphere_application(self):
        """Test restart_unisphere_application."""
        try:
            self.serviceability.restart_unisphere_application()
        except Exception:
            self.skipTest('Call has been made, No response expected. '
                          'Check Unisphere to see if it has been successful.')

    def test_get_symavoid_settings(self):
        """Test get_symavoid_settings."""
        unisphere_system = self.serviceability.get_symavoid_settings()
        self.assertTrue(unisphere_system)
        self.assertIsInstance(unisphere_system, dict)
        self.assertIn(SYMM_LIST, unisphere_system.keys())
        self.assertIn(SYMM_AVOID_LIST, unisphere_system.keys())

    def test_update_symavoid_settings(self):
        """Test update_symavoid_settings.
        Removes and readds symm to symm avoid list"""
        unisphere_system = self.serviceability.get_unisphere_system()
        if (SYMM_AVOID_LIST in unisphere_system.keys()) and \
                (len(unisphere_system[SYMM_AVOID_LIST]) > 0):
            symmetrix = unisphere_system[SYMM_AVOID_LIST][0]
            systems = self.serviceability.update_symavoid_settings(
                action='RemoveFromSymmavoid',
                symm_list=[symmetrix])
            self.assertIsInstance(systems, dict)
            self.assertIn(SYMM_LIST, systems.keys())
            self.assertIn(SYMM_AVOID_LIST, systems.keys())
            self.serviceability.update_symavoid_settings(
                action='AddToSymmavoid', symm_list=[symmetrix])
        else:
            self.skipTest('Skipping test as not enough symms in symm avoid')

    def test_get_solutions_enabler_application(self):
        """Test get_solutions_enabler_application."""
        get_se_app = self.serviceability.get_solutions_enabler_application()
        self.assertTrue(get_se_app)
        self.assertIsInstance(get_se_app, dict)
        self.assertIn(SE_APPLICATIONS, get_se_app.keys())
        self.assertIn(VERSION, get_se_app.keys())
        self.assertIn(ACCESS_ID, get_se_app.keys())
        self.assertIn(SE_NETHOST, get_se_app.keys())

    def test_get_solutions_enabler_configuration(self):
        """Test get_solutions_enabler_configuration."""
        se_conf = self.serviceability.get_solutions_enabler_configuration()
        self.assertTrue(se_conf)
        self.assertIsInstance(se_conf, dict)
        self.assertIn(SE_BASE_CONFIGURATION, se_conf.keys())
        self.assertIn(SE_SERVICE_CONFIGURATION, se_conf.keys())

    def test_get_solutions_enabler_system(self):
        """Test get_solutions_enabler_system."""
        se_system = self.serviceability.get_solutions_enabler_system()
        self.assertTrue(se_system)
        self.assertIsInstance(se_system, dict)
        self.assertIn(SYMM_LIST, se_system.keys())
        self.assertIn(SYMM_AVOID_LIST, se_system.keys())

    def test_import_custom_certificate(self):
        """Test import_custom_certificate with invalid path."""
        self.assertRaises(
            exception.InvalidInputException,
            self.serviceability.import_custom_certificate,
            node_name='Semgmt0',
            keyfile='/fake',
            certfile='/fake',
            trustfile='/fake'
        )

    def test_replace_self_signed_certificate(self):
        """Test replace_self_signed_certificate."""
        self_signed_cert = self.serviceability.replace_self_signed_certificate(
            node_name='Semgmt0')
        self.assertTrue(self_signed_cert)
        self.assertIsInstance(self_signed_cert, dict)
        self.assertIn(NODE_DISPLAYNAME, self_signed_cert.keys())
