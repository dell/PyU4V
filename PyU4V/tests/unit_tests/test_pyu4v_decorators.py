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
"""Test PyU4V decorators."""

import inspect
import testtools

from unittest import mock

from PyU4V.performance import PerformanceFunctions
from PyU4V.utils import decorators


class PyU4VDecoratorsTest(testtools.TestCase):
    """Test PyU4V decorators."""

    def test_performance_recommendation_preserves_metadata(self):
        """Test the performance recommendation preserves function metadata."""
        def get_metrics(resource, array_id=None):
            """Get metrics for a resource."""
            return resource, array_id

        wrapped = decorators.performance_enhanced_recommendation(
            'PerformanceFunctions')(get_metrics)

        self.assertEqual(get_metrics.__name__, wrapped.__name__)
        self.assertEqual(get_metrics.__qualname__, wrapped.__qualname__)
        self.assertEqual(get_metrics.__module__, wrapped.__module__)
        self.assertEqual(get_metrics.__doc__, wrapped.__doc__)
        self.assertEqual(inspect.signature(get_metrics),
                         inspect.signature(wrapped))
        self.assertIs(get_metrics, wrapped.__wrapped__)

    @mock.patch.object(decorators.LOG, 'info')
    def test_performance_recommendation_forwards_call(self, mock_log):
        """Test the performance recommendation transparently forwards calls."""
        response = mock.sentinel.response

        def get_metrics(resource, array_id=None):
            """Get metrics for a resource."""
            self.assertEqual('Array', resource)
            self.assertEqual('000197800123', array_id)
            return response

        wrapped = decorators.performance_enhanced_recommendation(
            'PerformanceFunctions')(get_metrics)

        self.assertIs(
            response, wrapped('Array', array_id='000197800123'))
        mock_log.assert_called_once_with(
            'For improved usability and code efficiency by reducing the '
            'number of API calls, consider using performance_enhanced.py '
            'functions instead of PerformanceFunctions.get_metrics. For '
            'further information please consult the PyU4V documentation.')

    def test_performance_recommendation_propagates_exception(self):
        """Test the performance recommendation propagates exceptions."""
        expected_exception = RuntimeError('test failure')

        def get_metrics():
            """Get metrics for a resource."""
            raise expected_exception

        wrapped = decorators.performance_enhanced_recommendation(
            'PerformanceFunctions')(get_metrics)

        exc = self.assertRaises(RuntimeError, wrapped)
        self.assertIs(expected_exception, exc)

    def test_performance_method_exposes_original_metadata(self):
        """Test a decorated public performance method exposes its metadata."""
        method = PerformanceFunctions.get_array_stats

        self.assertEqual('get_array_stats', method.__name__)
        self.assertEqual(
            'PerformanceFunctions.get_array_stats', method.__qualname__)
        self.assertEqual('PyU4V.performance', method.__module__)
        self.assertIsNotNone(method.__doc__)
        self.assertEqual(
            "(self, metrics, array_id=None, data_format='Average', "
            "start_time=None, end_time=None, recency=None)",
            str(inspect.signature(method)))
        self.assertEqual(inspect.signature(method.__wrapped__),
                         inspect.signature(method))
