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
"""test_pyu4v_conn.py."""

import testtools

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import config_handler
from PyU4V.utils import constants
from PyU4V.utils import exception


class PyU4VUnivmaxConnTest(testtools.TestCase):
    """Test Unisphere connection."""

    def setUp(self):
        """Setup."""
        super(PyU4VUnivmaxConnTest, self).setUp()
        self.data = pcd.CommonData()
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(
                username='smc', password='smc', server_ip='10.0.0.75',
                port='8443', verify=False, interval=5, retries=200,
                array_id=self.data.array, application_type='pyu4v')
            self.common = self.conn.common
            self.common.interval = 1
            self.common.retries = 1

    def test_close_session(self):
        """Test close_session closes both REST clients."""
        with mock.patch.object(
                self.conn.rest_client, 'close_session') as primary_close:
            with mock.patch.object(
                    self.conn.enhanced_rest_client,
                    'close_session') as enhanced_close:
                self.conn.close_session()
        primary_close.assert_called_once()
        enhanced_close.assert_called_once()

    def test_set_requests_timeout(self):
        """Testing set_requests_timeout."""
        self.conn.set_requests_timeout(300)
        self.assertEqual(300, self.conn.rest_client.timeout)
        self.assertEqual(300, self.conn.enhanced_rest_client.timeout)

    def test_set_array_id(self):
        """Testing set_array_id reaches every array-scoped component."""
        array_id = '000123456789'
        self.conn.set_array_id(array_id)

        root_components = (
            self.conn.clone, self.conn.provisioning, self.conn.performance,
            self.conn.replication, self.conn.snapshot, self.conn.srdf,
            self.conn.metro_dr, self.conn.migration, self.conn.wlp,
            self.conn.snapshot_policy, self.conn.system,
            self.conn.serviceability, self.conn.performance_enhanced,
            self.conn.volumes, self.conn.storage_groups,
            self.conn.enhanced_api, self.conn.settings,
        )
        nested_components = (
            self.conn.clone.provisioning,
            self.conn.performance.real_time,
            self.conn.replication.provisioning,
            self.conn.replication._snapshot,
            self.conn.replication._srdf,
            self.conn.snapshot.provisioning,
            self.conn.srdf.provisioning,
            self.conn.metro_dr.provisioning,
        )

        self.assertEqual(array_id, self.conn.array_id)
        for component in root_components + nested_components:
            self.assertEqual(array_id, component.array_id)

    def test_set_array_id_propagates_to_replication_delegates(self):
        """set_array_id must reach the snapshot/srdf instances that the
        deprecated conn.replication.* calls delegate to."""
        self.conn.set_array_id('000123456789')
        self.assertEqual(
            '000123456789', self.conn.replication._snapshot.array_id)
        self.assertEqual(
            '000123456789', self.conn.replication._srdf.array_id)
        # The shared instances must be identical objects, not copies.
        self.assertIs(self.conn.snapshot, self.conn.replication._snapshot)
        self.assertIs(self.conn.srdf, self.conn.replication._srdf)

    @mock.patch.object(univmax_conn.U4VConn, 'validate_unisphere')
    @mock.patch.object(rest_requests.RestRequests, 'establish_rest_session',
                       return_value=pf.FakeRequestsSession())
    def test_api_key_authentication_configures_both_clients(
            self, mock_session, mock_validate):
        """An explicit API key must be used by both REST clients."""
        conn = univmax_conn.U4VConn(
            server_ip='10.0.0.75', port='8443',
            array_id=self.data.array, api_key='test-token')

        for client in (conn.rest_client, conn.enhanced_rest_client):
            self.assertEqual('test-token', client.token)
            self.assertEqual(
                'Bearer test-token', client.headers['Authorization'])
            self.assertIsNone(client.username)
            self.assertIsNone(client.password)
        self.assertEqual(2, mock_session.call_count)
        mock_validate.assert_called_once()

    def test_set_u4v_version_propagates_to_all_modules(self):
        """set_u4v_version must propagate live to every feature module."""
        self.conn.set_u4v_version('100')
        for comp in (
                self.conn.common, self.conn.snapshot.common,
                self.conn.srdf.common, self.conn.provisioning.common,
                self.conn.system.common, self.conn.settings.common,
                self.conn.serviceability.common, self.conn.replication.common,
                self.conn.replication._snapshot.common,
                self.conn.replication._srdf.common,
                self.conn.volumes.common, self.conn.storage_groups.common):
            self.assertEqual('100', comp.UNI_VERSION)
        # Per-module version properties resolve from the same source.
        self.assertEqual('100', self.conn.provisioning.version)
        self.assertEqual('100', self.conn.system.version)
        self.assertEqual('100', self.conn.settings.version)
        self.assertEqual('100', self.conn.serviceability.version)
        self.assertEqual('100', self.conn.replication.version)

    def test_set_u4v_version_reset_falls_back_to_default(self):
        """Resetting the version falls back to the packaged default."""
        self.conn.set_u4v_version('100')
        self.conn.set_u4v_version(None)
        self.assertEqual(
            constants.UNISPHERE_VERSION, self.conn.common.UNI_VERSION)
        self.assertEqual(
            constants.UNISPHERE_VERSION, self.conn.snapshot.common.UNI_VERSION)

    def test_validate_unisphere_failed_check(self):
        """Test Unisphere version validation fail scenario."""
        with mock.patch.object(self.common, 'get_uni_version',
                               return_value=('v9.0.0', '90')):
            self.assertRaises(SystemExit, self.conn.validate_unisphere)


class PyU4VUnivmaxConnTestConfigFile(testtools.TestCase):

    @mock.patch.object(univmax_conn.U4VConn, 'validate_unisphere')
    @mock.patch.object(rest_requests.RestRequests, 'establish_rest_session',
                       return_value=pf.FakeRequestsSession())
    def test_api_key_overrides_config_basic_credentials(
            self, mock_session, mock_validate):
        """Config credentials must not replace an explicit API key."""
        config_file, config_dir = pf.FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        try:
            conn = univmax_conn.U4VConn(
                array_id=pcd.CommonData.array, api_key='test-token')
            for client in (conn.rest_client, conn.enhanced_rest_client):
                self.assertEqual('test-token', client.token)
                self.assertIsNone(client.username)
                self.assertIsNone(client.password)
            self.assertEqual(2, mock_session.call_count)
            mock_validate.assert_called_once()
        finally:
            pf.FakeConfigFile.delete_fake_config_file(
                config_file, config_dir)

    def test_init_config_file_all_settings(self):
        """Test initialisation of U4VConn using all required settings."""
        config_file, config_dir = pf.FakeConfigFile.create_fake_config_file(
            verify=True)
        univmax_conn.file_path = config_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            conn = univmax_conn.U4VConn()
            self.assertEqual(pcd.CommonData.array, conn.array_id)
            self.assertIsInstance(conn.rest_client,
                                  rest_requests.RestRequests)
            self.assertEqual('smc', conn.rest_client.username)
            self.assertEqual('smc', conn.rest_client.password)
            self.assertTrue(conn.rest_client.verify_ssl)
            self.assertEqual('https://10.0.0.75:8443/univmax/restapi',
                             conn.rest_client.base_url)
            self.assertEqual(pcd.CommonData.remote_array, conn.remote_array)
            pf.FakeConfigFile.delete_fake_config_file(config_file, config_dir)

    def test_init_config_file_no_array_set(self):
        """Test initialisation of U4VConn with no array set."""
        config_file, config_dir = pf.FakeConfigFile.create_fake_config_file(
            array=None)
        univmax_conn.file_path = config_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            conn = univmax_conn.U4VConn()
            self.assertIsNone(conn.array_id)
            pf.FakeConfigFile.delete_fake_config_file(config_file, config_dir)

    def test_init_config_verify_exception(self):
        """Test initialisation of U4VConn with SSL verification set."""
        config_file, config_dir = pf.FakeConfigFile.create_fake_config_file(
            verify_key=False)
        univmax_conn.file_path = config_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            conn = univmax_conn.U4VConn()
            self.assertTrue(conn.rest_client.verify_ssl)
            pf.FakeConfigFile.delete_fake_config_file(config_file, config_dir)

    def test_init_config_missing_data_exception(self):
        """Test initialisation of U4VConn with missing data."""
        with mock.patch.object(config_handler, 'set_logger_and_config',
                               return_value=None):
            self.assertRaises(exception.MissingConfigurationException,
                              univmax_conn.U4VConn, pcd.CommonData.array)

    def test_init_config_file_no_remote_array_set(self):
        """Test initialisation of U4VConn with no remote array set."""
        config_file, config_dir = pf.FakeConfigFile.create_fake_config_file(
            remote_array=None)
        univmax_conn.file_path = config_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            conn = univmax_conn.U4VConn()
            self.assertIsNone(conn.remote_array)
            pf.FakeConfigFile.delete_fake_config_file(config_file, config_dir)
