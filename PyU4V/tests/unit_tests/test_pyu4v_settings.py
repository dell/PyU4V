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
"""test_pyu4v_settings.py."""
from unittest.mock import MagicMock

import testtools

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V import version


class PyU4VsettingsTest(testtools.TestCase):
    """Test Settings functions."""

    def setUp(self):
        """Setup."""
        super(PyU4VsettingsTest, self).setUp()
        self.data = pcd.CommonData()
        self.version = version.API_VERSION
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.provisioning = self.conn.provisioning
            self.settings = self.conn.settings
            self.common = univmax_conn.CommonFunctions

    def tearDown(self):
        """tearDown."""
        super(PyU4VsettingsTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_update_performance_registration_settings(self):
        """Test update_performance_registration_settings."""
        self.settings.common.modify_resource = MagicMock(
            return_value=pcd.CommonData.performance_registration_settings)
        response = self.settings.update_performance_registration_settings(
            diagnostic=True, real_time=True, file=True, array_id=self)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, dict)

    def test_get_alert_policies(self):
        """Test get_alert_policies."""
        self.conn.set_array_id = MagicMock(return_value=None)
        self.settings.common.get_request = MagicMock(
            return_value=pcd.CommonData.alert_policies)
        result = self.settings.get_alert_policies()
        self.assertEqual(pcd.CommonData.alert_policies, result)

    def test_get_alert_notification_agent_details(self):
        """Test get_alert_notification_agent_details."""
        self.settings.common.get_request = MagicMock(
            return_value=pcd.CommonData.alert_details)
        result = self.settings.get_alert_notification_agent_details()
        self.settings.common.get_request.assert_called_once_with(
            target_uri=f"/{self.settings.common.UNI_VERSION}/settings/alert/"
                       f"notification/agent_details", resource_type=None)
        self.assertEqual(pcd.CommonData.alert_details, result)

    def test_get_system_thresholds(self):
        """Test get_system_thresholds."""
        self.conn.set_array_id = MagicMock(return_value=None)
        self.settings.common.get_request = MagicMock(
            return_value=pcd.CommonData.system_thresholds)
        result = self.settings.get_system_thresholds()
        self.assertEqual(pcd.CommonData.system_thresholds, result)

    def test_set_system_thresholds(self):
        """Test set_system_thresholds."""
        self.conn.set_array_id = MagicMock(return_value=None)
        self.settings.common.modify_resource = MagicMock(
            return_value=pcd.CommonData.system_thresholds)
        result = self.settings.update_system_thresholds(
            payload=pcd.CommonData.system_thresholds)
        self.settings.common.modify_resource.assert_called_once_with(
            target_uri=f"/{self.settings.common.UNI_VERSION}/"
                       f"settings/symmetrix/"
                       f"000197800123/alert/system_threshold",
            resource_type=None, payload=pcd.CommonData.system_thresholds)
        self.assertEqual(pcd.CommonData.system_thresholds, result)

    def test_get_notification_settings(self):
        """Test get_notification_settings."""
        self.conn.set_array_id = MagicMock(return_value=None)
        self.settings.common.get_request = MagicMock(
            return_value=pcd.CommonData.notification_settings)
        result = self.settings.get_alert_notification_settings()
        self.settings.common.get_request.assert_called_once_with(
            target_uri=f"/{self.settings.common.UNI_VERSION}/"
                       f"settings/symmetrix/"
                       f"000197800123/alert/notification", resource_type=None)
        self.assertEqual(pcd.CommonData.notification_settings, result)

    def test_update_alert_targets_preserves_partial_payload(self):
        """A supplied partial payload is copied and sent unchanged."""
        supplied_payload = {'syslog': {'enabled': True}}
        expected_payload = {'syslog': {'enabled': True}}
        self.settings.common.create_resource = MagicMock(
            return_value=expected_payload)

        result = self.settings.update_alert_notification_targets(
            payload=supplied_payload)

        self.assertEqual(expected_payload, supplied_payload)
        self.settings.common.create_resource.assert_called_once_with(
            target_uri=f"/{self.settings.common.UNI_VERSION}/settings/alert/"
                       f"notification",
            resource_type=None, payload=expected_payload)
        self.assertEqual(expected_payload, result)

    def test_update_alert_targets_can_disable_each_target(self):
        """Explicit False values disable email, SNMP, and syslog."""
        expected_payload = {
            'email': {'enabled': False},
            'snmp': {'enabled': False},
            'syslog': {'enabled': False}}
        self.settings.common.create_resource = MagicMock(
            return_value=expected_payload)

        self.settings.update_alert_notification_targets(
            enable_email=False, enable_snmp=False, enable_syslog=False)

        self.settings.common.create_resource.assert_called_once_with(
            target_uri=f"/{self.settings.common.UNI_VERSION}/settings/alert/"
                       f"notification",
            resource_type=None, payload=expected_payload)

    def test_update_alert_targets_accepts_integer_snmp_v3(self):
        """The documented integer SNMPv3 value retains all target fields."""
        expected_payload = {
            'snmp': {
                'enabled': True,
                'snmp_trap_targets': [{
                    'host': 'snmp.example.com',
                    'port': 162,
                    'version': 3,
                    'security_model': 'usm',
                    'authorization': {
                        'username': 'snmp-user',
                        'password': 'snmp-password',
                        'passphrase': 'snmp-passphrase'},
                    'tls': {
                        'security_name': 'tls-name',
                        'certificate_authority_pem': 'pem-data'}}]}}
        self.settings.common.create_resource = MagicMock(
            return_value=expected_payload)

        self.settings.update_alert_notification_targets(
            enable_snmp=True, snmp_host='snmp.example.com', snmp_port=162,
            snmp_version=3, snmp_security_model='usm',
            snmp_username='snmp-user', snmp_password='snmp-password',
            snmp_passphrase='snmp-passphrase', tls_security_name='tls-name',
            certificate_authority_pem='pem-data')

        self.settings.common.create_resource.assert_called_once_with(
            target_uri=f"/{self.settings.common.UNI_VERSION}/settings/alert/"
                       f"notification",
            resource_type=None, payload=expected_payload)
