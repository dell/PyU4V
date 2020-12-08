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
"""test_pyu4v_system.py."""

import testtools
import time

from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

from PyU4V import common
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants
from PyU4V.utils import exception
from PyU4V.utils import file_handler

ARRAY_ID = constants.ARRAY_ID
ARRAY_NUM = constants.ARRAY_NUM
HEALTH = constants.HEALTH
HEALTH_CHECK = constants.HEALTH_CHECK
SG_ID = constants.SG_ID
SG_NUM = constants.SG_NUM
SYMMETRIX = constants.SYMMETRIX
SYSTEM = constants.SYSTEM
TAG = constants.TAG
TAG_NAME = constants.TAG_NAME
ALERT_ID = pcd.CommonData.alert_id
ALERT = constants.ALERT
AUDIT_LOG_RECORD = constants.AUDIT_LOG_RECORD
EXPORT_FILE = constants.EXPORT_FILE
AUDIT_LOG_FILENAME = constants.AUDIT_LOG_FILENAME
SUCCESS = constants.SUCCESS
BINARY_DATA = constants.BINARY_DATA
AUDIT_RECORD_PATH = constants.AUDIT_RECORD_PATH


class PyU4VSystemTest(testtools.TestCase):
    """Test System."""

    def setUp(self):
        """Setup."""
        super(PyU4VSystemTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.common = self.conn.common
            self.system = self.conn.system

    def test_get_system_health(self):
        """Test get_system_health."""
        health_check_result = self.system.get_system_health()
        self.assertEqual(self.data.array_health, health_check_result)

    def test_list_system_health_check(self):
        """Test list_system_health_checks."""
        health_check_list = self.system.list_system_health_check()
        self.assertEqual(self.data.array_health_check_list, health_check_list)

    def test_get_health_check_details(self):
        """Test get_health_check_details."""
        health_check = self.system.get_health_check_details(health_check_id=1)
        self.assertEqual(self.data.health_check_response, health_check)

    def test_perform_health_check(self):
        """Test perform_health_check."""
        run_test = self.system.perform_health_check()
        self.assertEqual(run_test, self.data.perform_health_check_response)

    def test_delete_health_check(self):
        """Test delete_health_check."""
        common.CommonFunctions.delete_resource = MagicMock(
            side_effect=self.common.delete_resource)
        self.system.delete_health_check(health_check_id=1)
        common.CommonFunctions.delete_resource.assert_called_once_with(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=self.conn.array_id, resource_type=HEALTH,
            resource_type_id=HEALTH_CHECK, object_type=1)

    def test_get_disk_id_list(self):
        """Test get_disk_id_list."""
        disk_list = self.system.get_disk_id_list(failed=True)
        self.assertEqual(self.data.disk_list, disk_list)

    def test_get_disk_details(self):
        """Test get_disk_details."""
        disk_info = self.system.get_disk_details(disk_id='1')
        self.assertEqual(self.data.disk_info, disk_info)

    def test_get_tags(self):
        """Test get_tags."""
        common.CommonFunctions.get_resource = MagicMock(
            side_effect=self.common.get_resource)

        tag_list = self.system.get_tags(
            array_id=self.conn.array_id, tag_name='UNIT-TEST',
            storage_group_id='TEST-SG', num_of_storage_groups=1,
            num_of_arrays=3)

        common.CommonFunctions.get_resource.assert_called_once_with(
            category=SYSTEM, resource_level=TAG, params={
                ARRAY_ID: self.conn.array_id, TAG_NAME: 'UNIT-TEST',
                SG_ID: 'TEST-SG', SG_NUM: '1', ARRAY_NUM: '3'})
        self.assertEqual(self.data.tag_list, tag_list)

    def test_get_tagged_objects(self):
        """Test get_tagged_objects."""
        tagged_objects = self.system.get_tagged_objects(tag_name='UNIT-TEST')
        self.assertEqual(self.data.tagged_objects, tagged_objects)

    def test_get_alert_summary(self):
        """Test get_alert_summary."""
        alert_summary = self.system.get_alert_summary()
        self.assertEqual(self.data.alert_summary, alert_summary)

    def test_get_alert_ids(self):
        """Test get_alert_ids."""
        alert_ids = self.system.get_alert_ids(
            array='123456789', _type='Server', severity='Warning', state='New',
            created_date='1234455', _object='BE', object_type='Director',
            acknowledged=True, description='Alert')
        self.assertEqual(self.data.alert_list['alertId'], alert_ids)

    def test_get_alert_details(self):
        """Test get_alert_details."""
        alert_details = self.system.get_alert_details(
            alert_id=ALERT_ID)
        self.assertEqual(self.data.alert_details, alert_details)

    @mock.patch.object(common.CommonFunctions, 'modify_resource')
    def test_acknowledge_alert(self, mck_modify):
        """Test acknowledge_alert."""
        ref_payload = {'editAlertActionParam': 'ACKNOWLEDGE'}
        self.system.acknowledge_alert(alert_id=ALERT_ID)
        mck_modify.assert_called_once_with(
            category=SYSTEM, resource_level=ALERT,
            resource_level_id=ALERT_ID, payload=ref_payload)

    @mock.patch.object(common.CommonFunctions, 'delete_resource')
    def test_delete_alert(self, mck_delete):
        """Test delete_alert."""
        self.system.delete_alert(alert_id=ALERT_ID)
        mck_delete.assert_called_once_with(
            category=SYSTEM, resource_level=ALERT, resource_level_id=ALERT_ID)

    @mock.patch.object(
        common.CommonFunctions, 'download_file',
        return_value=pf.FakeResponse(200, dict(), content=b'test_binary_data'))
    def test_download_settings_success_return_binary(self, mck_dl):
        """Test _download_settings success binary data returned."""
        response = self.system._download_settings(request_body=dict(),
                                                  return_binary=True)
        mck_dl.assert_called_once_with(
            category=constants.SYSTEM, resource_level=constants.SETTINGS,
            resource_type=constants.EXPORT_FILE, payload=dict())
        self.assertTrue(response['success'])
        self.assertIn('binary_data', response.keys())
        self.assertEqual(b'test_binary_data', response['binary_data'])

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch.object(
        common.CommonFunctions, 'download_file',
        return_value=pf.FakeResponse(200, dict(), content=b'test_binary_data'))
    def test_download_settings_success_write_file(self, mck_dl, mck_open):
        """Test _download_settings success"""
        response = self.system._download_settings(request_body=dict())
        mck_dl.assert_called_once_with(
            category=constants.SYSTEM, resource_level=constants.SETTINGS,
            resource_type=constants.EXPORT_FILE, payload=dict())
        mck_open.assert_called_once()
        self.assertTrue(response['success'])
        self.assertIn(str(Path.cwd()), str(response['settings_path']))
        self.assertIn(constants.SETTINGS_FILENAME_TEMPLATE,
                      str(response['settings_path']))

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch.object(
        common.CommonFunctions, 'download_file',
        return_value=pf.FakeResponse(200, dict(), content=b'test_binary_data'))
    def test_download_settings_success_write_file_custom_path(self, mck_dl,
                                                              mck_open):
        """Test _download_settings success"""
        response = self.system._download_settings(
            request_body=dict(), file_name='test', dir_path=Path.home())
        mck_dl.assert_called_once_with(
            category=constants.SYSTEM, resource_level=constants.SETTINGS,
            resource_type=constants.EXPORT_FILE, payload=dict())
        mck_open.assert_called_once()
        self.assertTrue(response['success'])
        self.assertIn(str(Path.home()), str(response['settings_path']))
        self.assertIn('test.zip', str(response['settings_path']))

    @mock.patch.object(common.CommonFunctions, 'download_file',
                       return_value=None)
    def test_download_settings_fail_no_response(self, mck_dl):
        """Test _download_settings fail no response from API."""
        response = self.system._download_settings(request_body=dict())
        mck_dl.assert_called_once_with(
            category=constants.SYSTEM, resource_level=constants.SETTINGS,
            resource_type=constants.EXPORT_FILE, payload=dict())
        self.assertEqual({'success': False}, response)

    @mock.patch.object(
        common.CommonFunctions, 'download_file',
        return_value=pf.FakeResponse(200, dict(), content=b'test_binary_data'))
    def test_download_settings_dir_path_exception(self, mck_dl):
        """Test _download_settings directory doesn't exist exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system._download_settings,
            request_body=dict(), dir_path='fake')
        mck_dl.assert_called_once_with(
            category=constants.SYSTEM, resource_level=constants.SETTINGS,
            resource_type=constants.EXPORT_FILE, payload=dict())

    def test_download_all_settings(self):
        """Test download_all_settings."""
        ref_request_body = {
            constants.FILE_PASSWORD: 'test_password',
            constants.SRC_ARRAY: self.data.remote_array}
        with mock.patch.object(self.system, '_download_settings') as mck_dl:
            self.system.download_all_settings(
                file_password='test_password', dir_path='/test/file/path',
                file_name='test_filename', array_id=self.data.remote_array,
                return_binary=True)
            mck_dl.assert_called_once_with(
                request_body=ref_request_body, dir_path='/test/file/path',
                file_name='test_filename', return_binary=True)

    def test_download_unisphere_settings_1_2_params(self):
        """Test download_unisphere_settings success 1 & 2 output params."""
        ref_request_body = {
            constants.FILE_PASSWORD: 'test_password',
            constants.SRC_ARRAY: self.conn.array_id,
            constants.EXCLUDE_SYS_SETTINGS: [constants.ALL_SETTINGS],
            constants.EXCLUDE_UNI_SETTINGS: [constants.UNI_ALERT_SETTINGS,
                                             constants.UNI_PERF_PREF_SETTINGS]}
        with mock.patch.object(self.system, '_download_settings') as mck_dl:
            self.system.download_unisphere_settings(
                file_password='test_password', dir_path='/test/file/path',
                file_name='test_filename', return_binary=True,
                exclude_alert_notification_settings=True,
                exclude_performance_preference_settings=True)
            mck_dl.assert_called_once_with(
                request_body=ref_request_body, dir_path='/test/file/path',
                file_name='test_filename', return_binary=True)

    def test_download_unisphere_settings_3_4_params(self):
        """Test download_unisphere_settings success 3 & 4 output params."""
        ref_request_body = {
            constants.FILE_PASSWORD: 'test_password',
            constants.SRC_ARRAY: self.conn.array_id,
            constants.EXCLUDE_SYS_SETTINGS: [constants.ALL_SETTINGS],
            constants.EXCLUDE_UNI_SETTINGS: [
                constants.UNI_PERF_USER_SETTINGS,
                constants.UNI_PERF_METRIC_SETTINGS]}
        with mock.patch.object(self.system, '_download_settings') as mck_dl:
            self.system.download_unisphere_settings(
                file_password='test_password', dir_path='/test/file/path',
                file_name='test_filename', return_binary=True,
                exclude_performance_user_templates=True,
                exclude_performance_metric_settings=True)
            mck_dl.assert_called_once_with(
                request_body=ref_request_body, dir_path='/test/file/path',
                file_name='test_filename', return_binary=True)

    def test_download_unisphere_settings_all_excluded_exception(self):
        """Test download_unisphere_settings all settings excluded exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.download_unisphere_settings,
            file_password='test', exclude_alert_notification_settings=True,
            exclude_performance_preference_settings=True,
            exclude_performance_user_templates=True,
            exclude_performance_metric_settings=True)

    def test_download_system_settings_1_2_params(self):
        """Test download_system_settings success 1 & 2 output params."""
        ref_request_body = {
            constants.FILE_PASSWORD: 'test_password',
            constants.SRC_ARRAY: self.data.remote_array,
            constants.EXCLUDE_SYS_SETTINGS: [
                constants.SYS_ALERT_SETTINGS,
                constants.SYS_ALERT_NOTIFI_SETTINGS],
            constants.EXCLUDE_UNI_SETTINGS: [constants.ALL_SETTINGS]}

        with mock.patch.object(self.system, '_download_settings') as mck_dl:
            self.system.download_system_settings(
                file_password='test_password', dir_path='/test/file/path',
                file_name='test_filename', array_id=self.data.remote_array,
                return_binary=True, exclude_alert_policy_settings=True,
                alert_level_notification_settings=True)
            mck_dl.assert_called_once_with(
                request_body=ref_request_body, dir_path='/test/file/path',
                file_name='test_filename', return_binary=True)

    def test_download_system_settings_3_4_params(self):
        """Test download_system_settings success 3 & 4 output params."""
        ref_request_body = {
            constants.FILE_PASSWORD: 'test_password',
            constants.SRC_ARRAY: self.data.remote_array,
            constants.EXCLUDE_SYS_SETTINGS: [
                constants.SYS_THRESH_SETTINGS,
                constants.SYS_PERF_THRESH_SETTINGS],
            constants.EXCLUDE_UNI_SETTINGS: [constants.ALL_SETTINGS]}

        with mock.patch.object(self.system, '_download_settings') as mck_dl:
            self.system.download_system_settings(
                file_password='test_password', dir_path='/test/file/path',
                file_name='test_filename', array_id=self.data.remote_array,
                return_binary=True, exclude_system_threshold_settings=True,
                exclude_performance_threshold_settings=True)
            mck_dl.assert_called_once_with(
                request_body=ref_request_body, dir_path='/test/file/path',
                file_name='test_filename', return_binary=True)

    def test_download_system_settings_all_excluded_exception(self):
        """Test download_system_settings all settings excluded exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.download_system_settings,
            file_password='test', exclude_alert_policy_settings=True,
            alert_level_notification_settings=True,
            exclude_system_threshold_settings=True,
            exclude_performance_threshold_settings=True)

    @mock.patch.object(common.CommonFunctions, 'upload_file')
    @mock.patch('builtins.open', return_value=__file__)
    def test_upload_settings(self, mck_open, mck_up):
        """Test upload_settings success."""
        ref_form_data = {
            constants.ZIP_FILE: __file__,
            constants.TGT_ARRAYS: self.data.remote_array,
            constants.FILE_PASSWORD: 'test_password'}
        self.system.upload_settings(file_password='test_password',
                                    file_path=__file__,
                                    array_id=self.data.remote_array)
        mck_up.assert_called_once_with(
            category=constants.SYSTEM,
            resource_level=constants.SETTINGS,
            resource_type=constants.IMPORT_FILE,
            form_data=ref_form_data)

    @mock.patch.object(common.CommonFunctions, 'upload_file')
    def test_upload_settings_binary_data(self, mck_up):
        """Test upload_settings binary data success."""
        ref_form_data = {
            constants.ZIP_FILE: b'test_binary_data',
            constants.TGT_ARRAYS: self.conn.array_id,
            constants.FILE_PASSWORD: 'test_password'}
        self.system.upload_settings(file_password='test_password',
                                    binary_data=b'test_binary_data')
        mck_up.assert_called_once_with(
            category=constants.SYSTEM,
            resource_level=constants.SETTINGS,
            resource_type=constants.IMPORT_FILE,
            form_data=ref_form_data)

    def test_upload_settings_path_exception(self):
        """Test upload_settings path doesn't exist exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.upload_settings,
            file_password='test', file_path='/fake')

    def test_upload_settings_invalid_data_type(self):
        """Test upload_settings invalid data type"""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.upload_settings,
            file_password='test', binary_data='/fake')

    def test_get_audit_log_list(self):
        """Test get_audit_log_list success."""
        end = int(time.time())
        # Set start time 24hrs + 1 second to trigger LOG warning
        start = end - (60 * 60 * 24) - 1
        response = self.system.get_audit_log_list(
            start_time=start, end_time=end, array_id='test', user_name='test',
            host_name='test', client_host='test', message='test',
            record_id='test', activity_id='test', application_id='test',
            application_version='test', task_id='test', process_id='test',
            vendor_id='test', os_type='test', os_revision='test',
            api_library='test', api_version='test', audit_class='test',
            action_code='test', function_class='test')
        self.assertTrue(response)
        self.assertIsInstance(response, list)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value={'count': 0})
    def test_get_audit_log_list_no_content(self, mck_get):
        """Test upload_settings binary data success."""
        end = int(time.time())
        start = end
        response = self.system.get_audit_log_list(
            start_time=start, end_time=end)
        self.assertFalse(response)
        self.assertIsInstance(response, list)

    def test_get_audit_log_record(self):
        """Test get_audit_log_record."""
        response = self.system.get_audit_log_record(record_id='test')
        self.assertTrue(response)
        self.assertIsInstance(response, dict)

    @mock.patch.object(
        common.CommonFunctions, 'download_file',
        return_value=pf.FakeResponse(200, dict(), content=b'test_binary_data'))
    def test_download_audit_log_record_return_binary(self, mck_dl):
        """Test download_audit_log_record return binary."""
        ref_req_body = {AUDIT_LOG_FILENAME: 'test'}
        response = self.system.download_audit_log_record(
            file_name='test', return_binary=True)
        mck_dl.assert_called_once_with(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=self.system.array_id,
            resource_type=AUDIT_LOG_RECORD, resource=EXPORT_FILE,
            payload=ref_req_body)
        self.assertTrue(response[SUCCESS])
        self.assertIn(BINARY_DATA, response.keys())
        self.assertEqual(b'test_binary_data', response[BINARY_DATA])

    @mock.patch.object(file_handler, 'write_binary_data_to_file',
                       return_value='/test/test.pdf')
    def test_download_audit_log_record_write_file(self, mck_write):
        """Test download_audit_log_record write to file."""
        ref_response = pf.FakeResponse(200, dict(),
                                       content=b'test_binary_data')
        with mock.patch.object(
                common.CommonFunctions, 'download_file',
                return_value=ref_response) as mck_dl:
            ref_req_body = {AUDIT_LOG_FILENAME: 'test'}
            response = self.system.download_audit_log_record(
                file_name='test', dir_path='test')
            mck_dl.assert_called_once_with(
                category=SYSTEM, resource_level=SYMMETRIX,
                resource_level_id=self.system.array_id,
                resource_type=AUDIT_LOG_RECORD, resource=EXPORT_FILE,
                payload=ref_req_body)
            mck_write.assert_called_once_with(
                data=ref_response, file_extension=constants.PDF_SUFFIX,
                file_name='test', dir_path='test')
            self.assertTrue(response[SUCCESS])
            self.assertIn('/test/test.pdf', str(response[AUDIT_RECORD_PATH]))

    @mock.patch.object(file_handler, 'write_binary_data_to_file',
                       return_value='/test/test.pdf')
    def test_download_audit_log_record_write_file_no_name(self, mck_write):
        """Test download_audit_log_record no file name provided."""
        ref_response = pf.FakeResponse(200, dict(),
                                       content=b'test_binary_data')
        with mock.patch.object(
                common.CommonFunctions, 'download_file',
                return_value=ref_response) as mck_dl:
            response = self.system.download_audit_log_record()
            mck_dl.assert_called_once()
            mck_write.assert_called_once()
            self.assertTrue(response[SUCCESS])
            self.assertIn('/test/test.pdf', str(response[AUDIT_RECORD_PATH]))

    def test_get_director_list(self):
        """Test get_director_list."""
        array_id = self.data.array
        dir_list = self.system.get_director_list(array_id=array_id)
        self.assertTrue(dir_list)
        self.assertIsInstance(dir_list, list)
        self.assertEqual([self.data.director_id1, self.data.director_id2],
                         dir_list)

    def test_get_iscsi_director_list(self):
        """Test get_director_list iscsi_only set to True."""
        array_id = self.data.array
        iscsi_dir_list = self.system.get_director_list(
            array_id=array_id, iscsi_only=True)
        self.assertTrue(iscsi_dir_list)
        self.assertIsInstance(iscsi_dir_list, list)
        self.assertEqual([self.data.director_id2], iscsi_dir_list)

    def test_get_director_port_list(self):
        """Test get_director_port_list."""
        director_id = self.data.director_id1
        dir_port_list = self.system.get_director_port_list(
            director_id=director_id, iscsi_target=False)
        self.assertTrue(dir_port_list)
        self.assertIsInstance(dir_port_list, list)
        self.assertEqual(self.data.port_key_list.get('symmetrixPortKey'),
                         dir_port_list)

    def test_get_ip_interface_list(self):
        """Test get_ip_interface_list"""
        director_id = self.data.director_id2
        port_id = 0
        ip_int_list = self.system.get_ip_interface_list(
            director_id=director_id, port_id=port_id)
        self.assertTrue(ip_int_list)
        self.assertIsInstance(ip_int_list, list)
        self.assertEqual(self.data.ip_interface_list.get('ipInterfaceId'),
                         ip_int_list)

    def test_get_ip_interface(self):
        """Test get_ip_interface."""
        director_id = self.data.director_id2
        port_id = 0
        interface_id = self.data.ip_interface_address_network
        ip_int_info = self.system.get_ip_interface(
            director_id=director_id, port_id=port_id,
            interface_id=interface_id)

        self.assertTrue(ip_int_info)
        self.assertIsInstance(ip_int_info, dict)
        self.assertEqual(self.data.ip_interface_details, ip_int_info)
