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
"""snapshot_policy.py."""
import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

REPLICATION = constants.REPLICATION
SYMMETRIX = constants.SYMMETRIX
SNAPSHOT_POLICY = constants.SNAPSHOT_POLICY
policy_interval_enum = {
    '10 Minutes': 10,
    '12 Minutes': 12,
    '20 Minutes': 20,
    '30 Minutes': 30,
    '1 Hour': 60,
    '2 Hours': 120,
    '3 Hours': 180,
    '4 Hours': 240,
    '6 Hours': 360,
    '8 Hours': 480,
    '1 Day': 1440,
    '7 Days': 10080}


class SnapshotPolicyFunctions(object):

    def __init__(self, array_id, rest_client):
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.array_id = array_id

    def get_snapshot_policy_list(self):
        """Given a snapshot policy name, return snapshot policy details.

        :returns: snapshot policy names -- list
        """
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SNAPSHOT_POLICY)
        return response.get('name', list()) if response else list()

    def get_snapshot_policy(self, snapshot_policy_name):
        """Given a snapshot policy name, return snapshot policy details.

        :param snapshot_policy_name: name of the snapshot policy -- str
        :returns: snapshot policy details -- dict
        """
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SNAPSHOT_POLICY,
            resource_type_id=snapshot_policy_name)

    def create_snapshot_policy(
            self, snapshot_policy_name, interval, cloud_retention_days=None,
            cloud_provider_name=None, local_snapshot_policy_secure=False,
            local_snapshot_policy_snapshot_count=None, offset_mins=None,
            compliance_count_warning=None, compliance_count_critical=None,
            _async=False):
        """Create a new snapshot policy.

        :param snapshot_policy_name: the snapshot policy name -- str
        :param interval: The value of the interval counter for snapshot
                         policy execution. Must be one of '10 Minutes',
                         '12 Minutes', '15 Minutes', '20 Minutes',
                         '30 Minutes', '1 Hour',
                         '2 Hours', '3 Hours', '4 Hours', '6 Hours',
                         '8 Hours', '12 Hours', '1 Day', '7 Days' -- enum
        :param cloud_retention_days: part of cloud_snapshot_policy_details
                                     number of days to retain the policy
                                     -- int
        :param cloud_provider_name: part of cloud_snapshot_policy_details
                                    the cloud provider name -- str
        :param local_snapshot_policy_secure: secure snapshots may only be
                                             terminated after they expire or
                                             by Dell EMC support -- bool
        :param local_snapshot_policy_snapshot_count: the max snapshot count
                                                     of the policy -- int
        :param offset_mins: Defines when, within the interval the snapshots
                            will be taken for a specified Snapshot Policy.
                            The offset must be less than the interval of
                            the Snapshot Policy. The format must be in minutes
                            -- int
        :param compliance_count_warning: The Number of snapshots which are
                                         not failed or bad when compliance
                                         changes to warning. -- int
        :param compliance_count_critical: The Number of snapshots which are
                                          not failed or bad when compliance
                                          changes to critical. -- int
        :param _async: is the operation asynchronous
        """
        payload = dict()

        if snapshot_policy_name:
            payload.update(
                {'snapshot_policy_name': snapshot_policy_name})
        else:
            msg = 'Snapshot policy name cannot be None.'
            LOG.exception(msg)
            raise exception.InvalidInputException(data=msg)

        if cloud_provider_name:
            if not cloud_retention_days:
                msg = ('If cloud_provider_name is set, cloud_retention_days '
                       'cannot be None.')
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg)

            cloud_snapshot_policy_details = {
                'cloud_retention_days': cloud_retention_days,
                'cloud_provider_name': cloud_provider_name}
            payload.update({
                'cloud_snapshot_policy_details':
                    cloud_snapshot_policy_details})
        elif local_snapshot_policy_snapshot_count:
            local_snapshot_policy_details = {
                'snapshot_count': local_snapshot_policy_snapshot_count}
            if local_snapshot_policy_secure:
                local_snapshot_policy_details.update(
                    {'secure': local_snapshot_policy_secure})
                LOG.warning('The secure snap option cannot be enabled or '
                            'disabled on an existing policy. Secure '
                            'snapshots may only be terminated after '
                            'they expire or by customer-authorized '
                            'Dell EMC support.')

            payload.update({
                'local_snapshot_policy_details':
                    local_snapshot_policy_details})
        else:
            msg = ('One of cloud snapshot policy or local snapshot policy '
                   'must be chosen. Check that you have the minimum '
                   'parameters set.')
            LOG.exception(msg)
            raise exception.InvalidInputException(data=msg)

        msg = ('The interval supplied must be one of \'10 Minutes\', '
               '\'12 Minutes\', \'15 Minutes\' etc.')
        if interval:
            try:
                index = [x.lower() for x in (
                    constants.SNAPSHOT_POLICY_INTERVALS)].index(
                    interval.lower())
            except ValueError as error:
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg) from error
            payload.update({
                'interval': constants.SNAPSHOT_POLICY_INTERVALS[index]})
        else:
            message = 'interval cannot be None. {}'.format(msg)
            LOG.exception(message)
            raise exception.InvalidInputException(data=message)

        if offset_mins:
            payload.update({'offset_mins': offset_mins})
        if compliance_count_warning:
            payload.update(
                {'compliance_count_warning': compliance_count_warning})
        if compliance_count_critical:
            payload.update(
                {'compliance_count_critical': compliance_count_critical})

        if _async:
            payload.update(constants.ASYNC_UPDATE)

        return self.create_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SNAPSHOT_POLICY, payload=payload)

    def modify_snapshot_policy(
            self, snapshot_policy_name, action, interval=None,
            offset_mins=None, snapshot_count=None,
            compliance_count_warning=None, compliance_count_critical=None,
            storage_group_names=None, new_snapshot_policy_name=None,
            _async=False):
        """Modify a snapshot policy

        This can be action: [Modify, Suspend, Resume, AssociateToStorageGroups,
        DisassociateFromStorageGroups]. A modify of the snapshot policy or
        adding or removing storage groups associated with the policy.

        :param snapshot_policy_name: the snapshot policy name-- str
        :param action: the modification action, must be one of
                       'AssociateToStorageGroups',
                       'DisassociateFromStorageGroups'
                       'Modify', 'Suspend', 'Resume'
        :param interval: The value of the interval counter for snapshot
                         policy execution. Must be one of '10 Minutes',
                         '12 Minutes', '15 Minutes', '20 Minutes',
                         '30 Minutes', '1 Hour',
                         '2 Hours', '3 Hours', '4 Hours', '6 Hours',
                         '8 Hours', '12 Hours', '1 Day', '7 Days' -- enum
        :param offset_mins: The number of minutes after 00:00 on Monday
                            to first run the service policy. The offset
                            must be less than the interval of
                            the Snapshot Policy. The format must be in minutes
                            -- int
        :param snapshot_count: The maximum number of snapshots that should be
                               maintained for a specified Snapshot Policy.
                               The maximum count must be between 1 to 1024.
        :param compliance_count_warning: The Number of snapshots which are
                                         not failed or bad when compliance
                                         changes to warning. The warning
                                         compliance count cannot be set to 0
                                         and must be less than or equal to
                                         the maximum count of the Snapshot
                                         Policy. -- int
        :param compliance_count_critical: The Number of snapshots which are
                                          not failed or bad when compliance
                                          changes to critical. If the warning
                                          compliance count is also set, the
                                          critical compliance count must be
                                          less than or equal to that. -- int
        :param storage_group_names: List of storage group names -- list
        :param new_snapshot_policy_name: change the name if set -- str
        :param _async: is the operation asynchronous
        """
        payload = dict()
        if not snapshot_policy_name:
            msg = 'Snapshot policy name cannot be None.'
            LOG.exception(msg)
            raise exception.InvalidInputException(data=msg)

        msg = ('The action supplied must be one of \'Modify\', '
               '\'Suspend\', \'Resume\', \'AssociateToStorageGroups\', '
               '\'DisassociateFromStorageGroups\'.')
        if action:
            try:
                index = [x.lower() for x in (
                    constants.SNAPSHOT_POLICY_ACTIONS)].index(
                    action.lower())
            except ValueError as error:
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg) from error
        else:
            message = 'The action cannot be None. {}'.format(msg)
            LOG.exception(message)
            raise exception.InvalidInputException(data=message)

        payload.update({
            'action': constants.SNAPSHOT_POLICY_ACTIONS[index]})

        if action.lower() == constants.ASSOCIATE_TO_STORAGE_GROUPS.lower():
            LOG.info('Associating storage groups to {spn}.'.format(
                spn=snapshot_policy_name))
            if not storage_group_names:
                msg = 'storage_group_names cannot be None.'
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg)

            associate_to_storage_group_param = dict()
            storage_group_name_param = {
                'storage_group_name': storage_group_names}
            associate_to_storage_group_param.update(
                {'associate_to_storage_group': storage_group_name_param})
            payload.update(associate_to_storage_group_param)
        elif action.lower() == (
                constants.DISASSOCIATE_FROM_STORAGE_GROUPS.lower()):
            LOG.info('Disassociating storage groups from {spn}.'.format(
                spn=snapshot_policy_name))
            if not storage_group_names:
                msg = 'storage_group_names cannot be None.'
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg)

            disassociate_from_storage_group_param = dict()
            storage_group_name_param = {
                'storage_group_name': storage_group_names}
            disassociate_from_storage_group_param.update({
                'disassociate_from_storage_group':
                    storage_group_name_param})
            payload.update(disassociate_from_storage_group_param)
        elif action.lower() == constants.MODIFY_POLICY.lower():
            LOG.info('Modifying {spn}.'.format(spn=snapshot_policy_name))
            modify_param = dict()
            if new_snapshot_policy_name:
                modify_param.update({
                    'snapshot_policy_name': new_snapshot_policy_name})
            if interval:
                modify_param.update(
                    {'interval_mins': policy_interval_enum.get(interval)})
            if offset_mins:
                modify_param.update({'offset_mins': offset_mins})
            if snapshot_count:
                modify_param.update({'snapshot_count': snapshot_count})
            if compliance_count_warning:
                modify_param.update({
                    'compliance_count_warning': compliance_count_warning})
            if compliance_count_critical:
                modify_param.update({
                    'compliance_count_critical': compliance_count_critical})
            if modify_param:
                payload.update({'modify': modify_param})
            else:
                msg = 'No modify payload received.'
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg)

        elif action.lower() == constants.SUSPEND_POLICY.lower():
            LOG.info('Suspending {spn}.'.format(spn=snapshot_policy_name))
        elif action.lower() == constants.RESUME_POLICY.lower():
            LOG.info('Resuming {spn}.'.format(spn=snapshot_policy_name))

        if _async:
            payload.update(constants.ASYNC_UPDATE)

        return self.modify_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SNAPSHOT_POLICY,
            resource_type_id=snapshot_policy_name,
            payload=payload)

    def delete_snapshot_policy(self, snapshot_policy_name):
        """Delete a snapshot policy

        :param snapshot_policy_name: the snapshot policy name-- str
        """
        if not snapshot_policy_name:
            msg = 'Snapshot policy name cannot be None.'
            LOG.exception(msg)
            raise exception.InvalidInputException(data=msg)

        self.delete_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SNAPSHOT_POLICY,
            resource_type_id=snapshot_policy_name)
