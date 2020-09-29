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
"""test_pyu4v_performance.py."""

import testtools
import time

from unittest import mock

from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V.tests.unit_tests import pyu4v_performance_data as pd
from PyU4V import univmax_conn
from PyU4V.utils import exception
from PyU4V.utils import performance_constants as pc


class PyU4VPerformanceTest(testtools.TestCase):
    """Test Unisphere real-time performance."""

    def setUp(self):
        """setUp."""
        super(PyU4VPerformanceTest, self).setUp()
        self.p_data = pd.PerformanceData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.p_data.array)
            self.perf = self.conn.performance
            self.rt = self.perf.real_time
            self.common = self.conn.common
            self.time_now = int(time.time()) * 1000

    def tearDown(self):
        """tearDown."""
        super(PyU4VPerformanceTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_set_array_id(self):
        """Test set_array_id."""
        array_id = self.p_data.remote_array
        self.rt.set_array_id(array_id)
        self.assertEqual(self.rt.array_id, array_id)

    def test_set_recency(self):
        """Test set_recency."""
        recency = 6
        self.rt.set_recency(recency)
        self.assertEqual(self.rt.recency, recency)

    def test_is_timestamp_current_true(self):
        """Test is_timestamp_current true condition."""
        self.rt.recency = 1
        self.assertTrue(self.rt.is_timestamp_current(timestamp=self.time_now))

    def test_is_timestamp_current_false(self):
        """Test is_timestamp_current false condition."""
        ten_mins_ago = self.time_now - (pc.ONE_MINUTE * 10)
        # Set recency to 20 so we know minutes input parm is overriding it
        self.rt.recency = 20
        self.assertFalse(self.rt.is_timestamp_current(timestamp=ten_mins_ago,
                                                      minutes=9))

    def test_get_categories(self):
        """Test get_categories."""
        response = self.rt.get_categories()
        ref_response = self.p_data.rt_categories.get(pc.CATEGORY_NAME)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(ref_response, response)

    def test_get_categories_empty(self):
        """Test get_categories no response empty list."""
        with mock.patch.object(
                self.rt, 'get_request', return_value=dict()):
            response = self.rt.get_categories()
            self.assertTrue(isinstance(response, list))
            self.assertEqual(list(), response)

    def test_get_category_metrics(self):
        """Test get_category_metrics."""
        response = self.rt.get_category_metrics(category=pc.ARRAY)
        ref_response = self.p_data.rt_metrics.get(pc.METRIC_NAME)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(ref_response, response)

    def test_get_category_metrics_empty(self):
        """Test get_category_metrics no response empty list."""
        with mock.patch.object(
                self.rt, 'get_request', return_value=dict()):
            response = self.rt.get_categories()
            self.assertTrue(isinstance(response, list))
            self.assertEqual(list(), response)

    def test_get_timestamps(self):
        """Test get_timestamps no array_id set."""
        response = self.rt.get_timestamps()
        self.assertTrue(isinstance(response, list))
        self.assertEqual(2, len(response))

    def test_get_timestamps_array_id(self):
        """Test get_timestamps array_id set."""
        response = self.rt.get_timestamps(array_id=self.p_data.array)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(1, len(response))
        self.assertEqual(self.p_data.array, response[0].get(pc.SYMM_ID))

    def test_get_category_keys(self):
        """Test get_category_keys."""
        response = self.rt.get_category_keys(category=pc.ARRAY)
        ref_response = self.p_data.rt_keys.get(pc.KEYS)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(ref_response, response)

    def test_get_category_keys_empty(self):
        """Test get_category_keys no response empty list."""
        with mock.patch.object(
                self.rt, 'post_request', return_value=dict()):
            response = self.rt.get_category_keys(category=pc.ARRAY)
            self.assertTrue(isinstance(response, list))
            self.assertEqual(list(), response)

    def test_validate_real_time_input_all_valid(self):
        """Test _validate_real_time_input."""
        start = self.time_now - pc.ONE_MINUTE
        self.rt.recency = 1
        self.rt._validate_real_time_input(
            start_date=start, end_date=self.time_now, category=pc.ARRAY,
            metrics=[pc.All_CAP], instance_id=self.p_data.array)

    def test_validate_real_time_input_invalid_category(self):
        """Test _validate_real_time_input invalid category input."""
        start = self.time_now - pc.ONE_MINUTE
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now, category='fake',
            metrics=[pc.All_CAP], instance_id=self.p_data.array)

    def test_validate_real_time_input_invalid_metric(self):
        """Test _validate_real_time_input invalid metric input."""
        start = self.time_now - pc.ONE_MINUTE
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now, category=pc.ARRAY,
            metrics=['fake_metric'], instance_id=self.p_data.array)

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
            metrics=[pc.All_CAP], instance_id=self.rt.array_id)

    def test_validate_real_time_input_delta_too_short(self):
        """Test _validate_real_time_input delta too short."""
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=self.time_now, end_date=self.time_now,
            category=pc.ARRAY, metrics=[pc.All_CAP],
            instance_id=self.rt.array_id)

    def test_validate_real_time_input_delta_too_long(self):
        """Test _validate_real_time_input delta too long."""
        start = self.time_now - (pc.ONE_HOUR + pc.ONE_MINUTE)
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=self.time_now,
            category=pc.ARRAY, metrics=[pc.All_CAP],
            instance_id=self.rt.array_id)

    def test_validate_real_time_input_timestamp_not_recent(self):
        """Test _validate_real_time_input timestamp not recent."""
        end = self.time_now - (pc.ONE_MINUTE * 10)
        start = end - pc.ONE_MINUTE
        self.rt.recency = 1
        self.assertRaises(
            exception.InvalidInputException, self.rt._validate_real_time_input,
            start_date=start, end_date=end, category=pc.ARRAY,
            metrics=[pc.All_CAP], instance_id=self.rt.array_id)

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
        self.rt.recency = 1
        start = self.time_now - pc.ONE_MINUTE
        category = pc.FE_DIR
        metrics = 'aLL'
        instance_id = self.p_data.fe_dir_id

        ref_params = {
            pc.SYMM_ID: self.rt.array_id, pc.START_DATE: start,
            pc.END_DATE: self.time_now, pc.CATEGORY: category,
            pc.METRICS: [pc.All_CAP], pc.INSTANCE_ID: instance_id}
        ref_response = {
            pc.ARRAY_ID: self.rt.array_id, pc.START_DATE_SN: start,
            pc.END_DATE_SN: self.time_now, pc.TIMESTAMP: self.time_now,
            pc.REAL_TIME_SN: True, pc.INSTANCE_ID_SN: instance_id,
            pc.REP_LEVEL: self.common.convert_to_snake_case(category),
            pc.RESULT: self.common.get_iterator_results(
                self.p_data.rt_perf_metrics)}

        with mock.patch.object(self.rt, '_validate_real_time_input'):
            with mock.patch.object(
                    self.rt, 'post_request',
                    return_value=self.p_data.rt_perf_metrics) as mck_post:
                response = self.rt.get_performance_data(
                    start_date=start, end_date=self.time_now,
                    category=category, metrics=metrics,
                    array_id=self.rt.array_id, instance_id=instance_id)
                mck_post.assert_called_once_with(
                    no_version=True, category=pc.PERFORMANCE,
                    resource_level=pc.REAL_TIME, resource_type=pc.METRICS,
                    payload=ref_params)
                self.assertEqual(ref_response, response)

    def test_get_array_metrics(self):
        """Test get_array_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_array_metrics()
            mck_get.assert_called_once_with(pc.ARRAY)

    def test_get_array_keys(self):
        """Test get_array_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_array_keys()
            mck_get.assert_called_once_with(pc.ARRAY)

    def test_get_array_stats(self):
        """Test get_array_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_array_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.ARRAY,
                metrics='All', array_id=self.rt.array_id)

    def test_get_backend_director_metrics(self):
        """Test get_backend_director_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_backend_director_metrics()
            mck_get.assert_called_once_with(pc.BE_DIR)

    def test_get_backend_director_keys(self):
        """Test get_backend_director_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_backend_director_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.BE_DIR, self.rt.array_id)

    def test_get_backend_director_stats(self):
        """Test get_backend_director_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_backend_director_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.be_dir_id, array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.BE_DIR,
                metrics='All', instance_id=self.p_data.be_dir_id,
                array_id=self.rt.array_id)

    def test_get_backend_port_metrics(self):
        """Test get_backend_port_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_backend_port_metrics()
            mck_get.assert_called_once_with(pc.BE_PORT)

    def test_get_backend_port_keys(self):
        """Test get_backend_port_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_backend_port_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.BE_PORT, self.rt.array_id)

    def test_get_backend_port_stats(self):
        """Test get_backend_port_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_backend_port_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.be_port_id, array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.BE_PORT,
                metrics='All', instance_id=self.p_data.be_port_id,
                array_id=self.rt.array_id)

    def test_get_external_director_metrics(self):
        """Test get_external_director_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_external_director_metrics()
            mck_get.assert_called_once_with(pc.EXT_DIR)

    def test_get_external_director_keys(self):
        """Test get_external_director_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_external_director_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.EXT_DIR, self.rt.array_id)

    def test_get_external_director_stats(self):
        """Test get_external_director_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_external_director_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.ext_dir_id, array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.EXT_DIR,
                metrics='All', instance_id=self.p_data.ext_dir_id,
                array_id=self.rt.array_id)

    def test_get_frontend_director_metrics(self):
        """Test get_frontend_director_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_frontend_director_metrics()
            mck_get.assert_called_once_with(pc.FE_DIR)

    def test_get_frontend_director_keys(self):
        """Test get_frontend_director_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_frontend_director_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.FE_DIR, self.rt.array_id)

    def test_get_frontend_director_stats(self):
        """Test get_frontend_director_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_frontend_director_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.fe_dir_id, array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.FE_DIR,
                metrics='All', instance_id=self.p_data.fe_dir_id,
                array_id=self.rt.array_id)

    def test_get_frontend_port_metrics(self):
        """Test get_backend_port_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_frontend_port_metrics()
            mck_get.assert_called_once_with(pc.FE_PORT)

    def test_get_frontend_port_keys(self):
        """Test get_frontend_port_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_frontend_port_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.FE_PORT, self.rt.array_id)

    def test_get_frontend_port_stats(self):
        """Test get_frontend_port_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_frontend_port_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.fe_port_id, array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.FE_PORT,
                metrics='All', instance_id=self.p_data.fe_port_id,
                array_id=self.rt.array_id)

    def test_get_rdf_director_metrics(self):
        """Test get_rdf_director_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_rdf_director_metrics()
            mck_get.assert_called_once_with(pc.RDF_DIR)

    def test_get_rdf_director_keys(self):
        """Test get_rdf_director_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_rdf_director_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.RDF_DIR, self.rt.array_id)

    def test_get_rdf_director_stats(self):
        """Test get_rdf_director_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_rdf_director_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.rdf_dir_id, array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.RDF_DIR,
                metrics='All', instance_id=self.p_data.rdf_dir_id,
                array_id=self.rt.array_id)

    def test_get_rdf_port_metrics(self):
        """Test get_rdf_port_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_rdf_port_metrics()
            mck_get.assert_called_once_with(pc.RDF_PORT)

    def test_get_rdf_port_keys(self):
        """Test get_rdf_port_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_rdf_port_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.RDF_PORT, self.rt.array_id)

    def test_get_rdf_port_stats(self):
        """Test get_rdf_port_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_rdf_port_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.rdf_port_id, array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.RDF_PORT,
                metrics='All', instance_id=self.p_data.rdf_port_id,
                array_id=self.rt.array_id)

    def test_get_storage_group_metrics(self):
        """Test get_storage_group_metrics."""
        with mock.patch.object(self.rt, 'get_category_metrics') as mck_get:
            self.rt.get_storage_group_metrics()
            mck_get.assert_called_once_with(pc.SG)

    def test_get_storage_group_keys(self):
        """Test get_storage_group_keys."""
        with mock.patch.object(self.rt, 'get_category_keys') as mck_get:
            self.rt.get_storage_group_keys(array_id=self.rt.array_id)
            mck_get.assert_called_once_with(pc.SG, self.rt.array_id)

    def test_get_storage_group_stats(self):
        """Test get_storage_group_stats."""
        start = self.time_now - pc.ONE_MINUTE
        with mock.patch.object(self.rt, 'get_performance_data') as mck_get:
            self.rt.get_storage_group_stats(
                start_date=start, end_date=self.time_now, metrics='All',
                instance_id=self.p_data.storage_group_id,
                array_id=self.rt.array_id)
            mck_get.assert_called_once_with(
                start_date=start, end_date=self.time_now, category=pc.SG,
                metrics='All', instance_id=self.p_data.storage_group_id,
                array_id=self.rt.array_id)
