# Copyright (c) 2021 Dell Inc. or its subsidiaries.
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
"""test_pyu4v_performance.py."""

import socket
import testtools
import time

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V.tests.unit_tests import pyu4v_performance_data as pd
from PyU4V import univmax_conn
from PyU4V.utils import exception
from PyU4V.utils import file_handler
from PyU4V.utils import performance_constants as pc


class PyU4VPerformanceTest(testtools.TestCase):
    """Test Unisphere performance."""

    def setUp(self):
        """setUp."""
        super(PyU4VPerformanceTest, self).setUp()
        self.p_data = pd.PerformanceData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.p_data.array)
            self.perf = self.conn.performance
            self.common = self.conn.common
            self.time_now = int(time.time()) * 1000

    def tearDown(self):
        """tearDown."""
        super(PyU4VPerformanceTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_set_array_id(self):
        """Test set_array_id."""
        array_id = self.p_data.remote_array
        self.perf.set_array_id(array_id)
        self.assertEqual(self.perf.array_id, array_id)

    def test_set_timestamp(self):
        """Test set_timestamp."""
        time_now = int(time.time())
        self.perf.set_timestamp(time_now)
        self.assertEqual(self.perf.timestamp, time_now)

    def test_set_recency(self):
        """Test set_recency."""
        recency = 6
        self.perf.set_recency(recency)
        self.assertEqual(self.perf.recency, recency)

    def test_is_array_performance_registered_enabled(self):
        """Test is_array_performance_registered True."""
        self.assertTrue(self.perf.is_array_performance_registered())

    def test_is_array_performance_registered_disabled(self):
        """Test is_array_performance_registered False."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_is_registered_false):
            self.assertFalse(self.perf.is_array_performance_registered())

    def test_is_array_diagnostic_performance_registered_true(self):
        """Test is_array_diagnostic_performance_registered True."""
        self.assertTrue(self.perf.is_array_diagnostic_performance_registered())

    def testis_array_diagnostic_performance_registered_false(self):
        """Test is_array_diagnostic_performance_registered False."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_is_registered_false):
            self.assertFalse(self.perf.is_array_performance_registered())

    def test_is_array_real_time_performance_registered_true(self):
        """Test is_array_real_time_performance_registered True."""
        self.assertTrue(self.perf.is_array_real_time_performance_registered())

    def test_is_array_real_time_performance_registered_false(self):
        """Test is_array_real_time_performance_registered False."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_reg_details_disabled):
            self.assertFalse(
                self.perf.is_array_real_time_performance_registered())

    def test_is_array_real_time_performance_registered_exception_catch(self):
        with mock.patch.object(
                self.perf, 'get_request',
                side_effect=exception.VolumeBackendAPIException):
            self.assertFalse(
                self.perf.is_array_real_time_performance_registered())

    def test_get_array_registration_details(self):
        """Test get_array_registration_details."""
        response = self.perf.get_array_registration_details()
        self.assertIsNotNone(response)
        self.assertIsInstance(response, dict)

    def test_get_array_registration_details_empty(self):
        """Test get_array_registration_details."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value={'registrationDetailsInfo': list()}):
            response = self.perf.get_array_registration_details()
            self.assertFalse(response)
            self.assertIsInstance(response, dict)

    def test_enable_diagnostic_data_collection_success(self):
        """Test enable_diagnostic_data_collection success scenario."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_is_registered_false):
            with mock.patch.object(
                    self.perf, 'post_request',
                    side_effect=self.perf.post_request) as mck_p:
                self.perf.enable_diagnostic_data_collection()
                mck_p.assert_called_once_with(
                    category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                    resource_type=pc.REGISTER, payload={
                        pc.SYMM_ID: self.perf.array_id,
                        pc.REG_DIAGNOSTIC: True, pc.REAL_TIME: False})

    def test_enable_diagnostic_data_collection_fail_already_enabled(self):
        """Test enable_diagnostic_data_collection fail - already enabled."""
        with mock.patch.object(
                self.perf, 'post_request',
                side_effect=self.perf.post_request) as mck_p:
            self.perf.enable_diagnostic_data_collection()
            mck_p.assert_not_called()

    def test_enable_diagnostic_data_collection_fail_not_applied(self):
        """Test enable_diagnostic_data_collection fail - change not applied."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_is_registered_false):
            with mock.patch.object(
                    self.perf, 'post_request',
                    return_value=self.p_data.array_register_fail) as mck_p:
                self.assertRaises(exception.VolumeBackendAPIException,
                                  self.perf.enable_diagnostic_data_collection)
                mck_p.assert_called_once_with(
                    category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                    resource_type=pc.REGISTER, payload={
                        pc.SYMM_ID: self.perf.array_id,
                        pc.REG_DIAGNOSTIC: True, pc.REAL_TIME: False})

    def test_enable_diagnostic_data_collection_fail_no_msg(self):
        """Test enable_diagnostic_data_collection fail - no response msg."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_is_registered_false):
            with mock.patch.object(
                    self.perf, 'post_request', return_value=dict()) as mck_p:
                self.assertRaises(exception.VolumeBackendAPIException,
                                  self.perf.enable_diagnostic_data_collection)
                mck_p.assert_called_once_with(
                    category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                    resource_type=pc.REGISTER, payload={
                        pc.SYMM_ID: self.perf.array_id,
                        pc.REG_DIAGNOSTIC: True, pc.REAL_TIME: False})

    def test_disable_diagnostic_data_collection_success(self):
        """Test disable_diagnostic_data_collection success."""
        with mock.patch.object(
                self.perf, 'post_request',
                side_effect=self.perf.post_request) as mck_p:
            self.perf.disable_diagnostic_data_collection()
            mck_p.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={
                    pc.SYMM_ID: self.perf.array_id,
                    pc.REG_DIAGNOSTIC: False, pc.REAL_TIME: False})

    def test_disable_diagnostic_data_collection_fail_already_disabled(self):
        """Test disable_diagnostic_data_collection fail - already disabled."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_is_registered_false):
            with mock.patch.object(
                    self.perf, 'post_request',
                    side_effect=self.perf.post_request) as mck_p:
                self.perf.disable_diagnostic_data_collection()
                mck_p.assert_not_called()

    def test_disable_diagnostic_data_collection_fail_not_applied(self):
        """Test disable_diagnostic_data_collection failure - not applied."""
        with mock.patch.object(
                self.perf, 'post_request',
                return_value=self.p_data.array_register_fail) as mck_p:
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.disable_diagnostic_data_collection)
            mck_p.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={
                    pc.SYMM_ID: self.perf.array_id,
                    pc.REG_DIAGNOSTIC: False, pc.REAL_TIME: False})

    def test_disable_diagnostic_data_collection_fail_no_msg(self):
        """Test disable_diagnostic_data_collection failure - no response."""
        with mock.patch.object(
                self.perf, 'post_request', return_value=dict()) as mck_p:
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.disable_diagnostic_data_collection)
            mck_p.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={
                    pc.SYMM_ID: self.perf.array_id,
                    pc.REG_DIAGNOSTIC: False, pc.REAL_TIME: False})

    def test_enable_real_time_data_collection_success(self):
        """Test enable_real_time_data_collection success."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_reg_details_disabled):
            with mock.patch.object(
                    self.perf, 'post_request',
                    side_effect=self.perf.post_request) as mck_p:
                self.perf.enable_real_time_data_collection(
                    storage_group_list='test')
                mck_p.assert_called_once_with(
                    category='performance', resource_level='Array',
                    resource_type='register',
                    payload={'symmetrixId': '000197800123',
                             'diagnostic': True,
                             'realtime': True,
                             'selectedSGs': 'test',
                             'file': False})

    def test_disable_real_time_data_collection_success(self):
        """Test disable_real_time_data_collection success.

        Diagnostic registration is left as True here because fake response
        object returns True by default for array diagnostic perf registration.
        """
        with mock.patch.object(
                self.perf, 'post_request',
                side_effect=self.perf.post_request) as mck_p:
            self.perf.disable_real_time_data_collection()
            mck_p.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={
                    pc.SYMM_ID: self.perf.array_id,
                    pc.REG_DIAGNOSTIC: True, pc.REAL_TIME: False})

    def test_disable_real_time_data_collection_fail_already_disabled(self):
        """Test disable_real_time_data_collection fail - already disabled."""
        with mock.patch.object(
                self.perf, 'get_request',
                return_value=self.p_data.array_reg_details_disabled):
            with mock.patch.object(
                    self.perf, 'post_request',
                    side_effect=self.perf.post_request) as mck_p:
                self.perf.disable_real_time_data_collection()
                mck_p.assert_not_called()

    def test_disable_real_time_data_collection_fail_not_applied(self):
        """Test disable_real_time_data_collection fail - not applied..

        Diagnostic registration is left as True here because fake response
        object returns True by default for array diagnostic perf registration.
        """
        with mock.patch.object(
                self.perf, 'post_request',
                return_value=self.p_data.array_register_fail) as mck_p:
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.disable_real_time_data_collection)
            mck_p.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={
                    pc.SYMM_ID: self.perf.array_id,
                    pc.REG_DIAGNOSTIC: True, pc.REAL_TIME: False})

    def test_disable_real_time_data_collection_fail_no_msg(self):
        """Test disable_real_time_data_collection fail - no response msg."""
        with mock.patch.object(
                self.perf, 'post_request', return_value=dict()) as mck_p:
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.disable_real_time_data_collection)
            mck_p.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={
                    pc.SYMM_ID: self.perf.array_id,
                    pc.REG_DIAGNOSTIC: True, pc.REAL_TIME: False})

    def test_backup_performance_database_success(self):
        """Test backup_performance_database success."""
        filename = '{prefix}-{host}'.format(prefix=pc.FILENAME_PREFIX,
                                            host=socket.gethostname())
        with mock.patch.object(
                self.perf, 'post_request') as mck_bu:
            self.perf.backup_performance_database(last_day_of_diagnostic=True,
                                                  named_real_time_traces=True)
            mck_bu.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.BACKUP, payload={
                    pc.SYMM_ID: self.conn.array_id, pc.FILENAME: filename,
                    pc.NAMED_RT_TRACES: True, pc.LAST_DAY_DIAG: True})

    def test_backup_performance_database_exception(self):
        """Test backup_performance_database exception."""
        with mock.patch.object(
                self.perf, 'post_request',
                side_effect=exception.VolumeBackendAPIException,
                return_value=self.p_data.array_backup_fail):
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.backup_performance_database)

    def test_get_last_available_timestamp(self):
        """Test get_last_available_timestamp."""
        timestamp = self.perf.get_last_available_timestamp(
            array_id=self.p_data.array)
        ref_response = self.p_data.array_keys
        array_info = ref_response[pc.ARRAY_INFO][0]
        self.assertEqual(array_info.get(pc.LA_DATE), timestamp)

    def test_get_last_available_timestamp_exception(self):
        """Test get_last_available_timestamp exception case."""
        with mock.patch.object(self.perf, 'get_request',
                               return_value=self.p_data.array_keys_empty):
            self.assertRaises(exception.ResourceNotFoundException,
                              self.perf.get_last_available_timestamp)

    def test_is_timestamp_current_true(self):
        """Test is_timestamp_current true condition."""
        two_mins_ago = self.time_now - (pc.ONE_MINUTE * 2)
        self.assertTrue(self.perf.is_timestamp_current(timestamp=two_mins_ago))

    def test_is_timestamp_current_false(self):
        """Test is_timestamp_current false condition."""
        ten_mins_ago = self.time_now - (pc.ONE_MINUTE * 10)
        # Set recency to 20 so we know minutes input parm is overriding it
        self.perf.recency = 20
        self.assertFalse(self.perf.is_timestamp_current(timestamp=ten_mins_ago,
                                                        minutes=9))

    def test_get_timestamp_by_hour_start_only(self):
        """Test get_timestamp_by_hour start input only."""
        two_hours_ago = self.time_now - (pc.ONE_HOUR * 2)
        start_time, end_time = self.perf.get_timestamp_by_hour(
            start_time=two_hours_ago, hours_difference=1)
        self.assertEqual((end_time - start_time), pc.ONE_HOUR)

    def test_get_timestamp_by_hour_end_only(self):
        """Test get_timestamp_by_hour end input only."""
        start_time, end_time = self.perf.get_timestamp_by_hour(
            end_time=self.time_now, hours_difference=3)
        self.assertEqual((end_time - start_time), pc.ONE_HOUR * 3)

    def test_get_timestamp_by_hour_no_start_or_end(self):
        """Test get_timestamp_by_hour with hour difference only."""
        start_time, end_time = self.perf.get_timestamp_by_hour(
            hours_difference=5)
        self.assertEqual((end_time - start_time), pc.ONE_HOUR * 5)

    def test_get_rb_key(self):
        """Test _get_rb_key where category matches if statement."""
        # This function is only relevant for V4 arrays where new categories
        # use systemId instead of symmetrixId
        self.perf.is_v4 = True
        response = self.perf._get_rb_key(category='SDNASServer')
        self.assertEqual(pc.SYSTEM_ID, response)

    def test_run_v4_filesystem_request_invalid_input_exception(self):
        """Test _run_v4_filesystem_request with invalid input."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf._run_v4_filesystem_request,
                          category='TEST', request_body={},
                          keys=True, metrics=True)

        self.assertRaises(exception.InvalidInputException,
                          self.perf._run_v4_filesystem_request,
                          category='TEST', request_body={},
                          keys=False, metrics=False)

    def test_run_v4_filesystem_request_filesystem(self):
        """Test _run_v4_filesystem_request for filesystem."""
        rt = 'filesystem'
        with mock.patch.object(
                self.perf, 'post_request') as mck_request:
            self.perf._run_v4_filesystem_request(
                category='FileSystem', request_body={}, keys=True)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.FILE,
                resource_type=rt, object_type=pc.KEYS, payload={})

    def test_run_v4_filesystem_request_interface(self):
        """Test _run_v4_filesystem_request for interface."""
        rt = 'Interface'
        with mock.patch.object(
                self.perf, 'post_request') as mck_request:
            self.perf._run_v4_filesystem_request(
                category='Interface', request_body={}, keys=True)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.FILE,
                resource_type=rt, object_type=pc.KEYS, payload={})

    def test_run_v4_filesystem_request_node(self):
        """Test _run_v4_filesystem_request for node."""
        rt = 'node'
        with mock.patch.object(
                self.perf, 'post_request') as mck_request:
            self.perf._run_v4_filesystem_request(
                category='Node', request_body={}, metrics=True)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.FILE,
                resource_type=rt, object_type=pc.METRICS, payload={})

    def test_run_v4_filesystem_request_server(self):
        """Test _run_v4_filesystem_request for server."""
        rt = 'server'
        with mock.patch.object(
                self.perf, 'post_request') as mck_request:
            self.perf._run_v4_filesystem_request(
                category='Server', request_body={}, metrics=True)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.FILE,
                resource_type=rt, object_type=pc.METRICS, payload={})

    def test_get_performance_key_list_post_with_inputs(self):
        """Test get_performance_key_list post with all inputs set."""
        time_now = int(time.time())
        ref_request_body = {
            'symmetrixId': self.p_data.array,
            'directorId': self.p_data.fe_dir_id,
            'storageGroupId': self.p_data.storage_group_id,
            'storageContainerId': self.p_data.storage_container_id,
            'storageResourceId': self.p_data.storage_resource_id,
            'startDate': time_now, 'endDate': time_now}
        with mock.patch.object(
                self.perf, 'post_request',
                return_value=self.p_data.fe_dir_keys) as mck_request:
            key_response = self.perf.get_performance_key_list(
                category=pc.FE_DIR, array_id=self.p_data.array,
                director_id=self.p_data.fe_dir_id,
                storage_group_id=self.p_data.storage_group_id,
                storage_container_id=self.p_data.storage_container_id,
                storage_resource_id=self.p_data.storage_resource_id,
                start_time=time_now, end_time=time_now)

            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.FE_DIR,
                resource_type=pc.KEYS, payload=ref_request_body)

            self.assertEqual(key_response, self.p_data.fe_dir_keys)

    def test_get_performance_key_list_exceptions(self):
        """Test get_performance_key_list exceptions"""
        # Invalid category
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_performance_key_list, 'FAKECAT')
        # No keys returned
        with mock.patch.object(
                self.perf, 'get_request',
                side_effect=[self.p_data.perf_cats, None]):
            self.assertRaises(exception.ResourceNotFoundException,
                              self.perf.get_performance_key_list, 'Array')

    def test_get_performance_key_list_array_get(self):
        """Test get_performance_key_list get with Array category."""
        with mock.patch.object(
                self.perf, 'get_request',
                side_effect=[
                    self.p_data.perf_cats,
                    self.p_data.array_keys]) as mck_request:
            key_response = self.perf.get_performance_key_list(
                category=pc.ARRAY)
            self.assertEqual(2, mck_request.call_count)
            self.assertEqual(key_response, self.p_data.array_keys)

    def test_get_performance_key_list_exception(self):
        """Test get_performance_key_list with invalid category."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_performance_key_list, 'FAKE_CAT')

    def test_get_performance_key_list_v4_filesystem_call(self):
        """Test get_performance_key_list V4 filesystem call."""
        with mock.patch.object(
                self.perf, '_run_v4_filesystem_request') as mck_request:
            self.perf.get_performance_key_list(
                category='SDNASFileSystem')
            mck_request.assert_called_once_with(
                'SDNASFileSystem', {}, keys=True)

    def test_get_performance_categories_list(self):
        """Test get_performance_categories_list."""
        cat_list = self.perf.get_performance_categories_list()
        self.assertTrue(cat_list)

    def test_validate_category(self):
        """Test _validate_category pass."""
        self.perf.validate_category(pc.ARRAY)

    def test_validate_category_exception(self):
        """Test _validate_category exception."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.validate_category, 'FAKE_CAT')

    def test_get_performance_metrics_list(self):
        """Test get_performance_metrics_list success."""
        array_metrics = self.perf.get_performance_metrics_list(
            pc.ARRAY, kpi_only=False)
        self.assertIsInstance(array_metrics, list)
        self.assertNotEqual(array_metrics, list())

    def test_get_performance_metrics_list_exception(self):
        """Test get_performance_metrics_list invalid category."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_performance_metrics_list, 'FAKE_CAT')

    def test_format_metrics(self):
        """Test format_metrics success."""
        test_metrics = 'single_metric'
        formatted_metrics = self.perf.format_metrics(test_metrics)
        self.assertIsInstance(formatted_metrics, list)

        test_metrics = ['single_metric']
        formatted_metrics = self.perf.format_metrics(test_metrics)
        self.assertIsInstance(formatted_metrics, list)

    def test_format_metrics_exception(self):
        """Test format_metrics exception invalid input type."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.format_metrics, dict())

    def test_extract_timestamp_keys_array_path_start_time(self):
        """Test extract_timestamp_keys for array start time."""
        response, __ = self.perf.extract_timestamp_keys(
            array_id=self.p_data.array, category=pc.ARRAY)
        full_response = self.p_data.array_keys.get(pc.ARRAY_INFO)
        ref_time = full_response[0].get(pc.FA_DATE)
        self.assertEqual(ref_time, response)

    def test_extract_timestamp_keys_array_path_end_time(self):
        """Test extract_timestamp_keys for array end time."""
        __, response = self.perf.extract_timestamp_keys(
            array_id=self.p_data.array, category=pc.ARRAY)
        full_response = self.p_data.array_keys.get(pc.ARRAY_INFO)
        ref_time = full_response[0].get(pc.LA_DATE)
        self.assertEqual(ref_time, response)

    def test_extract_timestamp_keys_key_tgt_path(self):
        """Test extract_timestamp_keys for key target."""
        __, response = self.perf.extract_timestamp_keys(
            array_id=self.p_data.array, category=pc.FE_DIR,
            key_tgt_id=self.p_data.fe_dir_id)

        full_response = self.p_data.fe_dir_keys.get(pc.FE_DIR_INFO)
        ref_time = full_response[0].get(pc.LA_DATE)
        self.assertEqual(ref_time, response)

    def test_extract_timestamp_keys_empty(self):
        """Test extract_timestamp_keys exception."""
        with mock.patch.object(self.perf, 'get_performance_key_list',
                               return_value=self.p_data.array_keys_empty):
            start, end = self.perf.extract_timestamp_keys(
                self.p_data.array, pc.ARRAY)
            self.assertIsNone(start)
            self.assertIsNone(end)

    def test_format_time_input_no_end_time(self):
        """Test format_time_input no end time specified."""
        five_mins_ago = self.time_now - (pc.ONE_MINUTE * 5)
        with mock.patch.object(self.perf, 'get_last_available_timestamp',
                               return_value=self.time_now) as mck_get_time:
            start_time, end_time = self.perf.format_time_input(
                self.p_data.array, start_time=five_mins_ago)
            mck_get_time.assert_called_once_with(self.p_data.array)
            self.assertIsInstance(start_time, str)
            self.assertIsInstance(end_time, str)
            self.assertEqual(start_time, str(five_mins_ago))
            self.assertEqual(end_time, str(self.time_now))

    def test_format_time_input_no_start_time(self):
        """Test format_time_input no start time specified."""
        five_mins_ago = self.time_now - (pc.ONE_MINUTE * 5)
        with mock.patch.object(
                self.perf, 'extract_timestamp_keys',
                return_value=(five_mins_ago, None)) as mck_get_time:
            start_time, end_time = self.perf.format_time_input(
                self.p_data.array, pc.ARRAY, end_time=self.time_now)
            mck_get_time.assert_called_once_with(
                array_id=self.p_data.array, category=pc.ARRAY,
                director_id=None, key_tgt_id=None)
            self.assertIsInstance(start_time, str)
            self.assertIsInstance(end_time, str)
            self.assertEqual(start_time, str(five_mins_ago))
            self.assertEqual(end_time, str(self.time_now))

    def test_format_time_input_no_time(self):
        """Test format_time_input no time specified."""
        with mock.patch.object(
                self.perf, 'extract_timestamp_keys',
                return_value=(self.time_now, self.time_now)) as mck_get_time:
            start_time, end_time = self.perf.format_time_input(
                self.p_data.array, pc.ARRAY)
            mck_get_time.assert_called_once_with(
                array_id=self.p_data.array, category=pc.ARRAY,
                director_id=None, key_tgt_id=None)
            self.assertIsInstance(start_time, str)
            self.assertIsInstance(end_time, str)
            self.assertEqual(start_time, str(self.time_now))
            self.assertEqual(start_time, end_time)

    def test_format_time_get_end_time_exception(self):
        """Test format_time_input get end time exception."""
        with mock.patch.object(self.perf, 'get_last_available_timestamp',
                               return_value=None):
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.format_time_input,
                              array_id=self.p_data.array, category=pc.ARRAY,
                              start_time=self.time_now)

    def test_format_time_get_start_time_exception(self):
        """Test format_time_input get start time exception."""
        with mock.patch.object(self.perf, 'extract_timestamp_keys',
                               return_value=(None, None)):
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.format_time_input,
                              array_id=self.p_data.array, category=pc.ARRAY,
                              end_time=self.time_now)

    def test_format_time_get_no_time_exception(self):
        """Test format_time_input get both start and end time exception."""
        with mock.patch.object(self.perf, 'extract_timestamp_keys',
                               return_value=(None, None)):
            self.assertRaises(exception.VolumeBackendAPIException,
                              self.perf.format_time_input,
                              array_id=self.p_data.array, category=pc.ARRAY)

    def test_format_time_input_exception_wrong_length(self):
        """Test format_time_input exception timestamp invalid."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.format_time_input,
                          self.p_data.array, pc.ARRAY,
                          start_time=123, end_time=123)

    def test_format_time_input_exception_start_after_end(self):
        """Test format_time_input exception start time after end time."""
        end_time = self.time_now - (pc.ONE_MINUTE * 5)
        self.assertRaises(exception.InvalidInputException,
                          self.perf.format_time_input,
                          self.p_data.array, pc.ARRAY,
                          start_time=self.time_now, end_time=end_time)

    def test_get_performance_stats(self):
        """Test get_performance_stats with full run through."""
        ref_payload = {
            'symmetrixId': self.p_data.array, 'dataFormat': pc.AVERAGE,
            'startDate': str(self.time_now), 'endDate': str(self.time_now),
            'metrics': ['PercentBusy']}
        ref_response = {
            'array_id': self.p_data.array, 'start_date': str(self.time_now),
            'end_date': str(self.time_now), 'reporting_level': 'array',
            'result': self.p_data.perf_metrics_resp[
                'resultList']['result'], 'timestamp': str(self.time_now)}
        with mock.patch.object(
                self.perf, 'post_request',
                return_value=self.p_data.perf_metrics_resp) as mck_request:
            response = self.perf.get_performance_stats(
                category=pc.ARRAY, metrics='PercentBusy',
                array_id=self.p_data.array, start_time=self.time_now,
                end_time=self.time_now, recency=True)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.METRICS, payload=ref_payload)
            self.assertTrue(response)
            self.assertEqual(response, ref_response)

    def test_get_performance_stats_request_body_disk_tech(self):
        """Test get_performance_stats with request body variant 1."""
        array_metrics = self.perf.get_performance_metrics_list(
            category=pc.ARRAY)

        ref_payload = {
            'symmetrixId': self.p_data.array, 'dataFormat': pc.AVERAGE,
            'startDate': str(self.time_now), 'endDate': str(self.time_now),
            'metrics': array_metrics,
            'directorId': self.p_data.fe_dir_id,
            'diskTechnology': self.p_data.disk_technology}
        with mock.patch.object(
                self.perf, 'post_request',
                return_value=self.p_data.perf_metrics_resp) as mck_request:
            self.perf.get_performance_stats(
                category=pc.ARRAY, metrics=pc.KPI,
                array_id=self.p_data.array, start_time=self.time_now,
                end_time=self.time_now, recency=True,
                request_body={'directorId': self.p_data.fe_dir_id,
                              'diskTechnology': self.p_data.disk_technology})
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.METRICS, payload=ref_payload)

    def test_get_performance_stats_request_body_other_tgt_id(self):
        """Test get_performance_stats with request body variant 2."""
        array_metrics = self.perf.get_performance_metrics_list(
            category=pc.ARRAY)
        ref_payload = {
            'symmetrixId': self.p_data.array, 'dataFormat': pc.MAXIMUM,
            'startDate': str(self.time_now), 'endDate': str(self.time_now),
            'metrics': array_metrics,
            'directorId': self.p_data.fe_dir_id,
            'portId': self.p_data.fe_port_id}
        with mock.patch.object(
                self.perf, 'post_request',
                return_value=self.p_data.perf_metrics_resp) as mck_request:
            self.perf.get_performance_stats(
                category=pc.ARRAY, metrics=pc.ALL,
                array_id=self.p_data.array, start_time=self.time_now,
                end_time=self.time_now, recency=True, data_format='Maximum',
                request_body={'directorId': self.p_data.fe_dir_id,
                              'portId': self.p_data.fe_port_id})
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.METRICS, payload=ref_payload)

    def test_get_performance_stats_filesystem_call(self):
        """Test get_performance_stats with filesystem call."""
        ref_response = {
            'startDate': str(self.time_now), 'endDate': str(self.time_now),
            'dataFormat': pc.AVERAGE, 'metrics': ['PercentBusy'],
            'systemId': self.p_data.array}

        with mock.patch.object(
                self.perf, '_run_v4_filesystem_request') as mck_request:
            self.perf.get_performance_stats(
                category=pc.SDNAS_FS, metrics='PercentBusy',
                array_id=self.p_data.array, start_time=self.time_now,
                end_time=self.time_now, recency=True)
            mck_request.assert_called_once_with(
                pc.SDNAS_FS, ref_response, metrics=True)

    def test_get_performance_stats_with_recency_exception(self):
        """Test get_performance_stats recency check exception."""
        one_hour_ago = self.time_now - pc.ONE_HOUR
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.perf.get_performance_stats, category=pc.ARRAY,
                          metrics='PercentBusy', array_id=self.p_data.array,
                          start_time=one_hour_ago, end_time=one_hour_ago,
                          recency=True)

    def test_get_performance_stats_invalid_data_format(self):
        """Test get_performance_stats recency check exception."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_performance_stats, category=pc.ARRAY,
                          metrics=['PercentBusy'], array_id=self.p_data.array,
                          start_time=self.time_now, end_time=self.time_now,
                          recency=True, data_format='INVALID_FORMAT')

    def test_get_days_to_full_array(self):
        """Test get_days_to_full array info."""
        response = self.perf.get_days_to_full(array_id=self.p_data.array,
                                              array_to_full=True)
        self.assertEqual(response, self.p_data.days_to_full_resp.get(
            pc.DAYS_TO_FULL_RESULT))

    def test_get_days_to_full_srp(self):
        """Test get_days_to_full srp info."""
        with mock.patch.object(
                self.perf, 'post_request', return_value=dict()) as mck_request:
            response = self.perf.get_days_to_full(
                array_id=self.p_data.array, srp_to_full=True)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.DAYS_TO_FULL,
                payload={'symmetrixId': self.p_data.array,
                         'category': pc.SRP})
            self.assertFalse(response)

    def test_get_days_to_full_thin_pool(self):
        """Test get_days_to_full thin pool info."""
        with mock.patch.object(
                self.perf, 'post_request', return_value=dict()) as mck_request:
            response = self.perf.get_days_to_full(
                array_id=self.p_data.array, thin_pool_to_full=True)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.DAYS_TO_FULL,
                payload={'symmetrixId': self.p_data.array,
                         'category': pc.THIN_POOL})
            self.assertFalse(response)

    def test_get_days_to_full_exception(self):
        """Test get_days_to_full no category set exception."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_days_to_full, self.p_data.array)

    def test_get_threshold_categories(self):
        """Test get_threshold_categories."""
        response = self.perf.get_threshold_categories()
        self.assertIsInstance(response, list)
        self.assertTrue(response)

    def test_get_threshold_category_settings(self):
        """Test get_threshold_category_settings."""
        response = self.perf.get_threshold_category_settings(
            category=pc.ARRAY)
        self.assertIsInstance(response, dict)
        self.assertIsNotNone(response)
        self.assertEqual(response.get(pc.CATEGORY), pc.ARRAY)

    def test_update_threshold_settings(self):
        """Test update_threshold_settings."""
        category, metric, alert = 'Array', 'PercentBusy', True
        first_threshold, second_threshold = 80, 90
        first_threshold_occurrences = 2
        first_threshold_samples = 10
        first_threshold_severity = pc.INFO_LVL
        second_threshold_occurrences = 2
        second_threshold_samples = 20
        second_threshold_severity = pc.WARN_LVL

        ref_payload = {
            pc.METRIC: metric, pc.ALERT: alert,
            pc.FIRST_THRESH: str(first_threshold),
            pc.FIRST_THRESH_OCC: str(first_threshold_occurrences),
            pc.FIRST_THRESH_SAMP: str(first_threshold_samples),
            pc.FIRST_THRESH_SEV: first_threshold_severity,
            pc.SEC_THRESH: str(second_threshold),
            pc.SEC_THRESH_OCC: str(second_threshold_occurrences),
            pc.SEC_THRESH_SAMP: str(second_threshold_samples),
            pc.SEC_THRESH_SEV: second_threshold_severity}

        with mock.patch.object(self.perf, 'put_request') as mck_request:
            self.perf.update_threshold_settings(
                category, metric, first_threshold, second_threshold, alert,
                first_threshold_occurrences, first_threshold_samples,
                first_threshold_severity, second_threshold_occurrences,
                second_threshold_samples, second_threshold_severity)
            mck_request.assert_called_once_with(
                category=pc.PERFORMANCE, resource_level=pc.THRESHOLD,
                resource_type=pc.UPDATE, resource_type_id=category,
                payload=ref_payload)

    def test_set_thresholds_from_csv(self):
        """Test set_perfthresholds_csv."""
        threshold_settings = self.p_data.threshold_settings_resp.get(
            pc.PERF_THRESH)

        mock_csv_data = {pc.CATEGORY: list(), pc.METRIC: list(),
                         pc.KPI: list(), pc.ALERT_ERR: list(),
                         pc.FIRST_THRESH: list(), pc.SEC_THRESH: list()}
        for threshold_setting in threshold_settings:
            mock_csv_data[pc.CATEGORY].append(
                self.p_data.threshold_settings_resp.get(pc.CATEGORY))
            mock_csv_data[pc.METRIC].append(threshold_setting.get(pc.METRIC))
            mock_csv_data[pc.KPI].append(threshold_setting.get(pc.KPI))
            mock_csv_data[pc.ALERT_ERR].append(
                threshold_setting.get(pc.ALERT_ERR))
            mock_csv_data[pc.FIRST_THRESH].append(
                threshold_setting.get(pc.FIRST_THRESH))
            mock_csv_data[pc.SEC_THRESH].append(
                threshold_setting.get(pc.SEC_THRESH))

        with mock.patch.object(file_handler, 'read_csv_values',
                               return_value=mock_csv_data):
            with mock.patch.object(
                    self.perf, 'update_threshold_settings') as mck_update:

                self.perf.set_thresholds_from_csv('fake_csv_path')
                self.assertEqual(mck_update.call_count, 1)

    def test_set_thresholds_from_csv_invalid_threshold_values(self):
        """Test set_perfthresholds_csv."""
        threshold_settings = self.p_data.threshold_settings_resp.get(
            pc.PERF_THRESH)

        mock_csv_data = {pc.CATEGORY: list(), pc.METRIC: list(),
                         pc.KPI: list(), pc.ALERT_ERR: list(),
                         pc.FIRST_THRESH: list(), pc.SEC_THRESH: list()}

        for threshold_setting in threshold_settings:
            mock_csv_data[pc.CATEGORY].append(
                self.p_data.threshold_settings_resp.get(pc.CATEGORY))
            mock_csv_data[pc.METRIC].append(threshold_setting.get(pc.METRIC))
            mock_csv_data[pc.KPI].append(threshold_setting.get(pc.KPI))
            mock_csv_data[pc.ALERT_ERR].append(
                threshold_setting.get(pc.ALERT_ERR))
            mock_csv_data[pc.FIRST_THRESH].append(10)
            mock_csv_data[pc.SEC_THRESH].append(10)

        with mock.patch.object(file_handler, 'read_csv_values',
                               return_value=mock_csv_data):
            with mock.patch.object(
                    self.perf, 'update_threshold_settings') as mck_update:
                self.perf.set_thresholds_from_csv('fake_csv_path')
                self.assertEqual(mck_update.call_count, 0)

    def test_generate_threshold_settings_csv(self):
        """Test generate_threshold_settings_csv."""
        data_for_csv = list()
        data_for_csv.append([pc.CATEGORY, pc.METRIC, pc.FIRST_THRESH,
                             pc.SEC_THRESH, pc.ALERT_ERR, pc.KPI])
        threshold_settings = self.p_data.threshold_settings_resp.get(
            pc.PERF_THRESH)
        for threshold in threshold_settings:
            category = pc.ARRAY
            data_for_csv.append([
                category, threshold.get(pc.METRIC),
                threshold.get(pc.FIRST_THRESH), threshold.get(pc.SEC_THRESH),
                threshold.get(pc.ALERT_ERR), threshold.get(pc.KPI)])
        with mock.patch.object(file_handler, 'write_to_csv_file') as mck_write:
            self.perf.generate_threshold_settings_csv(
                output_csv_path='fake_csv')
            mck_write.assert_called_once_with('fake_csv', data_for_csv)

    def test_get_array_keys(self):
        """Test get_array_keys."""
        response = self.perf.get_array_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.SYMM_ID))

    def test_get_array_stats(self):
        """Test get_array_stats."""
        response = self.perf.get_array_stats(
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.ARRAY))

    def test_get_backend_director_keys(self):
        """Test get_backend_director_keys."""
        response = self.perf.get_backend_director_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DIR_ID))

    def test_get_backend_director_stats(self):
        """Test get_backend_director_stats."""
        response = self.perf.get_backend_director_stats(
            director_id=self.p_data.fe_port_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.BE_DIR))

    def test_get_backend_emulation_keys(self):
        """Test get_backend_emulation_keys."""
        response = self.perf.get_backend_emulation_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.BE_EMU_ID))

    def test_get_backend_emulation_stats(self):
        """Test get_backend_emulation_stats."""
        response = self.perf.get_backend_emulation_stats(
            emulation_id=self.p_data.be_emu_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.BE_EMU))

    def test_get_backend_port_keys(self):
        """Test get_backend_port_keys."""
        response = self.perf.get_backend_port_keys(
            director_id=self.p_data.fe_port_id)
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.PORT_ID))

    def test_get_backend_port_stats(self):
        """Test get_backend_port_stats."""
        response = self.perf.get_backend_port_stats(
            director_id=self.p_data.be_dir_id,
            port_id=self.p_data.be_port_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.BE_PORT))

    def test_get_board_keys(self):
        """Test get_board_keys."""
        response = self.perf.get_board_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.BOARD_ID))

    def test_get_board_stats(self):
        """Test get_board_stats."""
        response = self.perf.get_board_stats(
            board_id=self.p_data.board_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.BOARD))

    def test_get_cache_partition_keys(self):
        """Test get_cache_partition_keys."""
        response = self.perf.get_cache_partition_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.CACHE_PART_ID))

    def test_get_cache_partition_perf_stats(self):
        """Test get_cache_partition_perf_stats."""
        response = self.perf.get_cache_partition_perf_stats(
            cache_partition_id=self.p_data.cache_part_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.CACHE_PART))

    def test_get_cloud_provider_keys(self):
        """Test get_cloud_provider_keys."""
        response = self.perf.get_cloud_provider_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.CLOUD_PROVIDER_ID))

    def test_get_cloud_provider_stats(self):
        """Test get_cloud_provider_stats."""
        response = self.perf.get_cloud_provider_stats(
            cloud_provider_id=self.p_data.cloud_provider_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.CLOUD_PROVIDER))

    def test_get_device_group_keys(self):
        """Test get_device_group_keys."""
        response = self.perf.get_device_group_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DEV_GRP_ID))

    def test_get_device_group_stats(self):
        """Test get_device_group_stats."""
        response = self.perf.get_device_group_stats(
            device_group_id=self.p_data.device_group_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.DEV_GRP))

    def test_get_disk_group_keys(self):
        """Test get_disk_group_keys."""
        response = self.perf.get_disk_group_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DISK_GRP_ID))

    def test_get_disk_group_stats(self):
        """Test get_disk_group_stats."""
        response = self.perf.get_disk_group_stats(
            disk_group_id=self.p_data.disk_group_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.DISK_GRP))

    def test_get_eds_director_keys(self):
        """Test get_eds_director_keys."""
        response = self.perf.get_eds_director_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DIR_ID))

    def test_get_eds_director_stats(self):
        """Test get_eds_director_stats."""
        response = self.perf.get_eds_director_stats(
            director_id=self.p_data.eds_dir_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.EDS_DIR))

    def test_get_eds_emulation_keys(self):
        """Test get_eds_emulation_keys."""
        response = self.perf.get_eds_emulation_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.EDS_EMU_ID))

    def test_get_eds_emulation_stats(self):
        """Test get_eds_emulation_stats."""
        response = self.perf.get_eds_emulation_stats(
            emulation_id=self.p_data.eds_emu_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.EDS_EMU))

    def test_get_em_director_keys(self):
        """Test get_eds_director_keys."""
        response = self.perf.get_em_director_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DIR_ID))

    def test_get_em_director_stats(self):
        """Test get_eds_director_stats."""
        response = self.perf.get_em_director_stats(
            director_id=self.p_data.em_dir_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.EM_DIR))

    def test_get_external_disk_keys(self):
        """Test get_external_disk_keys."""
        response = self.perf.get_external_disk_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DISK_ID))

    def test_get_external_disk_stats(self):
        """Test get_external_disk_stats."""
        response = self.perf.get_external_disk_stats(
            disk_id=self.p_data.ext_disk_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.EXT_DISK))

    def test_get_frontend_director_keys(self):
        """Test get_frontend_director_keys."""
        response = self.perf.get_frontend_director_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DIR_ID))

    def test_get_frontend_director_stats(self):
        """Test get_frontend_director_stats."""
        response = self.perf.get_frontend_director_stats(
            director_id=self.p_data.fe_dir_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.FE_DIR))

    def test_get_frontend_emulation_keys(self):
        """Test get_frontend_emulation_keys."""
        response = self.perf.get_frontend_emulation_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.FE_EMU_ID))

    def test_get_frontend_emulation_stats(self):
        """Test get_frontend_emulation_stats."""
        response = self.perf.get_frontend_emulation_stats(
            emulation_id=self.p_data.fe_emu_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.FE_EMU))

    def test_get_frontend_port_keys(self):
        """Test get_frontend_port_keys."""
        response = self.perf.get_frontend_port_keys(
            director_id=self.p_data.fe_dir_id)
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.PORT_ID))

    def test_get_frontend_port_stats(self):
        """Test get_frontend_port_stats."""
        response = self.perf.get_frontend_port_stats(
            director_id=self.p_data.fe_dir_id,
            port_id=self.p_data.fe_port_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.FE_PORT))

    def test_get_ficon_emulation_keys(self):
        """Test get_ficon_emulation_keys."""
        response = self.perf.get_ficon_emulation_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.FICON_EMU_ID))

    def test_get_ficon_emulation_stats(self):
        """Test get_ficon_emulation_stats."""
        response = self.perf.get_ficon_emulation_stats(
            ficon_emulation_id=self.p_data.ficon_emu_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.FICON_EMU))

    def test_get_ficon_port_thread_keys(self):
        """Test get_ficon_port_thread_keys."""
        response = self.perf.get_ficon_port_thread_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.FICON_PORT_THR_ID))

    def test_get_ficon_port_thread_stats(self):
        """Test get_ficon_port_thread_stats."""
        response = self.perf.get_ficon_port_thread_stats(
            ficon_port_thread_id=self.p_data.ficon_port_thread_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.FICON_PORT_THR))

    def test_get_ficon_emulation_thread_keys(self):
        """Test get_ficon_emulation_thread_keys."""
        response = self.perf.get_ficon_emulation_thread_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.FICON_EMU_THR_ID))

    def test_get_ficon_emulation_thread_stats(self):
        """Test get_ficon_emulation_thread_stats."""
        response = self.perf.get_ficon_emulation_thread_stats(
            ficon_emulation_thread_id=self.p_data.ficon_emu_thread_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.FICON_EMU_THR))

    def test_get_host_keys(self):
        """Test get_host_keys."""
        response = self.perf.get_host_keys(
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.HOST_ID))

    def test_get_host_stats(self):
        """Test get_ficon_port_thread_stats."""
        response = self.perf.get_host_stats(
            host_id=self.p_data.host_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.HOST))

    def test_get_im_director_keys(self):
        """Test get_im_director_keys."""
        response = self.perf.get_im_director_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DIR_ID))

    def test_get_im_director_stats(self):
        """Test get_im_director_stats."""
        response = self.perf.get_im_director_stats(
            director_id=self.p_data.im_dir_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.IM_DIR))

    def test_get_im_emulation_keys(self):
        """Test get_im_emulation_keys."""
        response = self.perf.get_im_emulation_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.IM_EMU_ID))

    def test_get_im_emulation_stats(self):
        """Test get_im_emulation_stats."""
        response = self.perf.get_im_emulation_stats(
            emulation_id=self.p_data.im_emu_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.IM_EMU))

    def test_get_initiator_perf_keys(self):
        """Test get_initiator_perf_keys."""
        response = self.perf.get_initiator_perf_keys(
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.INIT_ID))

    def test_get_initiator_stats(self):
        """Test get_initiator_stats."""
        response = self.perf.get_initiator_stats(
            initiator_id=self.p_data.init_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.INIT))

    def test_get_ip_interface_keys(self):
        """Test get_ip_interface_keys."""
        response = self.perf.get_ip_interface_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.IP_INT_ID))

    def test_get_ip_interface_stats(self):
        """Test get_ip_interface_stats."""
        response = self.perf.get_ip_interface_stats(
            ip_interface_id=self.p_data.ip_interface_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.IP_INT))

    def test_get_iscsi_target_keys(self):
        """Test get_iscsi_target_keys."""
        response = self.perf.get_iscsi_target_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.ENDPOINT_ID_METRICS))

    def test_get_iscsi_target_stats(self):
        """Test get_iscsi_target_stats."""
        response = self.perf.get_iscsi_target_stats(
            iscsi_target_id=self.p_data.iscsi_target_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.ENDPOINT))

    def test_get_masking_view_keys(self):
        """Test get_masking_view_keys."""
        response = self.perf.get_masking_view_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.MV_ID))

    def test_get_masking_view_stats(self):
        """Test get_masking_view_stats."""
        response = self.perf.get_masking_view_stats(
            masking_view_id=self.p_data.masking_view_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.MV))

    def test_get_port_group_keys(self):
        """Test get_port_group_keys."""
        response = self.perf.get_port_group_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.PG_ID))

    def test_get_port_group_stats(self):
        """Test get_port_group_stats."""
        response = self.perf.get_port_group_stats(
            port_group_id=self.p_data.port_group_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.PG))

    def test_get_rdfa_keys(self):
        """Test get_rdfa_keys."""
        response = self.perf.get_rdfa_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.RA_GRP_ID))

    def test_get_rdfa_stats(self):
        """Test get_rdfa_stats."""
        response = self.perf.get_rdfa_stats(
            rdfa_group_id=self.p_data.rdfa_group_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.RDFA))

    def test_get_rdfs_keys(self):
        """Test get_rdfs_keys."""
        response = self.perf.get_rdfs_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.RA_GRP_ID))

    def test_get_rdfs_stats(self):
        """Test get_rdfs_stats."""
        response = self.perf.get_rdfs_stats(
            rdfs_group_id=self.p_data.rdfs_group_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.RDFS))

    def test_get_rdf_director_keys(self):
        """Test get_rdf_director_keys."""
        response = self.perf.get_rdf_director_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.DIR_ID))

    def test_get_rdf_director_stats(self):
        """Test get_rdf_director_stats."""
        response = self.perf.get_rdf_director_stats(
            director_id=self.p_data.rdf_dir_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.RDF_DIR))

    def test_get_rdf_emulation_keys(self):
        """Test get_rdf_emulation_keys."""
        response = self.perf.get_rdf_emulation_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.RDF_EMU_ID))

    def test_get_rdf_emulation_stats(self):
        """Test get_rdf_emulation_stats."""
        response = self.perf.get_rdf_emulation_stats(
            emulation_id=self.p_data.rdf_emu_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.RDF_EMU))

    def test_get_rdf_port_keys(self):
        """Test get_rdf_port_keys."""
        response = self.perf.get_rdf_port_keys(
            director_id=self.p_data.rdf_dir_id)
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.PORT_ID))

    def test_get_rdf_port_stats(self):
        """Test get_rdf_port_stats."""
        response = self.perf.get_rdf_port_stats(
            director_id=self.p_data.rdf_dir_id,
            port_id=self.p_data.rdf_port_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.RDF_PORT))

    def test_get_sdnas_filesystem_keys(self):
        """Test get_sdnas_filesystem_keys."""
        response = self.perf.get_sdnas_filesystem_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.SDNAS_FS_ID))

    def test_get_sdnas_filesystem_stats(self):
        """Test get_sdnas_filesystem_stats."""
        response = self.perf.get_sdnas_filesystem_stats(
            sdnas_filesystem_id=self.p_data.sdnas_filesystem_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.SDNAS_FS))

    def test_get_sdnas_interface_keys(self):
        """Test get_sdnas_interface_keys."""
        response = self.perf.get_sdnas_interface_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.SDNAS_INTERFACE_ID))

    def test_get_sdnas_interface_stats(self):
        """Test get_sdnas_interface_stats."""
        response = self.perf.get_sdnas_interface_stats(
            sdnas_interface_id=self.p_data.sdnas_interface_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.SDNAS_INTERFACE))

    def test_get_sdnas_node_keys(self):
        """Test get_sdnas_node_keys."""
        response = self.perf.get_sdnas_node_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.SDNAS_NODE_ID))

    def test_get_sdnas_node_stats(self):
        """Test get_sdnas_node_stats."""
        response = self.perf.get_sdnas_node_stats(
            sdnas_node_id=self.p_data.sdnas_node_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.SDNAS_NODE))

    def test_get_sdnas_server_keys(self):
        """Test get_sdnas_server_keys."""
        response = self.perf.get_sdnas_server_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.SDNAS_SERVER_ID))

    def test_get_sdnas_server_stats(self):
        """Test get_sdnas_server_stats."""
        response = self.perf.get_sdnas_server_stats(
            sdnas_server_id=self.p_data.sdnas_server_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.SDNAS_SERVER))

    def test_get_storage_container_keys(self):
        """Test get_storage_container_keys."""
        response = self.perf.get_storage_container_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.STORAGE_CONT_ID))

    def test_get_storage_container_stats(self):
        """Test get_storage_container_stats."""
        response = self.perf.get_storage_container_stats(
            storage_container_id=self.p_data.storage_container_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.STORAGE_CONT))

    def test_get_storage_group_keys(self):
        """Test get_storage_group_keys."""
        response = self.perf.get_storage_group_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.SG_ID))

    def test_get_storage_group_stats(self):
        """Test get_storage_group_stats."""
        response = self.perf.get_storage_group_stats(
            storage_group_id=self.p_data.storage_group_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.SG))

    def test_get_storage_resource_pool_keys(self):
        """Test get_storage_resource_pool_keys."""
        response = self.perf.get_storage_resource_pool_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.SRP_ID))

    def test_get_storage_resource_pool_stats(self):
        """Test get_storage_group_by_pool_stats."""
        response = self.perf.get_storage_resource_pool_stats(
            srp_id=self.p_data.srp_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.SRP))

    def test_get_storage_resource_keys(self):
        """Test get_storage_resource_keys."""
        response = self.perf.get_storage_resource_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.STORAGE_RES_ID))

    def test_get_storage_resource_stats(self):
        """Test get_storage_resource_stats."""
        response = self.perf.get_storage_resource_stats(
            storage_resource_id=self.p_data.storage_resource_id,
            storage_container_id=self.p_data.storage_resource_id,
            metrics=pc.KPI, start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.STORAGE_RES))

    def test_get_thin_pool_keys(self):
        """Test get_thin_pool_keys."""
        response = self.perf.get_thin_pool_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.POOL_ID))

    def test_get_thin_pool_stats(self):
        """Test get_thin_pool_stats."""
        response = self.perf.get_thin_pool_stats(
            thin_pool_id=self.p_data.thin_pool_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('reporting_level'),
                         self.common.convert_to_snake_case(pc.THIN_POOL))

    def test_get_volume_stats(self):
        """Test get_thin_pool_stats."""
        response = self.perf.get_volume_stats(
            volume_range_start='00123', volume_range_end='00123',
            start_time=self.time_now, end_time=self.time_now,
            data_format='Average')
        self.assertIsInstance(response, dict)

    def test_get_zhyperlink_port_keys(self):
        """Test get_zhyperlink_port_keys."""
        response = self.perf.get_zhyperlink_port_keys()
        self.assertIsInstance(response, list)
        self.assertTrue(response[0].get(pc.PORT_ID))

    def test_get_zhyperlink_port_stats(self):
        """Test get_zhyperlink_port_stats."""
        response = self.perf.get_zhyperlink_port_stats(
            zhyperlink_port_id=self.p_data.zhyperlink_port_id, metrics=pc.KPI,
            start_time=self.time_now, end_time=self.time_now)
        self.assertIsInstance(response, dict)
        self.assertEqual(
            response.get('reporting_level'),
            self.common.convert_to_snake_case(pc.ZHYPER_LINK_PORT))
