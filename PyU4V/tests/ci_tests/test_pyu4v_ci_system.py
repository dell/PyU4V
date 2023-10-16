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

import random
import re
import testtools
import time

from pathlib import Path
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
LOCAL_USER = constants.LOCAL_USER
TAG = constants.TAG
TAG_NAME = constants.TAG_NAME
TEST_RES = constants.TEST_RES
TYPE = constants.TYPE
VENDOR = constants.VENDOR
ALERT_SUMMARY_KEYS = constants.ALERT_SUMMARY_KEYS
RECORD_ID = constants.RECORD_ID
USERNAME = constants.USERNAME
HOST_NAME = constants.HOST_NAME
CLIENT_HOST = constants.CLIENT_HOST
MESSAGE = constants.MESSAGE
ACTIVITY_ID = constants.ACTIVITY_ID
APP_ID = constants.APP_ID
APP_VERSION = constants.APP_VERSION
TASK_ID = constants.TASK_ID
PROCESS_ID = constants.PROCESS_ID
VENDOR_ID = constants.VENDOR_ID
OS_TYPE = constants.OS_TYPE
OS_REV = constants.OS_REV
API_LIB = constants.API_LIB
API_VER = constants.API_VER
AUDIT_CLASS = constants.AUDIT_CLASS
ACTION_CODE = constants.ACTION_CODE
FUNC_CLASS = constants.FUNC_CLASS
SUCCESS = constants.SUCCESS
AUDIT_RECORD_PATH = constants.AUDIT_RECORD_PATH
BINARY_DATA = constants.BINARY_DATA


class CITestSystem(base.TestBaseTestCase, testtools.TestCase):
    """Test System."""

    def setUp(self):
        """setUp."""
        super(CITestSystem, self).setUp()
        self.common = self.conn.common
        self.system = self.conn.system
        self.is_v4 = self.common.is_array_v4(self.conn.array_id)

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
        except exception.ResourceNotFoundException:
            self.skipTest('Skip get health check - there are no health '
                          'checks available')

        health_check_id = health_check_list.get(HEALTH_CHECK_ID)[0]

        health_check = self.system.get_health_check_details(
            health_check_id=health_check_id)
        self.assertIsInstance(health_check_list, dict)
        run_checks = health_check.get(TEST_RES, list())
        try:
            self.assertEqual(len(run_checks), 9)
        except AssertionError:
            self.assertEqual(len(run_checks), 8)

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
        try:
            tag_list = self.system.get_tags().get('tag_name')
            self.assertIsInstance(tag_list, list)
        except (exception.ResourceNotFoundException, IndexError):
            self.skipTest('Skip get_tagged_objects - there are no tagged '
                          'objects available.')

    def test_get_alert_summary(self):
        """Test get_alert_summary."""
        alert_summary = self.system.get_alert_summary()
        for key in ALERT_SUMMARY_KEYS:
            self.assertIn(key, alert_summary['serverAlertSummary'])

    def test_get_alert_ids(self):
        """Test get_alert_ids."""
        alert_ids = self.system.get_alert_ids()
        self.assertIsInstance(alert_ids, list)

    def test_get_alert_details(self):
        """Test get_alert_details."""
        alert_ids = self.system.get_alert_ids()
        if len(alert_ids) == 0:
            self.skipTest('Skip get alert details - there are no alerts')

        alert_id = alert_ids[0]
        alert_details = self.system.get_alert_details(alert_id=alert_id)
        self.assertTrue(alert_details)
        self.assertIsInstance(alert_details, dict)

    def test_acknowledge_alert(self):
        """Test acknowledge_alert."""
        alert_ids = self.system.get_alert_ids(acknowledged=False)
        if len(alert_ids) == 0:
            self.skipTest('Skip Acknowledge alert - there are no'
                          ' unacknowledged alerts')

        alert_id = alert_ids[0]
        self.system.acknowledge_alert(alert_id=alert_id)
        acknowledged_alert_ids = self.system.get_alert_ids(acknowledged=True)
        self.assertIn(alert_id, acknowledged_alert_ids)

    def test_delete_alert(self):
        """Test delete_alert."""
        alert_ids = self.system.get_alert_ids(acknowledged=False)
        if len(alert_ids) == 0:
            self.skipTest('Skip Acknowledge alert - there are no'
                          ' unacknowledged alerts')

        alert_id = alert_ids[0]
        self.system.delete_alert(alert_id=alert_id)
        alert_ids = self.system.get_alert_ids(acknowledged=True)
        self.assertNotIn(alert_id, alert_ids)

    def test_download_all_settings(self):
        """Test download_all_settings default params."""
        response = self.system.download_all_settings(
            file_password='ci_test')
        self.assertTrue(response['success'])
        self.assertIn(str(Path.cwd()), str(response['settings_path']))
        self.assertIn(constants.SETTINGS_FILENAME_TEMPLATE,
                      str(response['settings_path']))
        self.assertIn('settings_time', response.keys())
        self.cleanup_pyu4v_zip_files_in_directory(directory=Path.cwd())

    def test_download_all_settings_binary_return(self):
        """Test download_all_settings default params."""
        response = self.system.download_all_settings(
            file_password='ci_test', return_binary=True)
        self.assertTrue(response['success'])
        self.assertIn('binary_data', response.keys())
        self.assertIsInstance(response['binary_data'], bytes)
        self.assertIn('settings_time', response.keys())
        self.assertNotIn('settings_path', response.keys())

    def test_download_all_settings_custom_file_path_custom_name(self):
        """Test download_all_settings with custom path and name."""
        temp_dir_path = self.create_temp_directory()
        file_name = 'PyU4V-Settings-CustomFileName'
        response = self.system.download_all_settings(
            file_password='ci_test', dir_path=str(temp_dir_path),
            file_name=file_name)
        self.assertTrue(response['success'])
        self.assertIn(temp_dir_path, str(response['settings_path']))
        self.assertIn(file_name, str(response['settings_path']))
        self.assertIn('settings_time', response.keys())

    def test_download_all_settings_invalid_path(self):
        """Test download_all_settings invalid path exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.download_all_settings, file_password='ci_test',
            dir_path='/fake')

    def test_download_unisphere_settings_1_2(self):
        """Test download_unisphere_settings 1 & 2 exclude settings."""
        temp_dir_path = self.create_temp_directory()
        response = self.system.download_unisphere_settings(
            file_password='ci_test', dir_path=str(temp_dir_path),
            exclude_alert_notification_settings=True,
            exclude_performance_preference_settings=True)
        self.assertTrue(response['success'])
        self.assertIn(temp_dir_path, str(response['settings_path']))
        self.assertIn('settings_time', response.keys())

    def test_download_unisphere_settings_3_4(self):
        """Test download_unisphere_settings 3 & 4 exclude settings."""
        temp_dir_path = self.create_temp_directory()
        response = self.system.download_unisphere_settings(
            file_password='ci_test', dir_path=str(temp_dir_path),
            exclude_performance_user_templates=True,
            exclude_performance_metric_settings=True)
        self.assertTrue(response['success'])
        self.assertIn(temp_dir_path, str(response['settings_path']))
        self.assertIn('settings_time', response.keys())

    def test_download_unisphere_settings_exclude_exception(self):
        """Test download_unisphere_settings exclude all settings exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.download_unisphere_settings,
            file_password='ci_test', exclude_alert_notification_settings=True,
            exclude_performance_preference_settings=True,
            exclude_performance_user_templates=True,
            exclude_performance_metric_settings=True)

    def test_download_system_settings_1_2(self):
        """Test download_system_settings 1 & 2 exclude settings."""
        temp_dir_path = self.create_temp_directory()
        response = self.system.download_system_settings(
            file_password='ci_test', dir_path=str(temp_dir_path),
            exclude_alert_policy_settings=True,
            alert_level_notification_settings=True)
        self.assertTrue(response['success'])
        self.assertIn(temp_dir_path, str(response['settings_path']))
        self.assertIn('settings_time', response.keys())

    def test_download_system_settings_3_4(self):
        """Test download_system_settings 3 & 4 exclude settings."""
        temp_dir_path = self.create_temp_directory()
        response = self.system.download_system_settings(
            file_password='ci_test', dir_path=str(temp_dir_path),
            exclude_system_threshold_settings=True,
            exclude_performance_threshold_settings=True)
        self.assertTrue(response['success'])
        self.assertIn(temp_dir_path, str(response['settings_path']))
        self.assertIn('settings_time', response.keys())

    def test_download_system_settings_exclude_exception(self):
        """Test download_unisphere_settings exclude all settings exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.download_system_settings,
            file_password='ci_test', exclude_alert_policy_settings=True,
            alert_level_notification_settings=True,
            exclude_system_threshold_settings=True,
            exclude_performance_threshold_settings=True)

    def test_upload_settings(self):
        """Test upload_settings."""
        temp_dir_path = self.create_temp_directory()
        array_short_id = self.conn.array_id[-3:]
        file_name = 'ci-array-{arr}-settings'.format(arr=array_short_id)

        array_settings = self.system.download_system_settings(
            file_password='ci_test', dir_path=temp_dir_path,
            file_name=file_name, array_id=self.conn.array_id)
        self.assertTrue(array_settings['settings_path'].is_file())

        response = self.system.upload_settings(
            file_password='ci_test', file_path=array_settings['settings_path'],
            array_id=self.conn.array_id)
        self.assertTrue(response['success'])

    def test_upload_binary_settings(self):
        """Test upload_settings with binary data."""
        array_settings = self.system.download_system_settings(
            file_password='ci_test', return_binary=True)
        time.sleep(5)
        response = self.system.upload_settings(
            file_password='ci_test', binary_data=array_settings['binary_data'])
        self.assertTrue(response['success'])

    def test_upload_settings_fake_path_exception(self):
        """Test upload_settings invalid path exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.upload_settings,
            file_password='ci_test', file_path='/fake')

    def test_upload_settings_invalid_data_type(self):
        """Test upload_settings invalid data type."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.upload_settings,
            file_password='test', binary_data='/fake')

    def test_get_audit_log_list(self):
        """Test get_audit_log_list."""
        end = int(time.time())
        start = end - ((60 * 60 * 24) + 1)
        response = self.system.get_audit_log_list(
            start_time=start, end_time=end)
        self.assertTrue(response)
        self.assertIsInstance(response, list)
        self.assertIsInstance(response[0], dict)

    def test_get_audit_log_list_empty(self):
        """Test get_audit_log_list no results returned."""
        # we might get unlucky here and have a log at precisely the same time,
        # run a few times to mitigate the chance
        for i in range(5):
            try:
                end = int(time.time())
                response = self.system.get_audit_log_list(
                    start_time=end, end_time=end)
                self.assertFalse(response)
                self.assertIsInstance(response, list)
                break
            except AssertionError:
                if i < 4:
                    pass
                else:
                    self.skipTest('Could not get empty log list returned.')

    def test_get_audit_log_list_input_params(self):
        """Test get_audit_log_list input params."""
        end = int(time.time())
        start = end - (60 * 60 * 24)
        response = self.system.get_audit_log_list(
            start_time=start, end_time=end)
        self.assertTrue(response)

        # Not every record has every field populated, so we run this test a
        # number of times to increase chances of 100% coverage
        for i in range(5):
            record = random.choice(response)
            record_id = record.get(RECORD_ID)

            record_detail = self.system.get_audit_log_record(record_id)
            self.assertTrue(response)
            self.assertIsInstance(record_detail, dict)

            user_name = record_detail.get(USERNAME)
            host_name = record_detail.get(HOST_NAME)
            client_host = record_detail.get(CLIENT_HOST)
            message = record_detail.get(MESSAGE)
            activity_id = record_detail.get(ACTIVITY_ID)
            application_id = record_detail.get(APP_ID)
            application_version = record_detail.get(APP_VERSION)
            task_id = record_detail.get(TASK_ID)
            process_id = record_detail.get(PROCESS_ID)
            vendor_id = record_detail.get(VENDOR_ID)
            os_type = record_detail.get(OS_TYPE)
            os_revision = record_detail.get(OS_REV)
            api_library = record_detail.get(API_LIB)
            api_version = record_detail.get(API_VER)
            audit_class = record_detail.get(AUDIT_CLASS)
            action_code = record_detail.get(ACTION_CODE)
            function_class = record_detail.get(FUNC_CLASS)

            response = self.system.get_audit_log_list(
                start_time=start, end_time=end, user_name=user_name,
                host_name=host_name, client_host=client_host, message=message,
                record_id=record_id, activity_id=activity_id, task_id=task_id,
                application_id=application_id, process_id=process_id,
                application_version=application_version, vendor_id=vendor_id,
                os_type=os_type, os_revision=os_revision,
                api_library=api_library, api_version=api_version,
                audit_class=audit_class, action_code=action_code,
                function_class=function_class)
            self.assertTrue(response)
            self.assertIsInstance(response, list)
            self.assertEqual(1, len(response))
            self.assertIsInstance(response[0], dict)
            self.assertEqual(record_id, response[0].get(RECORD_ID))

    def test_download_audit_log_record(self):
        """Test download_audit_log_record write to file."""
        temp_dir_path = Path(self.create_temp_directory())
        response = self.system.download_audit_log_record(
            dir_path=str(temp_dir_path), timeout=448)
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertTrue(response.get(SUCCESS))
        self.assertIn(AUDIT_RECORD_PATH, response.keys())
        self.assertIn(str(temp_dir_path),
                      str(response.get(AUDIT_RECORD_PATH)))

    def test_download_audit_log_record_return_binary(self):
        """Test download_audit_log_record return binary data."""
        response = self.system.download_audit_log_record(
            return_binary=True, timeout=448)
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertTrue(response.get(SUCCESS))
        self.assertIn(BINARY_DATA, response.keys())
        self.assertIsInstance(response.get(BINARY_DATA), bytes)

    # def test_get_director_list(self):
    #     """Test get_director_list."""
    #     response = self.system.get_director_list()
    #     self.assertTrue(response)
    #     self.assertIsInstance(response, list)

    def test_get_director_list_iscsi_only(self):
        """Test get_director_list iscsi_only set as True."""
        dir_list = self.system.get_director_list(iscsi_only=True)
        if not dir_list:
            self.skipTest(
                'test_get_director_list_iscsi_only - No iSCSI Directors '
                'available in CI environment.')

        self.assertIsInstance(dir_list, list)
        if self.is_v4:
            self.assertIn('OR', dir_list[0])
        else:
            self.assertIn('SE', dir_list[0])

    def test_get_director_from_port_list(self):
        """Test get_director_port_list."""
        director_list = self.system.get_director_list()
        director_id = None
        for director in director_list:
            if self.common.is_array_v4(self.conn.array_id):
                if director[:2] in ['OR']:
                    director_id = director
                    break
            elif director[:2] in ['FA', 'DF', 'RF', 'SE']:
                director_id = director
                break
        response = self.system.get_director_port_list(director_id=director_id)
        self.assertTrue(response)
        self.assertIsInstance(response, list)

    def test_get_director_port_list_iscsi_target_set(self):
        """Test get_director_port_list with iscsi_only set as True."""
        iscsi_dir_list = self.system.get_director_list(iscsi_only=True)
        if not iscsi_dir_list:
            self.skipTest('No iSCSI Directors available in CI environment.')
        director_id = random.choice(iscsi_dir_list)

        all_ports = self.system.get_director_port_list(
            director_id=director_id)
        self.assertTrue(all_ports)
        self.assertIsInstance(all_ports, list)
        try:
            tgt_ports = self.system.get_directory_port_iscsi_endpoint_list(
                director_id=director_id, iscsi_endpoint=True)
            if tgt_ports:
                self.assertTrue(tgt_ports)
                self.assertIsInstance(tgt_ports, list)
        except exception.ResourceNotFoundException:
            tgt_ports = list()
        try:
            not_tgt_ports = self.system.get_directory_port_iscsi_endpoint_list(
                director_id=director_id, iscsi_endpoint=False)
            if not_tgt_ports:
                self.assertTrue(not_tgt_ports)
                self.assertIsInstance(not_tgt_ports, list)
        except exception.ResourceNotFoundException:
            not_tgt_ports = list()

        self.assertEqual(len(all_ports),
                         (len(tgt_ports) + len(not_tgt_ports)))

    def test_get_ip_interface_list(self):
        """Test get_ip_interface_list."""
        found_ip_list = False

        iscsi_dir_list = self.system.get_director_list(iscsi_only=True)
        if not iscsi_dir_list:
            self.skipTest('No iSCSI Directors available in CI environment.')
        for dir_id in iscsi_dir_list:
            port_list = self.system.get_directory_port_iscsi_endpoint_list(
                director_id=dir_id, iscsi_endpoint=False)
            if not port_list:
                continue
            for port in port_list:
                port_id = port.get('portId')
                ip_interface_list = self.system.get_ip_interface_list(
                    director_id=dir_id, port_id=port_id)
                if not ip_interface_list:
                    continue

                self.assertTrue(ip_interface_list)
                self.assertIsInstance(ip_interface_list, list)
                found_ip_list = True

        if not found_ip_list:
            self.skipTest('No IP interfaces available in CI environment.')

    def test_get_ip_interface(self):
        """Test get_ip_interface."""
        found_ip = False

        iscsi_dir_list = self.system.get_director_list(iscsi_only=True)
        if not iscsi_dir_list:
            self.skipTest('test_get_ip_interface - No iSCSI Directors '
                          'available in CI environment.')
        for dir_id in iscsi_dir_list:
            port_list = self.system.get_directory_port_iscsi_endpoint_list(
                director_id=dir_id, iscsi_endpoint=False)
            if not port_list:
                continue
            for port in port_list:
                port_id = port.get('portId')
                ip_interface_list = self.system.get_ip_interface_list(
                    director_id=dir_id, port_id=port_id)
                if not ip_interface_list:
                    continue

                ip_interface_details = self.system.get_ip_interface(
                    director_id=dir_id, port_id=port_id,
                    interface_id=ip_interface_list[0])
                self.assertTrue(ip_interface_details)
                self.assertIsInstance(ip_interface_details, dict)
                found_ip = True

        if not found_ip:
            self.skipTest('No IP interfaces available in CI environment.')

    def test_change_local_user_password(self):
        """Test change_local_user_password, if success return is None"""
        try:
            change_password = self.system.change_local_user_password(
                username='testchange', current_password='manuallyset',
                new_password='newpassword')
            self.assertEqual(None, change_password)
        except exception.VolumeBackendAPIException:
            self.skipTest('Skip Password Change - please run test manually')

    def test_get_director(self):
        """Test get_director."""
        availability = 'availability'
        director_number = 'director_number'
        director_slot_number = 'director_slot_number'
        director_list = self.system.get_director_list()
        if not director_list:
            self.skipTest('Skipping test_get_director - no directors.')
        for director in director_list:
            director_details = self.system.get_director(director)
            self.assertIsInstance(director_details, dict)
            self.assertIn(availability, director_details)
            self.assertIn(director_number, director_details)
            self.assertIn(director_slot_number, director_details)
            self.assertIn(constants.DIRECTOR_ID, director_details)
            self.assertIn(constants.NUM_OF_PORTS, director_details)
            if not self.is_v4:
                self.assertIn(constants.NUM_OF_CORES, director_details)
                self.assertIsInstance(
                    director_details[constants.NUM_OF_CORES], int)
            self.assertIsInstance(director_details[availability], str)
            self.assertIsInstance(director_details[director_number], int)
            self.assertIsInstance(director_details[director_slot_number], int)
            director_id = director_details[constants.DIRECTOR_ID]
            self.assertIsInstance(director_id, str)
            self.assertIsInstance(
                director_details[constants.NUM_OF_PORTS], int)
            self.assertIsNotNone(re.match(constants.DIRECTOR_SEARCH_PATTERN,
                                          director_id))

    def test_get_director_list(self):
        """Test get_director_list."""
        director_list = self.system.get_director_list()
        if not director_list:
            self.skipTest('Skipping test_get_director_list - no directors.')
        self.assertIsInstance(director_list, list)
        for director in director_list:
            self.assertIsInstance(director, str)
            self.assertIsNotNone(re.match(constants.DIRECTOR_SEARCH_PATTERN,
                                          director))

    def test_get_director_port(self):
        """Test get_director_port."""
        director_port_list = self.provision.get_port_list()
        if not director_port_list:
            self.skipTest('Skipping test_get_director_port as no ports exist')
        director_port = director_port_list[0]
        director = director_port[constants.DIRECTOR_ID]
        port = director_port[constants.PORT_ID]
        port_details = self.system.get_director_port(
            director, port)
        self._validate_director_port(port_details)

    def test_get_director_port_list(self):
        """Test get_director_port_list."""
        director_list = self.system.get_director_list()
        if not director_list:
            self.skipTest('Skipping test_get_director_port_list '
                          'as no directors exist')
        director = director_list[0]
        director_port_list = self.system.get_director_port_list(
            director)
        if not director_list:
            self.skipTest('Skipping test_get_director_port_list '
                          'as no port exist for the director')
        self.assertIsInstance(director_port_list, list)
        for director_port in director_port_list:
            self.assertIsInstance(director_port, dict)
            self.assertIn(constants.DIRECTOR_ID, director_port)
            self.assertIn(constants.PORT_ID, director_port)
            director_id = director_port[constants.DIRECTOR_ID]
            port_id = director_port[constants.PORT_ID]
            self.assertIsInstance(director_id, str)
            self.assertIsInstance(port_id, str)
            self.assertIsNotNone(
                re.match(constants.DIRECTOR_SEARCH_PATTERN, director_id))
            self.assertIsNotNone(
                re.match(constants.PORT_SEARCH_PATTERN, port_id))

    def test_get_port_identifier(self):
        """Test get_port_identifier."""
        director_port_list = self.provision.get_port_list()
        if not director_port_list:
            self.skipTest('Skipping test_get_port_identifier '
                          'as no ports exist for that array')
        director_port = director_port_list[0]
        director = director_port[constants.DIRECTOR_ID]
        port = director_port[constants.PORT_ID]
        port_identifier = self.system.get_port_identifier(
            director, port)
        if not port_identifier:
            self.skipTest('Skipping test_get_port_identifier '
                          'as no port identifier exists for that'
                          'port')
        self.assertIsInstance(port_identifier, str)
        search_pattern = '{wwn}|{iqn}'.format(
            wwn=constants.WWN_SEARCH_PATTERN_16,
            iqn=constants.ISCSI_IQN_SEARCH_PATTERN)
        self.assertIsNotNone(
            re.match(search_pattern, port_identifier))

    def _validate_director_port(self, port_details):
        """Helper method for validating get director port return details.

        :param port_details: port details -- dict
        """
        symmetrix_port = 'symmetrixPort'
        port_interface = 'port_interface'
        port_status = 'port_status'
        director_status = 'director_status'
        num_of_hypers = 'num_of_hypers'
        max_speed = 'max_speed'
        self.assertIsInstance(port_details, dict)
        self.assertIn(symmetrix_port, port_details)
        port_details = port_details[symmetrix_port]
        symmetrix_port_key = port_details[constants.SYMMETRIX_PORT_KEY]
        self.assertIsInstance(symmetrix_port_key, dict)
        self.assertIn(constants.DIRECTOR_ID, symmetrix_port_key)
        self.assertIn(constants.PORT_ID, symmetrix_port_key)
        self.assertIsInstance(symmetrix_port_key[constants.PORT_ID], str)
        director_id = symmetrix_port_key[constants.DIRECTOR_ID]
        self.assertIsInstance(director_id, str)
        self.assertIsNotNone(
            re.match(constants.DIRECTOR_SEARCH_PATTERN, director_id))
        if port_interface in port_details:
            self.assertIsInstance(port_details[port_interface], str)
        if port_status in port_details:
            self.assertIsInstance(port_details[port_status], str)
        if director_status in port_details:
            self.assertIsInstance(port_details[director_status], str)
        if constants.TYPE in port_details:
            self.assertIsInstance(port_details[constants.TYPE], str)
        if constants.NUM_OF_CORES in port_details:
            self.assertIsInstance(port_details[constants.NUM_OF_CORES], int)
        if num_of_hypers in port_details:
            self.assertIsInstance(port_details[num_of_hypers], int)
        if max_speed in port_details:
            self.assertIsInstance(port_details[max_speed], str)

    def test_get_iscsi_ip_address_and_iqn(self):
        """Test get_iscsi_ip_address_and_iqn."""
        ip_addresses = []
        port_list = self.provision.get_port_list()
        if not port_list:
            self.skipTest('Skipping test_get_iscsi_ip_address_and_iqn '
                          'as no ports were found')
        if not self.is_v4:
            iscsi_director_ports = [p for p in port_list if 'SE-' in p[
                constants.DIRECTOR_ID]]
        else:
            # V4 iscsi
            iscsi_director_ports = self.system.get_iscsi_director_port_list_v4(
                'test_get_iscsi_ip_address_and_iqn')
        if not iscsi_director_ports:
            self.skipTest('Skipping test_get_iscsi_ip_address_and_iqn '
                          'as SE director ports were found')
        for se_director_port in iscsi_director_ports:
            director_id = se_director_port[constants.DIRECTOR_ID]
            port_id = se_director_port[constants.PORT_ID]
            iscsi_id = self.provision.format_director_port(
                director_id, port_id)
            ip_addresses, iqn = (
                self.system.get_iscsi_ip_address_and_iqn(iscsi_id))

            if not ip_addresses:
                continue
            self.assertIsInstance(ip_addresses, list)
            for ip in ip_addresses:
                valid_ip = (
                    self.common.check_ipv4(
                        ip) or self.common.check_ipv6(ip))
                self.assertIsInstance(ip, str)
                self.assertTrue(valid_ip)
            self.assertIsNotNone(iqn)
            # self.assertIsNotNone(
            #     re.match(constants.ISCSI_IQN_SEARCH_PATTERN, iqn))
        if not ip_addresses:
            self.skipTest('Skipping test_get_iscsi_ip_address_and_iqn '
                          'as no ip_addresses were found for iSCSI.')

    def test_get_any_director_port(self):
        """Test get_any_director_port."""
        if not self.is_v4:
            fa_directors = self.system.get_fa_directors()
            if not fa_directors:
                self.skipTest('Skipping test_get_any_director_port '
                              'as no FA directors found.')
            fa_director = fa_directors[0]
            port = self.system.get_any_director_port(fa_director)
            self.assertIsNotNone(port)
            self.assertIsInstance(port, str)
        else:
            or_directors = self.system.get_or_directors()
            if not or_directors:
                self.skipTest('Skipping test_get_any_director_port '
                              'as no FA directors found.')
            or_director = or_directors[0]
            port = self.system.get_any_director_port(or_director)
            self.assertIsNotNone(port)
            self.assertIsInstance(port, str)

    def test_get_iscsi_director_port_list_v4(self):
        """test_get_iscsi_director_port_list_v4."""
        if not self.is_v4:
            self.skipTest('Skipping test_get_iscsi_director_port_list_v4 '
                          '- this if V4 only')
        directors = self.conn.system.get_director_list()
        if not directors:
            self.skipTest('test_get_iscsi_director_port_list_v4 - '
                          'Could not find any directors.')
        port_list = self.conn.system.get_iscsi_director_port_list_v4(
            directors)
        self.assertIsInstance(port_list, list)
        self.assertTrue('OR' in port_list[0].get('directorId'))
        port_info = self.system.get_director_port(
            port_list[0].get('directorId'), port_list[0].get('portId'))
        self.assertEqual(
            ['iSCSI'],
            port_info.get('symmetrixPort').get('enabled_protocol'))

    def test_get_fc_director_port_list_v4(self):
        """test_get_fc_director_port_list_v4."""
        if not self.is_v4:
            self.skipTest('Skipping test_get_fc_director_port_list_v4 '
                          '- this if V4 only')
        directors = self.conn.system.get_director_list()
        if not directors:
            self.skipTest('test_get_fc_director_port_list_v4 - '
                          'Could not find any directors.')
        port_list = self.conn.system.get_fc_director_port_list_v4(
            directors)
        self.assertIsInstance(port_list, list)
        self.assertTrue('OR' in port_list[0].get('directorId'))
        port_info = self.system.get_director_port(
            port_list[0].get('directorId'), port_list[0].get('portId'))
        self.assertEqual(
            ['SCSI_FC'],
            port_info.get('symmetrixPort').get('enabled_protocol'))

    def test_get_nvme_director_port_list_v4(self):
        """test_get_nvme_director_port_list_v4."""
        if not self.is_v4:
            self.skipTest('Skipping test_get_nvme_director_port_list_v4 '
                          '- this if V4 only')
        directors = self.conn.system.get_director_list()
        if not directors:
            self.skipTest('test_get_nvme_director_port_list_v4 - '
                          'Could not find any directors.')
        port_list = self.conn.system.get_nvme_director_port_list_v4(
            directors)
        if not port_list:
            self.skipTest('test_get_nvme_director_port_list_v4 - '
                          'Could not find any NVMe Ports.')
        self.assertIsInstance(port_list, list)
        self.assertTrue('OR' in port_list[0].get('directorId'))
        port_info = self.system.get_director_port(
            port_list[0].get('directorId'), port_list[0].get('portId'))
        self.assertEqual(
            ['NVMe/FC'],
            port_info.get('symmetrixPort').get('enabled_protocol'))

    def test_get_rdf_director_port_list_v4(self):
        """test_get_rdf_director_port_list_v4."""
        if not self.is_v4:
            self.skipTest('Skipping test_get_rdf_director_port_list_v4 '
                          '- this if V4 only')
        directors = self.conn.system.get_director_list()
        if not directors:
            self.skipTest('test_get_rdf_director_port_list_v4 - '
                          'Could not find any directors.')
        port_list = self.conn.system.get_rdf_director_port_list_v4(
            directors)
        self.assertIsInstance(port_list, list)
        self.assertTrue('OR' in port_list[0].get('directorId'))
        port_info = self.system.get_director_port(
            port_list[0].get('directorId'), port_list[0].get('portId'))
        self.assertEqual(
            ['RDF_FC'],
            port_info.get('symmetrixPort').get('enabled_protocol'))

    def test_get_rdf_gige_director_port_list_v4(self):
        """test_get_rdf_gige_director_port_list_v4."""
        if not self.is_v4:
            self.skipTest('Skipping test_get_rdf_gige_director_port_list_v4 '
                          '- this if V4 only')
        directors = self.conn.system.get_director_list()
        if not directors:
            self.skipTest('test_get_rdf_gige_director_port_list_v4 - '
                          'Could not find any directors.')
        port_list = self.conn.system.get_rdf_gige_director_port_list_v4(
            directors)
        self.assertIsInstance(port_list, list)
        self.assertTrue('OR' in port_list[0].get('directorId'))
        port_info = self.system.get_director_port(
            port_list[0].get('directorId'), port_list[0].get('portId'))
        self.assertEqual(
            ['RDF_GigE'],
            port_info.get('symmetrixPort').get('enabled_protocol'))

    def test_set_director_port_online(self):
        """test_set_director_port_online."""
        self.skipTest('Skipping Test as it is disruptive to normal '
                      'operations, please run test manually')
        port_details = self.system.get_director_port(
            director='OR-1C', port_no='3').get('symmetrixPort')
        if port_details.get('port_status') == 'ON':
            port_details = self.system.set_director_port_online(
                director='OR-1C', port_no='3', port_online=False).get(
                'symmetrixPort')
            self.assertEqual('OFF', port_details.get('port_status'))
            port_details = self.system.set_director_port_online(
                director='OR-1C', port_no='3', port_online=True).get(
                'symmetrixPort')
            self.assertEqual('ON', port_details.get('port_status'))

    def test_get_management_server_resources(self):
        resource_usage = self.system.get_management_server_resources()
        self.assertIsInstance(resource_usage, dict)

    def test_refresh_array_details(self):
        refresh = self.system.refresh_array_details()
        self.assertEqual(refresh, None)

    def test_get_server_logging_level(self):
        log_level = self.system.get_server_logging_level()
        self.assertIn('server_logging_level', log_level)
        self.assertIn('restapi_logging_enabled', log_level)

    def test_set_server_logging_level(self):
        initial_log_level = self.system.get_server_logging_level()
        if initial_log_level['server_logging_level'] == 'INFO':
            server_log_level = 'WARN'
        else:
            server_log_level = 'INFO'
        changed_log_level = self.system.set_server_logging_level(
            server_log_level=server_log_level, restapi_logging_enabled=True)
        self.assertEqual(True, changed_log_level['restapi_logging_enabled'])
        self.assertEqual(server_log_level,
                         changed_log_level['server_logging_level'])
        reset = self.system.set_server_logging_level()
        self.assertEqual(initial_log_level, reset)

    def test_get_snmp_trap_configuration(self):
        snmp_config = self.system.get_snmp_trap_configuration()
        self.assertIn('engine_id', snmp_config)
        self.assertIn('snmp_traps', snmp_config)

    def test_set_snmp_trap_destination(self):
        self.skipTest(reason="Test Run manually")
        new_config = self.system.set_snmp_trap_destination(
            name='pyu4vunilinux2.crk.lab.emc.com', port=52)
        self.assertEquals('pyu4vunilinux2.crk.lab.emc.com', new_config['name'])
        self.system.delete_snmp_trap_destination(snmp_id=new_config['id'])

    def test_delete_snmp_trap_destination(self):
        snmp_id = self.system.set_snmp_trap_destination(
            name='10.60.156.28', port=52)['id']
        self.system.delete_snmp_trap_destination(snmp_id=snmp_id)
        config_after_delete = self.system.get_snmp_trap_configuration()
        self.assertNotIn(snmp_id, config_after_delete['snmp_traps'])

    def test_update_snmp_trap_destination(self):
        snmp_details = self.system.set_snmp_trap_destination(
            name='10.60.156.28', port=52)
        snmp_id = snmp_details['id']
        updated_snmp_destination = self.system.update_snmp_trap_destination(
            snmp_id=snmp_id, port=234)
        updated_port = updated_snmp_destination['port']
        updated_snmp_id = updated_snmp_destination['id']
        self.assertIs(234, updated_port)
        self.system.delete_snmp_trap_destination(snmp_id=updated_snmp_id)
