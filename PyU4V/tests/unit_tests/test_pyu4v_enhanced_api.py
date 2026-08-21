# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
"""test_pyu4v_ci_enhanced_api.py."""


import testtools

from unittest import mock
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import exception


class PyU4VEnhancedApiTest(testtools.TestCase):

    def setUp(self):
        """SetUp."""
        super(PyU4VEnhancedApiTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.enhanced_api = self.conn.enhanced_api
            self.common = univmax_conn.CommonFunctions

    def tearDown(self):
        """tearDown."""
        super(PyU4VEnhancedApiTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_storage_object_detail(self):
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.enhanced_api.get_storage_object_details(
                storage_object='volumes')
        mock_get.assert_called()

    def test_get_storage_object_details_default_exclusions(self):
        """Default selection excludes expensive nested attributes."""
        metadata = [
            {'name': 'id'}, {'name': 'snapshots'},
            {'name': 'rdf_infos'}, {'name': 'identifier'}]
        with mock.patch.object(
                self.enhanced_api, 'get_storage_object_meta_data',
                return_value=metadata), mock.patch.object(
                    self.common, 'get_request') as mock_get:
            self.enhanced_api.get_storage_object_details('volumes')

        mock_get.assert_called_once_with(
            target_uri=f"/{self.enhanced_api.enhanced_api_version}/systems/"
                       f"{self.data.array}/volumes?select=id,identifier",
            resource_type=None)

    def test_get_storage_object_details_empty_exclusions(self):
        """An empty exclusion list explicitly includes every attribute."""
        metadata = [
            {'name': 'id'}, {'name': 'snapshots'}, {'name': 'rdf_infos'}]
        with mock.patch.object(
                self.enhanced_api, 'get_storage_object_meta_data',
                return_value=metadata), mock.patch.object(
                    self.common, 'get_request') as mock_get:
            self.enhanced_api.get_storage_object_details(
                'volumes', exclude=[])

        mock_get.assert_called_once_with(
            target_uri=f"/{self.enhanced_api.enhanced_api_version}/systems/"
                       f"{self.data.array}/volumes"
                       f"?select=id,snapshots,rdf_infos",
            resource_type=None)

    def test_get_storage_object_details_preserves_explicit_selection(self):
        """Explicit selection bypasses metadata and is not modified."""
        selected = ['id', 'snapshots.name']
        with mock.patch.object(
                self.enhanced_api,
                'get_storage_object_meta_data') as metadata:
            with mock.patch.object(
                    self.common, 'get_request') as mock_get:
                self.enhanced_api.get_storage_object_details(
                    'volumes', filters=['id eq 00001'], select=selected)

        metadata.assert_not_called()
        self.assertEqual(['id', 'snapshots.name'], selected)
        mock_get.assert_called_once_with(
            target_uri=f"/{self.enhanced_api.enhanced_api_version}/systems/"
                       f"{self.data.array}/volumes"
                       f"?select=id,snapshots.name&filter=id eq 00001",
            resource_type=None)

    def test_get_storage_object_details_force_refresh_false(self):
        """An explicit false value preserves the existing request URI."""
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.enhanced_api.get_storage_object_details(
                storage_object='volumes', select=['id'],
                force_refresh=False)

        mock_get.assert_called_once_with(
            target_uri=f"/{self.enhanced_api.enhanced_api_version}/systems/"
                       f"{self.data.array}/volumes?select=id",
            resource_type=None)

    def test_get_storage_object_details_force_refresh_true(self):
        """A true value adds force_refresh after the existing query."""
        with mock.patch.object(
                self.common, 'get_request') as mock_get:
            self.enhanced_api.get_storage_object_details(
                storage_object='volumes', select=['id'],
                filters=['id eq 00001'], force_refresh=True)

        mock_get.assert_called_once_with(
            target_uri=f"/{self.enhanced_api.enhanced_api_version}/systems/"
                       f"{self.data.array}/volumes"
                       f"?select=id&filter=id eq 00001&force_refresh=true",
            resource_type=None)

    def test_get_storage_object_details_force_refresh_rate_limit(self):
        """HTTP 429 details propagate through the existing exception."""
        response = {'retry_after_ms': 328}
        with mock.patch.object(
                self.enhanced_api.common, 'request',
                return_value=(response, 429)) as mock_request:
            error = self.assertRaises(
                exception.VolumeBackendAPIException,
                self.enhanced_api.get_storage_object_details,
                storage_object='volumes', select=['id'],
                force_refresh=True)

        self.assertIn('retry_after_ms', str(error))
        self.assertIn('328', str(error))
        mock_request.assert_called_once()

    def test_get_storage_object_details_fpins(self):
        with mock.patch.object(
                self.common, 'get_request',
                return_value={}) as mock_get:
            self.enhanced_api.get_storage_object_details(
                storage_object='fpins')
        self.assertEqual(mock_get.call_count, 1)
        details_call = mock_get.call_args_list[0]
        target_uri = details_call[1].get(
            'target_uri', details_call[0][0] if details_call[0] else '')
        self.assertIn('fpins', target_uri)

    def test_get_storage_object_details_fpins_link_integrity_filter(self):
        fpin_metadata = [{'name': 'id'}, {'name': 'type'}]
        with mock.patch.object(
                self.common, 'get_request',
                side_effect=[fpin_metadata, {}]) as mock_get:
            self.enhanced_api.get_storage_object_details(
                storage_object='fpins',
                filters=['type eq Link_Integrity'])
        details_call = mock_get.call_args_list[-1]
        target_uri = details_call[1].get(
            'target_uri', details_call[0][0] if details_call[0] else '')
        self.assertIn('fpins', target_uri)
        self.assertIn('Link_Integrity', target_uri)

    def test_get_storage_object_details_fpins_multi_type_filter(self):
        fpin_metadata = [{'name': 'id'}, {'name': 'type'}]
        with mock.patch.object(
                self.common, 'get_request',
                side_effect=[fpin_metadata, {}]) as mock_get:
            self.enhanced_api.get_storage_object_details(
                storage_object='fpins',
                filters=['type in (Delivery;Congestion)'])
        details_call = mock_get.call_args_list[-1]
        target_uri = details_call[1].get(
            'target_uri', details_call[0][0] if details_call[0] else '')
        self.assertIn('fpins', target_uri)
        self.assertIn('Delivery', target_uri)
        self.assertIn('Congestion', target_uri)
