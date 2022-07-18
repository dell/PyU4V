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
"""file_handler.py"""

import csv
import logging

from pathlib import Path

from PyU4V.utils import constants
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

FILE_WRITE_MODE = constants.FILE_WRITE_MODE


def create_list_from_file(file_name):
    """Given a file, create a list from its contents.

    :param file_name: the path to the file -- str
    :returns: file contents -- list
    """
    with open(file_name) as f:
        list_item = f.readlines()
    raw_list = map(lambda s: s.strip(), list_item)
    return list(raw_list)


def read_csv_values(file_name, convert=False, delimiter=',', quotechar='|'):
    """Read any csv file with headers.

    You can extract the multiple lists from the headers in the CSV file.
    In your own script, call this function and assign to data variable,
    then extract the lists to the variables. Example:
    data = fh.read_csv_values(mycsv.csv)
    sg_name_list = data['sgname']
    policy_list = data['policy']

    :param file_name: path to CSV file -- str
    :param convert: convert strings to equivalent data type -- bool
    :param delimiter: delimiter kwarg for csv DictReader object -- str
    :param quotechar: quotechar kwarg for csv DictReader object -- str
    :returns: CSV parsed data -- dict
    """

    def _convert(s):
        # Convert a string representation of a bool or number to equivalent
        # types that can be used in Python
        if convert:
            try:
                if s.lower() == 'true':
                    s = True
                elif s.lower() == 'false':
                    s = False
                else:
                    s = float(s)
            except ValueError:
                pass
        return s

    try:
        infile = None
        with open(file_name, newline='') as infile:
            # read the file as a dictionary for each row ({header : value})
            reader = csv.DictReader(
                infile, delimiter=delimiter, quotechar=quotechar)
            data = dict()
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(_convert(value))
                    except KeyError:
                        data[header] = [_convert(value)]
    except FileNotFoundError as ex:
        raise ex
    except IOError:
        return None
    finally:
        if infile:
            infile.close()
    return data


def write_to_csv_file(file_name, data, delimiter=',', quotechar='|'):
    """Write list data to CSV spreadsheet.

    :param file_name: name of the file to be written to -- str
    :param data: data to be written to file -- list
    :param delimiter: delimiter kwarg for csv writer object -- str
    :param quotechar: quotechar kwarg for csv writer object -- str
    """
    if data:
        with open(bytes(file_name, 'UTF-8'), 'wt', newline='') as csv_file:
            event_writer = csv.writer(csv_file,
                                      delimiter=delimiter,
                                      quotechar=quotechar,
                                      quoting=csv.QUOTE_MINIMAL)
            event_writer.writerow(data[0])
            remaining_data = data[1:]

        if remaining_data:
            with open(bytes(file_name, 'UTF-8'), 'a', newline='') as csv_file:
                event_writer = csv.writer(csv_file,
                                          delimiter=delimiter,
                                          quotechar=quotechar,
                                          quoting=csv.QUOTE_MINIMAL)
                for line in remaining_data:
                    event_writer.writerow(line)
        else:
            LOG.error('Only one line of data was provided for writing to CSV '
                      'file.')
    else:
        LOG.error('No data was provided to write to CSV file.')


def write_dict_to_csv_file(
        file_path, dictionary, delimiter=',', quotechar='|'):
    """Write dictionary data to CSV spreadsheet.

    :param file_path: path including name of the file to be written to -- str
    :param dictionary: data to be written to file -- dict
    :param delimiter: delimiter kwarg for csv writer object -- str
    :param quotechar: quotechar kwarg for csv writer object -- str
    """
    columns = list(dictionary.keys())
    num_values = 0
    for column in columns:
        col_length = len(dictionary.get(column))
        if col_length > num_values:
            num_values = col_length

    data_for_file = list()
    data_for_file.append(columns)
    for i in range(0, num_values):
        csv_line = list()
        for column in columns:
            csv_line.append(dictionary.get(column)[i])
        data_for_file.append(csv_line)

    write_to_csv_file(file_path, data_for_file, delimiter, quotechar)


def write_binary_data_to_file(data, file_extension, file_name, dir_path=None):
    """Write Unisphere binary data to file.

    :param data: Unisphere REST response with data for writing -- json response
    :param file_extension: file extension used for writing to file -- str
    :param file_name: file name -- str
    :param dir_path: file write directory path -- str
    :returns: file name and write directory -- str
    """
    # Set file write directory
    if dir_path:
        try:
            path = Path(dir_path)
            assert path.is_dir() is True
        except (TypeError, AssertionError) as error:
            msg = ('Invalid file path supplied for download '
                   'location: {f}'.format(f=dir_path))
            LOG.error(msg)
            raise exception.InvalidInputException(msg) from error
    else:
        # No path set, use current working directory
        path = Path.cwd()

    # Set download file name with .zip extension
    f_name = Path(file_name)
    pdf_name = f_name.with_suffix(file_extension)
    # Join directory & OS idempotent path
    file_write_path = Path.joinpath(path, pdf_name)

    # Write binary file data to zip file
    with open(file_write_path, FILE_WRITE_MODE) as fd:
        LOG.info('Writing settings to: {p}'.format(p=file_write_path))
        for chunk in data.iter_content(chunk_size=128):
            fd.write(chunk)

    LOG.info('File writing complete.')
    return file_write_path
