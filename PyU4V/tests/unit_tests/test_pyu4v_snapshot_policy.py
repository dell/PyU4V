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
"""test_pyu4v_snapshot_policy.py."""

import testtools

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants
from PyU4V.utils import exception


class PyU4VSnapshotPolicyTest(testtools.TestCase):
    """Test replication."""

    def setUp(self):
        """Setup."""
        super(PyU4VSnapshotPolicyTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.snapshot_policy = self.conn.snapshot_policy

    def tearDown(self):
        """tearDown."""
        super(PyU4VSnapshotPolicyTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_snapshot_policy(self):
        """Test get_snapshot_policy."""
        snapshot_policy_details = self.snapshot_policy.get_snapshot_policy(
            self.data.snapshot_policy_name)
        self.assertEqual(
            self.data.snapshot_policy_info, snapshot_policy_details)

    def test_get_snapshot_policy_list(self):
        """Test get_snapshot_policy_list."""
        snapshot_policy_list = self.snapshot_policy.get_snapshot_policy_list()
        self.assertTrue(10 == len(snapshot_policy_list))

    def test_create_snapshot_policy_local_sp_success(self):
        """Test create_snapshot_policy with local snapshot policy."""
        snapshot_policy_name = 'new_local_sp'
        snapshot_policy_interval = '10 Minutes'
        with mock.patch.object(
                self.snapshot_policy, 'create_resource') as mock_create:
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, snapshot_policy_interval,
                local_snapshot_policy_snapshot_count=10)
            mock_create.assert_called_once()

    def test_create_snapshot_policy_local_sp_extra_settings_success(self):
        """Test create_snapshot_policy with local sp extra settings."""
        snapshot_policy_name = 'new_local_sp'
        snapshot_policy_interval = '10 Minutes'
        with mock.patch.object(
                self.snapshot_policy, 'create_resource') as mock_create:
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, snapshot_policy_interval,
                local_snapshot_policy_snapshot_count=10,
                offset_mins=5, compliance_count_warning=10,
                compliance_count_critical=2, _async=True)
            mock_create.assert_called_once()

    def test_create_snapshot_policy_local_sp_failure(self):
        """Test create_snapshot_policy with local sp missing param."""
        snapshot_policy_name = 'new_local_sp'
        snapshot_policy_interval = '1 Day'
        exception_message = (
            r'One of cloud snapshot policy or local snapshot policy must '
            r'be chosen. Check that you have the minimum parameters set.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, snapshot_policy_interval,
                local_snapshot_policy_secure=True)

    def test_create_snapshot_policy_cloud_sp_success(self):
        """Test create_snapshot_policy with cloud snapshot policy."""
        snapshot_policy_name = 'new_cloud_sp'
        snapshot_policy_interval = '1 Day'
        with mock.patch.object(
                self.snapshot_policy, 'create_resource') as mock_create:
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, snapshot_policy_interval,
                cloud_provider_name='my_cloud_provider',
                cloud_retention_days=10)
            mock_create.assert_called_once()

    def test_create_snapshot_policy_cloud_sp_failure(self):
        """Test create_snapshot_policy with cloud sp missing param."""
        snapshot_policy_name = 'new_cloud_sp'
        snapshot_policy_interval = '1 Day'
        exception_message = (
            r'Invalid input received: If cloud_provider_name is set, '
            r'cloud_retention_days cannot be None.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, snapshot_policy_interval,
                cloud_provider_name='my_cloud_provider')

    def test_create_snapshot_policy_no_sp_name(self):
        """Test create_snapshot_policy with no snapshot policy name."""
        snapshot_policy_interval = '10 Minutes'
        exception_message = (
            r'Invalid input received: Snapshot policy name cannot be None.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.create_snapshot_policy(
                None, snapshot_policy_interval,
                local_snapshot_policy_snapshot_count=30)

    def test_create_snapshot_policy_no_interval(self):
        """Test create_snapshot_policy with no interval."""
        snapshot_policy_name = 'no_interval_sp'
        exception_message = (r'Invalid input received: interval cannot be '
                             r'None. The interval supplied must be one '
                             r'of \'10 Minutes\', \'12 Minutes\', '
                             r'\'15 Minutes\' etc.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, None,
                local_snapshot_policy_snapshot_count=30)

    def test_create_snapshot_policy_interval_misspelt(self):
        """Test create_snapshot_policy with interval misspelt."""
        snapshot_policy_name = 'misspelt_interval_sp'
        exception_message = (r'Invalid input received: The interval supplied '
                             r'must be one of \'10 Minutes\', \'12 Minutes\', '
                             r'\'15 Minutes\' etc.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, '10 minnutes',
                local_snapshot_policy_snapshot_count=30)

    def test_create_snapshot_policy_no_cspd_or_lspd(self):
        """Test create_snapshot_policy with no cloud or local sp."""
        snapshot_policy_name = 'no_cspd_or_lspd'
        snapshot_policy_interval = '10 Minutes'
        exception_message = (
            r'Invalid input received: One of cloud snapshot '
            r'policy or local snapshot policy must be chosen.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.create_snapshot_policy(
                snapshot_policy_name, snapshot_policy_interval)

    def test_modify_snapshot_policy_modify_name_change_success(self):
        """Test modify_snapshot_policy name change success."""
        snapshot_policy_name = 'existing_sp_name'
        new_snapshot_policy_name = 'new_sp_name'
        with mock.patch.object(
                self.snapshot_policy, 'modify_resource') as mock_modify:
            self.snapshot_policy.modify_snapshot_policy_properties(
                snapshot_policy_name,
                new_snapshot_policy_name=new_snapshot_policy_name)
            mock_modify.assert_called_once()

    def test_modify_snapshot_policy_modify_extra_settings_success(self):
        """Test modify_snapshot_policy extra settings success."""
        snapshot_policy_name = 'existing_sp_name'
        new_snapshot_policy_name = 'new_sp_name'
        with mock.patch.object(
                self.snapshot_policy, 'modify_resource') as mock_modify:
            self.snapshot_policy.modify_snapshot_policy_properties(
                snapshot_policy_name,
                new_snapshot_policy_name=new_snapshot_policy_name,
                interval='12 Minutes', offset_mins=5, snapshot_count=30,
                compliance_count_warning=10, compliance_count_critical=5,
                _async=True)
            mock_modify.assert_called_once()

    def test_modify_snapshot_policy_no_snapshot_policy_name(self):
        """Test modify_snapshot_policy no snapshot policy name."""
        snapshot_policy_name = None
        new_snapshot_policy_name = 'new_sp_name'
        exception_message = (
            r'Invalid input received: Snapshot policy name cannot be None.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.modify_snapshot_policy_properties(
                snapshot_policy_name,
                new_snapshot_policy_name=new_snapshot_policy_name)

    def test_modify_snapshot_policy_no_action(self):
        """Test modify_snapshot_policy no action."""
        snapshot_policy_name = 'existing_sp_name'
        new_snapshot_policy_name = 'new_sp_name'
        action = None
        exception_message = (
            r'The action cannot be None. The action supplied must be one '
            r'of \'Modify\', \'Suspend\', \'Resume\', '
            r'\'AssociateToStorageGroups\', '
            r'\'DisassociateFromStorageGroups\'.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.modify_snapshot_policy(
                snapshot_policy_name, action,
                new_snapshot_policy_name=new_snapshot_policy_name)

    def test_modify_snapshot_policy_action_no_payload(self):
        """Test modify_snapshot_policy action with no payload."""
        snapshot_policy_name = 'existing_sp_name'
        exception_message = (
            r'Invalid input received: No modify payload received.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.modify_snapshot_policy_properties(
                snapshot_policy_name)

    def test_modify_snapshot_policy_incorrect_action(self):
        """Test modify_snapshot_policy incorrect action."""
        snapshot_policy_name = 'existing_sp_name'
        new_snapshot_policy_name = 'new_sp_name'
        action = 'modification'
        exception_message = (
            r'The action supplied must be one of \'Modify\', '
            r'\'Suspend\', \'Resume\', \'AssociateToStorageGroups\', '
            r'\'DisassociateFromStorageGroups\'.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.modify_snapshot_policy(
                snapshot_policy_name, action,
                new_snapshot_policy_name=new_snapshot_policy_name)

    def test_associate_to_storage_group_success(self):
        """Test modify_snapshot_policy associate with storage group."""
        snapshot_policy_name = 'existing_sp_name'
        with mock.patch.object(
                self.snapshot_policy, 'modify_resource') as mock_modify:
            self.snapshot_policy.associate_to_storage_groups(
                snapshot_policy_name,
                storage_group_names=self.data.snapshot_policy_sg_list)
            mock_modify.assert_called_once()

    def test_associate_to_storage_group_failure(self):
        """Test associate_to_storage_groups with no storage group."""
        snapshot_policy_name = 'existing_sp_name'
        exception_message = (
            r'Invalid input received: storage_group_names cannot be None.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.associate_to_storage_groups(
                snapshot_policy_name,
                storage_group_names=list())

    def test_disassociate_from_storage_group_success(self):
        """Test disassociate_from_storage_groups success."""
        snapshot_policy_name = 'existing_sp_name'
        with mock.patch.object(
                self.snapshot_policy, 'modify_resource') as mock_modify:
            self.snapshot_policy.disassociate_from_storage_groups(
                snapshot_policy_name,
                storage_group_names=self.data.snapshot_policy_sg_list)
            mock_modify.assert_called_once()

    def test_disassociate_from_storage_group_failure(self):
        """Test disassociate_from_storage_groups no storage group."""
        snapshot_policy_name = 'existing_sp_name'
        exception_message = (
            r'Invalid input received: storage_group_names cannot be None.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.disassociate_from_storage_groups(
                snapshot_policy_name,
                storage_group_names=list())

    def test_suspend_snapshot_policy_success(self):
        """Test suspend_snapshot_policy."""
        snapshot_policy_name = 'existing_sp_name'
        with mock.patch.object(
                self.snapshot_policy, 'modify_resource') as mock_modify:
            self.snapshot_policy.suspend_snapshot_policy(
                snapshot_policy_name)
            mock_modify.assert_called_once()

    def test_modify_snapshot_policy_resume_success(self):
        """Test resume_snapshot_policy."""
        snapshot_policy_name = 'existing_sp_name'
        with mock.patch.object(
                self.snapshot_policy, 'modify_resource') as mock_modify:
            self.snapshot_policy.resume_snapshot_policy(
                snapshot_policy_name)
            mock_modify.assert_called_once()

    def test_delete_snapshot_policy_delete_success(self):
        """Test delete_snapshot_policy."""
        snapshot_policy_name = 'existing_sp_name'
        with mock.patch.object(
                self.snapshot_policy, 'delete_resource') as mock_delete:
            self.snapshot_policy.delete_snapshot_policy(
                snapshot_policy_name)
            mock_delete.assert_called_once()

    def test_delete_snapshot_policy_delete_failure(self):
        """Test delete_snapshot_policy no snapshot policy name."""
        snapshot_policy_name = None
        exception_message = (
            r'Invalid input received: Snapshot policy name cannot be None.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.delete_snapshot_policy(
                snapshot_policy_name)

    def test_get_snapshot_policy_compliance_no_params(self):
        """Test test_get_snapshot_policy_compliance."""

        compliance_info = self.snapshot_policy.get_snapshot_policy_compliance(
            self.data.storagegroup_name)
        self.assertEqual(
            self.data.compliance_details, compliance_info)

    def test_get_snapshot_policy_compliance_epoch_params(self):
        """Test test_get_snapshot_policy_compliance."""

        compliance_info = self.snapshot_policy.get_snapshot_policy_compliance(
            self.data.storagegroup_name, from_epoch='1606826037',
            to_epoch='1606836037')
        self.assertEqual(
            self.data.compliance_details, compliance_info)

    def test_get_snapshot_policy_compliance_timestring_params(self):
        """Test test_get_snapshot_policy_compliance."""

        compliance_info = self.snapshot_policy.get_snapshot_policy_compliance(
            self.data.storagegroup_name, from_time_string='2020-12-01 15:00',
            to_time_string='2020-12-08 15:00')
        self.assertEqual(
            self.data.compliance_details, compliance_info)

    def test_get_snapshot_policy_compliance_mixed_params_1(self):
        """Test test_get_snapshot_policy_compliance."""

        compliance_info = self.snapshot_policy.get_snapshot_policy_compliance(
            self.data.storagegroup_name, from_epoch='1606826037',
            to_time_string='2020-12-08 15:00')
        self.assertEqual(
            self.data.compliance_details, compliance_info)

    def test_get_snapshot_policy_compliance_mixed_params_2(self):
        """Test test_get_snapshot_policy_compliance."""

        compliance_info = self.snapshot_policy.get_snapshot_policy_compliance(
            self.data.storagegroup_name, from_time_string='2020-12-01 15:00',
            to_epoch='1606836037')
        self.assertEqual(
            self.data.compliance_details, compliance_info)

    def test_get_snapshot_policy_compliance_missing_to_1(self):
        """Test get_snapshot_policy_compliance missing to param."""
        exception_message = (
            r'Invalid input received: from_time_string must be accompanied '
            r'with one of to_time_string or to_epoch.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.get_snapshot_policy_compliance(
                self.data.storagegroup_name,
                from_time_string='2020-12-01 15:00')

    def test_get_snapshot_policy_compliance_missing_to_2(self):
        """Test get_snapshot_policy_compliance missing to param."""
        exception_message = (
            r'Invalid input received: from_epoch must be accompanied '
            r'with one of to_epoch or to_time_string.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.get_snapshot_policy_compliance(
                self.data.storagegroup_name, from_epoch='1606826037')

    def test_get_snapshot_policy_compliance_missing_from_1(self):
        """Test get_snapshot_policy_compliance missing to param."""
        exception_message = (
            r'Invalid input received: to_time_string must be accompanied '
            r'with one of from_time_string or to_epoch.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.get_snapshot_policy_compliance(
                self.data.storagegroup_name,
                to_time_string='2020-12-01 15:00')

    def test_get_snapshot_policy_compliance_missing_from_2(self):
        """Test get_snapshot_policy_compliance missing to param."""
        exception_message = (
            r'Invalid input received: to_epoch must be accompanied with one '
            r'of from_epoch or from_time_string.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.get_snapshot_policy_compliance(
                self.data.storagegroup_name, to_epoch='1606836037')

    def test_get_snapshot_policy_compliance_missing_sg_name(self):
        """Test get_snapshot_policy_compliance missing to param."""
        exception_message = (
            r'Invalid input received: Storage group name cannot be None.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.get_snapshot_policy_compliance(None)

    def test_get_snapshot_policy_compliance_incorrect_epoch_format(self):
        """Test get_snapshot_policy_compliance incorrect epoch param."""
        exception_message = (
            r'Invalid input received: from_epoch 160682603 is in the wrong '
            r'format.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            self.snapshot_policy.get_snapshot_policy_compliance_epoch(
                self.data.storagegroup_name, from_epoch='160682603',
                to_epoch='1606836037')

    def test_get_snapshot_policy_compliance_incorrect_time_format(self):
        """Test get_snapshot_policy_compliance incorrect timestamp param."""
        exception_message = (
            r'Invalid input received: from_time_string 2020-12-1 15:00 is '
            r'in the wrong format.')
        with self.assertRaisesRegex(
                exception.InvalidInputException,
                exception_message):
            sp = self.snapshot_policy
            sp.get_snapshot_policy_compliance_human_readable_time(
                self.data.storagegroup_name,
                from_time_string='2020-12-1 15:00',
                to_time_string='2020-12-08 15:00')

    def test_verify_combination(self):
        """Test verify_combination."""
        self.assertIsNone(self.snapshot_policy.verify_combination(
            True, False, None, None))
        self.assertIsNone(self.snapshot_policy.verify_combination(
            False, False, '2020-12-1 15:00', None))
        self.assertIsNone(self.snapshot_policy.verify_combination(
            False, False, None, '1606836037'))
        self.assertIsNone(
            self.snapshot_policy.verify_combination(
                False, False, None, '1606836037'))
        self.assertIsNone(
            self.snapshot_policy.verify_combination(
                False, False, None, None))
        self.assertIsNotNone(
            self.snapshot_policy.verify_combination(True, True, None, None))
        self.assertIsNotNone(self.snapshot_policy.verify_combination(
            True, False, '2020-12-1 15:00', None))
        self.assertIsNotNone(self.snapshot_policy.verify_combination(
            False, False, '2020-12-1 15:00', '1606836037'))

    def test_verify_from_time_string_wrong_format(self):
        """Test verify_from_time_string wrong format."""
        exp_msg = 'to_time_string 2020-12-d1 15:00 is in the wrong format.'
        msg, query_params = self.snapshot_policy.verify_from_time_string(
            None, '2020-12-d1 15:00', '2020-12-10 15:00')
        self.assertEqual(exp_msg, msg)

    def test_verify_from_epoch_wrong_format_from_epoch(self):
        """Test verify_from_epoch wrong format from_epoch."""
        exp_msg = 'from_epoch 160683603d is in the wrong format.'
        msg, query_params = self.snapshot_policy.verify_from_epoch(
            '160683603d', '1606846030', None)
        self.assertEqual(exp_msg, msg)

    def test_verify_from_epoch_wrong_format_to_epoch(self):
        """Test verify_from_epoch wrong format to_epoch."""
        exp_msg = 'to_epoch 160684603d is in the wrong format.'
        msg, query_params = self.snapshot_policy.verify_from_epoch(
            '1606836030', '160684603d', None)
        self.assertEqual(exp_msg, msg)

    def test_verify_from_epoch_wrong_format_to_time_string(self):
        """Test verify_from_epoch wrong format to_time_string."""
        exp_msg = 'to_time_string 2020-12-01 5pm is in the wrong format.'
        msg, query_params = self.snapshot_policy.verify_from_epoch(
            '1606836030', None, '2020-12-01 5pm')
        self.assertEqual(exp_msg, msg)

    def test_verify_verify_input_params_wrong_combination(self):
        """Test verify_input_params wrong combination."""
        exp_msg = ('Only one of last_week, last_four_weeks, from_epoch, '
                   'from_time_string can be true or not None.')
        msg, query_params = self.snapshot_policy.verify_input_params(
            True, True, None, None, None, None)
        self.assertEqual(exp_msg, msg)

    def test_verify_verify_input_params_duplicate_to(self):
        """Test verify_input_params wrong combination."""
        exp_msg = ('to_epoch and to_time_string should not both be supplied '
                   'as they are different formats of the same thing.')
        msg, query_params = self.snapshot_policy.verify_input_params(
            False, False, '1606836030', '1606846030', None, '2020-12-10 15:00')
        self.assertEqual(exp_msg, msg)

    def test_get_snapshot_policy_storage_group_list(self):
        """Test get_snapshot_policy_storage_group_list"""
        sp = self.snapshot_policy
        snapshot_policy_name = constants.SNAPSHOT_POLICY_NAME_FOR_TEST
        snap_list = (
            sp.get_snapshot_policy_storage_group_list(
                snapshot_policy_name=snapshot_policy_name))
        self.assertIsInstance(snap_list, list)
