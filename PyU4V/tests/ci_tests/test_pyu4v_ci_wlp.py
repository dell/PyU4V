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
"""test_pyu4v_ci_wlp.py."""
import testtools

from PyU4V.tests.ci_tests import base
from PyU4V.utils import exception


class CITestWLP(base.TestBaseTestCase, testtools.TestCase):
    """Test WLP."""

    def setUp(self):
        """setUp."""
        super(CITestWLP, self).setUp()
        self.is_v4 = self.common.is_array_v4(self.conn.array_id)

    def test_get_wlp_capabilities(self):
        """Test get_wlp_information."""
        array_id = self.conn.array_id
        wlp_capabilities = self.conn.wlp.get_wlp_information(array_id)
        self.assertEqual(array_id, wlp_capabilities.get('symmetrixId'))
        assert 'lastProcessed' in wlp_capabilities
        assert 'nextUpdate' in wlp_capabilities

    def test_get_headroom_info_array(self):
        """Test get_headroom array details."""
        self.skipTest(reason="not supported in 10.1")
        headroom_stats = self.conn.wlp.get_headroom(self.conn.array_id)
        self.assertTrue(headroom_stats)
        for stats in headroom_stats:
            assert 'srpId' in stats
            assert 'emulation' in stats
            assert 'capacity' in stats

    def test_get_headroom_info_srp(self):
        """Test get_headroom SRP details."""
        self.skipTest(reason="Not supported in 10.1")
        srp_headroom_stats = self.conn.wlp.get_headroom(self.conn.array_id,
                                                        srp='SRP_1')
        for stats in srp_headroom_stats:
            self.assertTrue(stats)
            self.assertEqual('SRP_1', stats.get('srpId'))
            if not self.is_v4:
                assert 'serviceLevelId' in stats
            assert 'emulation' in stats
            assert 'capacity' in stats

    def test_get_headroom_info_service_level(self):
        """Test get_headroom Service Level details."""
        if self.is_v4:
            self.skipTest(
                'Service level headroom is not supported by V4 arrays.')
        sl_headroom_stats = self.conn.wlp.get_headroom(
            self.conn.array_id, srp='SRP_1', slo='Diamond')
        for stats in sl_headroom_stats:
            self.assertTrue(stats)
            self.assertEqual('SRP_1', stats.get('srpId'))
            self.assertEqual('Diamond', stats.get('serviceLevelId'))
            assert 'emulation' in stats
            assert 'capacity' in stats

    def test_get_headroom_info_workload_exception(self):
        """Test get_headroom PowerMax Workload exception."""
        if self.is_v4:
            self.skipTest(
                'Workload headroom is not supported by V4 arrays.')
        self.assertRaises(
            exception.ResourceNotFoundException,
            self.conn.wlp.get_headroom, self.conn.array_id, srp='SRP_1',
            slo='Diamond', workload='OLTP')

    def test_get_capabilities_no_array_set(self):
        """Test get_capabilities, no array set all local arrays returned."""
        response = self.conn.wlp.get_capabilities()
        self.assertTrue(response)
        self.assertIsInstance(response, list)

    def test_get_capabilities_array_set(self):
        """Test get_capabilities, array set only one array returned."""
        response = self.conn.wlp.get_capabilities(array_id=self.conn.array_id)
        self.assertTrue(response)
        self.assertIsInstance(response, list)
        self.assertEqual(1, len(response))
        self.assertEqual(self.conn.array_id, response[0].get('symmetrixId'))
