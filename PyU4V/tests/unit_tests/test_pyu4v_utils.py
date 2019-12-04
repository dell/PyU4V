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
"""test_pyu4v_utils.py."""
import configparser
import csv
import mock
import os
import six
import testtools

from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V.utils import config_handler
from PyU4V.utils import console
from PyU4V.utils import exception
from PyU4V.utils import file_handler


class PyU4VUtilsTest(testtools.TestCase):
    """Test common."""

    def setUp(self):
        """setUp."""
        super(PyU4VUtilsTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf = config_handler
        self.console = console
        self.file = file_handler
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file(
                'smc', 'smc', '10.0.0.75', '8443', self.data.array,
                False, True, True))

    def tearDown(self):
        """tearDown."""
        super(PyU4VUtilsTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    # utils.config_handler
    def test_set_logger_and_config(self):
        """Test test_set_logger_and_config."""
        user, password = 'smc', 'smc'
        ip, port = '10.0.0.75', '8443'
        verify = False
        array = self.data.array
        with mock.patch.object(self.conf, '_get_config_file',
                               return_value=self.conf_file):
            test_cfg = self.conf.set_logger_and_config()
            self.assertEqual(user, test_cfg.get('setup', 'username'))
            self.assertEqual(password, test_cfg.get('setup', 'password'))
            self.assertEqual(ip, test_cfg.get('setup', 'server_ip'))
            self.assertEqual(port, test_cfg.get('setup', 'port'))
            self.assertEqual(str(verify), test_cfg.get('setup', 'verify'))
            self.assertEqual(array, test_cfg.get('setup', 'array'))

    @mock.patch('os.path.isfile', return_value=True)
    def test_get_conf_file_with_path(self, mck_is_file):
        """Test test_get_conf_file_with_path."""
        conf_file_path = self.conf._get_config_file(file_path='path/to/file')
        self.assertEqual('path/to/file', conf_file_path)

    @mock.patch('os.path.isfile', return_value=True)
    def test_get_conf_file_no_path(self, mck_is_file):
        """Test test_get_conf_file_no_path."""
        conf_file_path = self.conf._get_config_file()
        self.assertEqual('PyU4V.conf', conf_file_path)

    @mock.patch('os.path.isfile', side_effect=[False, True])
    def test_get_conf_file_not_in_current_dir(self, mck_is_file):
        """Test test_get_conf_file_not_in_current_dir."""
        conf_file_path = self.conf._get_config_file()
        ref_path = os.path.normpath('{home_path}/.PyU4V/PyU4V.conf'.format(
            home_path=os.path.expanduser("~")))
        self.assertEqual(ref_path, conf_file_path)

    def test_get_config_and_set_logger(self):
        """Test test_get_config_and_set_logger."""
        ref_config = self.conf._get_config_and_set_logger(self.conf_file)
        self.assertIsInstance(ref_config, configparser.ConfigParser)

    def test_get_config_and_set_logger_nullhandler(self):
        """Test test_get_config_and_set_logger."""
        no_log_config, no_log_config_dir = (
            pf.FakeConfigFile.create_fake_config_file(write_log_config=False))
        ref_config = self.conf._get_config_and_set_logger(no_log_config)
        self.assertIsInstance(ref_config, configparser.ConfigParser)
        pf.FakeConfigFile.delete_fake_config_file(no_log_config,
                                                  no_log_config_dir)

    # utils.console
    @mock.patch('builtins.input', return_value='1')
    def test_choose_from_list(self, mck_input):
        """Test test_choose_from_list."""
        selection = self.console.choose_from_list('test', ['s1', 's2', 's3'])
        self.assertEqual('s2', selection)

    # utils.exception
    def test_default_error_msg(self):
        class FakePyU4VException(exception.PyU4VException):
            message = "default message"

        exc = FakePyU4VException()
        self.assertEqual('default message', six.text_type(exc))

    def test_error_msg(self):
        self.assertEqual(
            'test', six.text_type(exception.PyU4VException('test')))

    def test_default_error_msg_with_kwargs(self):
        class FakePyU4VException(exception.PyU4VException):
            message = "default message: %(code)s"

        exc = FakePyU4VException(code=500)
        self.assertEqual('default message: 500', six.text_type(exc))

    def test_error_msg_exception_with_kwargs(self):
        class FakePyU4VException(exception.PyU4VException):
            message = "default message: %(misspelled_code)s"

        exc = FakePyU4VException(code=500)
        self.assertEqual('default message: %(misspelled_code)s',
                         six.text_type(exc))

    def test_default_error_code(self):
        class FakePyU4VException(exception.PyU4VException):
            code = 404

        exc = FakePyU4VException()
        self.assertEqual(404, exc.kwargs['code'])

    def test_error_code_from_kwarg(self):
        class FakePyU4VException(exception.PyU4VException):
            code = 500

        exc = FakePyU4VException(code=404)
        self.assertEqual(404, exc.kwargs['code'])

    def test_error_msg_is_exception_to_string(self):
        msg = 'test message'
        exc1 = Exception(msg)
        exc2 = exception.PyU4VException(exc1)
        self.assertEqual(msg, exc2.msg)

    def test_exception_kwargs_to_string(self):
        msg = 'test message'
        exc1 = Exception(msg)
        exc2 = exception.PyU4VException(kwarg1=exc1)
        self.assertEqual(msg, exc2.kwargs['kwarg1'])

    def test_message_in_format_string(self):
        class FakePyU4VException(exception.PyU4VException):
            message = 'FakeCinderException: %(message)s'

        exc = FakePyU4VException(message='message')
        self.assertEqual('FakeCinderException: message', six.text_type(exc))

    def test_message_and_kwarg_in_format_string(self):
        class FakePyU4VException(exception.PyU4VException):
            message = 'Error %(code)d: %(message)s'

        exc = FakePyU4VException(message='message', code=404)
        self.assertEqual('Error 404: message', six.text_type(exc))

    def test_message_is_exception_in_format_string(self):
        class FakePyU4VException(exception.PyU4VException):
            message = 'Exception: %(message)s'

        msg = 'test message'
        exc1 = Exception(msg)
        exc2 = FakePyU4VException(message=exc1)
        self.assertEqual('Exception: test message', six.text_type(exc2))

    def test_exception_unicode(self):
        ref_exc = exception.PyU4VException()
        self.assertEqual(ref_exc.msg, ref_exc.__unicode__())

    # utils.file_handler
    @mock.patch('builtins.open', new_callable=mock.mock_open,
                read_data='Unit\nTest\nData')
    def test_create_list_from_file(self, mck_open):
        """Test test_create_list_from_file."""
        list_from_file = self.file.create_list_from_file(file_name='mock_file')
        self.assertEqual(['Unit', 'Test', 'Data'], list_from_file)
        mck_open.assert_called_with('mock_file')

    def test_create_list_from_file_fail(self):
        """Test test_create_list_from_file"""
        self.assertRaises(FileNotFoundError, self.file.create_list_from_file,
                          'no_file')

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_read_csv_values(self, mck_open):
        """Test read_csv_values."""
        csv_response = [
            {'kpi_a': '0.01', 'kpi_b': 'True'},
            {'kpi_a': '0.02', 'kpi_b': 'True'},
            {'kpi_a': '0.03', 'kpi_b': 'False'},
            {'kpi_a': 'mock', 'kpi_b': 'mock'}]

        with mock.patch.object(csv, 'DictReader', return_value=csv_response):
            csv_data = self.file.read_csv_values(file_name='mock_csv_file',
                                                 convert=True)
            reference_csv_response = {
                'kpi_a': [0.01, 0.02, 0.03, 'mock'],
                'kpi_b': [True, True, False, 'mock']}
            self.assertEqual(reference_csv_response, csv_data)

    def test_read_csv_values_fail(self):
        """Test test_create_list_from_file"""
        self.assertRaises(FileNotFoundError, self.file.read_csv_values,
                          'no_file')

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_write_to_csv_file(self, mck_open):
        """Test test_write_to_csv_file."""
        csv.writer = mock.Mock(writerow=mock.Mock())
        self.file.write_to_csv_file('test', [['kpi_a', 'kpi_b'],
                                             ['data_1', 'data_2'],
                                             ['data_3', 'data_4']])
        self.assertEqual(mck_open.call_count, 2)
        self.assertEqual(csv.writer.call_count, 2)
        self.assertEqual(csv.writer().writerow.call_count, 3)

    @mock.patch('PyU4V.utils.file_handler.LOG')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_write_to_csv_file_one_line(self, mck_open, mck_logger):
        """Test test_write_to_csv_file_one_line."""
        csv.writer = mock.Mock(writerow=mock.Mock())
        self.file.write_to_csv_file('test', [['kpi_a', 'kpi_b']])
        self.assertEqual(mck_open.call_count, 1)
        self.assertEqual(csv.writer.call_count, 1)
        self.assertEqual(csv.writer().writerow.call_count, 1)
        self.assertTrue(mck_logger.error.called)

    @mock.patch('PyU4V.utils.file_handler.LOG')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_write_to_csv_file_no_data(self, mck_open, mck_logger):
        """Test test_write_to_csv_file_no_data."""
        csv.writer = mock.Mock(writerow=mock.Mock())
        self.file.write_to_csv_file('test', list())
        self.assertEqual(mck_open.call_count, 0)
        self.assertEqual(csv.writer.call_count, 0)
        self.assertEqual(csv.writer().writerow.call_count, 0)
        self.assertTrue(mck_logger.error.called)

    def test_write_dict_to_csv_file(self):
        """Test write_dict_to_csv_file."""
        data_dict = {'col_1': [1, 2, 3, 4, 5], 'col_2': [6, 7, 8, 9, 10]}
        ref_csv_list = [['col_1', 'col_2'],
                        [1, 6], [2, 7], [3, 8], [4, 9], [5, 10]]
        with mock.patch.object(self.file, 'write_to_csv_file') as mck_csv:
            self.file.write_dict_to_csv_file('test.csv', data_dict)
            mck_csv.assert_called_once_with('test.csv', ref_csv_list)
