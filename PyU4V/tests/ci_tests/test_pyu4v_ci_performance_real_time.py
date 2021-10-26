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
"""test_pyu4v_ci_performance_real_time.py."""

import random
import testtools
import time

from PyU4V.tests.ci_tests import base
from PyU4V.tests.unit_tests import pyu4v_performance_data as pd
from PyU4V.utils import exception
from PyU4V.utils import performance_category_map
from PyU4V.utils import performance_constants as pc

CATEGORY_MAP = performance_category_map.performance_data


class CITestRealTimePerformance(base.TestBaseTestCase, testtools.TestCase):
    """Test Performance REST calls."""

    def setUp(self):
        """setUp."""
        super(CITestRealTimePerformance, self).setUp()
        self.perf = self.conn.performance
        self.rt = self.perf.real_time
        self.p_data = pd.PerformanceData()
        self.time_now = int(time.time() * 1000)
        if not self.perf.is_array_real_time_performance_registered(
                self.conn.array_id):
            self.skipTest(
                'Array {arr} is not diagnostic performance registered, '
                'skipping performance tests.'.format(arr=self.conn.array_id))

    def test_set_array_id(self):
        """Test set_array_id."""
        array_id = self.p_data.remote_array
        self.rt.set_array_id(array_id)
        self.assertEqual(self.rt.array_id, array_id)

    def test_set_recency(self):
        """Test set_recency."""
        recency = 9
        self.rt.set_recency(recency)
        self.assertEqual(self.rt.recency, recency)

    def test_is_timestamp_current_true(self):
        """Test is_timestamp_current true condition."""
        two_mins_ago = self.time_now - (pc.ONE_MINUTE * 1)
        self.rt.recency = 2
        self.assertTrue(self.rt.is_timestamp_current(timestamp=two_mins_ago))

    def test_is_timestamp_current_false(self):
        """Test is_timestamp_current false condition."""
        ten_mins_ago = self.time_now - (pc.ONE_MINUTE * 10)
        self.rt.recency = 20
        self.assertFalse(self.rt.is_timestamp_current(timestamp=ten_mins_ago,
                                                      minutes=9))

    def test_get_categories(self):
        """Test get_categories."""
        rt_cats = self.rt.get_categories()
        self.assertTrue(rt_cats)
        self.assertIsInstance(rt_cats, list)

    def test_get_category_metrics(self):
        """Test get_category_metrics."""
        rt_cats = self.rt.get_categories()
        for cat in rt_cats:
            metrics = self.rt.get_category_metrics(cat)
            self.assertTrue(metrics)
            self.assertIsInstance(metrics, list)

    def test_get_timestamps(self):
        """Test get_timestamps."""
        timestamps = self.rt.get_timestamps()
        for array in timestamps:
            self.assertTrue(array)
            self.assertIsInstance(array, dict)
            self.assertIn(pc.SYMM_ID, array.keys())
            self.assertIn(pc.FA_DATE, array.keys())
            self.assertIn(pc.LA_DATE, array.keys())
            self.assertIsInstance(array.get(pc.FA_DATE), int)
            self.assertIsInstance(array.get(pc.LA_DATE), int)

    def test_get_timestamps_array_id_set(self):
        """Test get_timestamps with array id set."""
        timestamps = self.rt.get_timestamps(array_id=self.rt.array_id)
        self.assertEqual(1, len(timestamps))
        array = timestamps[0]
        self.assertTrue(array)
        self.assertIsInstance(array, dict)
        self.assertIn(pc.SYMM_ID, array.keys())
        self.assertIn(pc.FA_DATE, array.keys())
        self.assertIn(pc.LA_DATE, array.keys())
        self.assertIsInstance(array.get(pc.FA_DATE), int)
        self.assertIsInstance(array.get(pc.LA_DATE), int)

    def test_get_category_keys(self):
        """Test get_category_keys."""
        rt_cats = self.rt.get_categories()
        for cat in rt_cats:
            rt_keys = self.rt.get_category_keys(cat)
            self.assertIsInstance(rt_keys, list)
            if rt_keys:
                self.assertIsInstance(rt_keys[0], str)

    def test_validate_real_time_input_all_valid(self):
        """Test _validate_real_time_input."""
        fe_keys = self.rt.get_frontend_director_keys()
        start = self.time_now - pc.ONE_MINUTE
        self.rt.recency = 1
        self.assertTrue(fe_keys)

        self.rt._validate_real_time_input(
            start_date=start, end_date=self.time_now, category=pc.FE_DIR,
            metrics=[pc.All_CAP], instance_id=fe_keys[0])

    def test_validate_real_time_input_invalid_category(self):
        """Test _validate_real_time_input invalid category input."""
        start = self.time_now - pc.ONE_MINUTE
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now, category='fake',
            metrics=[pc.All_CAP], instance_id=None)

    def test_validate_real_time_input_invalid_metric(self):
        """Test _validate_real_time_input invalid metric input."""
        start = self.time_now - pc.ONE_MINUTE
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now, category=pc.ARRAY,
            metrics=['fake_metric'], instance_id=None)

    def test_validate_real_time_input_missing_instance_id(self):
        """Test _validate_real_time_input missing instance id."""
        start = self.time_now - pc.ONE_MINUTE
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now, category=pc.FE_DIR,
            metrics=[pc.All_CAP], instance_id=None)

    def test_validate_real_time_input_bad_instance_id(self):
        """Test _validate_real_time_input bad instance id."""
        start = self.time_now - pc.ONE_MINUTE
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now, category=pc.ARRAY,
            metrics=[pc.All_CAP], instance_id='fake_array')

    def test_validate_real_time_input_wrong_timestamp_type(self):
        """Test _validate_real_time_input wrong timestamp type."""
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=111.111, end_date=111.111, category=pc.ARRAY,
            metrics=[pc.All_CAP], instance_id=None)

    def test_validate_real_time_input_delta_too_short(self):
        """Test _validate_real_time_input delta too short."""
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=self.time_now, end_date=self.time_now,
            category=pc.ARRAY, metrics=[pc.All_CAP], instance_id=None)

    def test_validate_real_time_input_delta_too_long(self):
        """Test _validate_real_time_input delta too long."""
        start = self.time_now - (pc.ONE_HOUR + pc.ONE_MINUTE)
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now, category=pc.ARRAY,
            metrics=[pc.All_CAP], instance_id=None)

    def test_validate_real_time_input_timestamp_not_recent(self):
        """Test _validate_real_time_input timestamp not recent."""
        end = self.time_now - (pc.ONE_MINUTE * 10)
        start = end - pc.ONE_MINUTE
        self.rt.recency = 1
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=end, category=pc.ARRAY,
            metrics=[pc.All_CAP], instance_id=None)

    def test_format_metrics(self):
        """Test format_metrics success."""
        test_metrics = 'all'
        formatted_metrics = self.rt.format_metrics(test_metrics)
        self.assertIsInstance(formatted_metrics, list)
        self.assertEqual([pc.All_CAP], formatted_metrics)

        test_metrics = ['metric_a', 'metric_b']
        formatted_metrics = self.rt.format_metrics(test_metrics)
        self.assertIsInstance(formatted_metrics, list)
        self.assertEqual(['metric_a', 'metric_b'], formatted_metrics)

    def test_format_metrics_exception(self):
        """Test format_metrics exception invalid input type."""
        self.assertRaises(exception.InvalidInputException,
                          self.rt.format_metrics, dict())

    def test_get_performance_data(self):
        """Test get_performance_data."""
        start = self.time_now - pc.ONE_MINUTE
        rt_data = self.rt.get_performance_data(
            start_date=start, end_date=self.time_now,
            category=pc.ARRAY, metrics=pc.All_CAP)

        self.assertTrue(rt_data)
        self.assertIsInstance(rt_data, dict)

        self.assertIn(pc.ARRAY_ID, rt_data.keys())
        self.assertEqual(self.rt.array_id, rt_data.get(pc.ARRAY_ID))

        self.assertIn(pc.START_DATE_SN, rt_data.keys())
        self.assertEqual(start, rt_data.get(pc.START_DATE_SN))

        self.assertIn(pc.END_DATE_SN, rt_data.keys())
        self.assertEqual(self.time_now, rt_data.get(pc.END_DATE_SN))

        self.assertIn(pc.TIMESTAMP, rt_data.keys())
        self.assertEqual(self.time_now, rt_data.get(pc.TIMESTAMP))

        self.assertIn(pc.REAL_TIME_SN, rt_data.keys())
        self.assertTrue(rt_data.get(pc.REAL_TIME_SN))

        self.assertIn(pc.REP_LEVEL, rt_data.keys())
        self.assertFalse(any(x.isupper() for x in rt_data.get(pc.REP_LEVEL)))

        self.assertIn(pc.RESULT, rt_data.keys())
        self.assertTrue(rt_data.get(pc.RESULT))

    def _run_real_time_stats_assertions(
            self, category, metrics_func, stats_func, keys_func=None):
        """Run CI test assertions on category stats call.

        :param category: the real-time category being tested -- str
        :param metrics_func: the function to get category metrics -- func
        :param stats_func: the function to get category stats -- func
        :param keys_func: the function to get category keys -- func
        """

        inst_req = True if category != pc.ARRAY else False
        instance_id = None
        last_available_date = self.time_now
        start = last_available_date - pc.ONE_MINUTE
        timestamps = self.rt.get_timestamps(self.rt.array_id)
        if timestamps:
            last_available_date = int(timestamps[0].get('lastAvailableDate'))
            start = last_available_date - pc.ONE_MINUTE
        else:
            self.skipTest('Skipping _run_real_time_stats_assertions - '
                          'Unable to get real time timestamps.')
        # If an instance id is required get a random choice from the available
        # keys for that category
        if inst_req:
            cat_keys = keys_func()
            if not cat_keys:
                self.skipTest(
                    'No real-time keys available for category: {cat}'.format(
                        cat=category))
            instance_id = random.choice(cat_keys)

        # Test 'All' metrics
        if inst_req:
            response = stats_func(
                start_date=start, end_date=last_available_date, metrics='All',
                instance_id=instance_id)
        else:
            response = stats_func(
                start_date=start, end_date=last_available_date, metrics='All')

        self.assertEqual(self.rt.array_id, response.get(pc.ARRAY_ID))
        self.assertEqual(self.common.convert_to_snake_case(category),
                         response.get(pc.REP_LEVEL))
        self.assertTrue(response.get(pc.RESULT))

        # Test individual metrics
        metrics = metrics_func()
        for metric in metrics:
            if inst_req:
                response = stats_func(
                    start_date=start, end_date=self.time_now, metrics=metric,
                    instance_id=instance_id)
            else:
                response = stats_func(
                    start_date=start, end_date=self.time_now, metrics=metric)

            self.assertTrue(response.get(pc.RESULT))
            perf_data = response.get(pc.RESULT)[0]
            self.assertIn(metric, perf_data.keys())

        # Test random selection of metrics in list format
        metrics = random.sample(metrics, k=int(len(metrics) / 2))
        if inst_req:
            response = stats_func(
                start_date=start, end_date=self.time_now, metrics=metrics,
                instance_id=instance_id)
        else:
            response = stats_func(
                start_date=start, end_date=self.time_now, metrics=metrics)
        self.assertTrue(response.get(pc.RESULT))
        perf_data = response.get(pc.RESULT)[0]
        for metric in metrics:
            self.assertIn(metric, perf_data.keys())

    def test_get_array_metrics(self):
        """Test get_array_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.ARRAY)
        metrics = self.rt.get_array_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_array_keys(self):
        """Test get_array_keys."""
        ref_keys = self.rt.get_category_keys(pc.ARRAY)
        keys = self.rt.get_array_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_array_stats(self):
        """Test get_array_stats."""
        self._run_real_time_stats_assertions(
            category=pc.ARRAY, metrics_func=self.rt.get_array_metrics,
            stats_func=self.rt.get_array_stats)

    def test_get_backend_director_metrics(self):
        """Test get_backend_director_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.BE_DIR)
        metrics = self.rt.get_backend_director_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_backend_director_keys(self):
        """Test get_backend_director_keys."""
        ref_keys = self.rt.get_category_keys(pc.BE_DIR)
        keys = self.rt.get_backend_director_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_backend_director_stats(self):
        """Test get_array_stats."""
        self._run_real_time_stats_assertions(
            category=pc.BE_DIR,
            keys_func=self.rt.get_backend_director_keys,
            metrics_func=self.rt.get_backend_director_metrics,
            stats_func=self.rt.get_backend_director_stats)

    def test_get_backend_port_metrics(self):
        """Test get_backend_port_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.BE_PORT)
        metrics = self.rt.get_backend_port_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_backend_port_keys(self):
        """Test get_backend_port_keys."""
        ref_keys = self.rt.get_category_keys(pc.BE_PORT)
        keys = self.rt.get_backend_port_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_backend_port_stats(self):
        """Test get_backend_port_stats."""
        self._run_real_time_stats_assertions(
            category=pc.BE_PORT,
            keys_func=self.rt.get_backend_port_keys,
            metrics_func=self.rt.get_backend_port_metrics,
            stats_func=self.rt.get_backend_port_stats)

    def test_get_external_director_metrics(self):
        """Test get_external_director_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.EXT_DIR)
        metrics = self.rt.get_external_director_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_external_director_keys(self):
        """Test get_external_director_keys."""
        ref_keys = self.rt.get_category_keys(pc.EXT_DIR)
        keys = self.rt.get_external_director_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_external_director_stats(self):
        """Test get_external_director_stats."""
        self._run_real_time_stats_assertions(
            category=pc.EXT_DIR,
            keys_func=self.rt.get_external_director_keys,
            metrics_func=self.rt.get_external_director_metrics,
            stats_func=self.rt.get_external_director_stats)

    def test_get_frontend_director_metrics(self):
        """Test get_frontend_director_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.FE_DIR)
        metrics = self.rt.get_frontend_director_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_frontend_director_keys(self):
        """Test get_frontend_director_keys."""
        ref_keys = self.rt.get_category_keys(pc.FE_DIR)
        keys = self.rt.get_frontend_director_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_frontend_director_stats(self):
        """Test get_frontend_director_stats."""
        self._run_real_time_stats_assertions(
            category=pc.FE_DIR,
            keys_func=self.rt.get_frontend_director_keys,
            metrics_func=self.rt.get_frontend_director_metrics,
            stats_func=self.rt.get_frontend_director_stats)

    def test_get_frontend_port_metrics(self):
        """Test get_frontend_port_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.FE_PORT)
        metrics = self.rt.get_frontend_port_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_frontend_port_keys(self):
        """Test get_frontend_port_keys."""
        ref_keys = self.rt.get_category_keys(pc.FE_PORT)
        keys = self.rt.get_frontend_port_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_frontend_port_stats(self):
        """Test get_frontend_port_stats."""
        self._run_real_time_stats_assertions(
            category=pc.FE_PORT,
            keys_func=self.rt.get_frontend_port_keys,
            metrics_func=self.rt.get_frontend_port_metrics,
            stats_func=self.rt.get_frontend_port_stats)

    def test_get_rdf_director_metrics(self):
        """Test get_rdf_director_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.RDF_DIR)
        metrics = self.rt.get_rdf_director_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_rdf_director_keys(self):
        """Test get_frontend_port_keys."""
        ref_keys = self.rt.get_category_keys(pc.RDF_DIR)
        keys = self.rt.get_rdf_director_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_rdf_director_stats(self):
        """Test get_rdf_director_stats."""
        self._run_real_time_stats_assertions(
            category=pc.RDF_DIR,
            keys_func=self.rt.get_rdf_director_keys,
            metrics_func=self.rt.get_rdf_director_metrics,
            stats_func=self.rt.get_rdf_director_stats)

    def test_get_rdf_port_metrics(self):
        """Test get_rdf_port_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.RDF_PORT)
        metrics = self.rt.get_rdf_port_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_rdf_port_keys(self):
        """Test get_rdf_port_keys."""
        ref_keys = self.rt.get_category_keys(pc.RDF_PORT)
        keys = self.rt.get_rdf_port_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_rdf_port_stats(self):
        """Test get_rdf_port_stats."""
        self._run_real_time_stats_assertions(
            category=pc.RDF_PORT,
            keys_func=self.rt.get_rdf_port_keys,
            metrics_func=self.rt.get_rdf_port_metrics,
            stats_func=self.rt.get_rdf_port_stats)

    def test_get_storage_group_metrics(self):
        """Test get_storage_group_metrics."""
        ref_metrics = self.rt.get_category_metrics(pc.SG)
        metrics = self.rt.get_storage_group_metrics()
        self.assertTrue(metrics)
        self.assertIsInstance(metrics, list)
        self.assertEqual(ref_metrics, metrics)

    def test_get_storage_group_keys(self):
        """Test get_storage_group_keys."""
        ref_keys = self.rt.get_category_keys(pc.SG)
        keys = self.rt.get_storage_group_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(ref_keys, keys)

    def test_get_storage_group_stats(self):
        """Test get_storage_group_stats."""
        self._run_real_time_stats_assertions(
            category=pc.SG,
            keys_func=self.rt.get_storage_group_keys,
            metrics_func=self.rt.get_storage_group_metrics,
            stats_func=self.rt.get_storage_group_stats)
