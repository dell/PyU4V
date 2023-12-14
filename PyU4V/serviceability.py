# Copyright (c) 2023 Dell Inc. or its subsidiaries.
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
"""serviceability.py."""

import logging
import time

from datetime import datetime
from pathlib import Path

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants
from PyU4V.utils import file_handler
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

SERVICEABILITY = constants.SERVICEABILITY
SYMMETRIX = constants.SYMMETRIX
SERVICEABILITY_LOG_FILENAME_TEMPLATE = \
    constants.SERVICEABILITY_LOG_FILENAME_TEMPLATE
STR_TIME_FORMAT = constants.STR_TIME_FORMAT
PDF_SUFFIX = constants.PDF_SUFFIX
SERVICEABILITY_LOG_FILENAME = constants.SERVICEABILITY_LOG_FILENAME
SERVICEABILITY_LOG_RECORD = constants.SERVICEABILITY_LOG_RECORD
SERVICEABILITY_EXPORT_FILE = constants.SERVICEABILITY_EXPORT_FILE
BINARY_DATA = constants.BINARY_DATA
SUCCESS = constants.SUCCESS
SERVICEABILITY_RECORD_PATH = constants.SERVICEABILITY_RECORD_PATH
SERVICEABILITY_RECORD_TIME = constants.SERVICEABILITY_RECORD_TIME
DEFAULT_NODE_NAME = constants.DEFAULT_NODE_NAME
IP_CONFIGURATION = constants.IP_CONFIGURATION
UPDATEIPV4 = constants.UPDATEIPV4
UPDATEIPV6 = constants.UPDATEIPV6
APPLICATION = constants.APPLICATION
UNISPHERE = constants.UNISPHERE
CONFIGURATION = constants.CONFIGURATION
SYSTEM = constants.SYSTEM
VASA = constants.VASA
DEFAULT_VASA = constants.DEFAULT_VASA
SOLUTIONS_ENABLER = constants.SOLUTIONS_ENABLER
ZIP_SUFFIX = constants.ZIP_SUFFIX
ALLOW_SERVICE_ACCESS = constants.ALLOW_SERVICE_ACCESS
CUSTOM_CERTIFICATE = constants.CUSTOM_CERTIFICATE
IMPORT = constants.IMPORT
SELF_SIGNED_CERTIFICATE = constants.SELF_SIGNED_CERTIFICATE
FILE_READ_MODE = constants.FILE_READ_MODE


class ServiceabilityFunctions(object):

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.get_request = self.common.get_request
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.upload_file = self.common.upload_file
        self.array_id = array_id
        self.version = constants.UNISPHERE_VERSION

    def get_local_system(self):
        """Get local powermax system serial number in the embedded environment
        with version v4 or higher.
        :returns: symmetrix id -- dict
        """
        return self.get_request(
            target_uri=f"/{self.version}/serviceability/symmetrix",
            resource_type=None)

    def get_ntp_settings(self, array_id=None):
        """Get current NTP server configuration.

        :param array_id: array id -- str
        :returns: ntp server -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(f"/{self.version}/serviceability/symmetrix/"
                                f"{array_id}", resource_type=None)

    def modify_ntp_settings(self, ntp_server, array_id=None):
        """Set a new NTP server information.

        This call will restart SMAS Service so Unisphere and REST will be
        unavailable while the configuration change takes effect please do not
        attempt any other calls until this has completed and changes have
        been verified.

        :param ntp_server: ntp server URL --str
        :param array_id: array id --str
        :returns: ntp server -- dict
        """
        payload = {'ntp_server': ntp_server}
        array_id = self.array_id if not array_id else array_id
        return self.common.modify_resource(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}",
            resource_type=None, payload=payload)

    def download_grab_files(self, array_id=None,
                            node_name=DEFAULT_NODE_NAME,
                            return_binary=False,
                            dir_path=None,
                            file_name=None,
                            timeout=None):
        """Download serviceability logs

        :param array_id: array serial number -- str
        :param node_name: Node name. Allowable values are Unisphere, Vasa0,
                          Vasa1, Vasadb, Semgmt0, Semgmt1  -- str
        :param return_binary: return binary data instead of writing audit
                              log record pdf to file -- bool
        :param dir_path: file write directory path, eg. "." will write to
                         script execution directory -- str
        :param file_name: file name, file exension .tar.gz will be applied
                          by the function -- str
        :param timeout: timeout, recommend setting a long timeout value as
                        grab file generation can take some time, e.g. 1000
                        -- int
        :returns: download details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        date_time = datetime.fromtimestamp(time.time())

        if not file_name:
            file_name = {SERVICEABILITY_LOG_FILENAME_TEMPLATE}

        req_body = {'node_name': node_name}

        response = self.common.download_file(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/export",
            resource_type=None, payload=req_body, timeout=timeout)

        return_dict = dict()

        # Return binary data, do not write to file
        if return_binary:
            return_dict[BINARY_DATA] = response.content
        # Write to file
        else:
            file_path = file_handler.write_binary_data_to_file(
                data=response, file_extension='.tar.gz', file_name=file_name,
                dir_path=dir_path)
            return_dict[SERVICEABILITY_RECORD_PATH] = file_path

        return_dict[SUCCESS] = True
        return_dict[SERVICEABILITY_RECORD_TIME] = date_time
        LOG.info('The serviceability log download request was successful.')

        return return_dict

    def get_ip_configuration(self, array_id=None):
        """Get current IPv4 information of U4P, VASA and SE and
        IPv6 information of U4P and SE.

        :param array_id: array id -- str
        :returns: IPInformation -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/ip_configuration", resource_type=None)

    def update_ip_configuration(self, array_id=None, action=None,
                                natone_ip_address=None, natone_netmask=None,
                                natone_gateway=None, nattwo_ip_address=None,
                                nattwo_netmask=None, nattwo_gateway=None):
        """Set new IPv4 information of U4P, VASA and SE. and set new
        IPv6 information of U4P and SE.

        During the NAT IP PUT operation, the existing Unisphere/REST server
        will restart and with New IP address.

        Please do not attempt any other calls until this has completed and
        changes have been verified.

        :param array_id: array id -- str
        :param action: update Options to modify (UpdateIPV4 or UpdateIPV6)
                       -- str
        :param natone_ip_address: primary ip address for unisphere
                                  instance connecting to port on node 1
                                  of array either IPV4 or IPV6 -- str
        :param natone_netmask: netmask for natone ip address -- str
        :param natone_gateway: gateway for natone ip address IPv4 or IPv6
                               -- str
        :param nattwo_ip_address: secondary ip address for unisphere
                                  instance connecting to port on node 2
                                  of array either IPV4 or IPV6 -- str
        :param nattwo_netmask: netmask for secondary IP connection either
                               IPV4 or IPV6 -- str
        :param nattwo_gateway: gateway for secondary IP connection either
                               IPV4 or IPV6 -- str
        :returns: IPInformation -- dict

        """
        payload = {}
        if action == UPDATEIPV4:
            payload = {
                'action': action,
                'update_ipv4': {
                    "natone_ip_address_ipv4": natone_ip_address,
                    "natone_netmask_ipv4": natone_netmask,
                    "natone_gateway_ipv4": natone_gateway,
                    "nattwo_ip_address_ipv4": nattwo_ip_address,
                    "nattwo_netmask_ipv4": nattwo_netmask,
                    "nattwo_gateway_ipv4": nattwo_gateway
                }
            }
        elif action == UPDATEIPV6:
            payload = {
                'action': action,
                'update_ipv6': {
                    "natone_ip_address_ipv6": natone_ip_address,
                    "natone_netmask_ipv6": natone_netmask,
                    "natone_gateway_ipv6": natone_gateway,
                    "nattwo_ip_address_ipv6": nattwo_ip_address,
                    "nattwo_netmask_ipv6": nattwo_netmask,
                    "nattwo_gateway_ipv6": nattwo_gateway,
                }
            }
        array_id = self.array_id if not array_id else array_id
        return self.modify_resource(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/ip_configuration", resource_type=None,
            payload=payload)

    def get_application(self, array_id=None):
        """Get a list of all embedded applications running on the array.

        :param array_id: array id -- str
        :returns: ApplicationInformation -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application", resource_type=None)

    def get_unisphere_application_details(self, array_id=None):
        """Get a list of information about Unisphere node.
        Get the access Id along with Unisphere server access.

        :param array_id: array id -- str
        :returns: UnisphereInformation -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/unisphere", resource_type=None)

    def modify_unisphere_service_access(self, action, array_id=None):
        """Enables Unisphere server access for remote support assistance.

        :param action: Unisphere server access options such as
                       AllowServerAccess and BlockServerAccess  --str
        :returns: ntp server -- dict
        """
        payload = {'action': action}
        array_id = self.array_id if not array_id else array_id
        return self.common.modify_resource(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/unisphere", resource_type=None,
            payload=payload)

    def restart_unisphere_application(self, array_id=None):
        """Restart the Unisphere server.

        Please do not attempt any other calls until this has completed
        and changes have been verified.

        :param array_id: array id --str
        :returns: will not return as Unisphere server restarts.

        """
        payload = {'action': 'RestartUnisphere'}
        array_id = self.array_id if not array_id else array_id
        return self.common.create_resource(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/unisphere", resource_type=None,
            payload=payload)

    def get_unisphere_configuration(self, array_id=None):
        """Get Unisphere configuration information.

        :param array_id: array id -- str
        :returns: ConfigArray -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/unisphere/configuration",
            resource_type=None)

    def get_symavoid_settings(self, array_id=None):
        """Get a list of available symmetrix and symavoid symmetrix.

        :param array_id: array id -- str
        :returns: UnisphereInformation -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(
            f"/{self.version}/serviceability/symmetrix/"
            f"{self.array_id}/application/unisphere/system",
            resource_type=None)

    def update_symavoid_settings(self, array_id=None,
                                 action=None, symm_list=None):
        """Add to symavoid list or remove a symmetrix from the symavoid list

        :param array_id: array id -- str
        :param action: AddToSymmavoid or RemoveFromSymmavoid, case sensitive
                       -- str
        :param symm_list: list of symms -- list
        :returns: IPInformation -- dict
        """
        payload = {}
        if action == 'AddToSymmavoid':
            payload = {
                'action': action,
                'add_to_symmavoid':
                    {
                        "symm_list": symm_list
                    }
            }
        elif action == 'RemoveFromSymmavoid':
            payload = {
                'action': action,
                'remove_from_symmavoid':
                    {
                        "symm_list": symm_list
                    }
            }

        array_id = self.array_id if not array_id else array_id
        return self.modify_resource(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/unisphere/system", resource_type=None,
            payload=payload)

    def get_solutions_enabler_application(self, array_id=None):
        """Get a list of information on each SE node and get the access Id,
        this function also returns se_nethost configuration for client
        server access.

        :param array_id: array id -- str
        :returns: SEInformation -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/solutions_enabler",
            resource_type=None)

    def modify_nethosts(self, action, host_name, user, array_id=None):
        """ Add or remove user and host to nethosts file for client server
        configuration.

        Current configuration can be checked with
        get_solutions_enabler_application() function

        :param action: add or remove - str
        :param host_name: name or ip of host to be added/rmoved to/from
                          nethost file -- str
        :param user: username to be granted access -- str
        :param array_id: array_id -- str
        :returns: net host configuration -- dict
        """

        array_id = self.array_id if not array_id else array_id
        if action.lower() == 'add':
            action = 'AddNethost'
            payload_action = 'add_nethost'
        elif action.lower() == 'remove':
            action = 'DeleteNethost'
            payload_action = 'delete_nethost'

        payload = {"action": action,
                   payload_action:
                       {
                           "node_name": host_name,
                           "user": user
                       }}
        return self.modify_resource(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/solutions_enabler",
            resource_type=None, payload=payload)

    def get_solutions_enabler_configuration(self, array_id=None):
        """Get SE base configuration values that are available in SE settings.

        :param array_id: array id -- str
        :returns: SEConfigInformation -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_request(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/solutions_enabler/configuration",
            resource_type=None)

    def modify_solutions_enabler_configuration(
            self, array_id=None, allow_symforce=None, use_access_id=None):
        """set SE configuration values.

        :param array_id: array id -- str
        :param allow_symforce: Indicates whether users can specify -symforce
                               when performing RDF control operations. The
                               allowable values for this option are TRUE and
                               FALSE. The default setting is FALSE. Changing
                               this value requires unisphere to be restarted
                               before it will take effect in the UI --bool
        :param use_access_id: This option applies to Symmetrix Access Control.
                              It specifies whether to use the access ID
                              generated on client or server. Used only on the
                              server side during client/server operations.
                              Possible values are: CLIENT: The client access
                              ID is used for every command performed. If a
                              client access ID is not available the command
                              will fail. SERVER: The server access ID is used
                              for every command performed. ANY:
                              If the client access ID is available it is used
                              for every command performed.
                              If it is not available then the server access ID
                              is used. The default setting is SERVER. --str
        :returns: ConfigArray -- dict
        """
        payload = {
            'se_base_configuration': {
                'general_symapi_options': {}}}
        if allow_symforce is not None:
            payload['se_base_configuration']['general_symapi_options'][
                'SYMAPI_ALLOW_RDF_SYMFORCE'] = allow_symforce
        if use_access_id is not None:
            payload['se_base_configuration']['general_symapi_options'][
                'SYMAPI_USE_ACCESS_ID'] = use_access_id
        array_id = self.array_id if not array_id else array_id
        return self.modify_resource(
            target_uri=f"/{self.version}/serviceability/symmetrix/{array_id}"
                       f"/application/solutions_enabler/configuration",
            resource_type=None, payload=payload)

    def import_custom_certificate(
            self, array_id=None, node_name=None, keyfile=None, certfile=None,
            trustfile=None):
        """Import custom certificate.

        :param array_id: array id -- str
        :param node_name: Specify the node name (Semgmt0/Semgmt1) for which
                          this certificate is imported. -- str
        :param keyfile: Path to alternate key file all_key.pem. -- str
        :param certfile: Path to alternate certificate file all.pem. -- str
        :param trustfile: Path to alternate trust certificate file
                          trust.pem. -- str
        :returns: SECertificateInfo -- dict
        """
        array_id = self.array_id if not array_id else array_id
        try:
            f_path = Path(keyfile)
            assert f_path.is_file() is True
            LOG.info('Uploading settings from {p}'.format(p=f_path))
            keyfiledata = open(f_path, FILE_READ_MODE)
        except (TypeError, AssertionError) as error:
            msg = (
                'Invalid file path supplied for settings upload '
                'location: {f}'.format(f=keyfile))
            LOG.error(msg)
            raise exception.InvalidInputException(msg) from error
        try:
            f_path = Path(trustfile)
            assert f_path.is_file() is True
            LOG.info('Uploading settings from {p}'.format(p=f_path))
            trustfiledata = open(f_path, FILE_READ_MODE)
        except (TypeError, AssertionError) as error:
            msg = (
                'Invalid file path supplied for settings upload '
                'location: {f}'.format(f=trustfile))
            LOG.error(msg)
            raise exception.InvalidInputException(msg) from error
        try:
            f_path = Path(certfile)
            assert f_path.is_file() is True
            LOG.info('Uploading settings from {p}'.format(p=f_path))
            certfiledata = open(f_path, FILE_READ_MODE)
        except (TypeError, AssertionError) as error:
            msg = (
                'Invalid file path supplied for settings upload '
                'location: {f}'.format(f=certfiledata))
            LOG.error(msg)
            raise exception.InvalidInputException(msg) from error
        form_data = {'node_name': node_name, 'keyfile': keyfiledata,
                     'trustfile': trustfiledata, 'certfile': certfiledata}

        return self.upload_file(
            category=SERVICEABILITY, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=APPLICATION,
            resource=SOLUTIONS_ENABLER, form_data=form_data,
            object_type=CUSTOM_CERTIFICATE, object_type_id=IMPORT)

    def replace_self_signed_certificate(self, array_id=None,
                                        node_name=None):
        """Replace SE Management Self signed certificate.

        :param array_id: array id -- str
        :param node_name: Specify the node name (Semgmt0/Semgmt1) for which
                          this self-signed certificate is created. -- str
        """
        array_id = self.array_id if not array_id else array_id
        payload = {'node_name': node_name}

        return self.common.create_resource(
            category=SERVICEABILITY, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=APPLICATION,
            object_type=SOLUTIONS_ENABLER,
            object_type_id=SELF_SIGNED_CERTIFICATE,
            payload=payload)
