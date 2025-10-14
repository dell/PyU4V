# Copyright(c) 2020 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0(the "License");
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
"""settings.py."""
import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)


class SettingsFunctions(object):

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id
        self.version = constants.UNISPHERE_VERSION

    def get_performance_registration_settings(self) -> dict:
        """List Array Performance Registration Settings.
        returns: Array Performance Registration Settings -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.version}/settings/registration/performance",
            resource_type=None)

    # Unipshere registration functions

    def update_performance_registration_settings(
            self, array_id: str, diagnostic: bool = True, real_time: bool =
            True, file: bool = False, real_time_storage_groups: list[str] =
            None):
        """Update Array Performance Registration Settings.
        :param array_id: The storage array ID -- string
        :param diagnostic: enable/disable diagnostic performance data
                           collection at 5 minute intervals -- bool
        :param real_time: enable/disable real-time performance data
                         collection at 5 second intervals, note enabling
                         this parameter also enables max values to be
                         returned on diagnostic metrics -- bool
        :param file: enable/disable file performance data collection -- bool
        :param real_time_storage_groups: Comma separated list of Storage Groups
                                         to collect realtime data on, requires
                                         realtime=True -- string
        returns: Array Performance Registration Settings -- dict
        """
        payload = {
            "registration_details": [{
                "system_id": array_id,
                "diagnostic": diagnostic,
                "real_time": real_time,
                "file": file}]}

        if real_time_storage_groups:
            payload.update({"selectedSGs": real_time_storage_groups})

        return self.common.modify_resource(
            target_uri=f"/{self.version}/settings/registration/performance",
            resource_type=None, payload=payload)

    def get_scg_configuration_details(self) -> dict:
        """List SCG Configuration Details.

        """

        query_params = {}
        return self.common.get_request(
            target_uri=f"/{self.version}/settings/registration/scg",
            resource_type=None, params=query_params)

    def get_scg_server_certificate_configuration(self) -> dict:
        """List SCG Server Certificate Configuration.

        """
        return self.common.get_request(
            target_uri=(f""
                        f"/{self.version}/"
                        f"settings/registration/scg/server_cert"),
            resource_type=None)

    def configure_scg_connection(self, unisphere_ip_address: str,
                                 gateway_host: str, scg_serial_number: str,
                                 model: str, server_cert: str, access_key: str,
                                 pin: str, gateway_port: int,
                                 unisphere_registered: bool,
                                 internal_connection: bool
                                 ) -> dict:
        """Configure SCG Connection.

        Configures Secure Connect Gateway (SCG).**SCG is a two-way remote
        connection between Dell EMC Customer Service and your Dell EMC products
        that enables remote monitoring, diagnosis, and repair. SRS assures
        availability and optimization of your Dell EMC infrastructure, and is a
        key component of Dell EMC's industry leading Customer Service.

        The connection is secure, high speed, and operates 24x7.The connection
        is also responsible for transporting data for the CloudIQ application
        which aggregates data from multiple Unisphere instances.
        Please note that the server certificate can be managed separately to
        the SCG configuration.

        :param unisphere_ip_address: Unisphere IP Address -- string
        :param gateway_host: Gateway Host -- string
        :param scg_serial_number: SCG Serial Number -- string
        :param model: Model -- string
        :param server_cert: Server Certificate from SCG Server, base64 encoded
                            -- string
        :param access_key: The access key used for registering to an SCG
                           -- string
        :param pin: The PIN used for registering to an SCG-- string
        :param gateway_port: The port of the SCG-- int
        :param unisphere_registered:  Indicates whether Unisphere has been
                                      registered with an SCG gateway or not
                                      -- bool
        :param internal_connection: Indicates whether SCG was registered over
                                    an internal connection or not -- bool

        """
        payload = {
            "unisphere_ip_address": unisphere_ip_address,
            "gateway_host": gateway_host,
            "scg_serial_number": scg_serial_number,
            "model": model,
            "server_cert": server_cert,
            "access_key": access_key,
            "pin": pin,
            "gateway_port": gateway_port,
            "unisphere_registered": unisphere_registered,
            "internal_connection": internal_connection
        }

        return self.common.create_resource(
            target_uri=f"/"
                       f"{self.version}/settings/registration/scg/connection"
                       f"", resource_type=None, payload=payload)

    def get_cloudiq_data_collection_configuration(self) -> dict:
        """List CloudIQ Data Collection Configuration.

        :param array_id: The storage array ID -- string
        """
        query_params = {}
        return self.common.get_request(
            target_uri=f"/{self.version}/settings/registration/cloudiq",
            resource_type=None, params=query_params)

    def register_cloudiq_data_collection(
            self, send_data: bool = None,
            data_collection_disabled: list[str, str] = [""]) -> dict:
        """Register CloudIQ Data Collection.
        SCG Gateway must be configured.
        :param send_data: send_data -- bool
        """
        payload = {
            "send_data": send_data,
            "data_collection_disabled": data_collection_disabled
        }
        return self.common.modify_resource(
            target_uri=f"/{self.version}/settings/registration/cloudiq",
            resource_type=None, payload=payload)

    # Functions for alert configurations
    def update_performance_thresholds_and_alerts(self, payload: dict) -> dict:
        """Set Global Thresholds and Alerts.

        :param payload: Global Thresholds and Alerts, can be a subset of the
                        overall payload from
                        get_performance_thresholds_and_alerts-- dict
        :sample payload:
                        {"global_performance_thresholds": [
                              {
                                "category": "Array",
                                "metric": "BEUtilization",
                                "kpi": 'true',
                                "alert_error": 'true',
                                "first_lower_threshold": "50",
                                "second_lower_threshold": "40",
                                "first_upper_threshold": "65",
                                "second_upper_threshold": "80"
                              }]

        """
        payload = payload
        return self.common.modify_resource(
            target_uri=f"/{self.version}/settings/alert/performance_threshold",
            resource_type=None, payload=payload)

    def get_performance_thresholds_and_alerts(self,
                                              enabled_alerts: bool = False,
                                              category: str = None) -> dict:
        """
        List Global Thresholds and Alerts.

        :param enabled_alerts: If True, return only enabled alerts. -- bool
        :param category: Filter alerts by a specific category. -- string
        :returns: Filtered Global Thresholds and Alerts as a dictionary.
                  Note returned values for thresholds will be in float as
                  non whole numbers can be set, this ensures a common ground
                  for numbers across all threshold types.
        """
        # Fetch all alerts
        all_alerts = self.common.get_request(
            target_uri=f"/{self.version}/settings/alert/performance_threshold",
            resource_type=None
        )

        filtered_alerts = {'global_performance_thresholds': []}

        for alert in all_alerts.get("global_performance_thresholds", []):
            if category and alert.get("category") != category:
                continue
            if enabled_alerts and not alert.get("alert_error"):
                continue
            filtered_alerts["global_performance_thresholds"].append(alert)

        return filtered_alerts

    def get_alert_notification_target_config(self) -> dict:
        """List Unisphere"s Alert Notification Configuration.

        returns: Unisphere's Alert Notification Settings -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.version}/settings/alert/notification",
            resource_type=None)

    def update_alert_notification_targets(
            self, payload: dict = None, enable_email: bool = None,
            email_server: str = None, sender_address: str = None,
            email_port: int = None, enable_syslog: bool = None,
            syslog_host: str = None, syslog_protocol: str = None,
            syslog_text_format: str = None, tls: bool = None,
            syslog_port: int = None,
            enable_snmp: bool = None, snmp_host: str = None,
            snmp_port: int = None,
            snmp_version: int = None, snmp_security_model: str = None,
            certificate_authority_pem: str = None,
            snmp_username: str = None, snmp_password: str = None,
            tls_security_name: str = None,
            snmp_passphrase: str = None) -> dict:
        """
        Update Unisphere's Alert Notification Target Settings.

        :payload: Alert Notification Settings, can be a subset of the
                        overall payload from
                        get_alert_notification_settings-- dict
        :param enable_email: Enable or disable email notifications -- bool
        :param email_server: Email server address -- string
        :param sender_address: Email sender address -- string
        :param email_port: Email port number -- int
        :param enable_syslog: Enable or disable syslog notifications -- bool
        :param syslog_host: Syslog server address -- string
        :param syslog_protocol: Syslog protocol(e.g., UDP, TCP) -- string
        :param syslog_text_format: Syslog text format(e.g., RFC5424) -- string
        :param tls: Enable or disable TLS for syslog notifications -- bool
        :param syslog_port: Syslog port number -- int
        :param enable_snmp: Enable or disable SNMP notifications -- bool
        :param snmp_host: SNMP server address -- string
        :param snmp_port: SNMP port number -- int
        :param snmp_version: SNMP version(e.g., 1,3) -- int
        :param snmp_security_model: SNMP security model(e.g. "usm" or "tsm")
                                    -- string
        :param certificate_authority_pem: cert in base64 format, for details on
                                          encoding see documentation at
                                          https://developer.dell.com/ -- string
        :param snmp_username: SNMP username -- string
        :param snmp_password: SNMP password -- string


        :returns: Unisphere's Alert Notification Settings -- dict




        This call is idempotent. It will also take a subet of the
        confifuration, you can
        provide updates to any category:
        email, SNMP, and/or syslog.
        """

        if not payload:
            payload = {}

        # Handle email settings
        if enable_email:
            email_payload = {
                "email": {
                    "enabled": enable_email,
                    "email_server": email_server,
                    "sender_address": sender_address,
                    "email_port": email_port
                }
            }
            if not all([email_server, sender_address, email_port]):
                raise ValueError(
                    "enable_email is True but email server, sender address, "
                    "or email port is missing.")

        else:
            email_payload = {"email": {
                "enabled": enable_email
            }}
        payload.update(email_payload)

        # Handle SNMP settings
        if enable_snmp:
            snmp_payload = {
                "snmp": {
                    "enabled": enable_snmp,
                    "snmp_trap_targets": [
                        {
                            "host": snmp_host,
                            "port": snmp_port,
                            "version": snmp_version
                        }
                    ]
                }
            }

            # SNMPv3 specific fields
            if snmp_version == "3":
                snmp_target = snmp_payload["snmp"]["snmp_trap_targets"][0]
                snmp_target["security_model"] = snmp_security_model
                snmp_target["authorization"] = {
                    "username": snmp_username,
                    "password": snmp_password,
                    "passphrase": snmp_passphrase
                }

                if tls_security_name and certificate_authority_pem:
                    snmp_target["tls"] = {
                        "security_name": tls_security_name,
                        "certificate_authority_pem": certificate_authority_pem
                    }
            else:
                snmp_payload = {
                    "snmp": {
                        "enabled": enable_snmp
                    }
                }

            payload.update(snmp_payload)

        # Handle syslog settings
        if enable_syslog:
            if not all([syslog_host, syslog_protocol, syslog_text_format,
                        tls is not None, syslog_port]):
                raise ValueError(
                    "enable_syslog is True but one or more required syslog "
                    "fields are missing.")

            syslog_payload = {
                "syslog": {
                    "enabled": enable_syslog,
                    "syslog_target": {
                        "host": syslog_host,
                        "protocol": syslog_protocol,
                        "text_format": syslog_text_format,
                        "tls": tls,
                        "port": syslog_port
                    }
                }
            }
            payload.update(syslog_payload)

        return self.common.create_resource(
            target_uri=f"/{self.version}/settings/alert/notification",
            resource_type=None, payload=payload)

    def get_alert_policies(
            self, array_id: str = None, name: str = None, type: str = None,
            applicable: bool = None, enabled: bool = None,
            email_notifications: bool = None,
            snmp_notifications: bool = None,
            syslog_notifications: bool = None) -> dict:
        """List Alert Policies.

        :param name: Optional value that filters returned list to display Alert
                     Policies based on Alert Policy name. e.g. equal to
                     "name=arrayEvents" or contains
                     "name=<like>array" -- string
        :param type: Optional value that filters returned list to display Alert
                     Policies based on alert policy category possible values
                     are "array" and "file" -- string
        :param applicable: Optional value that filters returned list to display
                           Alert Policies that are applicable to the storage
                           array(true/false) -- bool
        :param enabled: Optional value that filters returned list to display
                        Alert Policies that are enabled(true/false) -- bool
        :param email_notifications: Optional value that filters returned list
                                    to display Alert Policies that have email
                                    notifications enabled(true/false) --
                                    bool
        :param snmp_notifications: Optional value that filters returned list to
                                   display Alert Policies that have SNMP
                                   notifications enabled(true/false) -- string
        :param syslog_notifications: Optional value that filters returned list
                                     to display Alert Policies that have
                                     syslog notifications enabled
                                    (true/false) -- bool
        :param array_id: The storage array ID -- string
        """
        array_id = array_id if array_id else self.array_id
        query_params = {"name": name, "type": type, "applicable": applicable,
                        "enabled": enabled,
                        "email_notifications": email_notifications,
                        "snmp_notifications": snmp_notifications,
                        "syslog_notifications": syslog_notifications}
        return self.common.get_request(
            target_uri=f"/{self.version}/settings/symmetrix/{array_id}"
                       f"/alert/alert_policy",
            resource_type=None, params=query_params)

    def update_alert_policies(self, payload: dict,
                              array_id: str = None) -> dict:
        """Update Alert Policies.

        :param array_id: The storage array ID -- string
        :param payload: Optional payload, can be user supplied or generated
        from get_alert_policies, users can use a subset of payload if they
        are only wishing to do partial update -- dict

        """
        array_id = array_id if array_id else self.array_id
        return self.common.modify_resource(
            target_uri=f"/{self.version}/settings/symmetrix/{array_id}"
                       f"/alert/alert_policy",
            resource_type=None, payload=payload)

    def get_host_access_control_configuration(self,
                                              array_id: str = None) -> dict:
        """List Host Access Control Configuration.

        :param symmetrixId: symmetrixId -- string
        :param array_id: The storage array ID -- string
        """
        array_id = array_id if array_id else self.array_id
        return self.common.get_request(
            target_uri=(f"/{self.version}/settings/symmetrix"
                        f"/{array_id}/access_control/host_access"),
            resource_type=None)

    def get_authorization_rules(
            self, array_id: str = None, name: str = None,
            account_type: str = None,
            authority: str = None, qualifier: str = None,
            role: str = None) -> dict:
        """List Authorization Rules.

        :param array_id: symmetrixId -- string
        :param name: Optional value that filters returned list to display
                    Authorization Rules based on the name of the user or group
                    e.g. equal to "name=testUser" or contains
                    name=<like>test" -- string
        :param account_type: Optional value that filters returned list to
                             display Authorization Rules based on the
                             account type. Possible values are "user"
                             and "group" -- string
        :param authority: Supported authority types for Unisphere REST API are:
                          localDirectory, host, ldapSSL, windowsAD and sso (
                          Single Sign-On) or "none" -- string
        :param qualifier: Optional value that filters returned list to
                          display Authorization Rules based on the qualifier
                          e.g. equal to "qualifier=test" or contains
                          "qualifier=<like>test" -- string
        :param role: Optional value that filters returned list to display
                     Authorization Rules based on the role e.g. "role=admin"
                     -- string
        :returns: Authorization Rules -- dict
        """
        array_id = array_id if array_id else self.array_id
        query_params = {"name": name, "account_type": account_type,
                        "authority": authority, "qualifier": qualifier,
                        "role": role, }
        return self.common.get_request(
            target_uri=(f"/{self.version}/settings/symmetrix"
                        f"/{array_id}/access_control/authorization_rule"),
            resource_type=None, params=query_params)

    def create_authorization_rule(self, name: str, roles: list[str],
                                  account_type: str = None,
                                  authority: str = None, qualifier: str = None,
                                  array_id: str = None,
                                  local_rep: bool = False,
                                  local_rep_storage_groups: str = None,
                                  remote_rep: bool = False,
                                  local_rep_wildcard: str = None,
                                  remote_rep_storage_groups: str = None,
                                  remote_rep_wildcard: str = None,
                                  device_manage: bool = False,
                                  device_manage_storage_groups: str = None,
                                  device_manage_wildcard: str = None) -> dict:
        """
        Create an Authorization Rule.

        :param name: Name of the authorization rule (string)
        :param roles: List of roles (up to 4), e.g. ["admin", "monitor"].
                      Valid roles: admin, security_admin, storage_admin,
                      mainframe_admin, monitor, auditor, perf_monitor,
                      or "none"
        :param account_type: Account type (string)
        :param authority: Source of the authority ("LocalDirectory", "ldapSSL",
                          "windowsAD", "host", "sso", "none") -- string
        :param qualifier: Domain or Hostname -- string
        :param array_id: Storage array ID -- string
        :param local_rep: Enable local replication (bool)
        :param local_rep_storage_groups: Comma-separated list of SGs -- string
        :param local_rep_wildcard: Local rep wildcard -- string
        :param remote_rep: Enable remote replication (bool)
        :param remote_rep_storage_groups: Comma-separated list of SGs -- string
        :param remote_rep_wildcard: Remote rep wildcard -- string
        :param device_manage: Enable device management (bool)
        :param device_manage_storage_groups: Comma-separated list
                                             of SGs -- string
        :param device_manage_wildcard: Device management wildcard -- string
        """

        array_id = array_id or self.array_id

        if len(roles) > 4:
            raise ValueError("A user/group can have a maximum of 4 roles.")
        if "none" in roles and len(roles) > 1:
            raise ValueError("'none' cannot be combined with other roles.")

        def build_role_dict(enabled, storage_groups, wildcards):
            role_dict = {"enabled": enabled}
            if storage_groups is not None:
                role_dict["storage_groups"] = storage_groups
            if wildcards is not None:
                role_dict["wildcards"] = wildcards
            return role_dict

        payload = {
            "name": name,
            "account_type": account_type,
            "authority": authority,
            "qualifier": qualifier,
            "roles": {role: True for role in roles}
        }

        if local_rep:
            payload["roles"]["local_rep"] = build_role_dict(
                local_rep, local_rep_storage_groups, local_rep_wildcard
            )

        if remote_rep:
            payload["roles"]["remote_rep"] = build_role_dict(
                remote_rep, remote_rep_storage_groups, remote_rep_wildcard
            )

        if device_manage:
            payload["roles"]["device_manage"] = build_role_dict(
                device_manage, device_manage_storage_groups,
                device_manage_wildcard)

        return self.common.create_resource(
            target_uri=(f"/{self.version}/settings/symmetrix/"
                        f"{array_id}/access_control/authorization_rule"),
            resource_type=None,
            payload=payload
        )

    def update_authorization_rules(
            self, payload: dict, array_id: str = None) -> dict:
        """Update Authorization Rule.
        :param array_id: The storage array ID -- string
        :param payload: Optional payload, can be user supplied or generated
        from get_authorization_rules, users can use a subset of payload if they
        are only wishing to do partial update -- dict
        """
        array_id = array_id if array_id else self.array_id
        return self.common.modify_resource(
            target_uri=(f"/{self.version}/settings/symmetrix/"
                        f"{array_id}/access_control/authorization_rule"),
            resource_type=None, payload=payload)

    def get_system_thresholds(self, array_id: str = None, name: str = None,
                              applicable: bool = None, type: str = None,
                              unit: str = None, warning_threshold: int = None,
                              critical_threshold: int = None,
                              fatal_threshold: int = None,
                              email_notifications: bool = None,
                              snmp_notifications: bool = None,
                              syslog_notifications: bool = None) -> dict:
        """List System Threshold Alert Configuration for specified Array.

        :param array_id: symmetrixId -- string
        :param applicable: Optional value that filters returned list to display
                           System Thresholds that are applicable to the
                           storage array(true/false) -- string
        :param type: Optional value that filters returned list to display
                     System Thresholds based on system threshold category.
                     Possible values are "system", "srp" and
                     "storage_container" -- string
        :param unit: Optional value that filters returned list to display
                     System Thresholds based on system threshold category.
                     Possible values are "percent" -- int
        :param warning_threshold: Optional value that filters returned list to
                     display System Thresholds that are lt, gt or eq to the
                     specified warning threshold -- int
        :param critical_threshold: Optional value that filters returned list to
                                   display System Thresholds that are lt,
                                   gt or eq to the specified critical
                                   threshold -- int
        :param fatal_threshold: Optional value that filters returned list to
                                display System Thresholds that are lt,
                                gt or eq to the specified fatal threshold --
                                int
        :param email_notifications: Optional value that filters returned list
                                    to display System Thresholds that have
                                    email notifications enabled(true/false)
                                    -- string
        :param snmp_notifications: Optional value that filters returned list to
                                   display System Thresholds that have SNMP
                                   notifications enabled(true/false) -- string
        :param syslog_notifications: Optional value that filters returned list
                                     to display System Thresholds that have
                                     syslog notifications enabled(true/false)
                                     -- string
        :param array_id: The storage array ID -- string
        """
        array_id = array_id if array_id else self.array_id
        query_params = {"name": name, "applicable": applicable, "type": type,
                        "unit": unit, "warning_threshold": warning_threshold,
                        "critical_threshold": critical_threshold,
                        "fatal_threshold": fatal_threshold,
                        "email_notifications": email_notifications,
                        "snmp_notifications": snmp_notifications,
                        "syslog_notifications": syslog_notifications, }
        return self.common.get_request(
            target_uri=(f"/{self.version}/settings/symmetrix"
                        f"/{array_id}/alert/system_threshold"),
            resource_type=None, params=query_params)

    def update_system_thresholds(self, payload: dict,
                                 array_id: str = None) -> dict:
        """Update System Thresholds.

        :payload: payload, user built or generated from get_system_thresholds
                  -- dict
        """
        array_id = array_id if array_id else self.array_id
        payload = payload
        return self.common.modify_resource(
            target_uri=(
                f"/{self.version}/settings/symmetrix/"
                f"{array_id}/alert/system_threshold"), resource_type=None,
            payload=payload)

    def get_alert_notification_agent_details(self) -> dict:
        """List Alert Notification Agent Details.

        """
        return self.common.get_request(
            target_uri=(f""
                        f"/{self.version}/settings/alert/notification/"
                        f"agent_details"),
            resource_type=None)

    def get_alert_notification_settings(self, array_id: str = None) -> dict:
        """System Alert Notification Settings.
        Shows configuration of Alert Severity for System and Performance
        Alerts, per array.  Also shows subscription of Alert Notification for
        email subscribers.

        :param symmetrixId: symmetrixId -- string
        :param array_id: The storage array ID -- string
        """
        array_id = array_id if array_id else self.array_id
        return self.common.get_request(
            target_uri=(f"/{self.version}/settings/symmetrix"
                        f"/{array_id}/alert/notification"),
            resource_type=None)

    def update_alert_notifications(self, payload: dict, array_id: str = None) \
            -> dict:
        """Set/update Alert Notification Settings.
        Defines what alert severity is sent for System and Performance
        Alerts, per array.  Also sets subsciption of Alert Notification for
        email subscribers.

        :payload: payload, user built or generated from
                  get_alert_notification_settings
                  sample_payload = {'alert_severity': {
                  'system': {'fatal': True,
                       'critical': True,
                       'warning': True,
                       'normal': False,
                       'info': False},
                  'performance': {'critical': True,
                            'warning': True,
                            'info': False}},
                  'subscriptions': {'system': ['random.person@dell.com'],
                              'performance': ['random.person@dell.com'],
                              'jobs': [],
                              'reports': ['random.person@dell.com'],
                              'none': []}} -- dict
        :array_id: The storage array ID -- string
        """
        array_id = array_id if array_id else self.array_id
        payload = payload
        return self.common.modify_resource(
            target_uri=(
                f"/{self.version}/settings/symmetrix/"
                f"{array_id}/alert/notification"), resource_type=None,
            payload=payload)

    def get_storage_group_compliance_policy_allocation(
            self, array_id: str = None) -> dict:
        """Get Storage Group Compliance Policy Allocation.

        :param symmetrixId: symmetrixId -- string
        :param array_id: The storage array ID -- string
        """
        array_id = array_id if array_id else self.array_id
        query_params = {}
        return self.common.get_request(
            target_uri=(f"/{self.version}/settings/symmetrix"
                        f"/{array_id}/alert/compliance_alert_policy/"
                        f"storage_group"),
            resource_type=None, params=query_params)
