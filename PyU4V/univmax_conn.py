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
"""univmax_conn.py."""
import logging
import time

from PyU4V.common import CommonFunctions
from PyU4V.performance import PerformanceFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.replication import ReplicationFunctions
from PyU4V.rest_requests import RestRequests
from PyU4V.utils import config_handler
from PyU4V.utils import constants

file_path = None
CFG = config_handler.set_logger_and_config(file_path)
LOG = logging.getLogger(__name__)


class U4VConn(object):
    """U4VConn."""

    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=None,
                 u4v_version=constants.UNIVMAX_VERSION,
                 interval=5, retries=200, array_id=None):
        """__init__."""
        self.end_date = int(round(time.time() * 1000))
        self.start_date = (self.end_date - 3600000)
        self.array_id = array_id
        if not self.array_id:
            try:
                self.array_id = CFG.get('setup', 'array')
            except Exception:
                LOG.warning("No array id specified. Please set "
                            "array ID using the 'set_array_id(array_id)' "
                            "function.")
        if CFG is not None:
            if not username:
                username = CFG.get('setup', 'username')
            if not password:
                password = CFG.get('setup', 'password')
            if not server_ip:
                server_ip = CFG.get('setup', 'server_ip')
            if not port:
                port = CFG.get('setup', 'port')
        if verify is None:
            try:
                verify = CFG.get('setup', 'verify')
                if verify.lower() == 'false':
                    verify = False
                elif verify.lower() == 'true':
                    verify = True
            except Exception:
                verify = True
        base_url = "https://%s:%s/univmax/restapi" % (server_ip, port)
        self.rest_client = RestRequests(username, password, verify, base_url)
        self.request = self.rest_client.rest_request
        self.U4V_VERSION = u4v_version
        self.common = CommonFunctions(
            self.request, interval, retries, u4v_version)
        self.provisioning = ProvisioningFunctions(
            self.array_id, self.request, self.common, self.U4V_VERSION)
        self.performance = PerformanceFunctions(
            self.array_id, self.request, self.common,
            self.provisioning, self.U4V_VERSION)
        self.replication = ReplicationFunctions(
            self.array_id, self.request, self.common,
            self.provisioning, self.U4V_VERSION)

    def close_session(self):
        """Close the current rest session."""
        self.rest_client.close_session()

    def set_requests_timeout(self, timeout_value):
        """Set the requests timeout.

        :param timeout_value: the new timeout value - int
        """
        self.rest_client.timeout = timeout_value

    def set_array_id(self, array_id):
        """Set the array serial number.

        :param array_id: the array serial number
        """
        self.array_id = array_id
        self.performance.array_id = array_id
        self.provisioning.array_id = array_id
        self.replication.array_id = array_id
