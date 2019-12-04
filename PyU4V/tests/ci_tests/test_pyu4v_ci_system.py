# Copyright (c) 2019 Dell Inc. or its subsidiaries.
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
from unittest.mock import MagicMock

from PyU4V import common
from PyU4V.tests.ci_tests import base
from PyU4V.utils import constants
from PyU4V.utils import exception

ARRAY_ID = constants.ARRAY_ID
ARRAY_NUM = constants.ARRAY_NUM
CAPACITY = constants.CAPACITY
DISK_IDS = constants.DISK_IDS
HEALTH_CHECK_ID = constants.HEALTH_CHECK_ID
HEALTH_SCORE = constants.HEALTH_SCORE
JOB_ID = constants.JOB_ID
NAME = constants.NAME
RES_LINK = constants.RES_LINK
SG_ID = constants.SG_ID
SG_NUM = constants.SG_NUM
SPINDLE_ID = constants.SPINDLE_ID
STATUS = constants.STATUS
SYSTEM = constants.SYSTEM
TAG = constants.TAG
TAG_NAME = constants.TAG_NAME
TEST_RES = constants.TEST_RES
TYPE = constants.TYPE
VENDOR = constants.VENDOR


class CITestSystem(base.TestBaseTestCase, testtools.TestCase):
    """Test System."""

    def setUp(self):
        """setUp."""
        super(CITestSystem, self).setUp()
        self.common = self.conn.common
        self.system = self.conn.system

    def test_get_system_health(self):
        """Test get_system_health."""
        health = self.system.get_system_health()
        self.assertTrue(health)
        self.assertIsInstance(health, dict)
        self.assertIn(HEALTH_SCORE, health.keys())

    def test_health_check(self):
        """Test health check functionality complete.

        Note: This has to be tested in one combined test so we can ensure that
        delete is not called before we get the chance to test the other calls
        dependent on a health check existing. Unisphere only holds information
        on the last run health check, so if it is deleted before other calls
        are run then tests will be skipped.
        """
        # Run list health check test
        self._test_list_system_health_check()
        # Run get health check test
        self._test_get_health_check_details()
        # Run delete health check test
        self._test_delete_health_check()
        # Run perform health check test
        self._test_perform_health_check()

    def _test_list_system_health_check(self):
        """Test list_system_health_check."""
        health_check_list = None
        try:
            health_check_list = self.system.list_system_health_check()
        except exception.ResourceNotFoundException:
            self.skipTest('Skip list health check - there are no health '
                          'checks available')
        self.assertTrue(health_check_list)
        self.assertIsInstance(health_check_list, dict)

    def _test_get_health_check_details(self):
        """Test get_health_check_details."""
        health_check_list, health_check_id = None, None
        try:
            health_check_list = self.system.list_system_health_check()
            health_check_id = health_check_list.get(HEALTH_CHECK_ID)[0]
        except exception.ResourceNotFoundException:
            self.skipTest('Skip get health check - there are no health '
                          'checks available')

        health_check = self.system.get_health_check_details(
            health_check_id=health_check_id)
        self.assertIsInstance(health_check_list, dict)
        run_checks = health_check.get(TEST_RES)
        self.assertEqual(len(run_checks), 9)

    def _test_delete_health_check(self):
        """Test delete_health_check."""
        common.CommonFunctions.delete_resource = MagicMock(
            side_effect=self.common.delete_resource)

        health_check_list, health_check_id_1 = None, None
        try:
            health_check_list = self.system.list_system_health_check()
            health_check_id_1 = health_check_list.get(HEALTH_CHECK_ID)[0]
        except exception.ResourceNotFoundException:
            self.skipTest('Skip delete health check - there are no health '
                          'checks available')

        self.system.delete_health_check(health_check_id=health_check_id_1)
        common.CommonFunctions.delete_resource.assert_called_once()

        try:
            health_check_list = self.system.list_system_health_check()
            health_check_id_2 = health_check_list.get(HEALTH_CHECK_ID)[0]
            self.assertNotIn(health_check_id_2,
                             health_check_list.get(HEALTH_CHECK_ID))
        except exception.ResourceNotFoundException:
            # If we get an exception that no health checks are available then
            # we know the delete operation has been successful
            pass

    def _test_perform_health_check(self):
        """Test perform_health_check."""
        response = self.system.perform_health_check(description='CI-Test')
        self.assertTrue(response)
        self.assertTrue(response.get(JOB_ID))
        self.assertTrue(response.get(STATUS))
        self.assertTrue(response.get(RES_LINK))
        self.assertEqual('CI-Test', response.get(NAME))

    def test_get_disk_id_list(self):
        """Test get_disk_id_list."""
        full_list_disks = self.system.get_disk_id_list()
        failed_list_disks = self.system.get_disk_id_list(failed=True)
        self.assertTrue(set(failed_list_disks).issubset(full_list_disks))

    def test_get_disk_details(self):
        """Test get_disk_details"""
        disk_list = self.system.get_disk_id_list()
        disk_id = disk_list.get(DISK_IDS)[0]
        disk_info = self.system.get_disk_details(disk_id=disk_id)
        self.assertTrue(disk_info)
        self.assertTrue(disk_info.get(SPINDLE_ID))
        self.assertTrue(disk_info.get(TYPE))
        self.assertTrue(disk_info.get(VENDOR))
        self.assertTrue(disk_info.get(CAPACITY))

    def test_get_tags(self):
        """Test get_tags."""
        tags = self.system.get_tags()
        self.assertTrue(tags)

    def test_get_tags_filtered(self):
        """Test get_tags_filtered."""
        common.CommonFunctions.get_resource = MagicMock(
            side_effect=self.common.get_resource)

        response = self.system.get_tags(
            array_id=self.conn.array_id, tag_name='CI-TEST-NO-RESULT',
            storage_group_id='XX', num_of_storage_groups=1, num_of_arrays=3)

        common.CommonFunctions.get_resource.assert_called_once_with(
            category=SYSTEM, resource_level=TAG, params={
                ARRAY_ID: self.conn.array_id, TAG_NAME: 'CI-TEST-NO-RESULT',
                SG_ID: 'XX', SG_NUM: '1', ARRAY_NUM: '3'})

        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertIn(TAG_NAME, response.keys())

    def test_get_tagged_objects(self):
        """Test get_tagged_objects."""
        tag_id = None
        try:
            tag_list = self.system.get_tags()
            tag_id = tag_list.get(TAG_NAME)[0]
        except exception.ResourceNotFoundException:
            self.skipTest('Skip get_tagged_objects - there are no tagged '
                          'objects available.')
        tag_info = self.system.get_tagged_objects(tag_name=tag_id)
        self.assertTrue(tag_info)
        self.assertIsInstance(tag_info, dict)
