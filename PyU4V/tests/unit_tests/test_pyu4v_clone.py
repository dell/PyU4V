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
"""test_pyu4v_clone.py."""

import testtools

from unittest import mock

from PyU4V import common
from PyU4V import clone
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import exception


class PyU4VcloneTest(testtools.TestCase):
    """Test clone functions."""

    def setUp(self):
        """Setup."""
        super(PyU4VcloneTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.provisioning = self.conn.provisioning
            self.clone = self.conn.clone

    def tearDown(self):
        """tearDown."""
        super(PyU4VcloneTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_clone_target_storage_group_list(self):

    def test_get_clone_pairs_list(self):


        def test_get_clone_storage_group_pair_details(self):

        def test_create_clone(self):

        def test_terminate_clone(self):

        def test_establish_clone(self):

        def test_split_clone(self):

        def test_restore_clone(self):

        def test_set_clone_copy_mode(self):

        def test_clone_pairs_list(self):
