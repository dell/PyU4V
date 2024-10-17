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
LOCAL_USER = constants.LOCAL_USER
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
DIRECTOR = constants.DIRECTOR
PORT = constants.PORT


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
            payload=ref_req_body, timeout=None)
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
                payload=ref_req_body, timeout=None)
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

    def test_get_director_from_port_list(self):
        """Test get_director_port_list."""
        director_id = self.data.director_id1
        dir_port_list = self.system.get_director_port_list(
            director_id=director_id, filters={'iscsi_endpoint': 'false'})
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

    @mock.patch.object(common.CommonFunctions, 'modify_resource')
    def test_change_local_user_password(self, mck_modify):
        """Test change_local_user_password."""

        self.system.change_local_user_password(
            username='testchange', current_password='oldpass',
            new_password='newpassword')
        payload = {
            'username': 'testchange',
            'action': "SetPassword",
            'set_password': {
                'current_password': 'oldpass',
                'new_password': 'newpassword'
            }
        }
        mck_modify.assert_called_once_with(
            category=SYSTEM, resource_level=LOCAL_USER, payload=payload)

    def test_get_director_port_list(self):
        """Test get_director_port_list."""
        port_key_list = self.system.get_director_port_list(
            self.data.director_id1)
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_directory_port_iscsi_endpoint_list(self):
        """Test get_directory_port_iscsi_endpoint_list."""
        port_key_list = self.system.get_directory_port_iscsi_endpoint_list(
            self.data.director_id1, True)
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_directory_port_iscsi_endpoint_list_invalid_input(self):
        """Test get_directory_port_iscsi_endpoint_list."""
        self.assertRaises(
            exception.InvalidInputException,
            self.system.get_directory_port_iscsi_endpoint_list,
            self.data.director_id1, None)

    def test_get_port_identifier(self):
        """Test get_port_identifier."""
        wwn = self.system.get_port_identifier(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.wwnn1, wwn)

    def test_get_port_identifier_key_exception(self):
        """Test get_port_identifier with key exception."""
        with mock.patch.object(self.system,
                               'get_director_port',
                               return_value={'test': 'data'}):
            wwn = self.system.get_port_identifier(
                self.data.director_id1, self.data.port_id1)
            self.assertEqual(None, wwn)

    def test_get_director_port(self):
        """Test get_director_port."""
        port_details = self.system.get_director_port(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.port_list[0], port_details)

    def test_get_fa_directors(self):
        """Test get_fa_directors."""
        fa_director = self.data.director_id1
        se_director = self.data.director_id2
        directors = [fa_director, se_director]
        with mock.patch.object(self.system, 'get_director_list',
                               return_value=directors) as mck_get_dir:
            fa_directors = self.system.get_fa_directors()
            self.assertEqual([fa_director], fa_directors)
            mck_get_dir.assert_called_once()

    def test_get_or_directors(self):
        """Test get_or_directors."""
        or_director = self.data.or_director_id
        ef_director = self.data.ef_director_id
        em_director = self.data.em_director_id
        directors = [or_director, ef_director, em_director]
        with mock.patch.object(self.system, 'get_director_list',
                               return_value=directors) as mck_get_dir:
            or_directors = self.system.get_or_directors()
            self.assertEqual([or_director], or_directors)
            mck_get_dir.assert_called_once()

    def test_get_target_wwns_from_port_group(self):
        """Test get_target_wwns_from_port_group."""
        with mock.patch.object(
                self.system, 'get_port_group', return_value={
                    'symmetrixPortKey': [{
                        'directorId': self.data.director_id1,
                        'portId': self.data.port_id1}]}) as mck_get_grp:
            target_wwns = self.system.get_target_wwns_from_port_group(
                self.data.port_group_name_f)
            self.assertEqual([self.data.wwnn1], target_wwns)
            mck_get_grp.assert_called_once_with(self.data.port_group_name_f)

    def test_get_director(self):
        """Test get_director."""
        dir_details = self.system.get_director(self.data.director_id1)
        self.assertEqual(self.data.director_info, dir_details)

    def test_get_iscsi_ip_address_and_iqn(self):
        """Test get_iscsi_ip_address_and_iqn."""
        ip_addresses, iqn = self.system.get_iscsi_ip_address_and_iqn(
            'SE-4E:0')
        self.assertEqual([self.data.ip], ip_addresses)
        self.assertEqual(self.data.initiator, iqn)

    def test_get_any_director_port(self):
        """Test get_any_director_port."""
        return_val = [{constants.PORT_ID: self.data.port_id1}]
        with mock.patch.object(
                self.system, 'get_director_port_list',
                return_value=return_val) as mck_get_dir_port:
            port = self.system.get_any_director_port(
                self.data.director_id1)
            self.assertEqual(port, self.data.port_id1)
            mck_get_dir_port.assert_called_once_with(
                self.data.director_id1, filters=None)

    def test_get_fc_director_port_list_v4(self):
        """Test get_port_identifier with key exception."""
        with mock.patch.object(self.system,
                               'get_director_port_list',
                               return_value=self.data.v4_port_list):
            fc_director_port_list = self.system.get_fc_director_port_list_v4(
                [self.data.or_director_id])
            self.assertEqual(self.data.v4_port_list, fc_director_port_list)

    @mock.patch.object(common.CommonFunctions, 'modify_resource')
    def test_set_director_port_online(self, mck_modify):
        """Test set_director_port_online."""
        self.system.set_director_port_online(
            director=self.data.or_director_id, port_no=self.data.port_id1,
            port_online=False)
        payload = {
            'editPortActionParamType': {
                'onlineOfflineParamType': {
                    'port_online': False
                }
            }
        }
        mck_modify.assert_called_once_with(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=self.data.array,
            resource_type=DIRECTOR, resource_type_id=self.data.or_director_id,
            resource=PORT, resource_id=self.data.port_id1, payload=payload)

    def test_get_management_server_resources(self):
        with mock.patch.object(self.system,
                               'get_management_server_resources',
                               return_value=self.data.management_server_data):
            resource_usage = self.system.get_management_server_resources()
        self.assertIsInstance(resource_usage, dict)
        self.assertEqual(self.data.management_server_data, resource_usage)

    def test_refresh_array_details(self):
        with mock.patch.object(self.system,
                               'refresh_array_details',
                               return_value=None):
            refresh = self.system.refresh_array_details()
        self.assertEqual(refresh, None)

    def test_get_server_logging_level(self):
        with mock.patch.object(
                self.system, 'get_server_logging_level',
                return_value=self.data.server_log_level):
            log_level = self.system.get_server_logging_level()
        self.assertEqual(self.data.server_log_level, log_level)

    def test_set_server_logging_level(self):
        with mock.patch.object(
                self.system, 'set_server_logging_level',
                return_value=self.data.server_log_level):
            log_level = self.system.set_server_logging_level(
                server_log_level='Info', restapi_logging_enabled=True)
        self.assertEqual(self.data.server_log_level, log_level)

    def test_get_snmp_trap_configuration(self):
        with mock.patch.object(
                self.system, 'get_snmp_trap_configuration',
                return_value=self.data.snmp):
            snmp_config = self.system.get_snmp_trap_configuration()
        self.assertIn('engine_id', snmp_config)
        self.assertIn('snmp_traps', snmp_config)

    def test_set_snmp_trap_destination(self):
        with mock.patch.object(
                self.system, 'set_snmp_trap_destination',
                return_value=self.data.snmp):
            new_config = self.system.set_snmp_trap_destination(
                name='10.60.1.1', port=162)
        self.assertEquals('10.60.1.1', new_config['snmp_traps'][0]['name'])

    def test_delete_snmp_trap_destination(self):
        with mock.patch.object(
                self.system, 'delete_snmp_trap_destination') as mock_delete:
            self.system.delete_snmp_trap_destination(
                snmp_id="56910fe4-9c69-3100-a493-ff9455acc02d")
            mock_delete.assert_called_once()

    def test_update_snmp_trap_destination(self):
        with mock.patch.object(
                self.system, 'update_snmp_trap_destination') as mock_update:
            self.system.update_snmp_trap_destination(
                snmp_id="56910fe4-9c69-3100-a493-ff9455acc02d", port=431)
            mock_update.assert_called_once()

    def test_get_ldap_configuration(self):
        with mock.patch.object(
                self.system, 'get_ldap_configuration') as mock_get:
            self.system.get_ldap_configuration()
            mock_get.assert_called_once()

    def test_configure_ldap_authentication(self):
        with (mock.patch.object(
                self.system, 'configure_ldap_authentication') as
        mock_configure):
            self.system.configure_ldap_authentication(enabled=True)
            mock_configure.assert_called_once()
