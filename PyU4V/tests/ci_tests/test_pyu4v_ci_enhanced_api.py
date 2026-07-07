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

from PyU4V.tests.ci_tests import base


class CITestEnhancedApi(base.TestBaseTestCase, testtools.TestCase):

    def setUp(self):
        """SetUp."""
        super(CITestEnhancedApi, self).setUp()
        self.enhanced_api = self.conn.enhanced_api

    def test_get_fpin_meta_data(self):
        """Verify FPIN metadata endpoint returns attribute descriptors."""
        metadata = self.enhanced_api.get_storage_object_meta_data(
            storage_object='fpins')
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, list)
        if metadata:
            self.assertIn('name', metadata[0])

    def test_get_fpin_details(self):
        """Verify FPIN bulk details call succeeds.

        FPINs may or may not exist depending on whether the array has
        generated fabric events. The call itself must succeed.
        """
        result = self.enhanced_api.get_storage_object_details(
            storage_object='fpins')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_fpin_details_link_integrity_filter(self):
        """Verify FPIN details filtered to Link_Integrity type."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='fpins',
            filters=['type eq Link_Integrity'])
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_fpin_details_delivery_filter(self):
        """Verify FPIN details filtered to Delivery type."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='fpins',
            filters=['type eq Delivery'])
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_fpin_details_multi_type_filter(self):
        """Verify FPIN details with in-operator covering multiple types."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='fpins',
            filters=['type in (Delivery;Congestion)'])
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_fpin_details_with_select(self):
        """Verify FPIN details can restrict returned attributes via select."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='fpins',
            select=['id', 'type'])
        if result is not None:
            self.assertIsInstance(result, (dict, list))
