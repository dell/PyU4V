# Copyright (c) 2022 Dell Inc. or its subsidiaries.
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
"""test_pyu4v_ci_clone.py.py."""
import testtools

from PyU4V.tests.ci_tests import base

class CITestClone(base.TestBaseTestCase, testtools.TestCase):
    """Test clone Functions."""


    def setUp(self):
        """SetUp."""
        super(CITestClone, self).setUp()
        self.provisioning = self.conn.provisioning
        self.clone = self.conn.clone

    def test_get_clone_target_storage_group_list(self):
        """test_get_clone_target_storage_group_list. """

        storage_group_name, target_storage_group_name = self.create_clone()
        target_storage_group_list = (
            self.clone.get_clone_target_storage_group_list(
                storage_group_id=storage_group_name
            ))
        self.assertEquals(target_storage_group_name,
                          target_storage_group_list[0])

    def test_get_clone_pairs_list(self):
        """test_get_clone_pairs_list. """

        storage_group_name, target_storage_group_name = self.create_clone()
        clone_pairs_list = (
            self.clone.get_clone_pairs_list(
                storage_group_id=storage_group_name))
        self.assertIn('clone_count', clone_pairs_list)
        self.assertIn('clones', clone_pairs_list)
        self.assertEqual(1, clone_pairs_list.get('clone_count'))

    def test_get_clone_storage_group_pair_details(self):
        storage_group_name, target_storage_group_name = self.create_clone()
        storage_group_pairs_details = (
            self.clone.get_clone_storage_group_pair_details(
                storage_group_id=storage_group_name,
                target_storage_group_id=target_storage_group_name))
        self.assertEquals(storage_group_name, storage_group_pairs_details.get(
            'storage_group'))
        self.assertEquals(target_storage_group_name,
                     storage_group_pairs_details.get(
                         'target_storage_group'))

    def test_create_clone(self):
        storage_group_name, target_storage_group_name = self.create_clone()
        clone_pairs_list = (
            self.clone.get_clone_pairs_list(
                storage_group_id=storage_group_name))
        self.assertEqual(1, clone_pairs_list.get('clone_count'))


    def test_terminate_clone(self):
        storage_group_name, target_storage_group_name = self.create_clone()
        clone_pairs_list = (
            self.clone.get_clone_pairs_list(
                storage_group_id=storage_group_name))
        self.assertEqual(1, clone_pairs_list.get('clone_count'))
        self.clone.terminate_clone(
            storage_group_id=storage_group_name,
            target_storage_group_id=target_storage_group_name)
        clone_pairs_list_after_terminate = (
            self.clone.get_clone_pairs_list(
                storage_group_id=storage_group_name))
        self.assertEqual(
            0, clone_pairs_list_after_terminate.get('clone_count'))
        self.clone.create_clone(
            storage_group_id=storage_group_name,
            target_storage_group_id=target_storage_group_name)

    def test_establish_clone(self):
        storage_group_name, target_storage_group_name = self.create_clone()
        self.clone.establish_clone(
            storage_group_id=storage_group_name,
            target_storage_group_id=target_storage_group_name)
        pair_details = (
            self.clone.get_clone_storage_group_pair_details(
                storage_group_id=storage_group_name,
                target_storage_group_id=target_storage_group_name))
        self.assertEquals('Copied', pair_details.get('state')[0])

    def test_restore_and_split_clone(self):
        storage_group_name, target_storage_group_name = self.create_clone()
        self.clone.restore_clone(
            storage_group_id=storage_group_name,
            target_storage_group_id=target_storage_group_name
        )
        pair_details = (
            self.clone.get_clone_storage_group_pair_details(
                storage_group_id=storage_group_name,
                target_storage_group_id=target_storage_group_name))
        self.assertEquals('Restored', pair_details.get('state')[0])
        self.clone.split_clone(
            storage_group_id=storage_group_name,
            target_storage_group_id=target_storage_group_name
        )
        pair_details = (
            self.clone.get_clone_storage_group_pair_details(
                storage_group_id=storage_group_name,
                target_storage_group_id=target_storage_group_name))
        self.assertEquals('Split', pair_details.get('state')[0])
