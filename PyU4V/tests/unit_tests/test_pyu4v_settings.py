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

    def test_get_performance_registration_settings(self):
        """Test get_performance_registration_settings."""
        response = self.settings.get_performance_registration_settings()
        self.assertIsNotNone(response)
        self.assertIsInstance(response, dict)

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
            return_value=pcd.CommonData.alert_agent_details)
        result = self.settings.get_alert_notification_agent_details()
        self.settings.common.get_request.assert_called_once_with(
            target_uri=f"/{self.version}/settings/alert/notification"
                       f"/agent_details",
            resource_type=None, params={})
        self.assertEqual(pcd.CommonData.alert_agent_details, result)

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
        result = self.settings.set_system_thresholds(
            payload=pcd.CommonData.system_thresholds)
        self.settings.common.modify_resource.assert_called_once_with(
            target_uri=f"/{self.version}/settings/symmetrix/000197800123"
                       f"/alert/system_threshold",
            resource_type=None, payload=pcd.CommonData.system_thresholds)
        self.assertEqual(pcd.CommonData.system_thresholds, result)

    def test_get_notification_settings(self):
        """Test get_notification_settings."""
        self.conn.set_array_id = MagicMock(return_value=None)
        self.settings.common.get_request = MagicMock(
            return_value=pcd.CommonData.notification_settings)
        result = self.settings.get_notification_settings()
        self.settings.common.get_request.assert_called_once_with(
            target_uri=f"/{self.version}/settings/symmetrix/000197800123"
                       f"/alert/notification",
            resource_type=None, params={})
        self.assertEqual(pcd.CommonData.notification_settings, result)

    def test_storage_group_compliance_policy_allocation(self):
        """Test storage_group_compliance_policy_allocation."""
        self.conn.set_array_id = MagicMock(return_value=None)
        self.settings.common.get_request = MagicMock(
            return_value=pcd.CommonData.storage_group_compliance_policy)
        result = self.settings.storage_group_compliance_policy_allocation(
            payload=pcd.CommonData.storage_group_compliance_policy)
        self.settings.common.get_request.assert_called_once_with(
            target_uri=f"/{self.version}/settings/symmetrix/000197800123"
                       f"/storage_group_compliance_policy",
            resource_type=None, params={})
        self.assertEqual(
            pcd.CommonData.storage_group_compliance_policy, result)
