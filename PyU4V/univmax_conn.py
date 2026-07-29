# Copyright (c) 2026 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
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
from PyU4V.common import CommonFunctions, normalize_u4v_version
from PyU4V.clone import CloneFunctions
from PyU4V.metro_dr import MetroDRFunctions
from PyU4V.migration import MigrationFunctions
from PyU4V.performance import PerformanceFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.replication import ReplicationFunctions
from PyU4V.rest_requests import RestRequests
from PyU4V.snapshot import SnapshotFunctions
from PyU4V.snapshot_policy import SnapshotPolicyFunctions
from PyU4V.srdf import SRDFFunctions
from PyU4V.serviceability import ServiceabilityFunctions
from PyU4V.settings import SettingsFunctions
from PyU4V.system import SystemFunctions
from PyU4V.utils import config_handler
from PyU4V.utils import constants
from PyU4V.utils import exception
from PyU4V.workload_planner import WLPFunctions
from PyU4V.volumes import VolumesFunctions
from PyU4V.storage_groups import StorageGroupsFunctions
from PyU4V.performance_enhanced import EnhancedPerformanceFunctions
from PyU4V.enhanced_api import EnhancedAPIFunctions
from PyU4V.version import MAJOR_VERSION, API_VERSION

file_path = None
app_type = 'PyU4V-{v}'.format(v=constants.PYU4V_VERSION)
LOG = logging.getLogger(__name__)

SETUP = constants.SETUP
ARRAY = constants.ARRAY
R_ARRAY = constants.R_ARRAY
R_ARRAY_2 = constants.R_ARRAY_2
USERNAME = constants.USERNAME
PASSWORD = constants.PASSWORD
SERVER_IP = constants.SERVER_IP
PORT = constants.PORT
VERIFY = constants.VERIFY
MAJOR_VERSION = MAJOR_VERSION


class U4VConn(object):
    """U4VConn."""

    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=None,
                 u4v_version=None,
                 interval=5, retries=200, array_id=None,
                 application_type=app_type, remote_array=None,
                 remote_array_2=None, proxies=None, timeout=None,
                 api_key=None, skip_version_check=False):
        """__init__.
        Persist user-specified u4v_version across all calls.

        :param skip_version_check: When True, the minimum Unisphere version
                                   check is skipped and any custom
                                   ``u4v_version`` is accepted without failing
                                   validation. API calls default to the
                                   packaged version (see ``version.py``) unless
                                   a ``u4v_version`` is supplied, in which case
                                   that version is used for API calls. Requests
                                   unsupported at the resolved version return
                                   the server error (e.g. 404) for the caller
                                   to handle. Defaults to False. -- bool
        """
        config = config_handler.set_logger_and_config(file_path)
        self.end_date = int(round(time.time() * 1000))
        self.start_date = (self.end_date - 3600000)
        self.array_id = array_id
        self.remote_array = remote_array
        self.remote_array_2 = remote_array_2
        self.timeout = timeout if timeout is not None else 120
        # Cache of server-supported API versions, populated lazily by
        # validate_unisphere() when a custom API version is in use.
        self.supported_api_versions = None

        # When True, relax version validation: skip the minimum version check
        # and accept a custom u4v_version without failing (logs a warning
        # instead of exiting). May also be set via config [setup]
        # skip_version_check.
        self.skip_version_check = bool(skip_version_check)

        # Track custom API version intent
        if u4v_version:
            self.u4v_version = normalize_u4v_version(u4v_version)
            self.custom_api_version = True
        else:
            self.u4v_version = None
            self.custom_api_version = False

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
            # Explicit token authentication takes precedence over basic
            # credentials from the configuration file. Explicitly supplied
            # username/password values are still retained for compatibility,
            # but RestRequests will prefer the token when both are present.
            if not api_key:
                if not username:
                    username = config.get(SETUP, USERNAME)
                if not password:
                    password = config.get(SETUP, PASSWORD)
            if not server_ip:
                server_ip = config.get(SETUP, SERVER_IP)
            if not port:
                port = config.get(SETUP, PORT)

            # Optional Parameters for SRDF Remote array configurations
            if config.has_option(SETUP, R_ARRAY) and not remote_array:
                self.remote_array = config.get(SETUP, R_ARRAY)
            if config.has_option(SETUP, R_ARRAY_2) and not remote_array_2:
                self.remote_array_2 = config.get(SETUP, R_ARRAY_2)

            if config.has_option(SETUP, 'timeout') and timeout is None:
                self.timeout = int(config.get(SETUP, 'timeout'))

            if (config.has_option(SETUP, 'skip_version_check') and not
                    self.skip_version_check):
                self.skip_version_check = config.getboolean(
                    SETUP, 'skip_version_check')
                LOG.debug('skip_version_check sourced from config [setup]: %s',
                          self.skip_version_check)

            if (config.has_option(SETUP, 'u4v_version') and not (
                    self.custom_api_version)):
                self.u4v_version = normalize_u4v_version(
                    config.get(SETUP, 'u4v_version'))

                self.custom_api_version = True
                LOG.debug('u4v_version sourced from config [setup]: %s',
                          self.u4v_version)

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

        missing_server = server_ip is None or port is None
        missing_auth = not api_key and (
            username is None or password is None)
        if missing_server or missing_auth:
            # A server and either username/password or an API key are
            # required for both REST clients.
            raise exception.MissingConfigurationException

        # Initialise REST sessions
        base_url = f'https://{server_ip}:{port}/univmax/restapi'
        enhanced_api_url = f'https://{server_ip}:{port}/univmax/rest'

        self.rest_client = RestRequests(
            username=username, password=password, verify=verify,
            base_url=base_url, interval=interval, retries=retries,
            application_type=application_type, proxies=proxies,
            timeout=self.timeout, token=api_key)

        # Enhanced client
        self.enhanced_rest_client = RestRequests(
            username=username, password=password, verify=verify,
            base_url=enhanced_api_url, interval=interval, retries=retries,
            application_type=application_type, proxies=proxies,
            timeout=self.timeout, token=api_key)

# Persist version on clients so any downstream CommonFunctions can pick it up
        self.rest_client.u4v_version = self.u4v_version
        self.enhanced_rest_client.u4v_version = self.u4v_version

        # Request shortcut
        self.request = self.rest_client.rest_request

# CommonFunctions honors the passed version (or the rest_client attribute)
        self.common = CommonFunctions(self.rest_client, self.u4v_version)

        # Validate Unisphere (skip minimum check if custom version specified)
        self.validate_unisphere()

        # Initialize feature modules (no need to pass u4v_version; they will
        # use CommonFunctions internally, which reads rest_client.u4v_version)
        self.clone = CloneFunctions(self.array_id, self.rest_client)
        self.provisioning = ProvisioningFunctions(self.array_id,
                                                  self.rest_client)
        self.performance = PerformanceFunctions(self.array_id,
                                                self.rest_client)
        self.replication = ReplicationFunctions(self.array_id,
                                                self.rest_client)
        self.snapshot = SnapshotFunctions(self.array_id,
                                          self.rest_client)
        self.srdf = SRDFFunctions(self.array_id, self.rest_client)
        # Share the single snapshot/srdf instances with the replication
        # module so that set_array_id() and UNI_VERSION propagation reach
        # the delegated (deprecated) conn.replication.* calls.
        self.replication._snapshot = self.snapshot
        self.replication._srdf = self.srdf
        self.snapshot.common = self.replication.common
        self.srdf.common = self.replication.common
        self.metro_dr = MetroDRFunctions(self.array_id,
                                         self.rest_client)
        self.migration = MigrationFunctions(self.array_id,
                                            self.rest_client)
        self.wlp = WLPFunctions(self.array_id, self.rest_client)
        self.snapshot_policy = SnapshotPolicyFunctions(self.array_id,
                                                       self.rest_client)
        self.system = SystemFunctions(self.array_id, self.rest_client)
        self.serviceability = ServiceabilityFunctions(self.array_id,
                                                      self.rest_client)
        self.performance_enhanced = EnhancedPerformanceFunctions(
            self.array_id, self.enhanced_rest_client)
        self.volumes = VolumesFunctions(
            self.array_id, self.enhanced_rest_client)
        self.storage_groups = StorageGroupsFunctions(
            self.array_id, self.enhanced_rest_client)
        self.enhanced_api = EnhancedAPIFunctions(
            self.array_id, self.enhanced_rest_client)
        self.settings = SettingsFunctions(self.array_id, self.rest_client)

    def close_session(self):
        """Close the current rest session."""
        self.rest_client.close_session()
        self.enhanced_rest_client.close_session()

    def set_requests_timeout(self, timeout_value):
        """Set the requests timeout.
        :param timeout_value: the new timeout value -- int
        """
        self.rest_client.timeout = timeout_value
        self.enhanced_rest_client.timeout = timeout_value

    def set_array_id(self, array_id):
        """Set the array serial number.
        :param array_id: the array serial number -- str
        """
        self.array_id = array_id
        components = [
            self.clone, self.provisioning, self.performance,
            self.replication, self.snapshot, self.srdf, self.metro_dr,
            self.migration, self.wlp, self.snapshot_policy, self.system,
            self.serviceability, self.performance_enhanced, self.volumes,
            self.storage_groups, self.enhanced_api, self.settings,
        ]
        child_attributes = ('provisioning', 'real_time', '_snapshot', '_srdf')
        visited = set()

        while components:
            component = components.pop()
            component_id = id(component)
            if component_id in visited:
                continue
            visited.add(component_id)

            set_component_array = getattr(component, 'set_array_id', None)
            if callable(set_component_array):
                set_component_array(array_id)
            else:
                component.array_id = array_id

            for attribute in child_attributes:
                child = getattr(component, attribute, None)
                if child is not None:
                    components.append(child)

    def set_u4v_version(self, version: str):
        """Update the Unisphere API version and propagate.

        The version is stamped onto the two shared REST clients only. Every
        feature module resolves the version live via ``common.UNI_VERSION``
        (a property backed by ``rest_client.u4v_version``), so there is a
        single source of truth and no per-module update is required.

        :param version: Unisphere REST API version, or falsy to reset to the
                        packaged default -- str
        """
        self.u4v_version = normalize_u4v_version(version) if version else None
        self.custom_api_version = bool(version)

        # Single source of truth: stamp both shared clients.
        self.rest_client.u4v_version = self.u4v_version
        self.enhanced_rest_client.u4v_version = self.u4v_version

    def validate_unisphere(self):
        """Check that the minimum version of Unisphere is in-use.
        If the version of Unisphere used does not meet minimum requirements
        the application will exit gracefully, unless ``skip_version_check``
        is enabled, in which case a warning is logged and execution continues
        using the resolved API version (``u4v_version`` if supplied, otherwise
        the packaged default). Unsupported requests may then return server
        errors (e.g. 404) for the caller to handle.
        :raises: SystemExit
        """
        uni_ver, major_ver = self.common.get_uni_version()
        if self.custom_api_version:
            LOG.debug('A Custom API Version has been specified.')
            # Validate that the specified u4v_version is supported by the
            # server. Cache the supported versions for reuse.
            version_info = self.common.get_uni_version_info()
            supported_versions = version_info.get('supported_api_versions', [])
            self.supported_api_versions = supported_versions
            if self.u4v_version not in supported_versions:
                unsupported_msg = (
                    f'API version {self.u4v_version} is not supported by this '
                    f'Unisphere server. Supported versions: '
                    f'{supported_versions}. '
                    f'Exiting...')
                if self.skip_version_check:
                    LOG.warning(
                        'API version %s is not in the server-supported '
                        'versions %s. Continuing anyway because '
                        'skip_version_check is enabled; unsupported requests '
                        'may return errors (e.g. 404).',
                        self.u4v_version, supported_versions)
                else:
                    sys.exit(unsupported_msg)
        elif int(major_ver) < int(API_VERSION):
            msg = (
                f'Unisphere version {uni_ver} does not meet the minimum '
                f'requirement of v{MAJOR_VERSION} Please upgrade your '
                f'version of Unisphere to use this SDK. Exiting...')
            if self.skip_version_check:
                LOG.warning(
                    'Unisphere version %s does not meet the minimum '
                    'requirement of v%s, but skip_version_check is enabled. '
                    'API calls will use version %s; unsupported requests may '
                    'return errors (e.g. 404).',
                    uni_ver, MAJOR_VERSION, self.common.UNI_VERSION)
            else:
                sys.exit(msg)
        else:
            LOG.debug('Unisphere version {uv} passes minimum requirement '
                      'check.'.format(uv=uni_ver))
