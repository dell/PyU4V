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
"""univmax_conn.py."""

import logging
import sys
import time

from PyU4V.common import CommonFunctions
from PyU4V.migration import MigrationFunctions
from PyU4V.performance import PerformanceFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.replication import ReplicationFunctions
from PyU4V.rest_requests import RestRequests
from PyU4V.system import SystemFunctions
from PyU4V.utils import config_handler
from PyU4V.utils import constants
from PyU4V.utils import exception
from PyU4V.workload_planner import WLPFunctions

file_path = None
LOG = logging.getLogger(__name__)

SETUP = constants.SETUP
ARRAY = constants.ARRAY
R_ARRAY = constants.R_ARRAY
USERNAME = constants.USERNAME
PASSWORD = constants.PASSWORD
SERVER_IP = constants.SERVER_IP
PORT = constants.PORT
VERIFY = constants.VERIFY


class U4VConn(object):
    """U4VConn."""

    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=None,
                 u4v_version=constants.UNISPHERE_VERSION,
                 interval=5, retries=200, array_id=None,
                 application_type=None, remote_array=None):
        """__init__."""
        config = config_handler.set_logger_and_config(file_path)
        self.end_date = int(round(time.time() * 1000))
        self.start_date = (self.end_date - 3600000)
        self.array_id = array_id
        # Set array ID
        if not self.array_id:
            try:
                self.array_id = config.get(SETUP, ARRAY)
            except Exception:
                LOG.warning(
                    'No array id specified. Please set array ID using '
                    'U4VConn.set_array_id(array_id).')
        # Set environment config
        if config is not None:
            if not username:
                username = config.get(SETUP, USERNAME)
            if not password:
                password = config.get(SETUP, PASSWORD)
            if not server_ip:
                server_ip = config.get(SETUP, SERVER_IP)
            if not port:
                port = config.get(SETUP, PORT)
            # Optional Parameters for SRDF Remote array configurations
            if config.has_option(SETUP, R_ARRAY):
                if not remote_array:
                    self.remote_array = config.get(SETUP, R_ARRAY)
            else:
                self.remote_array = None

        # Set verification
        if verify is None:
            try:
                verify = config.get(SETUP, VERIFY)
                if verify.lower() == 'false':
                    verify = False
                elif verify.lower() == 'true':
                    verify = True
            except Exception:
                verify = True
        if None in [username, password, server_ip, port]:
            raise exception.MissingConfigurationException
        # Initialise REST session
        base_url = 'https://{server_ip}:{port}/univmax/restapi'.format(
            server_ip=server_ip, port=port)

        self.rest_client = RestRequests(
            username, password, verify, base_url, interval, retries,
            application_type)
        self.request = self.rest_client.rest_request
        self.common = CommonFunctions(self.rest_client)
        self.provisioning = ProvisioningFunctions(self.array_id,
                                                  self.rest_client)
        self.performance = PerformanceFunctions(self.array_id,
                                                self.rest_client)
        self.replication = ReplicationFunctions(self.array_id,
                                                self.rest_client)
        self.migration = MigrationFunctions(self.array_id,
                                            self.rest_client)
        self.wlp = WLPFunctions(self.array_id,
                                self.rest_client)
        self.system = SystemFunctions(self.array_id, self.rest_client)
        self.validate_unisphere()

    def close_session(self):
        """Close the current rest session."""
        self.rest_client.close_session()

    def set_requests_timeout(self, timeout_value):
        """Set the requests timeout.

        :param timeout_value: the new timeout value -- int
        """
        self.rest_client.timeout = timeout_value

    def set_array_id(self, array_id):
        """Set the array serial number.

        :param array_id: the array serial number -- str
        """
        self.array_id = array_id
        self.performance.array_id = array_id
        self.provisioning.array_id = array_id
        self.replication.array_id = array_id
        self.migration.array_id = array_id
        self.wlp.array_id = array_id
        self.system.array_id = array_id

    def validate_unisphere(self):
        """Check that the minimum version of Unisphere is in-use.

        If the version of Unisphere used does not meet minimum requirements
        the application will exit gracefully.

        :raises: SystemExit
        """
        uni_ver, major_ver = self.common.get_uni_version()
        if int(major_ver) < int(constants.UNISPHERE_VERSION):
            msg = ('Unisphere version {uv} does not meet the minimum '
                   'requirement of v9.1.0.x. Please upgrade your version of '
                   'Unisphere to use this SDK. Exiting...'.format(uv=uni_ver))
            sys.exit(msg)
        else:
            LOG.debug('Unisphere version {uv} passes minimum requirement'
                      'check.'.format(uv=uni_ver))
