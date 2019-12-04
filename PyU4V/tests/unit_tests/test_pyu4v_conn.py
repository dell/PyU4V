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
"""test_pyu4v_conn.py."""

import mock
import testtools

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import config_handler
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
        self.assertEqual('000123456789', self.conn.performance.array_id)
        self.assertEqual('000123456789', self.conn.provisioning.array_id)
        self.assertEqual('000123456789', self.conn.replication.array_id)
        self.assertEqual('000123456789', self.conn.migration.array_id)
        self.assertEqual('000123456789', self.conn.wlp.array_id)

    def test_validate_unisphere_failed_check(self):
        """Test Unisphere version validation fail scenario."""
        with mock.patch.object(self.common, 'get_uni_version',
                               return_value=('v9.0.0', '90')):
            self.assertRaises(SystemExit, self.conn.validate_unisphere)


class PyU4VUnivmaxConnTestConfigFile(testtools.TestCase):

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
