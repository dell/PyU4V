# Copyright (c) 2019 Dell Inc. or its subsidiaries.
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
"""test_pyu4v_ci_common.py."""
import os
import re
import tempfile
import testtools

from unittest.mock import MagicMock

from PyU4V import common
from PyU4V.tests.ci_tests import base
from PyU4V.utils import constants

UNISPHERE_VERSION = constants.UNISPHERE_VERSION


class CITestCommon(base.TestBaseTestCase, testtools.TestCase):
    """Test Common."""

    def setUp(self):
        """setUp."""
        super(CITestCommon, self).setUp()
        self.common = self.conn.common
        self.provision = self.conn.provisioning

    def test_common_for_create_volume(self):
        """Test methods used by create volume operation.

        Test wait_for_job_complete is called
        Test get_job_by_id is called
        Test _is_job_finished is called
        Test check_status_code_success is called
        Test wait_for_job is called
        Test _build_uri is called
        Test get_request is called
        Test _build_uri_get_version is called
        Test get_resource is NOT called
        """
        common.CommonFunctions.wait_for_job_complete = MagicMock(
            side_effect=self.common.wait_for_job_complete)
        common.CommonFunctions.get_job_by_id = MagicMock(
            side_effect=self.common.get_job_by_id)
        common.CommonFunctions._is_job_finished = MagicMock(
            side_effect=self.common._is_job_finished)
        common.CommonFunctions.check_status_code_success = MagicMock(
            side_effect=self.common.check_status_code_success)
        common.CommonFunctions.wait_for_job = MagicMock(
            side_effect=self.common.wait_for_job)
        common.CommonFunctions._build_uri = MagicMock(
            side_effect=self.common._build_uri)
        common.CommonFunctions.get_request = MagicMock(
            side_effect=self.common.get_request)
        common.CommonFunctions._build_uri_get_version = MagicMock(
            side_effect=self.common._build_uri_get_version)
        common.CommonFunctions.get_resource = MagicMock(
            side_effect=self.common.get_resource)
        common.CommonFunctions.read_csv_values = MagicMock(
            side_effect=self.common.read_csv_values)

        self.create_volume()

        common.CommonFunctions.wait_for_job_complete.assert_called()
        common.CommonFunctions.get_job_by_id.assert_called()
        common.CommonFunctions._is_job_finished.assert_called()
        common.CommonFunctions.check_status_code_success.assert_called()
        common.CommonFunctions.wait_for_job.assert_called()
        common.CommonFunctions._build_uri.assert_called()
        common.CommonFunctions.get_request.assert_called()
        common.CommonFunctions._build_uri_get_version.assert_called()
        common.CommonFunctions.get_resource.assert_called()
        # One that is not called
        common.CommonFunctions.read_csv_values.assert_not_called()

    def test_common_for_modify_host(self):
        """"Test methods used by create host operation.

        Test create_resource is called
        Test modify_resource is called
        """
        self.conn.provisioning.create_resource = MagicMock(
            side_effect=self.common.create_resource)
        self.conn.provisioning.modify_resource = MagicMock(
            side_effect=self.common.modify_resource)
        self.modify_host()
        self.conn.provisioning.create_resource.assert_called()
        self.conn.provisioning.modify_resource.assert_called()

    def test_create_list_from_file(self):
        """Test file_handler.create_list_from_file."""
        # Initialise path strings for temporary file and directory
        temp_dir, file_path = str(), str()
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Create path for temporary file
            file_path = os.path.join(temp_dir, 'temp_list.txt')
            # Initialise empty string and set length of file contents (line
            # count)
            data, list_length = str(), 5
            # Create file contents
            for i in range(0, list_length):
                data += 'value-{i}\n'.format(i=i)
            # Write file contents to the temporary file path
            with open(file_path, 'w') as my_file:
                my_file.writelines(data)
            # Using the file just written to, read contents and return list
            my_list = self.common.create_list_from_file(file_path)
            # Assert return is a list and of the correct length
            self.assertIsInstance(my_list, list)
            self.assertEqual(list_length, len(my_list))
            # Cleanup temporary files
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
        # If there are any exceptions raised ensure cleanup is carried out on
        # temporary files
        except Exception as e:
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_read_csv_values(self):
        """Test read_csv_values."""
        # Initialise path strings for temporary file and directory
        temp_dir, file_path = str(), str()
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Create path for temporary CSV file
            pyu4v_path = os.path.join(temp_dir, 'temp_spread.csv')
            # Initialise empty string
            data = str()
            # Create file contents
            for i in range(0, 9):
                val = 'key' if i <= 2 else 'value'
                data += '{prefix}-{num}'.format(prefix=val, num=i)
                data += '\n' if (i + 1) % 3 == 0 else ','
            # Write file contents to the temporary file path
            with open(pyu4v_path, 'w') as file:
                file.writelines(data)
            # Using the file just written to, read contents and return dict
            read_contents = self.common.read_csv_values(pyu4v_path)
            # Assert return is a dict
            self.assertIsInstance(read_contents, dict)
            ref_contents = {'key-0': ['value-3', 'value-6'],
                            'key-1': ['value-4', 'value-7'],
                            'key-2': ['value-5', 'value-8']}
            # Assert CSV reader returned expected populated dict
            self.assertEqual(ref_contents, read_contents)
            # Cleanup temporary files
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=pyu4v_path, temp_dir=temp_dir)
        # If there are any exceptions raised ensure cleanup is carried out on
        # temporary files
        except Exception as e:
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_get_uni_version(self):
        """Test get_uni_version."""
        version, major_version = self.common.get_uni_version()
        major = UNISPHERE_VERSION[0] + '.' + UNISPHERE_VERSION[1]
        self.assertTrue(re.match(r'^T|V' + major + r'\S+$', version))
        self.assertEqual(UNISPHERE_VERSION, major_version)

    def test_get_array_list(self):
        """Test get_array_list."""
        array_list = self.common.get_array_list()
        self.assertTrue(isinstance(array_list, list))
        self.assertIn(self.conn.array_id, array_list)

    def test_get_v3_or_newer_array_list(self):
        """Test get_v3_or_newer_array_list."""
        array_list = self.common.get_v3_or_newer_array_list()
        self.assertTrue(isinstance(array_list, list))
        self.assertIn(self.conn.array_id, array_list)

    def test_get_array(self):
        """Test get_array."""
        array = self.common.get_array(self.conn.array_id)
        self.assertEqual(self.conn.array_id, array['symmetrixId'])

    def test_get_wlp_information(self):
        """Test wlp_information."""
        wlp_dict = self.common.get_wlp_information(self.conn.array_id)
        self.assertEqual(self.conn.array_id, wlp_dict['symmetrixId'])

    def test_get_headroom(self):
        """Test get_headroom."""
        headroom_list = self.common.get_headroom(self.conn.array_id)
        self.assertTrue(isinstance(headroom_list, list))
        for i in range(len(headroom_list)):
            self.assertTrue(
                set({'emulation': 'CKD'}.items()).issubset(
                    set(headroom_list[i].items())) or
                set({'emulation': 'FBA'}.items()).issubset(
                    set(headroom_list[i].items())))

    def test_get_iterator_results(self):
        """Test get_iterator_results."""
        start_time, end_time = self.conn.performance.extract_timestamp_keys(
            category='Array')
        result = self.conn.performance.get_array_stats(
            metrics='PercentReads', start_time=start_time, end_time=end_time)
        self.assertTrue(result)
        self.assertIsInstance(result, dict)
        if result and len(result.get('result')) <= 1000:
            self.skipTest(
                'Skipping test_get_iterator_results because there is not '
                'enough performance data collected. It takes just under four '
                'days to build up enough data to return more than 1000 '
                'performance results. There are currently only {cnt} '
                'performance intervals available'.format(
                    cnt=len(result.get('result'))))
        else:
            self.assertTrue(len(result.get('result')) > 1000)
