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
import time

from PyU4V.tests.ci_tests import base
from PyU4V.utils import constants


class CITestSnapshotPolicy(base.TestBaseTestCase, testtools.TestCase):
    """Test Snapshot Policy Functions."""

    def setUp(self):
        """SetUp."""
        super(CITestSnapshotPolicy, self).setUp()
        self.snapshot_policy = self.conn.snapshot_policy
        self.provision = self.conn.provisioning
        self.snapshot_policy_name_for_test = (
            constants.SNAPSHOT_POLICY_NAME_FOR_TEST)

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

        self.snapshot_policy.modify_snapshot_policy_properties(
            original_snapshot_policy_name,
            new_snapshot_policy_name=modified_snapshot_policy_name)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                modified_snapshot_policy_name))
        self.assertEqual(modified_snapshot_policy_name,
                         snapshot_policy_info.get('snapshot_policy_name'))

        self.snapshot_policy.modify_snapshot_policy_properties(
            modified_snapshot_policy_name,
            new_snapshot_policy_name=original_snapshot_policy_name)

    def test_associate_disassociate_snapshot_policy(self):
        """Test associate and disassociate to/from storage groups."""
        snapshot_policy_name = self.create_snapshot_policy()
        storage_group_name = self.create_empty_storage_group()
        self.snapshot_policy.associate_to_storage_groups(
            snapshot_policy_name, storage_group_names=[storage_group_name])
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertEqual(1, snapshot_policy_info.get('storage_group_count'))
        self.snapshot_policy.disassociate_from_storage_groups(
            snapshot_policy_name, storage_group_names=[storage_group_name])
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertIsNone(snapshot_policy_info.get('storage_group_count'))

    def test_suspend_resume_snapshot_policy(self):
        """Test suspend_snapshot_policy and resume_snapshot_policy."""
        snapshot_policy_name = self.create_snapshot_policy()
        self.snapshot_policy.suspend_snapshot_policy(
            snapshot_policy_name)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertTrue(snapshot_policy_info.get('suspended'))
        self.snapshot_policy.resume_snapshot_policy(
            snapshot_policy_name)
        snapshot_policy_info = (
            self.snapshot_policy.get_snapshot_policy(
                snapshot_policy_name))
        self.assertFalse(snapshot_policy_info.get('suspended'))

    def test_modify_snapshot_policy_properties_extra_settings(self):
        """Test modify_snapshot_policy_properties extra settings."""
        snapshot_policy_name = self.create_snapshot_policy()
        job = self.snapshot_policy.modify_snapshot_policy_properties(
            snapshot_policy_name,
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
        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        self.assertEqual(
            [snapshot_policy_name],
            storage_group_details.get('snapshot_policies'))
        storage_group_name = storage_group_details.get('storageGroupId')

        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def get_storage_group_and_associated_snapshot_policy(self):

        snapshot_policy_name = self.create_snapshot_policy()
        storage_group_name = self.generate_name(object_type='sg')
        volume_name = self.generate_name()

        self.provision.create_storage_group(
            self.SRP, storage_group_name, self.SLO, None, False, 1, 1, 'GB',
            False, False, volume_name,
            snapshot_policy_ids=[snapshot_policy_name])
        storage_group_details = self.provision.get_storage_group(
            storage_group_name)
        return snapshot_policy_name, storage_group_details

    def cleanup_snapshot_policy_and_storage_group(
            self, snapshot_policy_name, storage_group_name):
        self.snapshot_policy.modify_snapshot_policy(
            snapshot_policy_name, constants.DISASSOCIATE_FROM_STORAGE_GROUPS,
            storage_group_names=[storage_group_name])

        self.addCleanup(self.delete_storage_group, storage_group_name)

    def test_get_snapshot_policy_compliance(self):
        """Test get_snapshot_policy_compliance."""
        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        compliance_details = (
            self.snapshot_policy.get_snapshot_policy_compliance(
                storage_group_name))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_compliance_epoch_time_seconds(self):
        """Test get_snapshot_policy_compliance epoch time."""
        from_epoch = str(int(time.time()))
        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        to_epoch = str(int(time.time()))
        compliance_details = (
            self.snapshot_policy.get_snapshot_policy_compliance_epoch(
                storage_group_name, from_epoch=from_epoch, to_epoch=to_epoch))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_compliance_epoch_time_milliseconds(self):
        """Test get_snapshot_policy_compliance epoch time."""
        from_epoch = str(int(time.time() * 1000))
        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        to_epoch = str(int(time.time() * 1000))
        compliance_details = (
            self.snapshot_policy.get_snapshot_policy_compliance_epoch(
                storage_group_name, from_epoch=from_epoch, to_epoch=to_epoch))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_compliance_human_readable_time(self):
        """Test get_snapshot_policy_compliance human readable time."""
        ts = time.gmtime()
        from_time_string = time.strftime("%Y-%m-%d %H:%M", ts)
        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        ts = time.gmtime()
        to_time_string = time.strftime("%Y-%m-%d %H:%M", ts)
        sp = self.snapshot_policy
        compliance_details = (
            sp.get_snapshot_policy_compliance_human_readable_time(
                storage_group_name, from_time_string=from_time_string,
                to_time_string=to_time_string))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_compliance_mixed_time(self):
        """Test get_snapshot_policy_compliance human readable time."""
        self.skipTest(reason='from human readable to to epoch bug')
        ts = time.gmtime()
        from_time_string = time.strftime("%Y-%m-%d %H:%M", ts)
        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        to_epoch = str(int(time.time()))
        compliance_details = (
            self.snapshot_policy.get_snapshot_policy_compliance(
                storage_group_name, from_time_string=from_time_string,
                to_epoch=to_epoch))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_compliance_mixed_time_2(self):
        """Test get_snapshot_policy_compliance human readable time."""
        from_epoch = str(int(time.time()))

        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        ts = time.gmtime()
        to_time_string = time.strftime("%Y-%m-%d %H:%M", ts)
        compliance_details = (
            self.snapshot_policy.get_snapshot_policy_compliance(
                storage_group_name, from_epoch=from_epoch,
                to_time_string=to_time_string))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_compliance_last_week(self):
        """Test get_snapshot_policy_compliance last week."""

        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        compliance_details = (
            self.snapshot_policy.get_snapshot_policy_compliance_last_week(
                storage_group_name))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_compliance_last_four_weeks(self):
        """Test get_snapshot_policy_compliance last four weeks."""

        snapshot_policy_name, storage_group_details = (
            self.get_storage_group_and_associated_snapshot_policy())
        storage_group_name = storage_group_details.get('storageGroupId')
        sp = self.snapshot_policy
        compliance_details = (
            sp.get_snapshot_policy_compliance_last_four_weeks(
                storage_group_name))
        self.assertEqual(storage_group_name, compliance_details.get(
            'storage_group_name'))
        self.assertEqual('NONE', compliance_details.get('compliance'))
        self.cleanup_snapshot_policy_and_storage_group(
            snapshot_policy_name, storage_group_name)

    def test_get_snapshot_policy_storage_group_list(self):
        """Test get_snapshot_policy_storage_group_list"""
        sp = self.snapshot_policy
        snapshot_policy_name = 'DailyDefault'
        snap_list = (
            sp.get_snapshot_policy_storage_group_list(
                snapshot_policy_name=snapshot_policy_name))
        self.assertIsInstance(snap_list, list)
