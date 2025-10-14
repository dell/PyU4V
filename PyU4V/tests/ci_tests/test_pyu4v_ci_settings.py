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
"""test_pyu4v_ci_wlp.py."""


import testtools


from PyU4V.tests.ci_tests import base


class CITestSettings(base.TestBaseTestCase, testtools.TestCase):
    """Test SEttings."""

    def setUp(self):
        """setUp."""
        super(CITestSettings, self).setUp()
        self.common = self.conn.common
        self.settings = self.conn.settings
        self.is_v4 = self.common.is_array_v4(self.conn.array_id)

    def test_get_performance_registration_settings(self):
        """Test get_performance_registration_settings."""
        perf_reg = self.settings.get_performance_registration_settings()
        self.assertIsNotNone(perf_reg)
        self.assertIsInstance(perf_reg, dict)
        self.assertIn('registration_details', perf_reg.keys())
        self.assertIn("system_id",
                      perf_reg['registration_details'][0].keys())
        self.assertIn("diagnostic",
                      perf_reg['registration_details'][0].keys())
        self.assertIn("real_time_storage_groups",
                      perf_reg['registration_details'][0].keys())

    def test_update_performance_registration_settings(self):
        """Test update_performance_registration_settings."""
        self.settings.update_performance_registration_settings(
            array_id=self.conn.array_id, diagnostic=False, real_time=False,
            real_time_storage_groups="")
        perf_reg_before = self.settings.get_performance_registration_settings()
        self.settings.update_performance_registration_settings(
            array_id=self.conn.array_id, diagnostic=True, real_time=True,
            real_time_storage_groups="")
        perf_reg_after = self.settings.get_performance_registration_settings()
        self.assertTrue(
            perf_reg_after['registration_details'][0]['diagnostic'])
        self.assertTrue(
            perf_reg_after['registration_details'][0]['real_time'])
        self.assertFalse(
            perf_reg_before['registration_details'][0]['diagnostic'])
        self.assertFalse(
            perf_reg_before['registration_details'][0]['real_time'])

    def test_get_scg_configuration_details(self):
        """Test get_scg_configuration_details."""
        scg_config = self.settings.get_scg_configuration_details()
        print(scg_config)
        self.assertIsNotNone(scg_config)
        self.assertIsInstance(scg_config, dict)
        self.assertIn('unisphere_registered', scg_config.keys())

    def test_update_scg_configuration_details(self, run_scg=False):
        """Test update_scg_configuration_details."""
        if not run_scg:
            self.skipTest("Manually Tested")
        else:
            scg_config = self.settings.get_scg_configuration_details()
            self.assertFalse(scg_config['unisphere_registered'])

    def test_get_scg_server_certificate_configuration(self):
        """Test get_scg_server_certificate_configuration."""
        scg_config = self.settings.get_scg_server_certificate_configuration()
        self.assertIsNotNone(scg_config)
        self.assertIsInstance(scg_config, dict)
        self.assertIn('unisphere_registered', scg_config.keys())

    def test_configure_scg_connection(self, run_scg=False):
        """Test configure_scg_connection."""
        if not run_scg:
            self.skipTest("Manually Tested")
        self.settings.configure_scg_connection(
            unisphere_ip_address="192.168.1.1", gateway_host="192.168.1.1",
            scg_serial_number="random", model="random",
            server_cert="random", access_key="random", pin="random",
            gateway_port="random", unisphere_registered=True,
            internal_connection=True)

    def test_get_cloudiq_data_collection_configuration(self):
        """Test get_cloudiq_data_collection_configuration."""
        cloudiq_config = (
            self.settings.get_cloudiq_data_collection_configuration())
        self.assertIsNotNone(cloudiq_config)
        self.assertIsInstance(cloudiq_config, dict)
        self.assertIn('unisphere_registered', cloudiq_config.keys())

    def test_register_cloudiq_data_collection(self):
        """Test update_cloudiq_data_collection_configuration."""
        action = self.settings.register_cloudiq_data_collection(
            send_data=True, data_collection_disabled=[])
        assert not action

    def test_update_performance_thresholds_and_alerts(self):
        """Test update_performance_thresholds_and_alerts."""
        payload = {"global_performance_thresholds": [
            {
                "category": "Array",
                "metric": "BEUtilization",
                "kpi": 'true',
                "alert_error": 'true',
                "first_lower_threshold": "50.0",
                "second_lower_threshold": "40.0",
                "first_upper_threshold": "65.0",
                "second_upper_threshold": "80.0"
            }]}
        self.settings.update_performance_thresholds_and_alerts(
            payload=payload)
        new_thresholds = self.settings.get_performance_thresholds_and_alerts(
            category="Array")
        for threshold in new_thresholds['global_performance_thresholds']:
            if (threshold['category'] == 'Array'
                    and threshold['metric'] == 'BEUtilization'):
                self.assertEqual(threshold['kpi'], True)
                self.assertEqual(threshold['alert_error'], True)
                self.assertEqual(threshold['first_lower_threshold'], '50.0')
                self.assertEqual(threshold['second_lower_threshold'], '40.0')
                self.assertEqual(threshold['first_upper_threshold'], '65.0')
                self.assertEqual(threshold['second_upper_threshold'], '80.0')

    def test_get_alert_notification_target_config(self):
        """Test get_alert_notification_target_config."""
        alert_config = self.settings.get_alert_notification_target_config()
        self.assertIsNotNone(alert_config)
        self.assertIsInstance(alert_config, dict)
        self.assertIn('email', alert_config.keys())
        self.assertIn('snmp', alert_config.keys())
        self.assertIn('syslog', alert_config.keys())

    def test_update_alert_notification_target(
            self, run_test=False, payload=None):
        """Test update_alert_notification_target.

        This test will be run manually.
        """
        if not run_test:
            self.skipTest("Manually Tested")
        else:
            self.settings.update_alert_notification_target(
                payload=payload)

    def test_get_alert_policies(self):
        """Test get_alert_policies."""
        alert_policies = self.settings.get_alert_policies()
        self.assertIsNotNone(alert_policies)
        self.assertIsInstance(alert_policies, dict)
        self.assertIn('alert_policies', alert_policies.keys())

    def test_update_alert_policies(self):
        """Test update_alert_policies.

        This test will be run manually.
        """
        payload_false = {"alert_policies": [
            {
                "name": "arrayComponentEvents",
                "type": "array",
                "enabled": False,
                "email_notifications": False,
                "snmp_notifications": False,
                "syslog_notifications": False
            }]}
        payload_true = {"alert_policies": [
            {
                "name": "arrayComponentEvents",
                "type": "array",
                "enabled": True,
                "email_notifications": True,
                "snmp_notifications": True,
                "syslog_notifications": True
            }]}
        self.settings.update_alert_policies(payload=payload_false)
        disabled_alert_policies = self.settings.get_alert_policies()
        for policy in disabled_alert_policies['alert_policies']:
            if policy['name'] == 'arrayComponentEvents':
                self.assertEqual(policy['enabled'], False)
                self.assertEqual(policy['email_notifications'], False)
                self.assertEqual(policy['snmp_notifications'], False)
                self.assertEqual(policy['syslog_notifications'], False)
        self.settings.update_alert_policies(payload=payload_true)
        enabled_alert_policies = self.settings.get_alert_policies()
        for policy in enabled_alert_policies['alert_policies']:
            if policy['name'] == 'arrayComponentEvents':
                self.assertEqual(policy['enabled'], True)
                self.assertEqual(policy['email_notifications'], True)
                self.assertEqual(policy['snmp_notifications'], True)
                self.assertEqual(policy['syslog_notifications'], True)

    def test_get_host_access_control_configuration(self):
        """Test get_host_access_control_configuration."""
        host_access_control_config = (
            self.settings.get_host_access_control_configuration())
        self.assertIsNotNone(host_access_control_config)
        self.assertIsInstance(host_access_control_config, dict)

    def test_get_authorization_rules(self):
        """Test get_authorization_rules."""
        authorization_rules = self.settings.get_authorization_rules()
        self.assertIsNotNone(authorization_rules)
        self.assertIsInstance(authorization_rules, dict)

    def test_create_authorization_rule(self, run_test=False):
        """Test create_authorization_rules.

        This test will be run manually. Authorization rules can not be
        delete via API for security reasons. Function verified 8/28/2025

        """

        if not run_test:
            self.skipTest("Manually Tested")
        else:
            authorization_rule = self.settings.create_authorization_rule(
                name="test3", account_type="user", authority="localDirectory",
                qualifier="VMAX", roles={"admin": "true"})
            self.assertIsNotNone(authorization_rule)

    def test_update_authorization_rules(self, run_test=False):
        """Test update_authorization_rules.

        This test will be run manually. Authorization rules can not be
        delete via API for security reasons. Function verified 8/28/2025
        """

        payload = {"authorization_rules": [
            {
                "name": "test3",
                "account_type": "user",
                "authority": "localDirectory",
                "qualifier": "VMAX",
                "roles": {"admin": "true"}
            }]}
        if not run_test:
            self.skipTest("Manually Tested")
        else:
            self.settings.update_authorization_rules(payload=payload)

    def test_get_system_thresholds(self):
        """Test get_system_thresholds."""
        system_thresholds = self.settings.get_system_thresholds()
        self.assertIsNotNone(system_thresholds)
        self.assertIsInstance(system_thresholds, dict)
        self.assertIn('system_thresholds', system_thresholds.keys())

    def test_get_system_thresholds_with_filter(self):
        """Test get_system_thresholds with filters applied."""
        system_thresholds_filtered = self.settings.get_system_thresholds(
            syslog_notifications=True)
        system_thresholds_unfiltered = self.settings.get_system_thresholds(
            self.assertIsNotNone(system_thresholds_filtered))
        for threshold in system_thresholds_filtered['system_thresholds']:
            if threshold['name'] == 'syslogNotifications':
                self.assertEqual(threshold['syslog_notifications'], True)
        self.assertGreater(
            len(system_thresholds_unfiltered['system_thresholds']),
            len(system_thresholds_filtered['system_thresholds']))

    def test_update_system_thresholds(self):
        """Test Update System Thresholds."""
        payload = {'system_thresholds': [{'name': 'backendMetaDataUsage',
                                          'type': 'system',
                                          'unit': 'percent',
                                          'warning_threshold': 60,
                                          'critical_threshold': 80,
                                          'fatal_threshold': 100,
                                          'email_notifications': False,
                                          'snmp_notifications': False,
                                          'syslog_notifications': False}]}
        self.settings.update_system_thresholds(payload=payload)
        new_filtered_threshold = self.settings.get_system_thresholds(
            name='backendMetaDataUsage', type='system')
        for threshold in new_filtered_threshold['system_thresholds']:
            if threshold['name'] == 'backendMetaDataUsage':
                self.assertEqual(threshold['syslog_notifications'], False)
        reset_payload = {'system_thresholds': [{'name': 'backendMetaDataUsage',
                                                'type': 'system',
                                                'unit': 'percent',
                                                'warning_threshold': 60,
                                                'critical_threshold': 80,
                                                'fatal_threshold': 100,
                                                'email_notifications': True,
                                                'snmp_notifications': True,
                                                'syslog_notifications': True}]}
        self.settings.update_system_thresholds(payload=reset_payload)
        reset_values = self.settings.get_system_thresholds(
            name='backendMetaDataUsage', type='system')
        for threshold in reset_values['system_thresholds']:
            if threshold['name'] == 'backendMetaDataUsage':
                self.assertEqual(threshold['syslog_notifications'], True)

    def test_get_alert_notification_agent_details(self):
        """Test get_alert_notification_agent_details."""
        alert_agent_details = (
            self.settings.get_alert_notification_agent_details())
        self.assertIsNotNone(alert_agent_details)
        self.assertIsInstance(alert_agent_details, dict)

    def test_get_alert_notification_settings(self):
        """Test get_notification_settings."""
        notification_settings = self.settings.get_alert_notification_settings()
        self.assertIsNotNone(notification_settings)
        self.assertIsInstance(notification_settings, dict)
        self.assertIn('alert_severity', notification_settings.keys())

    def test_update_alert_notifications(self):
        """Test update_notification_settings."""
        payload = {
            "alert_severity": {
                "system": {
                    "fatal": True,
                    "critical": True,
                    "warning": True,
                    "normal": False,
                    "info": False
                },
                "performance": {
                    "critical": True,
                    "warning": True,
                    "info": False
                }
            },
            "subscriptions": {
                "system": [
                    "random.person@dell.com"
                ],
                "performance": [
                    "random.person@dell.com"
                ],
                "jobs": [],
                "reports": [
                    "random.person@dell.com"
                ]
            }
        }

        self.settings.update_alert_notifications(
            payload=payload)
        updated_settings = self.settings.get_alert_notification_settings()
        self.assertIsNotNone(updated_settings)
        self.assertEqual(
            updated_settings['subscriptions']['system'][0],
            'random.person@dell.com')

    def test_get_storage_group_compliance_policy_allocation(self):
        """Test get_storage_group_compliance_policy_allocation."""
        storage_group_compliance_policy_allocation = (
            self.settings.get_storage_group_compliance_policy_allocation())
        self.assertIsNotNone(storage_group_compliance_policy_allocation)
        self.assertIsInstance(storage_group_compliance_policy_allocation, dict)
