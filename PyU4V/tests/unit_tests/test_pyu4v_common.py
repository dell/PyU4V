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
"""test_pyu4v_common.py."""

import csv
import mock
import testtools

from PyU4V import common
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants
from PyU4V.utils import exception

# Resource constants
SLOPROVISIONING = constants.SLOPROVISIONING
SYMMETRIX = constants.SYMMETRIX
VOLUME = constants.VOLUME
UNISPHERE_VERSION = constants.UNISPHERE_VERSION


class PyU4VCommonTest(testtools.TestCase):
    """Test common."""

    def setUp(self):
        """setUp."""
        super(PyU4VCommonTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn()
            self.common = self.conn.common
            self.common.interval = 1
            self.common.retries = 1

    def tearDown(self):
        """tearDown."""
        super(PyU4VCommonTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_wait_for_job_complete(self):
        """Test wait_for_job_complete."""
        _, _, status, _ = self.common.wait_for_job_complete(
            self.data.job_list[0])
        self.assertEqual('SUCCEEDED', status)

    @mock.patch.object(common.CommonFunctions, '_is_job_finished',
                       return_value=(True, '', 0, 'SUCCEEDED', ''))
    def test_wait_for_job_complete_running(self, mock_job):
        """Test wait_for_job_complete running."""
        _, _, status, _ = self.common.wait_for_job_complete(
            self.data.job_list[1])
        self.assertEqual('SUCCEEDED', status)

    @mock.patch.object(common.CommonFunctions, '_is_job_finished',
                       side_effect=[exception.VolumeBackendAPIException(
                           'random exception')])
    def test_wait_for_job_complete_exception(self, mock_job):
        """Test wait_for_job_complete exception."""
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.common.wait_for_job_complete,
                          self.data.job_list[1])

    @mock.patch.object(common.CommonFunctions, '_is_job_finished',
                       return_value=(False, '', 0, 'RUNNING', ''))
    def test_wait_for_job_complete_timeout(self, mock_job):
        """Test wait_for_job_complete timeout."""
        self.common.retries = 0
        rc, result, status, _ = self.common.wait_for_job_complete(
            self.data.job_list[1])
        self.assertEqual('RUNNING', status)
        self.assertEqual(-1, rc)
        self.assertIsNone(result)

    def test_get_job_by_id(self):
        """Test get_job_by_id."""
        job = self.common.get_job_by_id(self.data.job_list[0]['jobId'])
        self.assertEqual('SUCCEEDED', job['status'])
        self.assertEqual('12345', job['jobId'])

    @mock.patch.object(common.CommonFunctions, 'get_job_by_id',
                       return_value=pcd.CommonData.job_list[0])
    def test_is_job_finished_success(self, mock_job):
        job = self.common._is_job_finished(
            self.data.job_list[0]['jobId'])
        self.assertEqual((True, None, 0, 'SUCCEEDED', None), job)

    @mock.patch.object(common.CommonFunctions, 'get_job_by_id',
                       return_value=pcd.CommonData.job_list[2])
    def test_is_job_finished_failure(self, mock_job):
        job = self.common._is_job_finished(
            self.data.job_list[2]['jobId'])
        self.assertEqual((True, None, -1, 'FAILED', None), job)

    @mock.patch.object(common.CommonFunctions, 'get_job_by_id',
                       return_value=pcd.CommonData.job_list[1])
    def test_is_job_finished_incomplete(self, mock_job):
        job = self.common._is_job_finished(
            self.data.job_list[1]['jobId'])
        self.assertEqual((False, None, 0, 'RUNNING', None), job)

    def test_check_status_code_success(self):
        """Test check_status_code_success."""
        self.common.check_status_code_success(
            'test-success', 201, '')
        self.assertRaises(exception.ResourceNotFoundException,
                          self.common.check_status_code_success,
                          'test-404', 404, '')
        self.assertRaises(exception.UnauthorizedRequestException,
                          self.common.check_status_code_success,
                          'test-401', 401, '')
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.common.check_status_code_success,
                          'test-500', 500, '')

    @mock.patch.object(common.CommonFunctions, 'wait_for_job_complete',
                       side_effect=[(0, '', '', ''), (1, '', '', '')])
    def test_wait_for_job(self, mock_complete):
        """Test wait_for_job."""
        # Not an async job
        self.common.wait_for_job('sync-job', 200, {})
        mock_complete.assert_not_called()
        # Async, completes successfully
        self.common.wait_for_job('sync-job', 202, {})
        mock_complete.assert_called_once()
        # Async, job fails
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.common.wait_for_job, 'sync-job', 202, {})

    def test_build_uri_version_control(self):
        """Test _build_uri."""
        # No version supplied, use self.U4V_VERSION
        built_uri_1 = self.common._build_uri(
            category=SLOPROVISIONING, resource_level=SYMMETRIX,
            resource_level_id=self.data.array, resource_type=VOLUME)
        uri_1 = ('/{ver}/sloprovisioning/symmetrix/{array}/volume'.format(
            ver=UNISPHERE_VERSION, array=self.data.array))
        self.assertEqual(uri_1, built_uri_1)

        # version supplied as keyword argument
        resource_name = self.data.device_id
        version_2 = self.data.U4P_VERSION
        built_uri_2 = self.common._build_uri(
            category=SLOPROVISIONING, resource_level=SYMMETRIX,
            resource_level_id=self.data.array, resource_type=VOLUME,
            resource_type_id=resource_name, version=version_2)
        uri_2 = (
            '/{ver}/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
                ver=version_2, array=self.data.array, res=resource_name))
        self.assertEqual(uri_2, built_uri_2)

        # version and no_version keywords supplied, no_version overruled
        built_uri_3 = self.common._build_uri(
            category=SLOPROVISIONING, resource_level=SYMMETRIX,
            resource_level_id=self.data.array, resource_type=VOLUME,
            resource_type_id=resource_name, version=UNISPHERE_VERSION,
            no_version=True)
        uri_3 = (
            '/{ver}/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
                ver=UNISPHERE_VERSION, array=self.data.array,
                res=resource_name))
        self.assertEqual(uri_3, built_uri_3)

        # no_version flag passed, no version required for URI
        built_uri_4 = self.common._build_uri(
            category=SLOPROVISIONING, resource_level=SYMMETRIX,
            resource_level_id=self.data.array, resource_type=VOLUME,
            resource_type_id=resource_name, no_version=True)
        uri_4 = ('/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
            array=self.data.array, res=resource_name))
        self.assertEqual(uri_4, built_uri_4)

    def test_traditional_build_uri(self):
        """Test _build_uri."""
        # Only default args arrayID, category, resource_type passed
        built_uri = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume')
        temp_uri = (
            '/{}/sloprovisioning/symmetrix/{array}/volume'.format(
                self.data.U4P_VERSION, array=self.data.array))
        self.assertEqual(temp_uri, built_uri)

        # Default args passed along with resource_name and version kwarg
        built_uri_2 = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume',
            version=self.data.U4P_VERSION, resource_name=self.data.device_id)
        temp_uri_2 = (
            '/{}/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
                self.data.U4P_VERSION, array=self.data.array,
                res=self.data.device_id))
        self.assertEqual(temp_uri_2, built_uri_2)

    def test_new_build_uri_minimum(self):
        """Test _build_uri."""
        # Pass in only minimum required kwargs - version is optional
        built_uri_1 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix')
        temp_uri_1 = '/{}/sloprovisioning/symmetrix'.format(
            self.data.U4P_VERSION)
        self.assertEqual(temp_uri_1, built_uri_1)

    def test_new_build_uri_resource_level_id(self):
        """Test _build_uri."""
        # Pass in minimum kwargs with specified resource_level_id
        built_uri_2 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array)
        temp_uri_2 = ('/{}/sloprovisioning/symmetrix/{}'.format(
            self.data.U4P_VERSION, self.data.array))
        self.assertEqual(temp_uri_2, built_uri_2)

    def test_new_build_uri_resource_type(self):
        # Pass in minimum kwargs with specified resource_type
        built_uri_3 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup')
        temp_uri_3 = ('/{}/sloprovisioning/symmetrix/{}/{}'.format(
            self.data.U4P_VERSION, self.data.array, 'storagegroup'))
        self.assertEqual(temp_uri_3, built_uri_3)

    def test_new_build_uri_resource_type_id(self):
        # Pass in minimum kwargs with specified resource_type_id
        built_uri_4 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1)
        temp_uri_4 = ('/{}/sloprovisioning/symmetrix/{}/{}/{}'.format(
            self.data.U4P_VERSION, self.data.array, 'storagegroup',
            self.data.storagegroup_name_1))
        self.assertEqual(temp_uri_4, built_uri_4)

    def test_new_build_uri_resource(self):
        # Pass in minimum kwargs with specified resource
        built_uri_5 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap')
        temp_uri_5 = ('/{}/sloprovisioning/symmetrix/{}/{}/{}/{}'.format(
            self.data.U4P_VERSION, self.data.array, 'storagegroup',
            self.data.storagegroup_name_1, 'snap'))
        self.assertEqual(temp_uri_5, built_uri_5)

    def test_new_build_uri_resource_id(self):
        # Pass in minimum kwargs with specified resource_id
        built_uri_6 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap', resource_id=self.data.snapshot_name)
        temp_uri_6 = ('/{}/sloprovisioning/symmetrix/{}/{}/{}/{}/{}'.format(
            self.data.U4P_VERSION, self.data.array, 'storagegroup',
            self.data.storagegroup_name_1, 'snap', self.data.snapshot_name))
        self.assertEqual(temp_uri_6, built_uri_6)

    def test_new_build_uri_object_type(self):
        # Pass in minimum kwargs with specified object_type
        built_uri_7 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap', resource_id=self.data.snapshot_name,
            object_type='generation')
        temp_uri_7 = ('/{}/sloprovisioning/symmetrix/{}/{}/{}/{}/{}/{}'.format(
            self.data.U4P_VERSION, self.data.array, 'storagegroup',
            self.data.storagegroup_name_1, 'snap', self.data.snapshot_name,
            'generation'))
        self.assertEqual(temp_uri_7, built_uri_7)

    def test_new_build_uri_object_type_id(self):
        # Pass in minimum kwargs with specified object_type_id
        built_uri_8 = self.common._build_uri(
            version=self.data.U4P_VERSION, category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap', resource_id=self.data.snapshot_name,
            object_type='generation', object_type_id='1')
        temp_uri_8 = (
            '/{}/sloprovisioning/symmetrix/{}/{}/{}/{}/{}/{}/{}'.format(
                self.data.U4P_VERSION, self.data.array, 'storagegroup',
                self.data.storagegroup_name_1, 'snap',
                self.data.snapshot_name, 'generation', '1'))
        self.assertEqual(temp_uri_8, built_uri_8)

    def test_new_build_uri_performance(self):
        # Category is performance so no use of version in URI
        built_uri_9 = self.common._build_uri(
            category='performance', resource_level='Array',
            resource_type='keys')
        temp_uri_9 = '/performance/Array/keys'
        self.assertEqual(temp_uri_9, built_uri_9)

    def test_get_request(self):
        """Test get_request."""
        message = self.common.get_request('/version', resource_type='version')
        self.assertEqual(self.data.server_version, message)

    def test_get_resource(self):
        """Test get_resource."""
        # Traditional Method
        message = self.common.get_resource(
            self.data.array, 'sloprovisioning', 'volume',
            resource_name=None, params=None)
        self.assertEqual(self.data.volume_list[2], message)

        # New Method
        message_1 = self.common.get_resource(
            category='sloprovisioning',
            resource_level='symmetrix',
            resource_level_id=self.data.array,
            resource_type='volume')
        self.assertEqual(self.data.volume_list[2], message_1)

    def test_create_resource(self):
        """Test create_resource."""
        # Traditional Method
        message = self.common.create_resource(
            self.data.array, 'sloprovisioning', 'storagegroup', {})
        self.assertEqual(self.data.job_list[0], message)

        # New Method
        message_1 = self.common.create_resource(
            category='sloprovisioning',
            resource_level='storagegroup',
            resource_level_id=self.data.array)
        self.assertEqual(self.data.job_list[0], message_1)

    def test_modify_resource(self):
        """Test modify_resource."""
        # Traditional Method
        message = self.common.modify_resource(
            self.data.array, 'sloprovisioning', 'storagegroup', {})
        self.assertEqual(self.data.job_list[0], message)

        # New Method
        message_1 = self.common.modify_resource(
            category='sloprovisioning',
            resource_level='storagegroup',
            resource_level_id=self.data.array)
        self.assertEqual(self.data.job_list[0], message_1)

    def test_delete_resource(self):
        """Test delete_resource."""
        # Traditional Method
        self.common.delete_resource(
            self.data.array, 'sloprovisioning',
            'storagegroup', self.data.storagegroup_name)

        # New Method
        self.common.delete_resource(
            category='sloprovisioning',
            resource_level='storagegroup',
            resource_level_id=self.data.array,
            resource_type_id=self.data.storagegroup_name)

    def test_create_list_from_file(self):
        """Test create_list_from_file."""
        example_file = """Item1\nItem2\nItem3"""
        with mock.patch('builtins.open', mock.mock_open(
                read_data=example_file), create=True):
            list_from_file = self.common.create_list_from_file(example_file)
            self.assertTrue(isinstance(list_from_file, list))
            self.assertIn('Item1', list_from_file)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_read_csv_values(self, mck_open):
        """Test read_csv_values."""
        csv_response = [
            {'kpi_a': 'perf_data_1', 'kpi_b': 'perf_data_2'},
            {'kpi_a': 'perf_data_3', 'kpi_b': 'perf_data_4'},
            {'kpi_a': 'perf_data_5', 'kpi_b': 'perf_data_6'}]

        with mock.patch.object(csv, 'DictReader', return_value=csv_response):
            csv_data = self.common.read_csv_values(file_name='mock_csv_file')
            reference_csv_response = {
                'kpi_a': ['perf_data_1', 'perf_data_3', 'perf_data_5'],
                'kpi_b': ['perf_data_2', 'perf_data_4', 'perf_data_6']}
            self.assertTrue(isinstance(csv_data, dict))
            self.assertEqual(reference_csv_response, csv_data)

    def test_get_uni_version(self):
        """Test get_uni_version."""
        version, major_version = self.common.get_uni_version()
        self.assertEqual(self.data.server_version['version'], version)
        self.assertEqual(self.data.u4v_version, major_version)

    def test_get_array_list(self):
        """Test get_array_list."""
        array_list = self.common.get_array_list()
        self.assertEqual(self.data.symm_list['symmetrixId'], array_list)

    def test_get_v3_or_newer_array_list(self):
        """Test get_v3_or_newer_array_list."""
        array_list = self.common.get_v3_or_newer_array_list()
        self.assertEqual(self.data.symm_list['symmetrixId'], array_list)

    def test_get_array(self):
        """Test get_array."""
        array_details = self.common.get_array(self.data.array)
        self.assertEqual(self.data.symmetrix[0], array_details)

    def test_get_wlp_info_success(self):
        """Test get_wlp_information success."""
        with mock.patch.object(
                self.common, 'get_resource',
                return_value=self.data.wlp_info) as mck_wlp_info:
            wlp_info = self.common.get_wlp_information(self.data.array)
            self.assertEqual(self.data.wlp_info, wlp_info)
            mck_wlp_info.assert_called_once_with(
                category='wlp', resource_level='symmetrix',
                resource_level_id=self.data.array)

    def test_get_wlp_info_fail(self):
        """Test get_wlp_information fail."""
        with mock.patch.object(self.common, 'get_resource',
                               return_value=None):
            wlp_info = self.common.get_wlp_information(self.data.array)
            self.assertFalse(wlp_info)
            self.assertIsInstance(wlp_info, dict)

    def test_get_headroom_success(self):
        """Test get_headroom success."""
        with mock.patch.object(
                self.common, 'get_resource',
                return_value=self.data.headroom_array) as mck_head:
            headroom = self.common.get_headroom(
                self.data.array, self.data.workload, 'SRP_TEST', 'Gold')
            self.assertEqual(self.data.headroom_array['gbHeadroom'], headroom)
            params = {'srp': 'SRP_TEST', 'slo': 'Gold',
                      'workloadtype': self.data.workload}
            mck_head.assert_called_once_with(
                category='wlp', resource_level='symmetrix',
                resource_level_id=self.data.array, resource_type='headroom',
                params=params)

    def test_get_headroom_fail(self):
        """Test get_headroom fail."""
        with mock.patch.object(self.common, 'get_resource',
                               return_value=None):
            headroom = self.common.get_headroom(self.data.array,
                                                self.data.workload)
            self.assertFalse(headroom)
            self.assertIsInstance(headroom, list)

    def test_check_ipv4(self):
        """Test check_ipv4."""
        self.assertTrue(self.common.check_ipv4(self.data.ip))

    def test_check_ipv4_fail(self):
        """Test check_ipv4."""
        self.assertFalse(self.common.check_ipv4('invalid'))

    def test_check_ipv6(self):
        """Test check_ipv6."""
        self.assertTrue(self.common.check_ipv6(self.data.ipv6))

    def test_check_ipv6_fail(self):
        """Test check_ipv6."""
        self.assertFalse(self.common.check_ipv6('invalid'))

    def test_get_iterator_page_list(self):
        """Test get_iterator_page_list."""
        iterator_page = self.common.get_iterator_page_list('123', 1, 1000)
        self.assertEqual(self.data.iterator_page['result'], iterator_page)

    def test_get_iterator_results(self):
        rest_response_in = self.data.vol_with_pages
        ref_response = [{'volumeId': '00001'}, {'volumeId': '00002'}]
        response = self.common.get_iterator_results(rest_response_in)
        self.assertEqual(response, ref_response)

    def test_convert_to_snake_case(self):
        """Test convert_to_snake_case variations."""
        string_1 = 'CamelCase'
        string_2 = 'camelCase'
        string_3 = 'Camel_Case'
        string_4 = 'snake_case'

        self.assertEqual(self.common.convert_to_snake_case(string_1),
                         'camel_case')
        self.assertEqual(self.common.convert_to_snake_case(string_2),
                         'camel_case')
        self.assertEqual(self.common.convert_to_snake_case(string_3),
                         'camel_case')
        self.assertEqual(self.common.convert_to_snake_case(string_4),
                         'snake_case')
