# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
"""workload_planner.py."""

import logging
from typing import Any

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)

# Resource constants
SYMMETRIX = constants.SYMMETRIX
WLP = constants.WLP
HEADROOM = constants.HEADROOM
GB_HEADROOM = constants.GB_HEADROOM
SRP = constants.SRP
SLO = constants.SLO
WORKLOADTYPE = constants.WORKLOADTYPE


class WLPFunctions(object):

    def __init__(self, array_id: str, rest_client: Any) -> None:
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id

    def get_system_list(self) -> list[str]:
        """List workload planner eligible authorized system IDs.

        This call queries for a list of workload planner eligible
        authorized system IDs.

        :returns: system IDs -- list[str]
        """
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix",
            resource_type=None)
        return response.get("symmetrixId", list()) if response else list()

    def get_system(self, array_id: str | None = None) -> dict[str, Any]:
        """Get workload planner processing details for a system.

        This call queries for workload planner processing and data
        exclusion details for a specific system using its ID.

        :param array_id: The storage array ID -- string
        :returns: workload planner system details -- dict
        """
        array_id = array_id if array_id else self.array_id
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}",
            resource_type=None)

    def update_data_exclusion(
            self, exclusion_type: str, epoch_timestamp: int | None = None,
            excluded_bucket: list[int] | None = None,
            array_id: str | None = None) -> dict[str, Any]:
        """Update the data excluded from workload planner calculations.

        This call updates the data to be excluded from the workload
        planner calculations, either as a one-time exclusion identified by
        an epoch timestamp, or as a set of recurring exclusion buckets.

        :param exclusion_type: exclusion type, one of 'None', 'OneTime', or
                               'Recurring' -- string
        :param epoch_timestamp: epoch timestamp for a one-time exclusion,
                                required when ``exclusion_type`` is
                                'OneTime' -- int
        :param excluded_bucket: list of recurring exclusion bucket IDs,
                                required when ``exclusion_type`` is
                                'Recurring' -- list[int]
        :param array_id: The storage array ID -- string
        :returns: updated workload planner system details -- dict
        """
        array_id = array_id if array_id else self.array_id
        payload = {"exclusionType": exclusion_type}
        if epoch_timestamp is not None:
            payload["epochTimestamp"] = epoch_timestamp
        if excluded_bucket is not None:
            payload["excludedBucket"] = excluded_bucket
        return self.common.modify_resource(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}",
            resource_type=None, payload=payload)

    def get_storage_group_list(
            self, array_id: str | None = None) -> list[str]:
        """List workload planner eligible storage groups for a system.

        This call queries the list of workload planner eligible storage
        groups for a specific system using the system ID.

        :param array_id: The storage array ID -- string
        :returns: storage group names -- list[str]
        """
        array_id = array_id if array_id else self.array_id
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}/"
            f"storagegroup",
            resource_type=None)
        return response.get("storageGroupId", list()) if response else list()

    def get_storage_group(
            self, storage_group_id: str, array_id: str | None = None,
            filter: str | None = None) -> dict[str, Any]:
        """Get workload planner performance and planning details for a
        storage group.

        This call queries the performance and planning details for a
        specific storage group on a specific system using the storage
        group name and the system ID.

        :param storage_group_id: The storage group name -- string
        :param array_id: The storage array ID -- string
        :param filter: filter on a specific set of storage group data, use
                       'RTHistory' to show response time history in order
                       to find a timestamp for setting a one-time data
                       exclusion, all other data is shown by default
                       -- string
        :returns: workload planner storage group details -- dict
        """
        array_id = array_id if array_id else self.array_id
        query_params = {"filter": filter}
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}/"
            f"storagegroup/{storage_group_id}",
            resource_type=None, params=query_params)

    def update_storage_group(
            self, storage_group_id: str, action: str,
            storage_group_data_exclusion_param: dict[str, Any] | None = None,
            storage_group_rebase_param: dict[str, Any] | None = None,
            storage_group_set_host_io_limits_param: (
                dict[str, Any] | None) = None,
            array_id: str | None = None) -> dict[str, Any]:
        """Update workload planner settings for a storage group.

        This call is used to update the storage group plan, exclude
        storage group data, or set (recommended or custom) host I/O
        limits for a specific storage group on a specific system using
        the storage group name and the system ID.

        :param storage_group_id: The storage group name -- string
        :param action: update action, one of 'ExcludeStorageGroupData',
                       'RebaseStorageGroupPlan', or
                       'SetHostIOLimits' -- string
        :param storage_group_data_exclusion_param: data exclusion settings,
                                                   required when ``action``
                                                   is
                                                   'ExcludeStorageGroupData',
                                                   in the same shape as
                                                   :py:meth:`
                                                   update_data_exclusion`
                                                   e.g. ``{'exclusionType':
                                                   'OneTime',
                                                   'epochTimestamp':
                                                   1234567890}`` -- dict
        :param storage_group_rebase_param: rebase settings, required when
                                           ``action`` is
                                           'RebaseStorageGroupPlan' e.g.
                                           ``{'autofill': True}`` -- dict
        :param storage_group_set_host_io_limits_param: host I/O limit
                                                       settings, required
                                                       when ``action`` is
                                                       'SetHostIOLimits'
                                                       e.g.
                                                       ``{'metricLimit':
                                                       'IOPS',
                                                       'hostIoLimitIops':
                                                       10000}`` -- dict
        :param array_id: The storage array ID -- string
        :returns: updated workload planner storage group details -- dict
        """
        array_id = array_id if array_id else self.array_id
        payload = {"action": action}
        if storage_group_data_exclusion_param is not None:
            payload["storageGroupDataExclusionParam"] = (
                storage_group_data_exclusion_param)
        if storage_group_rebase_param is not None:
            payload["storageGroupRebaseParam"] = storage_group_rebase_param
        if storage_group_set_host_io_limits_param is not None:
            payload["storageGroupSetHostIoLimitsParam"] = (
                storage_group_set_host_io_limits_param)
        return self.common.modify_resource(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}/"
            f"storagegroup/{storage_group_id}",
            resource_type=None, payload=payload)

    def get_headroom(
            self, array_id: str | None = None, srp: str | None = None,
            slo: str | None = None,
            emulation: str | None = None) -> dict[str, Any]:
        """Get remaining headroom capacity for a system.

        This call queries the list of headroom for a specific system
        using its system ID.

        :param array_id: The storage array ID -- string
        :param srp: storage resource pool name, filters headroom objects
                    returned by SRP specified -- string
        :param slo: service level name, filters headroom objects returned
                    by service level specified -- string
        :param emulation: emulation, filters headroom objects returned by
                          emulation specified -- string
        :returns: headroom details -- dict
        """
        array_id = array_id if array_id else self.array_id
        query_params = {"srp": srp, "slo": slo, "emulation": emulation}
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}/"
            f"headroom",
            resource_type=None, params=query_params)

    def get_utilization(
            self, array_id: str | None = None, bucket: str | None = None,
            back_end_only: bool | None = None) -> dict[str, Any]:
        """Get system-component utilization values for a system.

        This call queries the system-component utilization values for
        the past two weeks. The utilization values shown are normalized
        to a best practice limit for each component type. By default,
        only the most limiting (highest utilization) value is shown for
        a given timestamp.

        :param array_id: The storage array ID -- string
        :param bucket: the bucket ID, displays all component utilization
                       values for the given bucket ID. A bucket is a four
                       hour time window, a week has 42 buckets (0-indexed),
                       bucket 0 is Sunday 12am-4am, 1 is Sunday 4am-8am,
                       etc -- string
        :param back_end_only: only show utilizations for back end
                              components, only back end components impact
                              headroom calculations -- bool
        :returns: utilization details -- dict
        """
        array_id = array_id if array_id else self.array_id
        query_params = {"bucket": bucket, "backEndOnly": back_end_only}
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}/"
            f"utilization",
            resource_type=None, params=query_params)

    def get_compliance_history(
            self, array_id: str | None = None,
            start_time: str | None = None, end_time: str | None = None,
            storage_group_id: str | None = None) -> dict[str, Any]:
        """Get compliance history for storage groups on a system.

        This call queries the list of all storage groups with a
        breakdown of the percentage of time each storage group spent in
        each compliance state over the past two weeks.

        :param array_id: The storage array ID -- string
        :param start_time: the start time (inclusive) for the query,
                           default is two weeks before the most current
                           processed data timestamp -- string
        :param end_time: the end time (inclusive) for the query, default
                         is the most current processed data timestamp
                         -- string
        :param storage_group_id: filter history by the specified storage
                                 group name, if specified a detailed event
                                 log will be shown, events include
                                 compliance state changes, data exclusion
                                 setting changes, service level or SRP
                                 changes, and workload type changes
                                 -- string
        :returns: compliance history details -- dict
        """
        array_id = array_id if array_id else self.array_id
        query_params = {"starttime": start_time, "endtime": end_time,
                        "storageGroupId": storage_group_id}
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/symmetrix/{array_id}/"
            f"compliancehistory",
            resource_type=None, params=query_params)

    def get_provisioning_template_list(self) -> list[str]:
        """List workload planner provisioning templates.

        This call queries for a list of Provisioning Templates created.

        :returns: provisioning template names -- list[str]
        """
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/provisioningtemplate",
            resource_type=None)
        return response.get("templateId", list()) if response else list()

    def get_provisioning_template(self, template_id: str) -> dict[str, Any]:
        """Get details for a workload planner provisioning template.

        This call queries for details for a specific provisioning
        template using its name.

        :param template_id: The provisioning template name -- string
        :returns: provisioning template details -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/provisioningtemplate/"
            f"{template_id}",
            resource_type=None)

    def create_provisioning_template(
            self, symmetrix_id: str, storage_group_id: str, template_id: str,
            response_time_target: float | None = None,
            number_of_volumes: int | None = None,
            volume_attribute: dict[str, Any] | None = None,
            host_io_limit_attributes: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a workload planner provisioning template.

        This call creates a new provisioning template from an existing
        storage group.

        :param symmetrix_id: The system ID for the source storage group
                             -- string
        :param storage_group_id: The source storage group name -- string
        :param template_id: The name for the new provisioning template
                            -- string
        :param response_time_target: override the response time target
                                     for the template -- float
        :param number_of_volumes: override the number of volumes for the
                                  template -- int
        :param volume_attribute: override the volume attributes for the
                                 template e.g. ``{'capacityUnit': 'GB',
                                 'volumeSize': 10}`` -- dict
        :param host_io_limit_attributes: override the host I/O limit
                                         attributes for the template e.g.
                                         ``{'metricLimit': 'IOPS',
                                         'hostIoLimitIops': 10000}`` -- dict
        :returns: provisioning template create response -- dict
        """
        payload = {"symmetrixId": symmetrix_id,
                   "storageGroupId": storage_group_id,
                   "templateId": template_id}
        overrides = {}
        if response_time_target is not None:
            overrides["responseTimeTarget"] = response_time_target
        if number_of_volumes is not None:
            overrides["numberOfVolumes"] = number_of_volumes
        if volume_attribute is not None:
            overrides["volumeAttribute"] = volume_attribute
        if host_io_limit_attributes is not None:
            overrides["hostIOLimitAttributes"] = host_io_limit_attributes
        if overrides:
            payload["provisioningTemplateOverrides"] = overrides
        return self.common.create_resource(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/provisioningtemplate",
            resource_type=None, payload=payload)

    def update_provisioning_template(
            self, template_id: str, updated_template_id: str | None = None,
            response_time_target: float | None = None,
            number_of_volumes: int | None = None,
            volume_attribute: dict[str, Any] | None = None,
            host_io_limit_attributes: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Update a workload planner provisioning template.

        This call updates the attributes for a specific provisioning
        template using its name.

        :param template_id: The provisioning template name -- string
        :param updated_template_id: rename the provisioning template
                                    -- string
        :param response_time_target: override the response time target
                                     for the template -- float
        :param number_of_volumes: override the number of volumes for the
                                  template -- int
        :param volume_attribute: override the volume attributes for the
                                 template e.g. ``{'capacityUnit': 'GB',
                                 'volumeSize': 10}`` -- dict
        :param host_io_limit_attributes: override the host I/O limit
                                         attributes for the template e.g.
                                         ``{'metricLimit': 'IOPS',
                                         'hostIoLimitIops': 10000}`` -- dict
        :returns: updated provisioning template details -- dict
        """
        payload = {}
        if updated_template_id is not None:
            payload["templateId"] = updated_template_id
        overrides = {}
        if response_time_target is not None:
            overrides["responseTimeTarget"] = response_time_target
        if number_of_volumes is not None:
            overrides["numberOfVolumes"] = number_of_volumes
        if volume_attribute is not None:
            overrides["volumeAttribute"] = volume_attribute
        if host_io_limit_attributes is not None:
            overrides["hostIOLimitAttributes"] = host_io_limit_attributes
        if overrides:
            payload["provisioningTemplateOverrides"] = overrides
        return self.common.modify_resource(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/provisioningtemplate/"
            f"{template_id}",
            resource_type=None, payload=payload)

    def delete_provisioning_template(self, template_id: str) -> None:
        """Delete a workload planner provisioning template.

        This call deletes an existing provisioning template using its
        name.

        :param template_id: The provisioning template name -- string
        """
        self.common.delete_resource(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/provisioningtemplate/"
            f"{template_id}",
            resource_type=None)

    def test_performance_impact(
            self, migration_impact_param: dict[str, Any] | None = None,
            create_masking_view_impact_param: dict[str, Any] | None = None,
            auto_resolve_conflicts: bool | None = None,
            details: bool | None = None) -> dict[str, Any]:
        """Test the performance impact of a requested configuration change.

        This call returns the performance impact of a requested
        configuration change, identifies the most suitable target
        system, populates system-specific default values, and returns
        fully populated configuration parameters and a URI for a
        subsequent configuration change REST call.

        :param migration_impact_param: migration performance impact
                                       parameters e.g.
                                       ``{'source_symmetrix_id':
                                       '000197900123',
                                       'source_storage_group_id':
                                       'example-sg'}`` -- dict
        :param create_masking_view_impact_param: create masking view
                                                 performance impact
                                                 parameters, see Unisphere
                                                 REST documentation for
                                                 the full nested
                                                 ``auto_port_group_param``,
                                                 ``auto_host_group_param``,
                                                 and
                                                 ``create_storage_group_param``
                                                 shapes -- dict
        :param auto_resolve_conflicts: automatically resolve
                                       configuration conflicts where
                                       possible -- bool
        :param details: if True, show details for all systems in two
                        lists, a list of suitable target systems with
                        associated performance impact details, and a
                        list of unsuitable systems with the reason for
                        unsuitability -- bool
        :returns: performance impact results -- dict
        """
        payload = {}
        if migration_impact_param is not None:
            payload["migration_impact_param"] = migration_impact_param
        if create_masking_view_impact_param is not None:
            payload["create_masking_view_impact_param"] = (
                create_masking_view_impact_param)
        if auto_resolve_conflicts is not None:
            payload["auto_resolve_conflicts"] = auto_resolve_conflicts
        details_query = ""
        if details is not None:
            details_query = f"?details={'true' if details else 'false'}"
        return self.common.create_resource(
            target_uri=f"/{self.common.UNI_VERSION}/wlp/performance_impact"
            f"{details_query}",
            resource_type=None, payload=payload)

    def get_wlp_information(
            self, array_id: str | None = None) -> dict[str, Any]:
        """Get workload planner system information.

        Compatibility wrapper for the pre-existing
        ``WLPFunctions.get_wlp_information`` call pattern, delegates to
        :py:meth:`get_system`.

        :param array_id: The storage array ID -- string
        :returns: workload planner system details -- dict
        """
        return self.get_system(array_id=array_id)
