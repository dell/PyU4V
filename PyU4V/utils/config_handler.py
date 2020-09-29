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
"""config_handler.py."""

try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config
import logging
import logging.config
import os


def set_logger_and_config(file_path=None):
    """Set logger and config file.

    :param file_path: path to PyU4V configuration file -- str
    :returns: config parser -- obj
    """
    cfg, conf_file = None, None
    # Get configuration file
    conf_file = _get_config_file(file_path)
    # Get configuration and logging settings
    if conf_file:
        cfg = _get_config_and_set_logger(conf_file)
    return cfg


def _get_config_file(file_path=None):
    """Get config file from file path, working directory, or ~/.PyU4V.

    :param file_path: path to file -- str
    :returns: config file path -- str
    """
    conf_file_name, conf_file = 'PyU4V.conf', None
    if file_path:
        if os.path.isfile(file_path):
            conf_file = file_path
    elif os.path.isfile(conf_file_name):
        conf_file = conf_file_name
    else:
        global_path = os.path.normpath('{home_path}/.PyU4V/PyU4V.conf'.format(
            home_path=os.path.expanduser('~')))
        if os.path.isfile(global_path):
            conf_file = global_path
    return conf_file


def _get_config_and_set_logger(file_path):
    """Get config file from file path, read settings, and set logger options.

    :param file_path: path to file -- str
    :returns: config parser -- obj
    """
    cfg = None
    try:
        cfg = Config.ConfigParser()
        cfg.read(file_path)
        logging.config.fileConfig(file_path)
        logging.getLogger(__name__)
    except Exception:
        logging.getLogger(__name__).addHandler(logging.NullHandler())
    return cfg
