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
"""test_pyu4v_ci_snapshot_policy.py."""
import testtools

from PyU4V.tests.ci_tests import base
from PyU4V.utils import constants


class CITestSnapshotPolicy(base.TestBaseTestCase, testtools.TestCase):
    """Test Snapshot Policy Functions."""

    def setUp(self):
        """SetUp."""
        super(CITestSnapshotPolicy, self).setUp()
        self.snapshot_policy = self.conn.snapshot_policy
        self.provision = self.conn.provisioning

    def test_get_snapshot_policy(self):
        """Test get_snapshot_policy."""
        snapshot_policy_name = self.create_snapshot_policy()
        snapshot_policy_info = self.snapshot_policy.get_snapshot_policy(
            snapshot_policy_name)
        self.assertEqual(snapshot_policy_name,
                         snapshot_policy_info.get('snapshot_policy_name'))

    def test_get_snapshot_policy_list(self):
        """Test get_snapshot_policy_list."""
        snapshot_policy_name = self.create_snapshot_policy()
        snapshot_policy_list = self.snapshot_policy.get_snapshot_policy_list()
        self.assertIn(snapshot_policy_name, snapshot_policy_list)

    def test_create_snapshot_policy_local_snapshot_policy_details(self):
        """Test create_snapshot_policy with local snapshot policy."""
        snapshot_policy_name = self.generate_name(object_type='sp')
        snapshot_policy_interval = '1 Day'
        job = self.snapshot_policy.create_snapshot_policy(
            snapshot_policy_name, snapshot_policy_interval,
            local_snapshot_policy_snapshot_count=30,
            offset_mins=5, compliance_count_warning=30,
            compliance_count_critical=5,
            _async=True)
        self.conn.common.wait_for_job_complete(job)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(snapshot_policy_name))
        self.assertEqual(snapshot_policy_name,
                         snapshot_policy_info.get('snapshot_policy_name'))
        self.assertEqual(1440, snapshot_policy_info.get('interval_minutes'))
        self.assertEqual(30, snapshot_policy_info.get('snapshot_count'))
        self.assertFalse(snapshot_policy_info.get('secure'))
        self.snapshot_policy.delete_snapshot_policy(snapshot_policy_name)

    def test_modify_snapshot_policy_name_change(self):
        """Test modify_snapshot_policy name change."""
        original_snapshot_policy_name = self.create_snapshot_policy()

        modified_snapshot_policy_name = self.generate_name(object_type='sp')

        self.snapshot_policy.modify_snapshot_policy(
            original_snapshot_policy_name, constants.MODIFY_POLICY,
            new_snapshot_policy_name=modified_snapshot_policy_name)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                modified_snapshot_policy_name))
        self.assertEqual(modified_snapshot_policy_name,
                         snapshot_policy_info.get('snapshot_policy_name'))

        self.snapshot_policy.modify_snapshot_policy(
            modified_snapshot_policy_name, constants.MODIFY_POLICY,
            new_snapshot_policy_name=original_snapshot_policy_name)

    def test_modify_snapshot_policy_associate_disassociate_storage_group(self):
        """Test modify_snapshot_policy associate and disassociate sg."""
        snapshot_policy_name = self.create_snapshot_policy()
        storage_group_name = self.create_empty_storage_group()
        self.snapshot_policy.modify_snapshot_policy(
            snapshot_policy_name, constants.ASSOCIATE_TO_STORAGE_GROUPS,
            storage_group_names=[storage_group_name])
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertEqual(1, snapshot_policy_info.get('storage_group_count'))
        self.snapshot_policy.modify_snapshot_policy(
            snapshot_policy_name, constants.DISASSOCIATE_FROM_STORAGE_GROUPS,
            storage_group_names=[storage_group_name])
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertIsNone(snapshot_policy_info.get('storage_group_count'))

    def test_modify_snapshot_policy_suspend_resume(self):
        """Test modify_snapshot_policy suspend and resume."""
        snapshot_policy_name = self.create_snapshot_policy()
        self.snapshot_policy.modify_snapshot_policy(
            snapshot_policy_name, constants.SUSPEND_POLICY)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertTrue(snapshot_policy_info.get('suspended'))
        self.snapshot_policy.modify_snapshot_policy(
            snapshot_policy_name, constants.RESUME_POLICY)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertFalse(snapshot_policy_info.get('suspended'))

    def test_modify_snapshot_policy_extra_settings(self):
        """Test modify_snapshot_policy extra settings."""
        snapshot_policy_name = self.create_snapshot_policy()
        job = self.snapshot_policy.modify_snapshot_policy(
            snapshot_policy_name, constants.MODIFY_POLICY,
            offset_mins=5, compliance_count_warning=30,
            compliance_count_critical=5, interval='12 Minutes',
            snapshot_count=40, _async=True)
        self.conn.common.wait_for_job_complete(job)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertEqual(5, snapshot_policy_info.get('offset_minutes'))
        self.assertEqual(12, snapshot_policy_info.get('interval_minutes'))
        self.assertEqual(
            30, snapshot_policy_info.get('compliance_count_warning'))
        self.assertEqual(
            5, snapshot_policy_info.get('compliance_count_critical'))

    def test_create_storage_group_with_snapshot_policy(self):
        """Test create_storage_group with snapshot policy."""
        snapshot_policy_name = self.create_snapshot_policy()
        storage_group_name = self.generate_name(object_type='sg')
        volume_name = self.generate_name()

        self.provision.create_non_empty_storage_group(
            self.SRP, storage_group_name, self.SLO, None,
            disable_compression=False, num_vols=1, vol_size=1,
            cap_unit='GB', vol_name=volume_name,
            snapshot_policy_ids=[snapshot_policy_name])
        storage_group_details = self.provision.get_storage_group(
            storage_group_name)
        self.assertEqual(
            [snapshot_policy_name],
            storage_group_details.get('snapshot_policies'))
        self.snapshot_policy.modify_snapshot_policy(
            snapshot_policy_name, constants.DISASSOCIATE_FROM_STORAGE_GROUPS,
            storage_group_names=[storage_group_name])

        self.addCleanup(self.delete_storage_group, storage_group_name)
