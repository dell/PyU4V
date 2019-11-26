# The MIT License (MIT)
# Copyright (c) 2018 Dell Inc. or its subsidiaries.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from PyU4V import common
from PyU4V import performance
from PyU4V import provisioning
from PyU4V import replication
from PyU4V import rest_requests
from PyU4V import univmax_conn
from PyU4V.utils import config_handler
from PyU4V.utils import exception

import mock
import testtools

from . import pyu4v_common_data as pcd  # noqa: H304
from . import pyu4v_fakes as pf  # noqa: H304


class PyU4VCommonTest(testtools.TestCase):
    """Test common."""

    def setUp(self):
        """setUp."""
        super(PyU4VCommonTest, self).setUp()
        self.data = pcd.CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=pf.FakeRequestsSession())
        config_file = pf.FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn(array_id=self.data.array)
        self.common = self.conn.common

    def test_wait_for_job_complete(self):
        """Test wait_for_job_complete."""
        _, _, status, _ = self.common.wait_for_job_complete(
            self.data.job_list[0])
        self.assertEqual('SUCCEEDED', status)

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
        resource_name_1 = None
        version_1 = None
        built_uri_1 = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume',
            resource_name=resource_name_1, version=version_1)
        temp_uri_1 = (
            '/84/sloprovisioning/symmetrix/{array}/volume'.format(
                ver=version_1, array=self.data.array))
        self.assertEqual(temp_uri_1, built_uri_1)

        # version supplied as keyword argument
        resource_name_2 = self.data.device_id
        version_2 = '90'
        built_uri_2 = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume',
            resource_name=resource_name_2, version=version_2)
        temp_uri_2 = (
            '/{ver}/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
                ver=version_2, array=self.data.array, res=resource_name_2))
        self.assertEqual(temp_uri_2, built_uri_2)

        # version and no_version keywords supplied, no_version overruled
        resource_name_3 = self.data.device_id
        version_3 = '90'
        built_uri_3 = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume',
            resource_name=resource_name_3, version=version_3, no_version=True)
        temp_uri_3 = (
            '/{ver}/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
                ver=version_3, array=self.data.array, res=resource_name_3))
        self.assertEqual(temp_uri_3, built_uri_3)

        # no_version flag passed, no version required for URI
        resource_name_4 = self.data.device_id
        built_uri_4 = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume',
            resource_name=resource_name_4, no_version=True)
        temp_uri_4 = (
            '/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
                array=self.data.array, res=resource_name_3))
        self.assertEqual(temp_uri_4, built_uri_4)

    def test_traditional_build_uri(self):
        """Test _build_uri."""
        # Only default args arrayID, category, resource_type passed
        built_uri = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume')
        temp_uri = (
            '/84/sloprovisioning/symmetrix/{array}/volume'.format(
                array=self.data.array))
        self.assertEqual(temp_uri, built_uri)

        # Default args passed along with resource_name and version kwarg
        built_uri_2 = self.common._build_uri(
            self.data.array, 'sloprovisioning', 'volume', version='90',
            resource_name=self.data.device_id)
        temp_uri_2 = (
            '/90/sloprovisioning/symmetrix/{array}/volume/{res}'.format(
                array=self.data.array, res=self.data.device_id))
        self.assertEqual(temp_uri_2, built_uri_2)

    def test_new_build_uri(self):
        """Test _build_uri."""
        # Pass in only minimum required kwargs - version is optional
        built_uri_1 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix',
        )
        temp_uri_1 = '/90/sloprovisioning/symmetrix'
        self.assertEqual(temp_uri_1, built_uri_1)

        # Pass in minimum kwargs with specified resource_level_id
        built_uri_2 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
        )
        temp_uri_2 = ('/90/sloprovisioning/symmetrix/{}'.format(
            self.data.array))
        self.assertEqual(temp_uri_2, built_uri_2)

        # Pass in same as before bus with resource_type
        built_uri_3 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup'
        )
        temp_uri_3 = ('/90/sloprovisioning/symmetrix/{}/{}'.format(
            self.data.array, 'storagegroup'))
        self.assertEqual(temp_uri_3, built_uri_3)

        # Pass in same as before bus with resource_type_id
        built_uri_4 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1
        )
        temp_uri_4 = ('/90/sloprovisioning/symmetrix/{}/{}/{}'.format(
            self.data.array, 'storagegroup', self.data.storagegroup_name_1))
        self.assertEqual(temp_uri_4, built_uri_4)

        # Pass in same as before bus with resource
        built_uri_5 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap'
        )
        temp_uri_5 = ('/90/sloprovisioning/symmetrix/{}/{}/{}/{}'.format(
            self.data.array, 'storagegroup', self.data.storagegroup_name_1,
            'snap'))
        self.assertEqual(temp_uri_5, built_uri_5)

        # Pass in same as before bus with resource_id
        built_uri_6 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap', resource_id=self.data.snapshot_name
        )
        temp_uri_6 = ('/90/sloprovisioning/symmetrix/{}/{}/{}/{}/{}'.format(
            self.data.array, 'storagegroup', self.data.storagegroup_name_1,
            'snap', self.data.snapshot_name))
        self.assertEqual(temp_uri_6, built_uri_6)

        # Pass in same as before bus with object_type
        built_uri_7 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap', resource_id=self.data.snapshot_name,
            object_type='generation'
        )
        temp_uri_7 = ('/90/sloprovisioning/symmetrix/{}/{}/{}/{}/{}/{}'.format(
            self.data.array, 'storagegroup', self.data.storagegroup_name_1,
            'snap', self.data.snapshot_name, 'generation'))
        self.assertEqual(temp_uri_7, built_uri_7)

        # Pass in same as before bus with object_type_id
        built_uri_8 = self.common._build_uri(
            version='90', category='sloprovisioning',
            resource_level='symmetrix', resource_level_id=self.data.array,
            resource_type='storagegroup',
            resource_type_id=self.data.storagegroup_name_1,
            resource='snap', resource_id=self.data.snapshot_name,
            object_type='generation', object_type_id='1'
        )
        temp_uri_8 = (
            '/90/sloprovisioning/symmetrix/{}/{}/{}/{}/{}/{}/{}'.format(
                self.data.array, 'storagegroup', self.data.storagegroup_name_1,
                'snap', self.data.snapshot_name, 'generation', '1'))
        self.assertEqual(temp_uri_8, built_uri_8)

        # Category is performance so no use of version in URI
        built_uri_9 = self.common._build_uri(
            category='performance', resource_level='Array',
            resource_type='keys')
        temp_uri_9 = '/performance/Array/keys'
        self.assertEqual(temp_uri_9, built_uri_9)

    def test_get_request(self):
        """Test get_request."""
        message = self.common.get_request(
            '/84/system/version', 'version', params=None)
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

    def test_get_iterator_page_list(self):
        """Test get_iterator_page_list."""
        iterator_page = self.common.get_iterator_page_list('123', 1, 1000)
        self.assertEqual(self.data.iterator_page['result'], iterator_page)

    def test_get_wlp_timestamp(self):
        """Test get_wlp_information."""
        wlp_timestamp = self.common.get_wlp_information(self.data.array)
        self.assertEqual(self.data.wlp['symmetrixDetails'], wlp_timestamp)

    def test_get_headroom(self):
        """Test get_headroom."""
        headroom = self.common.get_headroom(self.data.array,
                                            self.data.workload)
        self.assertEqual(self.data.headroom['headroom'], headroom)


class PyU4VPerformanceTest(testtools.TestCase):
    """Test Unisphere performance."""

    def setUp(self):
        """setUp."""
        super(PyU4VPerformanceTest, self).setUp()
        self.data = pcd.CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=pf.FakeRequestsSession())
        config_file = pf.FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn(array_id=self.data.array)
        self.common = self.conn.common
        self.data = pcd.CommonData()
        self.performance = self.conn.performance

    def test_get_array_metrics(self):
        """Test get_array_metrics."""
        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'array',
                'perf_data': [{"Reads": 32.146667, "timestamp": 1566466200000}]
            }
            actual_response = self.performance.get_array_metrics(
                start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response_legacy):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'array',
                'perf_data': [{"Reads": 32.146667, "timestamp": 1566466200000}]
            }
            actual_response = self.performance.get_array_metrics(
                start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=list()):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'array', 'perf_data': []}
            actual_response = self.performance.get_array_metrics(
                start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

    def test_get_sg_metrics(self):
        """Test get_sg_metrics."""
        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response):
            expected_response = {
                'symmetrixID': pcd.CommonData.array, 'sgname': 'test',
                'reporting_level': 'StorageGroup', 'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_storage_group_metrics(
                sg_id='test', start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response_legacy):
            expected_response = {
                'symmetrixID': pcd.CommonData.array, 'sgname': 'test',
                'reporting_level': 'StorageGroup', 'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_storage_group_metrics(
                sg_id='test', start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=list()):
            expected_response = {
                'symmetrixID': pcd.CommonData.array, 'sgname': 'test',
                'reporting_level': 'StorageGroup', 'perf_data': []}
            actual_response = self.performance.get_storage_group_metrics(
                sg_id='test', start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

    @mock.patch.object(performance.PerformanceFunctions,
                       'get_fe_director_list', return_value=['dir1', 'dir2'])
    def test_get_all_fe_dir_metrics(self, mck_dir_list):
        """Test get_all_fe_dir_metrics."""
        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'FEDirector', 'perf_data': [
                    {'directorID': 'dir1', 'perf_data': [
                        {"Reads": 32.146667, "timestamp": 1566466200000}]},
                    {'directorID': 'dir2', 'perf_data': [
                        {"Reads": 32.146667, "timestamp": 1566466200000}]}]}
            actual_response = self.performance.get_all_fe_director_metrics(
                start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response_legacy):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'FEDirector', 'perf_data': [
                    {'directorID': 'dir1', 'perf_data': [
                        {"Reads": 32.146667, "timestamp": 1566466200000}]},
                    {'directorID': 'dir2', 'perf_data': [
                        {"Reads": 32.146667, "timestamp": 1566466200000}]}]}
            actual_response = self.performance.get_all_fe_director_metrics(
                start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=list()):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'FEDirector', 'perf_data': [
                    {'directorID': 'dir1', 'perf_data': []},
                    {'directorID': 'dir2', 'perf_data': []}]}
            actual_response = self.performance.get_all_fe_director_metrics(
                start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

    @mock.patch.object(provisioning.ProvisioningFunctions, 'get_director',
                       return_value={'availability': 'Online',
                                     'director_id': 'FA-1D'})
    def test_get_director_info(self, mck_get_dir):
        """Test get_director_info."""
        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response):
            expected_response = {
                'symmetrixId': pcd.CommonData.array, 'director_id': 'FA-1D',
                'directorType': 'FE', 'reporting_level': 'Director',
                'availability': 'Online', 'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_director_info(
                director_id='FA-1D', start_date=1566466200000,
                end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response_legacy):
            expected_response = {
                'symmetrixId': pcd.CommonData.array, 'director_id': 'FA-1D',
                'directorType': 'FE', 'reporting_level': 'Director',
                'availability': 'Online', 'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_director_info(
                director_id='FA-1D', start_date=1566466200000,
                end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=list()):
            expected_response = {
                'symmetrixId': pcd.CommonData.array, 'director_id': 'FA-1D',
                'directorType': 'FE', 'reporting_level': 'Director',
                'availability': 'Online', 'perf_data': False,
                'perf_msg': 'No active Director performance data available'}
            actual_response = self.performance.get_director_info(
                director_id='FA-1D', start_date=1566466200000,
                end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

    def test_get_port_group_metrics(self):
        """Test get_port_group_metrics."""
        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'PortGroup', 'pgname': 'test',
                'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_port_group_metrics(
                pg_id='test', start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response_legacy):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'PortGroup', 'pgname': 'test',
                'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_port_group_metrics(
                pg_id='test', start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=[]):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'PortGroup', 'pgname': 'test',
                'perf_data': []}
            actual_response = self.performance.get_port_group_metrics(
                pg_id='test', start_date=1566466200000, end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

    def test_get_host_metrics(self):
        """Test get_host_metrics."""
        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'Host', 'HostID': 'test',
                'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_host_metrics(
                host='test', start_date=1566466200000,
                end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=self.data.perf_response_legacy):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'Host', 'HostID': 'test',
                'perf_data': [
                    {"Reads": 32.146667, "timestamp": 1566466200000}]}
            actual_response = self.performance.get_host_metrics(
                host='test', start_date=1566466200000,
                end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

        with mock.patch.object(self.performance, 'request',
                               return_value=list()):
            expected_response = {
                'symmetrixID': pcd.CommonData.array,
                'reporting_level': 'Host', 'HostID': 'test',
                'perf_data': []}
            actual_response = self.performance.get_host_metrics(
                host='test', start_date=1566466200000,
                end_date=1566466200000)
            self.assertEqual(expected_response, actual_response)

    def test_extract_perf_details(self):
        """Test extract_perf_details."""
        expected_response = [{"Reads": 32.146667, "timestamp": 1566466200000}]
        actual_response = self.performance._extract_perf_details(
            self.data.perf_response)
        self.assertEqual(expected_response, actual_response)


class PyU4VProvisioningTest(testtools.TestCase):
    """Test provisioning."""

    def setUp(self):
        """setUp."""
        super(PyU4VProvisioningTest, self).setUp()
        self.data = pcd.CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=pf.FakeRequestsSession())
        config_file = pf.FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn(array_id=self.data.array)
        self.common = self.conn.common
        self.provisioning = self.conn.provisioning

    def test_get_director(self):
        """Test get_director."""
        dir_details = self.provisioning.get_director(self.data.director_id1)
        self.assertEqual(self.data.director_info, dir_details)

    def test_get_director_list(self):
        """Test get_director_list."""
        dir_list = self.provisioning.get_director_list()
        self.assertEqual(self.data.director_list['directorId'], dir_list)

    def test_get_director_port(self):
        """Test get_director_port."""
        port_details = self.provisioning.get_director_port(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.port_list[0], port_details)

    def test_get_director_port_list(self):
        """Test get_director_port_list."""
        port_key_list = self.provisioning.get_director_port_list(
            self.data.director_id1)
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_port_identifier(self):
        """Test get_port_identifier."""
        wwn = self.provisioning.get_port_identifier(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.wwnn1, wwn)

    def test_get_host(self):
        """Test get_host."""
        host_details = self.provisioning.get_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual(self.data.initiatorgroup[0], host_details)

    def test_get_host_list(self):
        """Test get_host_list."""
        host_list = self.provisioning.get_host_list()
        self.assertEqual(self.data.host_list['hostId'], host_list)

    def test_create_host(self):
        """Test create_host."""
        host_flags = {'consistent_lun': 'true'}
        data = [self.data.wwnn1, self.data.wwpn2]
        with mock.patch.object(self.provisioning, 'create_resource') as \
                mock_create:
            self.provisioning.create_host(
                self.data.initiatorgroup_name_i, host_flags=host_flags,
                initiator_list=data, _async=True)
            new_ig_data = {'hostId': self.data.initiatorgroup_name_i,
                           'initiatorId': data,
                           'hostFlags': host_flags,
                           'executionOption': 'ASYNCHRONOUS'}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'host',
                payload=new_ig_data)
            mock_create.reset_mock()
            self.provisioning.create_host(
                self.data.initiatorgroup_name_i)
            new_ig_data2 = {'hostId': self.data.initiatorgroup_name_i}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'host',
                payload=new_ig_data2)

    def test_modify_host(self):
        """Test modify_host."""
        host_name = self.data.initiatorgroup_name_i
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_host(
                host_name, host_flag_dict={'consistent_lun': 'true'})
            self.provisioning.modify_host(
                host_name, remove_init_list=[self.data.wwnn1])
            self.provisioning.modify_host(
                host_name, add_init_list=[self.data.wwnn1])
            self.provisioning.modify_host(host_name, new_name='my-new-name')
            self.assertEqual(4, mock_mod.call_count)
            self.assertRaises(exception.InvalidInputException,
                              self.provisioning.modify_host, host_name)

    def test_delete_host(self):
        """Test delete_host."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_host(self.data.initiatorgroup_name_i)
            mock_delete.assert_called_once()

    def test_get_mvs_from_host(self):
        """Test get_mvs_from_host."""
        mv_list = self.provisioning.get_mvs_from_host(
            self.data.initiatorgroup_name_i)
        self.assertEqual([self.data.masking_view_name_i], mv_list)

    def test_get_initiator_ids_from_host(self):
        """Test get_initiator_ids_from_host."""
        init_list = self.provisioning.get_initiator_ids_from_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual([self.data.wwpn1], init_list)

    def test_get_hostgroup(self):
        """Test get_hostgroup."""
        hg_details = self.provisioning.get_hostgroup(self.data.hostgroup_id)
        self.assertEqual(self.data.hostgroup, hg_details)

    def test_get_hostgroup_list(self):
        """Test get_hostgroup_list."""
        hg_list = self.provisioning.get_hostgroup_list()
        self.assertEqual(self.data.hostgroup_list['hostGroupId'], hg_list)
        with mock.patch.object(
                self.provisioning, 'get_resource',
                return_value={'some_key': 'some_value'}):
            hg_list = self.provisioning.get_hostgroup_list()
            self.assertEqual([], hg_list)

    def test_create_hostgroup(self):
        """Test create_hostgroup."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_hostgroup(
                self.data.hostgroup_id, [self.data.initiatorgroup_name_f],
                host_flags={'flag': 1}, _async=True)
            self.provisioning.create_hostgroup(
                self.data.hostgroup_id, [self.data.initiatorgroup_name_f])
        self.assertEqual(2, mock_create.call_count)

    def test_modify_hostgroup(self):
        """Test modify_hostgroup."""
        hostgroup_name = self.data.hostgroup_id
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_hostgroup(
                hostgroup_name, host_flag_dict={'consistent_lun': 'true'})
            self.provisioning.modify_hostgroup(
                hostgroup_name, remove_host_list=['host1'])
            self.provisioning.modify_hostgroup(
                hostgroup_name, add_host_list=['host2'])
            self.provisioning.modify_hostgroup(
                hostgroup_name, new_name='my-new-name')
            self.assertEqual(4, mock_mod.call_count)
            self.assertRaises(exception.InvalidInputException,
                              self.provisioning.modify_hostgroup,
                              hostgroup_name)

    def test_delete_hostgroup(self):
        """Test delete_hostgroup."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_hostgroup(self.data.hostgroup_id)
            mock_delete.assert_called_once()

    def test_get_initiator(self):
        """Test get_initiator."""
        init_details = self.provisioning.get_initiator(self.data.wwpn1)
        self.assertEqual(self.data.initiator_list[0], init_details)

    def test_get_initiator_list(self):
        """Test get_initiator_list."""
        init_list = self.provisioning.get_initiator_list()
        self.assertEqual(
            self.data.initiator_list[2]['initiatorId'], init_list)

    def test_modify_initiator(self):
        """Test modify_initiator."""
        initiator_name = self.data.wwpn1
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_initiator(
                initiator_name, remove_masking_entry='true')
            self.provisioning.modify_initiator(
                initiator_name, replace_init=self.data.wwpn2)
            self.provisioning.modify_initiator(
                initiator_name, rename_alias=(
                    'new node name', 'new port name'))
            self.provisioning.modify_initiator(
                initiator_name, set_fcid='my-new-name')
            self.provisioning.modify_initiator(
                initiator_name, initiator_flags={'my-flag': 'value'})
            self.assertEqual(5, mock_mod.call_count)
            self.assertRaises(
                exception.InvalidInputException,
                self.provisioning.modify_initiator, initiator_name)

    def test_is_initiator_in_host(self):
        """Test is_initiator_in_host."""
        check = self.provisioning.is_initiator_in_host(self.data.wwpn1)
        self.assertTrue(check)
        check = self.provisioning.is_initiator_in_host('fake-init')
        self.assertFalse(check)

    def test_get_initiator_group_from_initiator(self):
        """Test get_initiator_group_from_initiator."""
        found_ig_name = self.provisioning.get_initiator_group_from_initiator(
            self.data.wwpn1)
        self.assertEqual(self.data.initiatorgroup_name_f, found_ig_name)

    def test_get_masking_view_list(self):
        """Test get_masking_view_list."""
        mv_list = self.provisioning.get_masking_view_list()
        self.assertEqual(self.data.maskingview[2]['maskingViewId'], mv_list)

    def test_get_masking_view(self):
        """Test get_masking_view."""
        mv_details = self.provisioning.get_masking_view(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.maskingview[0], mv_details)

    def test_create_masking_view_existing_components(self):
        """Test create_masking_view_existing_components."""
        pg_name = self.data.port_group_name_f
        sg_name = self.data.storagegroup_name_2
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_masking_view_existing_components(
                pg_name, 'my_masking_view', sg_name,
                host_group_name=self.data.hostgroup_id, _async=True)
            self.provisioning.create_masking_view_existing_components(
                pg_name, 'my_masking_view', sg_name, _async=True,
                host_name=self.data.initiatorgroup_name_f)
        self.assertEqual(2, mock_create.call_count)
        self.assertRaises(
            exception.InvalidInputException,
            self.provisioning.create_masking_view_existing_components,
            pg_name, 'my_masking_view', sg_name)

    def test_get_masking_views_from_storage_group(self):
        """Test get_masking_views_from_storage_group."""
        mv_list = self.provisioning.get_masking_views_from_storage_group(
            self.data.storagegroup_name_1)
        self.assertEqual(self.data.sg_details[1]['maskingview'], mv_list)

    def test_get_masking_views_by_host(self):
        """Test get_masking_views_by_host."""
        mv_list = self.provisioning.get_masking_views_by_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual(self.data.initiator_list[0]['maskingview'], mv_list)

    def test_get_element_from_masking_view_exception(self):
        """Test get_masking_view."""
        with mock.patch.object(self.provisioning, 'get_masking_view',
                               return_value=None):
            self.assertRaises(exception.ResourceNotFoundException,
                              self.provisioning.get_element_from_masking_view,
                              self.data.masking_view_name_f)

    def test_get_common_masking_views(self):
        """Test get_common_masking_views."""
        with mock.patch.object(
                self.provisioning, 'get_masking_view_list') as mock_list:
            self.provisioning.get_common_masking_views(
                self.data.port_group_name_f, self.data.initiatorgroup_name_f)
            mock_list.assert_called_once()

    def test_delete_masking_view(self):
        """Test delete_masking_view."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_masking_view(
                self.data.masking_view_name_f)
            mock_delete.assert_called_once()

    def test_rename_masking_view(self):
        """Test rename_masking_view."""
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.rename_masking_view(
                self.data.masking_view_name_f, 'new-name')
            mock_mod.assert_called_once()

    def test_get_host_from_maskingview(self):
        """Test get_host_from_maskingview."""
        ig_id = self.provisioning.get_host_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.initiatorgroup_name_f, ig_id)

    def test_get_storagegroup_from_maskingview(self):
        """Test get_storagegroup_from_maskingview."""
        sg_id = self.provisioning.get_storagegroup_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.storagegroup_name, sg_id)

    def test_get_portgroup_from_maskingview(self):
        """Test get_portgroup_from_maskingview."""
        pg_id = self.provisioning.get_portgroup_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.port_group_name_f, pg_id)

    def test_get_maskingview_connections(self):
        """Test get_maskingview_connections."""
        mv_conn_list = self.provisioning.get_maskingview_connections(
            self.data.masking_view_name_f)
        self.assertEqual(
            self.data.maskingview[0]['maskingViewConnection'], mv_conn_list)

    def test_find_host_lun_id_for_vol(self):
        """Test find_host_lun_id_for_vol."""
        host_lun_id = self.provisioning.find_host_lun_id_for_vol(
            self.data.masking_view_name_f, self.data.device_id)
        self.assertEqual(3, host_lun_id)
        with mock.patch.object(
                self.provisioning, 'get_maskingview_connections',
                side_effect=[[], [{'not_host_lun': 'value'}]]):
            for x in range(0, 2):
                host_lun_id2 = self.provisioning.find_host_lun_id_for_vol(
                    self.data.masking_view_name_f, self.data.device_id)
                self.assertIsNone(host_lun_id2)

    def test_get_port_list(self):
        """Test get_port_list."""
        port_key_list = self.provisioning.get_port_list()
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_portgroup(self):
        """Test get_portgroup."""
        pg_details = self.provisioning.get_portgroup(
            self.data.port_group_name_f)
        self.assertEqual(self.data.portgroup[0], pg_details)

    def test_get_portgroup_list(self):
        """Test get_portgroup_list."""
        pg_list = self.provisioning.get_portgroup_list()
        self.assertEqual(self.data.pg_list['portGroupId'], pg_list)

    def test_get_ports_from_pg(self):
        """Test get_ports_from_pg."""
        port_list = self.provisioning.get_ports_from_pg(
            self.data.port_group_name_f)
        self.assertEqual(['FA-1D:4'], port_list)

    def test_get_target_wwns_from_pg(self):
        """Test get_target_wwns_from_pg."""
        target_wwns = self.provisioning.get_target_wwns_from_pg(
            self.data.port_group_name_f)
        self.assertEqual([self.data.wwnn1], target_wwns)

    def test_get_iscsi_ip_address_and_iqn(self):
        """Test get_iscsi_ip_address_and_iqn."""
        ip_addresses, iqn = self.provisioning.get_iscsi_ip_address_and_iqn(
            'SE-4E:0')
        self.assertEqual([self.data.ip], ip_addresses)
        self.assertEqual(self.data.initiator, iqn)

    def test_create_portgroup(self):
        """Test create_portgroup."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_portgroup(
                self.data.port_group_name_f, self.data.director_id1,
                self.data.port_id1)
        mock_create.assert_called_once()

    def test_create_multiport_portgroup(self):
        """Test create_multiport_portgroup."""
        port_dict_list = [{'directorId': self.data.director_id1,
                           'portId': self.data.port_id1},
                          {'directorId': self.data.director_id2,
                           'portId': self.data.port_id2}, ]
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_multiport_portgroup(
                self.data.port_group_name_f, port_dict_list)
        mock_create.assert_called_once()

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'create_multiport_portgroup')
    @mock.patch.object(common.CommonFunctions, 'create_list_from_file',
                       return_value=['FA-1D:4', 'SE-4E:0'])
    def test_create_portgroup_from_file(self, mock_list, mock_create):
        """Test create_portgroup_from_file."""
        payload = [{'directorId': self.data.director_id1,
                    'portId': self.data.port_id1},
                   {'directorId': self.data.director_id2,
                    'portId': self.data.port_id2}]
        self.provisioning.create_portgroup_from_file('my-file', 'pg_id')
        mock_create.assert_called_once_with('pg_id', payload)

    def test_modify_portgroup(self):
        """Test modify_portgroup."""
        pg_name = self.data.port_group_name_f
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_portgroup(pg_name, remove_port='FA-1D:4')
            self.provisioning.modify_portgroup(
                pg_name, rename_portgroup='new-name')
            self.provisioning.modify_portgroup(pg_name, add_port='FA-1D:4')
            self.assertEqual(3, mock_mod.call_count)
            self.assertRaises(
                exception.InvalidInputException,
                self.provisioning.modify_portgroup, pg_name)

    def test_delete_portgroup(self):
        """Test delete_portgroup."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_del:
            self.provisioning.delete_portgroup(self.data.port_group_name_f)
            mock_del.assert_called_once()

    def test_get_slo_list(self):
        """Test get_slo_list."""
        slo_list = self.provisioning.get_slo_list()
        self.assertEqual(self.data.slo_list['sloId'], slo_list)

    def test_get_slo(self):
        """Test get_slo."""
        slo_details = self.provisioning.get_slo(self.data.slo)
        self.assertEqual(self.data.slo_details, slo_details)

    def test_modify_slo(self):
        """Test modify_slo."""
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_slo('Diamond', 'Diamante')
            mock_mod.assert_called_once()

    def test_get_srp(self):
        """Test get_srp."""
        srp_details = self.provisioning.get_srp(self.data.srp)
        self.assertEqual(self.data.srp_details, srp_details)

    def test_get_srp_list(self):
        """Test get_srp_list."""
        srp_list = self.provisioning.get_srp_list()
        self.assertEqual(self.data.srp_list['srpId'], srp_list)

    def test_get_compressibility_report(self):
        """Test get_compressibility_report."""
        report = self.provisioning.get_compressibility_report(self.data.srp)
        self.assertEqual(
            self.data.compr_report['storageGroupCompressibility'], report)

    def test_is_compression_capable(self):
        """Test is_compression_capable."""
        compr_capable = self.provisioning.is_compression_capable()
        self.assertTrue(compr_capable)

    def test_get_storage_group(self):
        """Test get_storage_group."""
        sg_details = self.provisioning.get_storage_group(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_details[0], sg_details)

    def test_get_storage_group_list(self):
        """Test get_storage_group_list."""
        sg_list = self.provisioning.get_storage_group_list(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_list['storageGroupId'], sg_list)

    def test_get_mv_from_sg(self):
        """Test get_mv_from_sg."""
        mv_list = self.provisioning.get_mv_from_sg(
            self.data.storagegroup_name_1)
        self.assertEqual(self.data.sg_details[1]['maskingview'], mv_list)

    def test_get_num_vols_in_sg(self):
        """Test get_num_vols_in_sg."""
        num_vols = self.provisioning.get_num_vols_in_sg(
            self.data.storagegroup_name)
        self.assertEqual(2, num_vols)

    def test_is_child_sg_in_parent_sg(self):
        """Test is_child_sg_in_parent_sg."""
        is_child = self.provisioning.is_child_sg_in_parent_sg(
            self.data.storagegroup_name_1, self.data.parent_sg)
        self.assertTrue(is_child)
        is_child2 = self.provisioning.is_child_sg_in_parent_sg(
            self.data.storagegroup_name_2, self.data.parent_sg)
        self.assertFalse(is_child2)

    def test_create_storage_group(self):
        """Test create_storage_group."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            # 1 - no slo, not async
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', None, None)
            payload1 = {
                'srpId': 'None',
                'storageGroupId': 'new-sg',
                'emulation': 'FBA'}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'storagegroup',
                payload=payload1)
            # 2 - slo set, is async
            mock_create.reset_mock()
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', self.data.slo, 'None', _async=True)
            payload2 = {
                'srpId': self.data.srp,
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'num_of_vols': 0, 'sloId': self.data.slo,
                     'workloadSelection': 'None',
                     'noCompression': 'false',
                     'volumeAttribute': {'volume_size': '0',
                                         'capacityUnit': 'GB'}}],
                'executionOption': 'ASYNCHRONOUS'}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'storagegroup',
                payload=payload2)

    def test_create_storage_group_full_allocated(self):
        """Test create_storage_group."""
        ppctroc = 'persist_preallocated_capacity_through_reclaim_or_copy'
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            # 1 - no slo, not async
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', None, None)
            payload1 = {
                'srpId': 'None',
                'storageGroupId': 'new-sg',
                'emulation': 'FBA'}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'storagegroup',
                payload=payload1)
            # 2 - slo set, is async
            mock_create.reset_mock()
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', self.data.slo, 'None',
                allocate_full=True, _async=True)
            payload2 = {
                'srpId': self.data.srp,
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'num_of_vols': 0, 'sloId': self.data.slo,
                     'workloadSelection': 'None',
                     'noCompression': 'true',
                     'allocate_capacity_for_each_vol': 'true',
                     ppctroc: 'true',
                     'volumeAttribute': {'volume_size': '0',
                                         'capacityUnit': 'GB'}}],
                'executionOption': 'ASYNCHRONOUS'}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'storagegroup',
                payload=payload2)

    def test_create_storage_group_vol_name(self):
        """Test create_storage_group."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            # 1 - no slo, not async
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', slo='Diamond', workload=None,
                num_vols=1, vol_size='1', vol_name='ID4TEST')
            payload1 = {
                'srpId': 'SRP_1',
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'num_of_vols': 1,
                     'sloId': 'Diamond',
                     'workloadSelection': None,
                     'noCompression': 'false',
                     'volumeIdentifier': {
                         'identifier_name': 'ID4TEST',
                         'volumeIdentifierChoice': 'identifier_name'},
                     'volumeAttribute': {'volume_size': '1',
                                         'capacityUnit': 'GB'}}]}

            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'storagegroup',
                payload=payload1)

    def test_create_non_empty_storagegroup(self):
        """Test create_non_empty_storagegroup."""
        with mock.patch.object(
                self.provisioning, 'create_storage_group') as mock_create:
            self.provisioning.create_non_empty_storagegroup(
                self.data.srp, 'new-sg', self.data.slo, self.data.workload,
                1, '2', 'GB')
            mock_create.assert_called_once()

    def test_create_empty_sg(self):
        """Test create_empty_sg."""
        with mock.patch.object(
                self.provisioning, 'create_storage_group') as mock_create:
            self.provisioning.create_empty_sg(
                self.data.srp, 'new-sg', self.data.slo, self.data.workload)
            mock_create.assert_called_once()

    def test_modify_storage_group(self):
        """Test modify_storage_group."""
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_storage_group(
                self.data.storagegroup_name, {})
            mock_mod.assert_called_once()

    def test_add_existing_vol_to_sg(self):
        """Test add_existing_vol_to_sg."""
        payload1 = {'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addSpecificVolumeParam': {
                    'volumeId': [self.data.device_id]}}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            # vol id, not list; not _async
            self.provisioning.add_existing_vol_to_sg(
                self.data.storagegroup_name, self.data.device_id)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload1)
            # vol ids in list form; _async is true
            mock_mod.reset_mock()
            self.provisioning.add_existing_vol_to_sg(
                self.data.storagegroup_name, [self.data.device_id], True)
            payload1.update({'executionOption': 'ASYNCHRONOUS'})
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload1)

    def test_add_new_vol_to_storagegroup(self):
        """Test add_new_vol_to_storagegroup."""
        add_vol_info = {
            'num_of_vols': 1, 'emulation': 'FBA', 'create_new_volumes': False,
            'volumeAttribute': {'volume_size': '10', 'capacityUnit': 'GB'}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            # no vol name; not _async
            self.provisioning.add_new_vol_to_storagegroup(
                self.data.storagegroup_name, 1, '10', 'GB')
            payload1 = {'editStorageGroupActionParam': {
                'expandStorageGroupParam': {
                    'addVolumeParam': add_vol_info}}}
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload1)
            # vol name required; _async is true
            mock_mod.reset_mock()
            add_vol_info.update({'volumeIdentifier': {
                'identifier_name': 'my-vol',
                'volumeIdentifierChoice': 'identifier_name'}})
            self.provisioning.add_new_vol_to_storagegroup(
                self.data.storagegroup_name, 1, '10', 'GB', True, 'my-vol')
            payload2 = {'editStorageGroupActionParam': {
                'expandStorageGroupParam': {'addVolumeParam': add_vol_info}},
                'executionOption': 'ASYNCHRONOUS'}
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload2)

    def test_remove_vol_from_storagegroup(self):
        """Test remove_vol_from_storagegroup."""
        payload1 = {'editStorageGroupActionParam': {
            'removeVolumeParam': {'volumeId': [self.data.device_id]}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            # vol id, not list; not _async
            self.provisioning.remove_vol_from_storagegroup(
                self.data.storagegroup_name, self.data.device_id)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload1)
            # vol ids in list form; _async is true
            mock_mod.reset_mock()
            self.provisioning.remove_vol_from_storagegroup(
                self.data.storagegroup_name, [self.data.device_id], True)
            payload1.update({'executionOption': 'ASYNCHRONOUS'})
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload1)

    def test_move_volumes_between_storagegroups(self):
        """Test move_volumes_between_storage_groups."""
        payload1 = ({'editStorageGroupActionParam': {
            'moveVolumeToStorageGroupParam': {
                'volumeId': [self.data.device_id],
                'storageGroupId': self.data.storagegroup_name_1,
                'force': 'false'}}})
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            # vol id, not list; not _async
            self.provisioning.move_volumes_between_storage_groups(
                self.data.device_id, self.data.storagegroup_name,
                self.data.storagegroup_name_1)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload1)
            # vol ids in list form; _async is true
            mock_mod.reset_mock()
            self.provisioning.move_volumes_between_storage_groups(
                [self.data.device_id], self.data.storagegroup_name,
                self.data.storagegroup_name_1, _async=True)
            payload1.update({'executionOption': 'ASYNCHRONOUS'})
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload1)

    def test_create_volume_from_sg_return_dev_id(self):
        """Test create_volume_from_sg_return_dev_id."""
        sg_name = self.data.storagegroup_name_1
        job = {'status': 'SUCCEEDED', 'jobId': '12345', 'result': 'created',
               'resourceLink': 'storagegroup/%s' % sg_name,
               'description': 'Creating new Volumes for MY-SG : [00001]'}
        with mock.patch.object(
                self.provisioning, 'add_new_vol_to_storagegroup',
                return_value=job):
            with mock.patch.object(self.provisioning, 'get_volume_list',
                                   return_value=['00001']):
                device_id = (
                    self.provisioning.create_volume_from_sg_return_dev_id(
                        'volume_name', sg_name, '2'))
                self.assertEqual(self.data.device_id, device_id)

    def test_add_child_sg_to_parent_sg(self):
        """Test add_child_sg_to_parent_sg."""
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.add_child_sg_to_parent_sg(
                self.data.storagegroup_name_1, self.data.parent_sg)
            mock_mod.assert_called_once()

    def test_remove_child_sg_from_parent_sg(self):
        """Test remove_child_sg_from_parent_sg."""
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.remove_child_sg_from_parent_sg(
                self.data.storagegroup_name_1, self.data.parent_sg)
            mock_mod.assert_called_once()

    def test_update_storagegroup_qos(self):
        """Test update_storagegroup_qos."""
        qos_specs = {'maxIOPS': '3000', 'DistributionType': 'Always'}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.update_storagegroup_qos(
                self.data.qos_storagegroup, qos_specs)
            mock_mod.assert_called_once()
        qos_specs2 = {'maxIOPS': '4000', 'DistributionType': 'oops'}
        self.assertRaises(exception.InvalidInputException,
                          self.provisioning.update_storagegroup_qos,
                          self.data.qos_storagegroup, qos_specs2)

    def test_set_host_io_limit_iops(self):
        """Test set_host_io_limit_iops_or_mbps."""
        with mock.patch.object(
                self.provisioning, 'update_storagegroup_qos') as mock_qos:
            self.provisioning.set_host_io_limit_iops_or_mbps(
                self.data.qos_storagegroup, '3000', 'Always')
            mock_qos.assert_called_once()

    def test_delete_storagegroup(self):
        """Test delete_storagegroup."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_storagegroup(self.data.storagegroup_name)
            mock_delete.assert_called_once()

    def test_get_volume(self):
        """Test get_volume."""
        vol_details = self.provisioning.get_volume(self.data.device_id)
        self.assertEqual(self.data.volume_details[0], vol_details)

    def test_get_volume_list(self):
        """Test get_volume_list."""
        vol_list = self.provisioning.get_volume_list()
        ref_vol_list = [self.data.device_id, self.data.device_id2]
        self.assertEqual(ref_vol_list, vol_list)

    def test_get_vols_from_storagegroup(self):
        """Test get_vols_from_storagegroup."""
        vol_list = self.provisioning.get_vols_from_storagegroup(
            self.data.storagegroup_name)
        ref_vol_list = [self.data.device_id, self.data.device_id2]
        self.assertEqual(ref_vol_list, vol_list)

    def test_get_storagegroup_from_vol(self):
        """Test get_storagegroup_from_vol."""
        sg_list = self.provisioning.get_storagegroup_from_vol(
            self.data.device_id)
        self.assertEqual([self.data.storagegroup_name], sg_list)

    def test_is_volume_in_storagegroup(self):
        """Test is_volume_in_storagegroup."""
        is_vol = self.provisioning.is_volume_in_storagegroup(
            self.data.device_id, self.data.storagegroup_name)
        self.assertTrue(is_vol)
        is_vol2 = self.provisioning.is_volume_in_storagegroup(
            self.data.device_id, self.data.storagegroup_name_1)
        self.assertFalse(is_vol2)

    def test_find_volume_device_id_success(self):
        """Test find_volume_device_id."""
        with mock.patch.object(self.provisioning, 'get_volume_list',
                               return_value=['00001']):
            device_id = self.provisioning.find_volume_device_id('my-vol')
            self.assertEqual(self.data.device_id, device_id)

    def test_find_volume_device_id_failure(self):
        """Test find_volume_device_id volume not found."""
        with mock.patch.object(self.provisioning, 'get_volume_list',
                               return_value=list()):
            device_id2 = self.provisioning.find_volume_device_id('not-my-vol')
            self.assertIsNone(device_id2)

    def test_find_volume_identifier(self):
        """Test find_volume_identifier."""
        vol_id = self.provisioning.find_volume_identifier(self.data.device_id)
        self.assertEqual('my-vol', vol_id)

    def test_get_size_of_device_on_array(self):
        """Test get_size_of_device_on_array."""
        vol_size = self.provisioning.get_size_of_device_on_array(
            self.data.device_id)
        self.assertEqual(2, vol_size)
        with mock.patch.object(
                self.provisioning, 'get_volume', return_value={}):
            self.assertRaises(exception.ResourceNotFoundException,
                              self.provisioning.get_size_of_device_on_array,
                              self.data.device_id)

    def test_modify_volume(self):
        """Test _modify_volume."""
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning._modify_volume(self.data.device_id, {})
            mock_mod.assert_called_once()

    def test_extend_volume(self):
        """Test extend_volume."""
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.extend_volume(self.data.device_id, '3')
            mock_mod.assert_called_once()

    def test_rename_volume(self):
        """Test rename_volume."""
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.rename_volume(self.data.device_id, None)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()
            self.provisioning.rename_volume(self.data.device_id, 'new-name')
            mock_mod.assert_called_once()

    def test_deallocate_volume(self):
        """Test deallocate_volume."""
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.deallocate_volume(self.data.device_id)
            mock_mod.assert_called_once()

    def test_delete_volume(self):
        """Test delete_volume."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_volume(self.data.device_id)
            mock_delete.assert_called_once()

    def test_get_workload_settings(self):
        """Test get_workload_settings."""
        wl_setting = self.provisioning.get_workload_settings()
        self.assertEqual(self.data.workloadtype['workloadId'], wl_setting)


class PyU4VReplicationTest(testtools.TestCase):
    """Test replication."""

    def setUp(self):
        """Setup."""
        super(PyU4VReplicationTest, self).setUp()
        self.data = pcd.CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=pf.FakeRequestsSession())
        config_file = pf.FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn(array_id=self.data.array)
        self.common = self.conn.common
        self.provisioning = self.conn.provisioning
        self.replication = self.conn.replication

    def test_get_replication_info(self):
        """Test get_replication_info."""
        rep_info = self.replication.get_replication_info()
        self.assertEqual(self.data.rep_info, rep_info)

    def test_check_snap_capabilities(self):
        """Test get_array_replication_capabilities."""
        capabilities = self.replication.get_array_replication_capabilities()
        self.assertEqual(
            self.data.capabilities['symmetrixCapability'][1], capabilities)

    def test_is_snapvx_licensed(self):
        """Test is_snapvx_licensed."""
        is_licensed = self.replication.is_snapvx_licensed()
        self.assertTrue(is_licensed)

    def test_get_storage_group_rep(self):
        """Test get_storage_group_rep."""
        rep_details = self.replication.get_storage_group_rep(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_details_rep[0], rep_details)

    def test_get_storage_group_rep_list(self):
        """Test get_storage_group_rep_list."""
        rep_list = self.replication.get_storage_group_rep_list(
            has_snapshots=True)
        self.assertEqual(self.data.sg_list_rep['name'], rep_list)

    def test_get_storagegroup_snapshot_list(self):
        """Test get_storagegroup_snapshot_list."""
        snap_list = self.replication.get_storagegroup_snapshot_list(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_snap_list['name'], snap_list)

    def test_create_storagegroup_snap(self):
        """Test create_storagegroup_snap."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_storagegroup_snap(
                self.data.storagegroup_name, 'snap_name')
            self.replication.create_storagegroup_snap(
                self.data.storagegroup_name, 'snap_name', ttl=2, hours=True)
            self.assertEqual(2, mock_create.call_count)

    def test_get_storagegroup_snapshot_generation_list(self):
        """Test get_storagegroup_snapshot_generation_list."""
        gen_list = self.replication.get_storagegroup_snapshot_generation_list(
            self.data.storagegroup_name, 'snap_name')
        self.assertEqual(self.data.sg_snap_gen_list['generations'], gen_list)

    def test_get_snapshot_generation_details(self):
        """Test get_snapshot_generation_details."""
        snap_details = self.replication.get_snapshot_generation_details(
            self.data.storagegroup_name, self.data.group_snapshot_name, 0)
        self.assertEqual(self.data.group_snap_vx, snap_details)

    @mock.patch.object(replication.ReplicationFunctions,
                       'get_snapshot_generation_details',
                       return_value=pcd.CommonData.expired_snap)
    @mock.patch.object(replication.ReplicationFunctions,
                       'get_storagegroup_snapshot_generation_list',
                       return_value=pcd.CommonData.sg_snap_gen_list)
    def test_find_expired_snapvx_snapshots(self, mock_gen_list, mock_snap):
        """Test find_expired_snapvx_snapshots."""
        ref_expired_snap_list = [
            {'storagegroup_name': self.data.storagegroup_name,
             'snapshot_name': self.data.group_snapshot_name,
             'generation_number': 0,
             'expiration_time': self.data.expired_snap[
                 'timeToLiveExpiryDate'],
             'linked_sg_name': self.data.target_group_name,
             'snap_creation_time': self.data.expired_snap['timestamp']}]
        expired_snap_list = (
            self.replication.find_expired_snapvx_snapshots())
        self.assertEqual(ref_expired_snap_list, expired_snap_list)

    def test_modify_storagegroup_snap(self):
        """Test modify_storagegroup_snap."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.modify_storagegroup_snap(
                self.data.storagegroup_name,
                self.data.target_group_name, self.data.group_snapshot_name)
            mock_mod.assert_called_once()

    def test_restore_snapshot(self):
        """Test restore_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.restore_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name)
            mock_mod.assert_called_once()

    def test_rename_snapshot(self):
        """Test rename_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.rename_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                'new-snap-name')
            mock_mod.assert_called_once()

    def test_link_gen_snapshot(self):
        """Test link_gen_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.link_gen_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                self.data.target_group_name, _async=True)
            mock_mod.assert_called_once()

    def test_unlink_gen_snapshot(self):
        """Test unlink_gen_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.unlink_gen_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                self.data.target_group_name, _async=True)
            mock_mod.assert_called_once()

    def test_delete_storagegroup_snapshot(self):
        """Test delete_storagegroup_snapshot."""
        with mock.patch.object(
                self.replication, 'delete_resource') as mock_delete:
            self.replication.delete_storagegroup_snapshot(
                self.data.storagegroup_name, self.data.snapshot_name)
            resource = ('storagegroup/{sg}/snapshot/{'
                        'snap}/generation/0'.format(
                            sg=self.data.storagegroup_name,
                            snap=self.data.snapshot_name))

            mock_delete.assert_called_once_with(self.data.array,
                                                'replication', resource)

    def test_is_vol_in_rep_session(self):
        """Test is_vol_in_rep_session."""
        snap_tgt, snap_src, rdf_grp = self.replication.is_vol_in_rep_session(
            self.data.device_id)
        self.assertTrue(snap_src)

    def test_get_rdf_group(self):
        """Test get_rdf_group."""
        rdfg_details = self.replication.get_rdf_group(self.data.rdf_group_no)
        self.assertEqual(self.data.rdf_group_details, rdfg_details)

    def test_get_rdf_group_list(self):
        """Test get_rdf_group_list."""
        rdfg_list = self.replication.get_rdf_group_list()
        self.assertEqual(self.data.rdf_group_list['rdfGroupID'], rdfg_list)

    def test_get_rdf_group_volume(self):
        """Test get_rdf_group_volume."""
        rdfg_vol = self.replication.get_rdf_group_volume(
            self.data.rdf_group_no, self.data.device_id)
        self.assertEqual(self.data.rdf_group_vol_details, rdfg_vol)

    def test_get_rdf_group_volume_list(self):
        """Test get_rdf_group_volume_list."""
        rdfg_vol_list = self.replication.get_rdf_group_volume_list(
            self.data.rdf_group_no)
        self.assertEqual(self.data.rdf_group_vol_list['name'], rdfg_vol_list)

    def test_are_vols_rdf_paired(self):
        """Test are_vols_rdf_paired."""
        paired, _, _ = self.replication.are_vols_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id2, self.data.rdf_group_no)
        self.assertTrue(paired)
        paired2, _, _ = self.replication.are_vols_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id3, self.data.rdf_group_no)
        self.assertFalse(paired2)

    def test_get_rdf_group_number(self):
        """Test get_rdf_group_number."""
        rdfn = self.replication.get_rdf_group_number(self.data.rdf_group_name)
        self.assertEqual(self.data.rdf_group_no, rdfn)

    def test_get_storagegroup_srdfg_list(self):
        """Test get_storagegroup_srdfg_list."""
        rdfg_list = self.replication.get_storagegroup_srdfg_list(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_rdf_list['rdfgs'], rdfg_list)

    def test_get_storagegroup_srdf_details(self):
        """Test get_storagegroup_srdf_details."""
        sg_rdf_details = self.replication.get_storagegroup_srdf_details(
            self.data.storagegroup_name, self.data.rdf_group_no)
        self.assertEqual(self.data.sg_rdf_details[0], sg_rdf_details)

    def test_create_storagegroup_srdf_pairings(self):
        """Test create_storagegroup_srdf_pairings."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_storagegroup_srdf_pairings(
                self.data.storagegroup_name, self.data.remote_array, 'Active')
            mock_create.assert_called_once()
            mock_create.reset_mock()
            self.replication.create_storagegroup_srdf_pairings(
                self.data.storagegroup_name, self.data.remote_array, 'Active',
                True, True, self.data.rdf_group_no)
            mock_create.assert_called_once()

    def test_create_storagegroup_srdf_pairings_newrdfg(self):
        """Test create_storagegroup_srdf_pairings."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_storagegroup_srdf_pairings(
                self.data.storagegroup_name, self.data.remote_array, 'Active')
            mock_create.assert_called_once()
            mock_create.reset_mock()
            self.replication.create_storagegroup_srdf_pairings(
                self.data.storagegroup_name, self.data.remote_array, 'Active',
                True, True, self.data.rdf_group_no, True)
            mock_create.assert_called_once()

    def test_modify_storagegroup_srdf(self):
        """Test test_modify_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            # Lowercase action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'suspend', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()
            # Uppercase action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'SUSPEND', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()
            # Correct case action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'SetMode', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()
            # Mixed case action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'sEtBIAs', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()

        # Invalid action passed, exception raised
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.replication.modify_storagegroup_srdf,
                          self.data.storagegroup_name, 'None',
                          self.data.rdf_group_no,)

    def test_suspend_storagegroup_srdf(self):
        """Test suspend_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.suspend_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no,
                suspend_options={'consExempt': 'true'}, _async=True)
            mock_mod.assert_called_once()

    def test_establish_storagegroup_srdf(self):
        """Test establish_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.establish_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no,
                establish_options={'full': 'true'}, _async=True)
            mock_mod.assert_called_once()

    def test_failover_storagegroup_srdf(self):
        """Test failover_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.failover_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no)
            mock_mod.assert_called_once()

    def test_failback_storagegroup_srdf(self):
        """Test failback_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.failback_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no)
            mock_mod.assert_called_once()

    def test_delete_storagegroup_srdf(self):
        """Test delete_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'delete_resource') as mock_delete:
            self.replication.delete_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no)
            mock_delete.assert_called_once()


class PyU4VMigrationTest(testtools.TestCase):
    """Test migration."""

    def setUp(self):
        """Setup."""
        super(PyU4VMigrationTest, self).setUp()
        self.data = pcd.CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=pf.FakeRequestsSession())
        config_file = pf.FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn(array_id=self.data.array)
        self.common = self.conn.common
        self.migration = self.conn.migration

    def test_get_migration_info(self):
        """Test get_migration_info."""
        migration_info = self.migration.get_migration_info()
        self.assertEqual(self.data.migration_info, migration_info)

    def test_create_migration_environment(self):
        """Test create_migration_enviroment."""
        with mock.patch.object(
                self.migration, 'create_resource') as mock_create:
            self.migration.create_migration_environment(
                target_array_id=self.data.remote_array)
            self.assertEqual(1, mock_create.call_count)

    def test_delete_migration_environment(self):
        """Test delete_migration_environment."""
        with mock.patch.object(
                self.migration, 'delete_resource') as mock_delete:
            self.migration.delete_migration_environment(
                self.data.remote_array)
            mock_delete.assert_called_once()

    def test_get_array_migration_capabilities(self):
        """Test get_array_migration_capabilities."""
        capabilities = self.migration.get_array_migration_capabilities()
        capabilities_ref = (
            self.data.migration_capabilities['storageArrayCapability'][0])
        self.assertEqual(capabilities_ref, capabilities)

    def test_get_environment_list(self):
        """Test get_environment_list."""
        environment_list = self.migration.get_environment_list()
        env_list_ref = self.data.migration_environment_list['arrayId']
        self.assertEqual(env_list_ref, environment_list)

    def test_get_environment(self):
        """Test get_environment."""
        env_name = self.data.migration_environment_list['arrayId'][0]
        environment_details = self.migration.get_environment(env_name)
        env_details_ref = self.data.migration_environment_details
        self.assertEqual(env_details_ref, environment_details)

    def test_delete_environment(self):
        """Test delete_environment."""
        with mock.patch.object(
                self.migration, 'delete_resource') as mock_delete:
            env_name = self.data.migration_environment_list['arrayId'][0]
            self.migration.delete_environment(env_name)
            mock_delete.assert_called_once()

    def test_get_storage_group_list(self):
        """Test get_storage_group_list."""
        storage_group_list = self.migration.get_storage_group_list()
        sg_list_ref = self.data.sg_list_migration['name']
        self.assertEqual(sg_list_ref, storage_group_list)

    def test_get_storage_group(self):
        """Test get_storage_group."""
        sg_name_ref = self.data.sg_list_migration['name'][0]
        storage_group = self.migration.get_storage_group(sg_name_ref)
        self.assertEqual(self.data.sg_details_migration[0], storage_group)

    def test_create_storage_group_migration(self):
        """Test create_storage_group_migration."""
        with mock.patch.object(
                self.migration, 'create_resource') as mock_create:
            self.migration.create_storage_group_migration(
                self.data.storagegroup_name, self.data.remote_array)
            self.assertEqual(1, mock_create.call_count)

    def test_modify_storage_group_migration(self):
        """Test modify_storage_group_migration."""
        with mock.patch.object(self.migration, 'modify_resource') as mock_mod:
            self.migration.modify_storage_group_migration(
                self.data.storagegroup_name, 'Recover')
            mock_mod.assert_called_once()

    def test_delete_storage_group_migration(self):
        """Test delete_storage_group_migration."""
        with mock.patch.object(
                self.migration, 'delete_resource') as mock_delete:
            self.migration.delete_storage_group_migration(
                self.data.storagegroup_name)
            mock_delete.assert_called_once()


class PyU4VRestRequestsTest(testtools.TestCase):
    """Testing Unisphere REST requests."""

    def setUp(self):
        """Setup."""
        super(PyU4VRestRequestsTest, self).setUp()
        self.data = pcd.CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=pf.FakeRequestsSession())
        self.rest = rest_requests.RestRequests('smc', 'smc', False, 'base_url')

    def test_rest_request_exception(self):
        """Test rest_request."""
        sc, msg = self.rest.rest_request('/fake_url', 'TIMEOUT')
        self.assertIsNone(sc)
        self.assertIsNone(msg)
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.rest.rest_request, '', 'EXCEPTION')


class PyU4VUnivmaxConnTest(testtools.TestCase):
    """Test Unisphere connection."""

    def setUp(self):
        """Setup."""
        super(PyU4VUnivmaxConnTest, self).setUp()
        self.data = pcd.CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=pf.FakeRequestsSession())
        config_file = pf.FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn()

    @mock.patch.object(rest_requests.RestRequests, 'close_session')
    def test_close_session(self, mock_close):
        """Test close_session."""
        self.conn.close_session()
        mock_close.assert_called_once()

    def test_set_requests_timeout(self):
        """Testing set_requests_timeout."""
        self.conn.set_requests_timeout(300)
        self.assertEqual(300, self.conn.rest_client.timeout)

    def test_set_array_id(self):
        """Testing set_array_id."""
        self.conn.set_array_id('000123456789')
        self.assertEqual('000123456789', self.conn.replication.array_id)

    def test_load_config_settings_from_file(self):
        user, password = 'smc', 'smc'
        ip, port = '10.0.0.75', '8443'
        base_uri = ('https://{ip}:{port}/univmax/restapi'.format(ip=ip,
                                                                 port=port))
        array = pcd.CommonData.array

        self.assertEqual(array, self.conn.array_id)
        self.assertIsInstance(self.conn.rest_client,
                              rest_requests.RestRequests)
        self.assertEqual(user, self.conn.rest_client.username)
        self.assertEqual(password, self.conn.rest_client.password)
        self.assertFalse(self.conn.rest_client.verifySSL)
        self.assertEqual(base_uri, self.conn.rest_client.base_url)

    def test_load_no_settings_exception_thrown(self):
        with mock.patch.object(config_handler, 'set_logger_and_config',
                               return_value=None):
            univmax_conn.file_path = None
            self.assertRaises(exception.MissingConfigurationException,
                              univmax_conn.U4VConn, pcd.CommonData.array)
