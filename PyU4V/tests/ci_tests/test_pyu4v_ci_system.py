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
            dir_path=str(temp_dir_path))
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertTrue(response.get(SUCCESS))
        self.assertIn(AUDIT_RECORD_PATH, response.keys())
        self.assertIn(str(temp_dir_path),
                      str(response.get(AUDIT_RECORD_PATH)))

    def test_download_audit_log_record_return_binary(self):
        """Test download_audit_log_record return binary data."""
        response = self.system.download_audit_log_record(return_binary=True)
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertTrue(response.get(SUCCESS))
        self.assertIn(BINARY_DATA, response.keys())
        self.assertIsInstance(response.get(BINARY_DATA), bytes)

    def test_get_director_list(self):
        """Test get_director_list."""
        response = self.system.get_director_list()
        self.assertTrue(response)
        self.assertIsInstance(response, list)

    def test_get_director_list_iscsi_only(self):
        """Test get_director_list iscsi_only set as True."""
        response = self.system.get_director_list(iscsi_only=True)
        self.assertTrue(response)
        self.assertIsInstance(response, list)
        for pmax_dir in response:
            self.assertIn('SE', pmax_dir)

    def test_get_director_port_list(self):
        """Test get_director_port_list."""
        director_list = self.system.get_director_list()
        director_id = None
        for director in director_list:
            if director[:2] in ['FA', 'DF', 'RF', 'SE']:
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

        tgt_ports = self.system.get_director_port_list(
            director_id=director_id, iscsi_target=True)
        self.assertTrue(tgt_ports)
        self.assertIsInstance(tgt_ports, list)

        not_tgt_ports = self.system.get_director_port_list(
            director_id=director_id, iscsi_target=False)
        self.assertTrue(not_tgt_ports)
        self.assertIsInstance(not_tgt_ports, list)

        self.assertEqual(len(all_ports),
                         (len(tgt_ports) + len(not_tgt_ports)))

    def test_get_ip_interface_list(self):
        """Test get_ip_interface_list."""
        found_ip_list = False

        iscsi_dir_list = self.system.get_director_list(iscsi_only=True)
        if not iscsi_dir_list:
            self.skipTest('No iSCSI Directors available in CI environment.')
        for dir_id in iscsi_dir_list:
            port_list = self.system.get_director_port_list(
                director_id=dir_id, iscsi_target=False)
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
            self.skipTest('No iSCSI Directors available in CI environment.')
        for dir_id in iscsi_dir_list:
            port_list = self.system.get_director_port_list(
                director_id=dir_id, iscsi_target=False)
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
