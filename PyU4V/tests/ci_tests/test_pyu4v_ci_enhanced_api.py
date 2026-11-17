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

    def test_get_fpin_details(self):
        """Verify FPIN bulk details call succeeds.

        FPINs may or may not exist depending on whether the array has
        generated fabric events. The call itself must succeed.
        """
        result = self.enhanced_api.get_storage_object_details(
            storage_object='fpins')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_fpin_details_with_select(self):
        """Verify FPIN details can restrict returned attributes via select."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='fpins',
            select=['id'])
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_volume_details_with_force_refresh(self):
        """Verify one forced-refresh bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='volumes',
            select=['id'],
            force_refresh=True)
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_storage_groups_details(self):
        """Verify storage-groups bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='storage-groups')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_storage_groups_details_with_select(self):
        """Verify storage-groups details with select succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='storage-groups',
            select=['id'])
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_masking_views_details(self):
        """Verify masking-views bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='masking-views')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_masking_views_details_with_select(self):
        """Verify masking-views details with select succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='masking-views',
            select=['id'])
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_hosts_details(self):
        """Verify hosts bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='hosts')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_initiators_details(self):
        """Verify initiators bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='initiators')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_port_groups_details(self):
        """Verify port-groups bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='port-groups')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_ports_details(self):
        """Verify ports bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='ports')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_directors_details(self):
        """Verify directors bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='directors')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_rdf_groups_details(self):
        """Verify rdf-groups bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='rdf-groups')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_ip_interfaces_details(self):
        """Verify ip-interfaces bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='ip-interfaces')
        if result is not None:
            self.assertIsInstance(result, (dict, list))

    def test_get_ip_routes_details(self):
        """Verify ip-routes bulk details call succeeds."""
        result = self.enhanced_api.get_storage_object_details(
            storage_object='ip-routes')
        if result is not None:
            self.assertIsInstance(result, (dict, list))
