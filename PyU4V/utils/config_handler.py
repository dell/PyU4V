# The MIT License (MIT)
# Copyright (c) 2019 Dell Inc. or its subsidiaries.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""config_handler.py."""

try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config
import logging
import logging.config
import os


def set_logger_and_config(file_path=None):
    """Set logger and config file."""
    cfg, conf_file, set_null_logger = None, None, True
    # register configuration file
    conf_file_name = 'PyU4V.conf'
    if file_path is not None:
        if os.path.isfile(file_path):
            conf_file = file_path
    elif os.path.isfile(conf_file_name):
        conf_file = conf_file_name
    else:
        global_path = os.path.normpath('~/.PyU4V/PyU4V.conf')
        if os.path.isfile(global_path):
            conf_file = global_path
    if conf_file is not None:
        set_null_logger = False
        try:
            cfg = Config.ConfigParser()
            cfg.read(conf_file)
            logging.config.fileConfig(conf_file)
            logging.getLogger(__name__)
        except Exception:
            set_null_logger = True
    if set_null_logger is True:
        # Set default logging handler to avoid "No handler found" warnings.
        try:  # Python 2.7+
            from logging import NullHandler
        except ImportError:
            class NullHandler(logging.Handler):
                def emit(self, record):
                    pass

        logging.getLogger(__name__).addHandler(NullHandler())

    return cfg
