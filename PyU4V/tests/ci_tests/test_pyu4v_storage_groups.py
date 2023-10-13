# Copyright (c) 2023 Dell Inc. or its subsidiaries.
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
"""test_pyu4v_ci_storage_groups.py."""
import testtools

from PyU4V.tests.ci_tests import base


class CITestStorageGroups(base.TestBaseTestCase, testtools.TestCase):

    def setUp(self):
        """SetUp."""
        super(CITestStorageGroups, self).setUp()
        self.storage_groups = self.conn.storage_groups

    def test_get_StorageGroups_meta_data(self):
        meta_data = self.storage_groups.get_storage_groups_meta_data()
        self.assertIn('name', meta_data[0])

    def test_get_StorageGroups_detail(self):
        sg_details = self.storage_groups.get_storage_groups_details()
        self.assertIn('id', sg_details['storage_groups'][0])
        self.assertIn('resource_type', sg_details['storage_groups'][0])
