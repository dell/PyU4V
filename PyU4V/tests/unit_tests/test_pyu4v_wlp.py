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
"""test_pyu4v_wlp.py."""
from unittest.mock import MagicMock

import testtools

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn


class PyU4VUnivmaxWLPTest(testtools.TestCase):
    """Test Unisphere connection."""

    def setUp(self):
        """Setup."""
        super(PyU4VUnivmaxWLPTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.wlp = self.conn.wlp

    def tearDown(self):
        """tearDown."""
        super(PyU4VUnivmaxWLPTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_system_list(self):
        """Test get_system_list."""
        self.wlp.common.get_request = MagicMock(
            return_value={"symmetrixId": [self.data.array]})

        result = self.wlp.get_system_list()

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix",
            resource_type=None)
        self.assertEqual([self.data.array], result)

    def test_get_system(self):
        """Test get_system."""
        self.wlp.common.get_request = MagicMock(
            return_value=self.data.wlp_info)

        result = self.wlp.get_system(array_id=self.data.array)

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}", resource_type=None)
        self.assertEqual(self.data.wlp_info, result)

    def test_get_system_default_array(self):
        """Test get_system with default array."""
        self.wlp.common.get_request = MagicMock(
            return_value=self.data.wlp_info)

        self.wlp.get_system()

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}", resource_type=None)

    def test_update_data_exclusion(self):
        """Test update_data_exclusion."""
        response = {"exclusionType": "OneTime"}
        self.wlp.common.modify_resource = MagicMock(return_value=response)

        result = self.wlp.update_data_exclusion(
            exclusion_type="OneTime", epoch_timestamp=1234,
            excluded_bucket=[0, 1], array_id=self.data.array)

        self.wlp.common.modify_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}",
            resource_type=None, payload={
                "exclusionType": "OneTime", "epochTimestamp": 1234,
                "excludedBucket": [0, 1]})
        self.assertEqual(response, result)

    def test_update_data_exclusion_minimal(self):
        """Test update_data_exclusion with only the required parameter."""
        response = {"exclusionType": "None"}
        self.wlp.common.modify_resource = MagicMock(return_value=response)

        result = self.wlp.update_data_exclusion(
            exclusion_type="None", array_id=self.data.array)

        self.wlp.common.modify_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}",
            resource_type=None, payload={"exclusionType": "None"})
        self.assertEqual(response, result)

    def test_get_storage_group_list(self):
        """Test get_storage_group_list."""
        response = {"storageGroupId": [self.data.storagegroup_name_1]}
        self.wlp.common.get_request = MagicMock(return_value=response)

        result = self.wlp.get_storage_group_list(array_id=self.data.array)

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}/storagegroup",
            resource_type=None)
        self.assertEqual(response["storageGroupId"], result)

    def test_get_storage_group(self):
        """Test get_storage_group."""
        response = {"storageGroupId": self.data.storagegroup_name_1}
        self.wlp.common.get_request = MagicMock(return_value=response)

        result = self.wlp.get_storage_group(
            storage_group_id=self.data.storagegroup_name_1,
            array_id=self.data.array, filter="RTHistory")

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}/storagegroup/{self.data.storagegroup_name_1}",
            resource_type=None, params={"filter": "RTHistory"})
        self.assertEqual(response, result)

    def test_update_storage_group(self):
        """Test update_storage_group."""
        response = {"action": "SetHostIOLimits"}
        io_limits_param = {"metricLimit": "IOPS", "hostIoLimitIops": 5000}
        self.wlp.common.modify_resource = MagicMock(return_value=response)

        result = self.wlp.update_storage_group(
            storage_group_id=self.data.storagegroup_name_1,
            action="SetHostIOLimits",
            storage_group_set_host_io_limits_param=io_limits_param,
            array_id=self.data.array)

        self.wlp.common.modify_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}/storagegroup/{self.data.storagegroup_name_1}",
            resource_type=None, payload={
                "action": "SetHostIOLimits",
                "storageGroupSetHostIoLimitsParam": io_limits_param})
        self.assertEqual(response, result)

    def test_update_storage_group_rebase(self):
        """Test update_storage_group with rebase param."""
        response = {"action": "RebaseStorageGroupPlan"}
        rebase_param = {"autofill": True}
        self.wlp.common.modify_resource = MagicMock(return_value=response)

        result = self.wlp.update_storage_group(
            storage_group_id=self.data.storagegroup_name_1,
            action="RebaseStorageGroupPlan",
            storage_group_rebase_param=rebase_param,
            array_id=self.data.array)

        self.wlp.common.modify_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}/storagegroup/{self.data.storagegroup_name_1}",
            resource_type=None, payload={
                "action": "RebaseStorageGroupPlan",
                "storageGroupRebaseParam": rebase_param})
        self.assertEqual(response, result)

    def test_get_headroom(self):
        """Test get_headroom."""
        self.wlp.common.get_request = MagicMock(
            return_value=self.data.headroom_array)

        result = self.wlp.get_headroom(
            array_id=self.data.array, srp='SRP_TEST', slo='Gold',
            emulation='FBA')

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}/headroom",
            resource_type=None,
            params={"srp": "SRP_TEST", "slo": "Gold", "emulation": "FBA"})
        self.assertEqual(self.data.headroom_array, result)

    def test_get_utilization(self):
        """Test get_utilization."""
        response = {"maxArrayComponentUtilization": list()}
        self.wlp.common.get_request = MagicMock(return_value=response)

        result = self.wlp.get_utilization(
            array_id=self.data.array, bucket='12', back_end_only=True)

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}/utilization",
            resource_type=None,
            params={"bucket": "12", "backEndOnly": True})
        self.assertEqual(response, result)

    def test_get_compliance_history(self):
        """Test get_compliance_history."""
        response = {"sloCompliance": list()}
        self.wlp.common.get_request = MagicMock(return_value=response)

        result = self.wlp.get_compliance_history(
            array_id=self.data.array, start_time='1000', end_time='2000',
            storage_group_id=self.data.storagegroup_name_1)

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/symmetrix/"
            f"{self.data.array}/compliancehistory",
            resource_type=None, params={
                "starttime": "1000", "endtime": "2000",
                "storageGroupId": self.data.storagegroup_name_1})
        self.assertEqual(response, result)

    def test_get_provisioning_template_list(self):
        """Test get_provisioning_template_list."""
        response = {"templateId": ["tpl-1"]}
        self.wlp.common.get_request = MagicMock(return_value=response)

        result = self.wlp.get_provisioning_template_list()

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/"
            f"provisioningtemplate",
            resource_type=None)
        self.assertEqual(["tpl-1"], result)

    def test_get_provisioning_template(self):
        """Test get_provisioning_template."""
        response = {"templateId": "tpl-1"}
        self.wlp.common.get_request = MagicMock(return_value=response)

        result = self.wlp.get_provisioning_template(template_id="tpl-1")

        self.wlp.common.get_request.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/"
            f"provisioningtemplate/tpl-1",
            resource_type=None)
        self.assertEqual(response, result)

    def test_create_provisioning_template(self):
        """Test create_provisioning_template."""
        response = {"templateId": "tpl-1"}
        volume_attribute = {"capacityUnit": "GB", "volumeSize": 10}
        self.wlp.common.create_resource = MagicMock(return_value=response)

        result = self.wlp.create_provisioning_template(
            symmetrix_id=self.data.array,
            storage_group_id=self.data.storagegroup_name_1,
            template_id="tpl-1", response_time_target=0.7,
            number_of_volumes=2, volume_attribute=volume_attribute)

        self.wlp.common.create_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/"
            f"provisioningtemplate",
            resource_type=None, payload={
                "symmetrixId": self.data.array,
                "storageGroupId": self.data.storagegroup_name_1,
                "templateId": "tpl-1",
                "provisioningTemplateOverrides": {
                    "responseTimeTarget": 0.7,
                    "numberOfVolumes": 2,
                    "volumeAttribute": volume_attribute}})
        self.assertEqual(response, result)

    def test_create_provisioning_template_minimal(self):
        """Test create_provisioning_template with only required params."""
        response = {"templateId": "tpl-1"}
        self.wlp.common.create_resource = MagicMock(return_value=response)

        result = self.wlp.create_provisioning_template(
            symmetrix_id=self.data.array,
            storage_group_id=self.data.storagegroup_name_1,
            template_id="tpl-1")

        self.wlp.common.create_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/"
            f"provisioningtemplate",
            resource_type=None, payload={
                "symmetrixId": self.data.array,
                "storageGroupId": self.data.storagegroup_name_1,
                "templateId": "tpl-1"})
        self.assertEqual(response, result)

    def test_update_provisioning_template(self):
        """Test update_provisioning_template."""
        response = {"templateId": "tpl-2"}
        io_limit_attrs = {"metricLimit": "IOPS", "hostIoLimitIops": 5000}
        self.wlp.common.modify_resource = MagicMock(return_value=response)

        result = self.wlp.update_provisioning_template(
            template_id="tpl-1", updated_template_id="tpl-2",
            response_time_target=0.8,
            host_io_limit_attributes=io_limit_attrs)

        self.wlp.common.modify_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/"
            f"provisioningtemplate/tpl-1",
            resource_type=None, payload={
                "templateId": "tpl-2",
                "provisioningTemplateOverrides": {
                    "responseTimeTarget": 0.8,
                    "hostIOLimitAttributes": io_limit_attrs}})
        self.assertEqual(response, result)

    def test_delete_provisioning_template(self):
        """Test delete_provisioning_template."""
        self.wlp.common.delete_resource = MagicMock(return_value=None)

        self.wlp.delete_provisioning_template(template_id="tpl-1")

        self.wlp.common.delete_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/"
            f"provisioningtemplate/tpl-1",
            resource_type=None)

    def test_test_performance_impact(self):
        """Test test_performance_impact."""
        migration_param = {
            "source_symmetrix_id": self.data.array,
            "source_storage_group_id": self.data.storagegroup_name_1}
        response = {"recommended": True}
        self.wlp.common.create_resource = MagicMock(return_value=response)

        result = self.wlp.test_performance_impact(
            migration_impact_param=migration_param,
            auto_resolve_conflicts=False, details=True)

        self.wlp.common.create_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/performance_impact"
            f"?details=true",
            resource_type=None, payload={
                "migration_impact_param": migration_param,
                "auto_resolve_conflicts": False})
        self.assertEqual(response, result)

    def test_test_performance_impact_no_details(self):
        """Test test_performance_impact without details query param."""
        response = {"recommended": True}
        self.wlp.common.create_resource = MagicMock(return_value=response)

        result = self.wlp.test_performance_impact()

        self.wlp.common.create_resource.assert_called_once_with(
            target_uri=f"/{self.wlp.common.UNI_VERSION}/wlp/"
            f"performance_impact",
            resource_type=None, payload={})
        self.assertEqual(response, result)

    def test_get_wlp_information_legacy(self):
        """Test get_wlp_information legacy wrapper."""
        with mock.patch.object(
                self.wlp, 'get_system',
                return_value=self.data.wlp_info) as mck_get_system:
            result = self.wlp.get_wlp_information(array_id=self.data.array)
            mck_get_system.assert_called_once_with(array_id=self.data.array)
            self.assertEqual(self.data.wlp_info, result)
