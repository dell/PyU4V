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
"""test_pyu4v_ci_performance.py."""
import os
import testtools
import time

from PyU4V.tests.ci_tests import base
from PyU4V.tests.unit_tests import pyu4v_performance_data as pd
from PyU4V.utils import exception
from PyU4V.utils import file_handler
from PyU4V.utils import performance_constants as pc


class CITestPerformance(base.TestBaseTestCase, testtools.TestCase):
    """Test Performance REST calls."""

    def setUp(self):
        """setUp."""
        super(CITestPerformance, self).setUp()
        self.perf = self.conn.performance
        self.p_data = pd.PerformanceData()
        self.time_now = int(time.time() * 1000)
        self.is_v4 = self.common.is_array_v4(self.conn.array_id)
        if not (self.perf.is_array_diagnostic_performance_registered(
                self.conn.array_id)):
            self.skipTest(
                'Array {arr} is not diagnostic performance registered, '
                'skipping performance tests.'.format(arr=self.conn.array_id))

    def test_set_array_id(self):
        """Test set_array_id."""
        array_id = self.p_data.remote_array
        self.perf.set_array_id(array_id)
        self.assertEqual(self.perf.array_id, array_id)

    def test_set_timestamp(self):
        """Test set_timestamp."""
        time_now = int(time.time())
        self.perf.set_timestamp(time_now)
        self.assertEqual(self.perf.timestamp, time_now)

    def test_set_recency(self):
        """Test set_recency."""
        recency = 9
        self.perf.set_recency(recency)
        self.assertEqual(self.perf.recency, recency)

    def test_is_array_performance_registered(self):
        """Test is_array_performance_registered invalid ID."""
        self.assertTrue(
            self.perf.is_array_performance_registered())
        self.assertFalse(
            self.perf.is_array_performance_registered('Fake'))

    def test_is_array_diagnostic_performance_registered(self):
        """Test is_array_diagnostic_performance_registered response format."""
        self.assertTrue(
            self.perf.is_array_diagnostic_performance_registered())
        self.assertFalse(
            self.perf.is_array_diagnostic_performance_registered('Fake'))

    def test_is_array_real_time_performance_registered(self):
        """Test is_array_real_time_performance_registered response format."""
        self.assertTrue(
            self.perf.is_array_real_time_performance_registered())
        self.assertFalse(
            self.perf.is_array_real_time_performance_registered('Fake'))

    def test_get_array_registration_details(self):
        """Test get_array_registration_details."""
        response = self.perf.get_array_registration_details()
        self.assertIsInstance(response, dict)
        self.assertEqual(self.conn.array_id, response.get(pc.SYMM_ID))
        self.assertIn(pc.REAL_TIME, response.keys())
        self.assertIn(pc.REG_DIAGNOSTIC, response.keys())
        self.assertIn(pc.COLLECTION_INT, response.keys())

    def test_backup_performance_database_success(self):
        """Test backup_performance_database success."""
        self.perf.backup_performance_database()

    def test_backup_performance_database_failure(self):
        """Test backup_performance_database exception."""
        self.assertRaises(
            exception.VolumeBackendAPIException,
            self.perf.backup_performance_database, array_id='FAKE')

    def test_get_last_available_timestamp(self):
        """Test get_last_available_timestamp."""
        timestamp = self.perf.get_last_available_timestamp()
        self.assertIsNotNone(timestamp)
        self.assertIsInstance(timestamp, int)

    def test_get_last_available_timestamp_exception(self):
        """Test get_last_available_timestamp exception case."""
        self.assertRaises(exception.ResourceNotFoundException,
                          self.perf.get_last_available_timestamp, '12345')

    def test_is_timestamp_current_true(self):
        """Test is_timestamp_current true condition."""
        two_mins_ago = self.time_now - (pc.ONE_MINUTE * 2)
        self.assertTrue(self.perf.is_timestamp_current(timestamp=two_mins_ago))

    def test_is_timestamp_current_false(self):
        """Test is_timestamp_current false condition."""
        ten_mins_ago = self.time_now - (pc.ONE_MINUTE * 10)
        self.perf.recency = 20
        self.assertFalse(self.perf.is_timestamp_current(timestamp=ten_mins_ago,
                                                        minutes=9))

    def test_get_timestamp_by_hour_start_only(self):
        """Test get_timestamp_by_hour start input only."""
        two_hours_ago = self.time_now - (pc.ONE_HOUR * 2)
        start_time, end_time = self.perf.get_timestamp_by_hour(
            start_time=two_hours_ago, hours_difference=1)
        self.assertEqual((end_time - start_time), pc.ONE_HOUR)

    def test_get_timestamp_by_hour_end_only(self):
        """Test get_timestamp_by_hour end input only."""
        start_time, end_time = self.perf.get_timestamp_by_hour(
            end_time=self.time_now, hours_difference=3)
        self.assertEqual((end_time - start_time), pc.ONE_HOUR * 3)

    def test_get_timestamp_by_hour_no_start_or_end(self):
        """Test get_timestamp_by_hour with hour difference only."""
        start_time, end_time = self.perf.get_timestamp_by_hour(
            hours_difference=5)
        self.assertEqual((end_time - start_time), pc.ONE_HOUR * 5)

    def test_get_performance_key_list_array_get(self):
        """Test get_performance_key_list get with Array category."""
        key_response = self.perf.get_performance_key_list(
            category=pc.ARRAY)
        array_time_keys = key_response.get(pc.ARRAY_INFO)[0]
        self.assertTrue(key_response)
        self.assertIn(pc.SYMM_ID, array_time_keys.keys())
        self.assertIn(pc.FA_DATE, array_time_keys.keys())
        self.assertIn(pc.LA_DATE, array_time_keys.keys())
        self.assertIsInstance(array_time_keys.get(pc.FA_DATE), int)
        self.assertIsInstance(array_time_keys.get(pc.LA_DATE), int)

    def test_get_performance_key_list_exception(self):
        """Test get_performance_key_list with invalid category."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_performance_key_list, 'FAKE_CAT')

    def test_get_performance_categories_list(self):
        """Test get_performance_categories_list."""
        cat_list = self.perf.get_performance_categories_list()
        self.assertTrue(cat_list)

    def test_validate_category(self):
        """Test _validate_category pass."""
        self.perf.validate_category(pc.ARRAY)

    def test_validate_category_exception(self):
        """Test _validate_category exception."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.validate_category, 'FAKE_CAT')

    def test_get_performance_metrics_list(self):
        """Test get_performance_metrics_list success."""
        array_metrics = self.perf.get_performance_metrics_list(
            pc.ARRAY, kpi_only=False)
        self.assertIsInstance(array_metrics, list)
        self.assertNotEqual(array_metrics, list())

    def test_get_performance_metrics_list_exception(self):
        """Test get_performance_metrics_list invalid category."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_performance_metrics_list, 'FAKE_CAT')

    def test_format_metrics(self):
        """Test format_metrics success."""
        test_metrics = 'single_metric'
        formatted_metrics = self.perf.format_metrics(test_metrics)
        self.assertIsInstance(formatted_metrics, list)

        test_metrics = ['single_metric']
        formatted_metrics = self.perf.format_metrics(test_metrics)
        self.assertIsInstance(formatted_metrics, list)

    def test_format_metrics_exception(self):
        """Test format_metrics exception invalid input type."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.format_metrics, dict())

    def test_extract_timestamp_keys(self):
        """Test extract_timestamp_keys."""
        fa_date, la_date = self.perf.extract_timestamp_keys(category=pc.ARRAY)
        self.assertTrue(fa_date)
        self.assertTrue(la_date)
        self.assertIsInstance(fa_date, int)
        self.assertIsInstance(la_date, int)
        self.assertTrue(fa_date < la_date)

    def test_format_time_input_no_start(self):
        """Test format_time_input no start time provided."""
        start, end = self.perf.format_time_input(category=pc.ARRAY,
                                                 end_time=self.time_now)
        self.assertTrue(start)
        self.assertIsInstance(start, str)
        self.assertTrue(int(start) < int(end))

    def test_format_time_input_no_end(self):
        """Test format_time_input no end time provided."""
        start_time = self.time_now - (pc.ONE_MINUTE * 20)
        start, end = self.perf.format_time_input(category=pc.ARRAY,
                                                 start_time=start_time)
        self.assertTrue(end)
        self.assertIsInstance(end, str)
        self.assertTrue(int(start) < int(end))

    def test_format_time_input_no_start_or_end(self):
        """Test format_time_input no end time provided."""
        start, end = self.perf.format_time_input(category=pc.ARRAY)
        self.assertTrue(start)
        self.assertTrue(end)
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertEqual(int(start), int(end))

    def test_format_time_input_exception_wrong_length(self):
        """Test format_time_input exception timestamp invalid."""
        self.assertRaises(
            exception.InvalidInputException, self.perf.format_time_input,
            self.p_data.array, pc.ARRAY, start_time=123, end_time=123)

    def test_format_time_input_exception_start_after_end(self):
        """Test format_time_input exception start time after end time."""
        end_time = self.time_now - (pc.ONE_MINUTE * 5)
        self.assertRaises(
            exception.InvalidInputException, self.perf.format_time_input,
            self.p_data.array, pc.ARRAY, start_time=self.time_now,
            end_time=end_time)

    def test_get_days_to_full_array(self):
        """Test get_days_to_full array level."""
        response = self.perf.get_days_to_full(array_to_full=True)
        self.assertTrue(response)
        self.assertIsInstance(response, list)
        response = response[0]
        self.assertIn('ProjectionDaysToFull', response.keys())
        self.assertEqual(self.conn.array_id, response.get('instanceId'))

    def test_get_days_to_full_srp(self):
        """Test get_days_to_full srp level."""
        response = self.perf.get_days_to_full(srp_to_full=True)
        self.assertTrue(response)
        self.assertIsInstance(response, list)
        response = response[0]
        self.assertIn('ProjectionDaysToFull', response.keys())
        self.assertIn('SRP_', response.get('instanceId'))

    def test_get_days_to_full_thin_pool(self):
        """Test get_days_to_full thin pool level."""
        if self.is_v4:
            self.skipTest('Thin Pool days to full are not enabled for V4.')
        response = self.perf.get_days_to_full(thin_pool_to_full=True)
        self.assertTrue(response)
        self.assertIsInstance(response, list)
        response = response[0]
        self.assertIn('ProjectionDaysToFull', response.keys())
        self.assertIn('instanceId', response.keys())

    def test_get_days_to_full_exception(self):
        """Test get_days_to_full no category set exception."""
        self.assertRaises(exception.InvalidInputException,
                          self.perf.get_days_to_full)

    def test_get_threshold_categories(self):
        """Test get_threshold_categories."""
        response = self.perf.get_threshold_categories()
        self.assertTrue(response)
        self.assertIsInstance(response, list)

    def test_get_threshold_category_settings(self):
        """Test get_threshold_category_settings."""
        response = self.perf.get_threshold_category_settings(
            category=pc.ARRAY)
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertEqual(pc.ARRAY, response.get(pc.CATEGORY))
        self.assertIn(pc.PERF_THRESH, response.keys())
        self.assertIsInstance(response.get(pc.PERF_THRESH), list)
        self.assertIsInstance(
            response.get('num_of_metric_performance_thresholds'), int)

    def test_update_threshold_settings(self):
        """Test set_perf_threshold_and_alert."""
        metric = 'PercentCacheWP'
        alert, f_threshold, s_threshold = None, None, None

        cat_thresh_settings = self.perf.get_threshold_category_settings(
            category=pc.ARRAY)
        for threshold in cat_thresh_settings.get(pc.PERF_THRESH):
            if threshold.get(pc.METRIC) == metric:
                alert = threshold.get(pc.ALERT_ERR)
                f_threshold = threshold.get(pc.FIRST_THRESH)
                s_threshold = threshold.get(pc.SEC_THRESH)
                break

        # Update threshold settings
        update_response = self.perf.update_threshold_settings(
            category=pc.ARRAY, metric=metric, first_threshold=f_threshold + 5,
            second_threshold=s_threshold + 5, alert=(not alert))
        self.assertTrue(update_response.get('success'))

        cat_thresh_settings = self.perf.get_threshold_category_settings(
            category=pc.ARRAY)
        for threshold in cat_thresh_settings.get(pc.PERF_THRESH):
            if threshold.get(pc.METRIC) == metric:
                self.assertEqual(threshold.get(pc.ALERT_ERR), (not alert))
                self.assertEqual(threshold.get(pc.FIRST_THRESH),
                                 f_threshold + 5)
                self.assertEqual(threshold.get(pc.SEC_THRESH),
                                 s_threshold + 5)

        # Change them back to original settings
        update_response = self.perf.update_threshold_settings(
            category=pc.ARRAY, metric=metric, first_threshold=f_threshold,
            second_threshold=s_threshold, alert=alert)
        self.assertTrue(update_response.get('success'))
        cat_thresh_settings = self.perf.get_threshold_category_settings(
            category=pc.ARRAY)
        for threshold in cat_thresh_settings.get(pc.PERF_THRESH):
            if threshold.get(pc.METRIC) == metric:
                self.assertEqual(threshold.get(pc.ALERT_ERR), alert)
                self.assertEqual(threshold.get(pc.FIRST_THRESH), f_threshold)
                self.assertEqual(threshold.get(pc.SEC_THRESH), s_threshold)

    def test_generate_threshold_settings_csv(self):
        """Test generate_threshold_settings_csv."""
        csv_file_name = 'test.csv'
        temp_dir = self.create_temp_directory()
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        self.perf.generate_threshold_settings_csv(csv_file_path)
        self.assertTrue(os.path.isfile(csv_file_path))

    def test_set_thresholds_from_csv(self):
        """Test set_thresholds_from_csv."""
        # Generate CSV settings file
        csv_file_name = 'test.csv'
        temp_dir = self.create_temp_directory()
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        self.perf.generate_threshold_settings_csv(
            csv_file_path, category='Array')
        self.assertTrue(os.path.isfile(csv_file_path))

        # Read CSV file
        csv_data = file_handler.read_csv_values(csv_file_path)

        # Make change to metric threshold
        num_metrics = len(csv_data.get('metric'))
        orig_values = (0, 0)
        updated_values = (0, 0)
        metric_set = 'PercentCacheWP'
        for i in range(0, num_metrics):
            metric = csv_data.get(pc.METRIC)[i]
            if metric == metric_set:
                orig_values = (csv_data.get(pc.FIRST_THRESH)[i],
                               csv_data.get(pc.SEC_THRESH)[i])
                updated_values = (int(orig_values[0]) + 5,
                                  int(orig_values[1]) + 10)
                csv_data[pc.FIRST_THRESH][i] = updated_values[0]
                csv_data[pc.SEC_THRESH][i] = updated_values[1]
                csv_data[pc.KPI][i] = True
                break

        # Write updated metrics list to CSV
        csv_file_name_updated = 'test_updated.csv'
        csv_file_path_updated = os.path.join(temp_dir, csv_file_name_updated)
        file_handler.write_dict_to_csv_file(csv_file_path_updated, csv_data)

        # Apply update to metrics via CSV
        self.perf.set_thresholds_from_csv(csv_file_path_updated)

        # Get updated threshold settings from Unisphere
        t_settings = self.perf.get_threshold_category_settings(pc.ARRAY)
        for t in t_settings.get(pc.PERF_THRESH):
            if t.get(pc.METRIC) == metric_set:
                self.assertEqual(t.get(pc.FIRST_THRESH), updated_values[0])
                self.assertEqual(t.get(pc.SEC_THRESH), updated_values[1])

        # Reapply old metric settings
        self.perf.set_thresholds_from_csv(csv_file_path)

        # Check old settings were successfully re-applied
        t_settings = self.perf.get_threshold_category_settings(pc.ARRAY)
        for t in t_settings.get(pc.PERF_THRESH):
            if t.get(pc.METRIC) == metric_set:
                self.assertEqual(t.get(pc.FIRST_THRESH), int(orig_values[0]))
                self.assertEqual(t.get(pc.SEC_THRESH), int(orig_values[1]))

    def test_performance_stats_max_format(self):
        """Test performance stats max data format."""
        array_metrics = self.perf.get_array_stats(
            metrics=pc.ALL, data_format=pc.MAXIMUM)
        self.assertTrue(array_metrics)
        self.assertIsInstance(array_metrics, dict)
        self.assertEqual(array_metrics.get(pc.ARRAY_ID), self.conn.array_id)

    def test_performance_stats_invalid_data_format(self):
        """Test performance stats invalid data format function."""
        self.assertRaises(
            exception.InvalidInputException, self.perf.get_array_stats,
            metrics=pc.ALL, data_format='FAKE')

    def test_performance_stats_recency_format(self):
        """Test performance stats recency function."""
        current_time = int(time.time()) * 1000
        # Set end_time as 20 mins ago, failing recency check
        end_time = current_time - (20 * pc.ONE_MINUTE)
        start_time = end_time

        self.assertRaises(
            exception.VolumeBackendAPIException, self.perf.get_array_stats,
            metrics=pc.ALL, start_time=start_time, end_time=end_time,
            recency=1)

    def test_array_performance_function(self):
        """Test array performance function."""
        # Test get_array_keys.
        array_keys = self.perf.get_array_keys()
        found_array = False
        for array in array_keys:
            self.assertIn(pc.SYMM_ID, array.keys())
            self.assertIn(pc.FA_DATE, array.keys())
            self.assertIn(pc.LA_DATE, array.keys())
            if array.get(pc.SYMM_ID) == self.conn.array_id:
                found_array = True
        self.assertTrue(found_array)
        # Test get_array_stats
        array_metrics = self.perf.get_performance_metrics_list(pc.ARRAY)
        dead_metrics = list()
        for metric in array_metrics:
            try:
                array_stats = self.perf.get_array_stats(metrics=metric)
                self.assertTrue(array_stats)
                self.assertIsInstance(array_stats, dict)
                self.assertEqual(array_stats.get(pc.ARRAY_ID),
                                 self.conn.array_id)
                perf_results = array_stats.get('result')[0]
                self.assertIn(metric, perf_results.keys())
            except exception.VolumeBackendAPIException:
                dead_metrics.append(metric)
        try:
            self.assertFalse(dead_metrics)
        except AssertionError:
            print('Dead metrics found in category Array: {m}'.format(
                m=dead_metrics))
            raise AssertionError

    def test_backend_director_performance_function(self):
        """Test BE director performance function."""
        category = pc.BE_DIR
        id_tag = pc.DIR_ID
        key_func = self.perf.get_backend_director_keys
        metrics_func = self.perf.get_backend_director_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_backend_emulation_performance_function(self):
        """Test BE emulation performance function."""
        if self.is_v4:
            self.skipTest('Backend Emulation is not supported by V4 arrays')
        category = pc.BE_EMU
        id_tag = pc.BE_EMU_ID
        key_func = self.perf.get_backend_emulation_keys
        metrics_func = self.perf.get_backend_emulation_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_backend_port_performance_function(self):
        """Test BE port performance function."""
        if self.is_v4:
            self.skipTest('Backend Ports are not supported by V4 arrays')
        category = pc.BE_PORT
        outer_tag = pc.DIR_ID
        inner_tag = pc.PORT_ID
        inner_keys_func = self.perf.get_backend_director_keys
        outer_key_func = self.perf.get_backend_port_keys
        outer_metrics_func = self.perf.get_backend_port_stats
        self.run_extended_input_performance_test_asserts(
            category, outer_tag, inner_tag, inner_keys_func, outer_key_func,
            outer_metrics_func)

    def test_board_performance_function(self):
        """Test board performance function."""
        category = pc.BOARD
        id_tag = pc.BOARD_ID
        key_func = self.perf.get_board_keys
        metrics_func = self.perf.get_board_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_cache_partition_performance_function(self):
        """Test cache partition performance function."""
        if self.is_v4:
            self.skipTest('Cache Partition is not supported by V4 arrays')
        category = pc.CACHE_PART
        id_tag = pc.CACHE_PART_ID
        key_func = self.perf.get_cache_partition_keys
        metrics_func = self.perf.get_cache_partition_perf_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_cloud_provider_performance_function(self):
        """Test cloud provider performance function."""
        category = pc.CLOUD_PROVIDER
        id_tag = pc.CLOUD_PROVIDER_ID
        key_func = self.perf.get_cloud_provider_keys
        metrics_func = self.perf.get_cloud_provider_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_device_group_performance_function(self):
        """Test device group by pool performance function."""
        category = pc.DEV_GRP
        id_tag = pc.DEV_GRP_ID
        key_func = self.perf.get_device_group_keys
        metrics_func = self.perf.get_device_group_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_disk_group_performance_function(self):
        """Test device group by pool performance function."""
        category = pc.DISK_GRP
        id_tag = pc.DISK_GRP_ID
        key_func = self.perf.get_disk_group_keys
        metrics_func = self.perf.get_disk_group_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_eds_director_performance_function(self):
        """Test EDS director performance function."""
        if self.is_v4:
            self.skipTest('EDS Directors are not supported by V4 arrays')
        category = pc.EDS_DIR
        id_tag = pc.DIR_ID
        key_func = self.perf.get_eds_director_keys
        metrics_func = self.perf.get_eds_director_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_eds_emulation_performance_function(self):
        """Test EDS emulation performance function."""
        if self.is_v4:
            self.skipTest('EDS Emulation is not supported by V4 arrays')
        category = pc.EDS_EMU
        id_tag = pc.EDS_EMU_ID
        key_func = self.perf.get_eds_emulation_keys
        metrics_func = self.perf.get_eds_emulation_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_em_director_performance_function(self):
        """Test EM Director performance function."""
        if not self.is_v4:
            self.skipTest('EM Directors are not supported by V3 arrays')
        category = pc.EM_DIR
        id_tag = pc.DIR_ID
        key_func = self.perf.get_em_director_keys
        metrics_func = self.perf.get_em_director_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_external_disk_performance_function(self):
        """Test external disk performance function."""
        if self.is_v4:
            self.skipTest('External Disk is not supported by V4 arrays')
        category = pc.EXT_DISK
        id_tag = pc.DISK_ID
        key_func = self.perf.get_external_disk_keys
        metrics_func = self.perf.get_external_disk_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_fe_director_performance_function(self):
        """Test FE director performance function."""
        category = pc.FE_DIR
        id_tag = pc.DIR_ID
        key_func = self.perf.get_frontend_director_keys
        metrics_func = self.perf.get_frontend_director_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_fe_emulation_performance_function(self):
        """Test FE emulation performance function."""
        if self.is_v4:
            self.skipTest('Frontend Emulation is not supported by V4 arrays')
        category = pc.FE_EMU
        id_tag = pc.FE_EMU_ID
        key_func = self.perf.get_frontend_emulation_keys
        metrics_func = self.perf.get_frontend_emulation_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_fe_port_performance_function(self):
        """Test FE port performance function."""
        category = pc.FE_PORT
        outer_tag = pc.DIR_ID
        inner_tag = pc.PORT_ID
        inner_keys_func = self.perf.get_frontend_director_keys
        outer_key_func = self.perf.get_frontend_port_keys
        outer_metrics_func = self.perf.get_frontend_port_stats
        self.run_extended_input_performance_test_asserts(
            category, outer_tag, inner_tag, inner_keys_func, outer_key_func,
            outer_metrics_func)

    def test_ficon_emulation_performance_function(self):
        """Test FICON emulation performance function."""
        if self.is_v4:
            self.skipTest('FICON Emulation is not supported by V4 arrays')
        category = pc.FICON_EMU
        id_tag = pc.FICON_EMU_ID
        key_func = self.perf.get_ficon_emulation_keys
        metrics_func = self.perf.get_ficon_emulation_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_ficon_emulation_thread_performance_function(self):
        """Test FICON emulation thread performance function."""
        category = pc.FICON_EMU_THR
        id_tag = pc.FICON_EMU_THR_ID
        key_func = self.perf.get_ficon_emulation_thread_keys
        metrics_func = self.perf.get_ficon_emulation_thread_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_ficon_port_thread_performance_function(self):
        """Test FICON port thread performance function."""
        category = pc.FICON_PORT_THR
        id_tag = pc.FICON_PORT_THR_ID
        key_func = self.perf.get_ficon_port_thread_keys
        metrics_func = self.perf.get_ficon_port_thread_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_host_performance_function(self):
        """Test host performance function."""
        category = pc.HOST
        id_tag = pc.HOST_ID
        key_func = self.perf.get_host_keys
        metrics_func = self.perf.get_host_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_im_director_performance_function(self):
        """Test IM director performance function."""
        if self.is_v4:
            self.skipTest('IM Directors are not supported by V4 arrays')
        category = pc.IM_DIR
        id_tag = pc.DIR_ID
        key_func = self.perf.get_im_director_keys
        metrics_func = self.perf.get_im_director_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_im_emulation_performance_function(self):
        """Test IM emulation performance function."""
        if self.is_v4:
            self.skipTest('IM Emulation is not supported by V4 arrays')
        category = pc.IM_EMU
        id_tag = pc.IM_EMU_ID
        key_func = self.perf.get_im_emulation_keys
        metrics_func = self.perf.get_im_emulation_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_initiator_performance_function(self):
        """Test initiator performance function."""
        category = pc.INIT
        id_tag = pc.INIT_ID
        key_func = self.perf.get_initiator_perf_keys
        metrics_func = self.perf.get_initiator_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_ip_interface_performance_function(self):
        """Test initiator by port performance function."""
        category = pc.IP_INT
        id_tag = pc.IP_INT_ID
        key_func = self.perf.get_ip_interface_keys
        metrics_func = self.perf.get_ip_interface_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_iscsi_target_performance_function(self):
        """Test initiator by port performance function."""
        category = pc.ENDPOINT
        id_tag = pc.ENDPOINT_ID_KEY
        key_func = self.perf.get_iscsi_target_keys
        metrics_func = self.perf.get_iscsi_target_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_endpoint_performance_function(self):
        """Test endpoint performance function."""
        category = pc.ENDPOINT
        id_tag = pc.ENDPOINT_ID_KEY
        key_func = self.perf.get_endpoint_keys
        metrics_func = self.perf.get_endpoint_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_masking_view_performance_function(self):
        """Test Masking View performance function."""
        category = pc.MV
        id_tag = pc.MV_ID
        key_func = self.perf.get_masking_view_keys
        metrics_func = self.perf.get_masking_view_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_port_group_performance_function(self):
        """Test port group performance function."""
        category = pc.PG
        id_tag = pc.PG_ID
        key_func = self.perf.get_port_group_keys
        metrics_func = self.perf.get_port_group_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_rdfa_performance_function(self):
        """Test RDFA performance function."""
        category = pc.RDFA
        id_tag = pc.RA_GRP_INFO
        key_func = self.perf.get_rdfa_keys
        metrics_func = self.perf.get_rdfa_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_rdfs_performance_function(self):
        """Test RDFS performance function."""
        category = pc.RDFS
        id_tag = pc.RA_GRP_ID
        key_func = self.perf.get_rdfs_keys
        metrics_func = self.perf.get_rdfs_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_rdf_director_performance_function(self):
        """Test RDF director performance function."""
        category = pc.RDF_DIR
        id_tag = pc.DIR_ID
        key_func = self.perf.get_rdf_director_keys
        metrics_func = self.perf.get_rdf_director_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_rdf_emulation_performance_function(self):
        """Test RDF emulation performance function."""
        if self.is_v4:
            self.skipTest('RDF Emulation is not supported by V4 arrays')
        category = pc.RDF_EMU
        id_tag = pc.RDF_EMU_ID
        key_func = self.perf.get_rdf_emulation_keys
        metrics_func = self.perf.get_rdf_emulation_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_rdf_port_performance_function(self):
        """Test RDF port performance function."""
        category = pc.RDF_PORT
        outer_tag = pc.DIR_ID
        inner_tag = pc.PORT_ID
        inner_keys_func = self.perf.get_rdf_director_keys
        outer_key_func = self.perf.get_rdf_port_keys
        outer_metrics_func = self.perf.get_rdf_port_stats
        self.run_extended_input_performance_test_asserts(
            category, outer_tag, inner_tag, inner_keys_func, outer_key_func,
            outer_metrics_func)

    def test_sdnas_filesystem_performance_function(self):
        """Test SDNAS filesystem performance function."""
        if not self.is_v4:
            self.skipTest('SDNAS is not supported by V3 arrays')
        category = pc.SDNAS_FS
        id_tag = pc.SDNAS_FS_ID
        key_func = self.perf.get_sdnas_filesystem_keys
        metrics_func = self.perf.get_sdnas_filesystem_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_sdnas_interface_performance_function(self):
        """Test SDNAS interface performance function."""
        if not self.is_v4:
            self.skipTest('SDNAS is not supported by V3 arrays')
        category = pc.SDNAS_INTERFACE
        id_tag = pc.SDNAS_INTERFACE_ID
        key_func = self.perf.get_sdnas_interface_keys
        metrics_func = self.perf.get_sdnas_interface_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_sdnas_node_performance_function(self):
        """Test SDNAS node performance function."""
        if not self.is_v4:
            self.skipTest('SDNAS is not supported by V3 arrays')
        category = pc.SDNAS_NODE
        id_tag = pc.SDNAS_NODE_ID
        key_func = self.perf.get_sdnas_node_keys
        metrics_func = self.perf.get_sdnas_node_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_sdnas_server_performance_function(self):
        """Test SDNAS server performance function."""
        if not self.is_v4:
            self.skipTest('SDNAS is not supported by V3 arrays')
        category = pc.SDNAS_SERVER
        id_tag = pc.SDNAS_SERVER_ID
        key_func = self.perf.get_sdnas_server_keys
        metrics_func = self.perf.get_sdnas_server_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_storage_container_performance_function(self):
        """Test storage container performance function."""
        category = pc.STORAGE_CONT
        id_tag = pc.STORAGE_CONT_ID
        key_func = self.perf.get_storage_container_keys
        metrics_func = self.perf.get_storage_container_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_storage_group_performance_function(self):
        """Test storage group performance function."""
        category = pc.SG
        id_tag = pc.SG_ID
        key_func = self.perf.get_storage_group_keys
        metrics_func = self.perf.get_storage_group_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_storage_resource_pool_performance_function(self):
        """Test storage resource pool performance function."""
        category = pc.SRP
        id_tag = pc.SRP_ID
        key_func = self.perf.get_storage_resource_pool_keys
        metrics_func = self.perf.get_storage_resource_pool_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_storage_resource_performance_function(self):
        """Test storage resource performance function."""
        sc_keys, sr_keys = None, None
        try:
            sc_keys = self.perf.get_storage_container_keys()
            sr_keys = self.perf.get_storage_resource_keys()
        except exception.ResourceNotFoundException:
            if not sc_keys:
                self.skipTest('There are no storage containers available in '
                              'this environment.')
            else:
                self.skipTest('There are no storage resources available in '
                              'this environment.')
        sc_id = sc_keys[0].get(pc.STORAGE_CONT_ID)
        response = None
        for time_key in sr_keys:
            sr_id = time_key.get(pc.STORAGE_RES_ID)
            try:
                response = self.perf.get_storage_resource_stats(sc_id, sr_id,
                                                                pc.KPI)
                break
            except exception.VolumeBackendAPIException:
                continue
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response.get(pc.RESULT), list)

    def test_thin_pool_performance_function(self):
        """Test thin pool performance function."""
        category = pc.THIN_POOL
        id_tag = pc.POOL_ID
        key_func = self.perf.get_thin_pool_keys
        metrics_func = self.perf.get_thin_pool_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)

    def test_get_volume_stats_device_range(self):
        """Test get_volume_stats function."""
        start_time, end_time = self.perf.get_timestamp_by_hour(
            hours_difference=1)
        results = self.perf.get_volume_stats(
            start_time=start_time, end_time=end_time,
            volume_range_start='00123',
            volume_range_end='00123', data_format='Average')
        self.assertIn('result', results)

    def test_get_volume_stats_storage_group_list(self):
        """Test get volume stats function with storage groups."""
        start_time, end_time = self.perf.get_timestamp_by_hour(
            hours_difference=1)
        sg_list = self.conn.provisioning.get_storage_group_list()
        sg_list = sg_list[:5]
        results = self.perf.get_volume_stats(
            start_time=start_time, end_time=end_time,
            storage_group_list=sg_list, data_format='Average')
        self.assertIn('result', results)

    def test_zhyperlink_port_performance_function(self):
        """Test zHyperlink Port performance function."""
        if not self.is_v4:
            self.skipTest('zHyperlink Ports are not supported by V3 arrays')
        category = pc.ZHYPER_LINK_PORT
        id_tag = pc.PORT_ID
        key_func = self.perf.get_zhyperlink_port_keys
        metrics_func = self.perf.get_zhyperlink_port_stats
        self.run_performance_test_asserts(category, id_tag, key_func,
                                          metrics_func)
