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
STORAGEGROUP = constants.STORAGEGROUP
COMPLIANCE = constants.COMPLIANCE
SNAPSHOT = constants.SNAPSHOT
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

    def get_snapshot_policy_storage_group_list(self, snapshot_policy_name):
        """Get list of storage groups associated to specified snapshot policy.

        :param snapshot_policy_name: name of the snapshot policy -- str
        :returns: snapshot policy details -- list
        """
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SNAPSHOT_POLICY,
            resource_type_id=snapshot_policy_name, object_type=STORAGEGROUP)
        return response.get('name', list()) if response else list()

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
                         '8 Hours', '12 Hours', '1 Day', '7 Days' -- str
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
                            the Snapshot Policy. For daily snapshots the offset
                            is the number of minutes after midnight UTC,
                            for weekly the offset is from midnight UTC on
                            the Sunday. The format must be in minutes -- int
        :param compliance_count_warning: The Number of snapshots which are
                                         not failed or bad when compliance
                                         changes to warning. -- int
        :param compliance_count_critical: The Number of snapshots which are
                                          not failed or bad when compliance
                                          changes to critical. -- int
        :param _async: is the operation asynchronous -- bool
        :returns: resource object -- dict
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

    def associate_to_storage_groups(
            self, snapshot_policy_name, storage_group_names, _async=False):
        """Associate a snapshot policy to storage group(s).

        :param snapshot_policy_name: the snapshot policy name -- str
        :param storage_group_names: List of storage group names -- list
        :param _async: is the operation asynchronous -- bool
        :returns: resource object -- dict
        """
        return self.modify_snapshot_policy(
            snapshot_policy_name, constants.ASSOCIATE_TO_STORAGE_GROUPS,
            storage_group_names=storage_group_names, _async=_async)

    def disassociate_from_storage_groups(
            self, snapshot_policy_name, storage_group_names, _async=False):
        """Disassociate a snapshot policy from storage group(s).

        :param snapshot_policy_name: the snapshot policy name -- str
        :param storage_group_names: List of storage group names -- list
        :param _async: is the operation asynchronous -- bool
        :returns: resource object -- dict
        """
        return self.modify_snapshot_policy(
            snapshot_policy_name, constants.DISASSOCIATE_FROM_STORAGE_GROUPS,
            storage_group_names=storage_group_names, _async=_async)

    def suspend_snapshot_policy(
            self, snapshot_policy_name, _async=False):
        """Suspend a snapshot policy.

        :param snapshot_policy_name: the snapshot policy name -- str
        :param _async: is the operation asynchronous -- bool
        :returns: resource object -- dict
        """
        return self.modify_snapshot_policy(
            snapshot_policy_name, constants.SUSPEND_POLICY,
            _async=_async)

    def resume_snapshot_policy(
            self, snapshot_policy_name, _async=False):
        """Suspend a snapshot policy

        :param snapshot_policy_name: the snapshot policy name -- str
        :param _async: is the operation asynchronous -- bool
        :returns: resource object -- dict
        """
        return self.modify_snapshot_policy(
            snapshot_policy_name, constants.RESUME_POLICY,
            _async=_async)

    def modify_snapshot_policy_properties(
            self, snapshot_policy_name, interval=None,
            offset_mins=None, snapshot_count=None,
            compliance_count_warning=None, compliance_count_critical=None,
            new_snapshot_policy_name=None, _async=False):
        """Suspend a snapshot policy

        :param snapshot_policy_name: the snapshot policy name -- str
        :param interval: The value of the interval counter for snapshot
                         policy execution. Must be one of '10 Minutes',
                         '12 Minutes', '15 Minutes', '20 Minutes',
                         '30 Minutes', '1 Hour',
                         '2 Hours', '3 Hours', '4 Hours', '6 Hours',
                         '8 Hours', '12 Hours', '1 Day', '7 Days' -- str
        :param offset_mins: The number of minutes after 00:00 on Monday
                            to first run the service policy. The offset
                            must be less than the interval of
                            the Snapshot Policy. The format must be in minutes
                            -- int
        :param snapshot_count: The maximum number of snapshots that should be
                               maintained for a specified Snapshot Policy.
                               The maximum count must be between 1 to 1024.
                               -- int
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
        :param new_snapshot_policy_name: change the name if set -- str
        :param _async: is the operation asynchronous -- bool
        :returns: resource object -- dict
        """
        return self.modify_snapshot_policy(
            snapshot_policy_name, constants.MODIFY_POLICY,
            interval=interval, offset_mins=offset_mins,
            snapshot_count=snapshot_count,
            compliance_count_warning=compliance_count_warning,
            compliance_count_critical=compliance_count_critical,
            new_snapshot_policy_name=new_snapshot_policy_name,
            _async=_async)

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

        :param snapshot_policy_name: the snapshot policy name -- str
        :param action: the modification action, must be one of
                       'AssociateToStorageGroups',
                       'DisassociateFromStorageGroups'
                       'Modify', 'Suspend', 'Resume' -- str
        :param interval: The value of the interval counter for snapshot
                         policy execution. Must be one of '10 Minutes',
                         '12 Minutes', '15 Minutes', '20 Minutes',
                         '30 Minutes', '1 Hour',
                         '2 Hours', '3 Hours', '4 Hours', '6 Hours',
                         '8 Hours', '12 Hours', '1 Day', '7 Days' -- str
        :param offset_mins: The number of minutes after 00:00 on Monday
                            to first run the service policy. The offset
                            must be less than the interval of
                            the Snapshot Policy. The format must be in minutes
                            -- int
        :param snapshot_count: The maximum number of snapshots that should be
                               maintained for a specified Snapshot Policy.
                               The maximum count must be between 1 to 1024.
                               -- int
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
        :param _async: is the operation asynchronous -- bool
        :returns: resource object -- dict
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

        :param snapshot_policy_name: the snapshot policy name -- str
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

    def get_snapshot_policy_compliance(
            self, storage_group_name, last_week=False, last_four_weeks=False,
            from_epoch=None, to_epoch=None, from_time_string=None,
            to_time_string=None):
        """Get compliance attributes on a storage group.

        :param storage_group_name: storage group name
        :param last_week: compliance in last week -- bool
        :param last_four_weeks: compliance in last four weeks -- bool
        :param from_epoch: timestamp since epoch -- str
                           e.g 1606820929 (seconds)
        :param to_epoch: timestamp since epoch -- str
                         e.g 1606820929 (seconds)
        :param from_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :param to_time_string: human readable date -- str
                               e.g 2020-12-01 15:00
        :returns: resource -- dict
        """
        if not storage_group_name:
            msg = 'Storage group name cannot be None.'
            LOG.exception(msg)
            raise exception.InvalidInputException(data=msg)

        msg, query_params = self.verify_input_params(
            last_week, last_four_weeks, from_epoch, to_epoch,
            from_time_string, to_time_string)
        if msg:
            LOG.exception(msg)
            raise exception.InvalidInputException(data=msg)

        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_name,
            resource=COMPLIANCE, object_type=SNAPSHOT,
            params=query_params)

    def get_snapshot_policy_compliance_last_week(
            self, storage_group_name):
        """Get compliance attributes on a storage group for the last week.

        :param storage_group_name: storage group name
        :returns: resource -- dict
        """
        return self.get_snapshot_policy_compliance(
            storage_group_name, last_week=True)

    def get_snapshot_policy_compliance_last_four_weeks(
            self, storage_group_name):
        """Get compliance attributes for the last four weeks.

        Get compliance attributes on a storage group for the last
        four weeks

        :param storage_group_name: storage group name
        :returns: resource -- dict
        """
        return self.get_snapshot_policy_compliance(
            storage_group_name, last_four_weeks=True)

    def get_snapshot_policy_compliance_epoch(
            self, storage_group_name, from_epoch=None, to_epoch=None):
        """Get compliance attributes for the last four weeks.

        Get compliance attributes on a storage group for the last
        four weeks

        :param storage_group_name: storage group name
        :param from_epoch: timestamp since epoch -- str
                           e.g 1606820929 (seconds)
        :param to_epoch: timestamp since epoch -- str
                         e.g 1606820929 (seconds)
        :returns: resource -- dict
        """
        return self.get_snapshot_policy_compliance(
            storage_group_name, from_epoch=from_epoch, to_epoch=to_epoch)

    def get_snapshot_policy_compliance_human_readable_time(
            self, storage_group_name, from_time_string=None,
            to_time_string=None):
        """Get compliance attributes for the last four weeks.

        Get compliance attributes on a storage group for the last
        four weeks

        :param storage_group_name: storage group name
        :param from_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :param to_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :returns: resource -- dict
        """
        return self.get_snapshot_policy_compliance(
            storage_group_name, from_time_string=from_time_string,
            to_time_string=to_time_string)

    def verify_input_params(
            self, last_week, last_four_weeks, from_epoch, to_epoch,
            from_time_string, to_time_string):
        """Verify the input parameters for compliance.

        :param last_week: compliance in last week -- bool
        :param last_four_weeks: compliance in last four weeks -- bool
        :param from_epoch: timestamp since epoch -- str
                           e.g 1606820929 (seconds)
        :param to_epoch: timestamp since epoch -- str
                         e.g 1606820929 (seconds)
        :param from_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :param to_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :returns: msg or None -- str
                  query_params -- dict

        """
        msg = self.verify_combination(
            last_week, last_four_weeks, from_epoch, from_time_string)
        if msg:
            return msg, None
        msg, query_params = self.verify_from_epoch(
            from_epoch, to_epoch, to_time_string)
        if msg:
            return msg, None
        if to_epoch:
            if not from_epoch and not from_time_string:
                return ('to_epoch must be accompanied with one of from_epoch '
                        'or from_time_string.', None)
            if to_time_string:
                return ('to_epoch and to_time_string should not both '
                        'be supplied as they are different formats of the '
                        'same thing.', None)
        msg, query_params = self.verify_from_time_string(
            to_epoch, to_time_string, from_time_string)
        if msg:
            return msg, None
        if to_time_string:
            if not from_time_string and not from_epoch:
                return ('to_time_string must be accompanied with one of '
                        'from_time_string or to_epoch.', None)

        return None, query_params

    @staticmethod
    def verify_combination(
            last_week, last_four_weeks, from_epoch, from_time_string):
        """Verify the valid combinations for compliance.

        :param last_week: compliance in last week -- bool
        :param last_four_weeks: compliance in last four weeks -- bool
        :param from_epoch: timestamp since epoch -- str
                           e.g 1606820929 (seconds)
        :param from_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :returns: msg or None -- str
        """
        input_params_list = (
            [last_week, last_four_weeks, from_epoch, from_time_string])
        if len([i for i in input_params_list if i]) > 1:
            return ('Only one of last_week, last_four_weeks, from_epoch, '
                    'from_time_string can be true or not None.')
        return None

    def verify_from_epoch(
            self, from_epoch, to_epoch, to_time_string):
        """Verify the the from_epoch param for compliance.

        :param from_epoch: timestamp since epoch -- str
                           e.g 1606820929 (seconds)
        :param to_epoch: timestamp since epoch -- str
                         e.g 1606820929 (seconds)
        :param to_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :returns: msg or None -- str
                  query_params -- dict
        """
        query_params = dict()
        if from_epoch:
            if self.common.check_epoch_timestamp(from_epoch):
                if not to_epoch and not to_time_string:
                    return ('from_epoch must be accompanied with one of '
                            'to_epoch or to_time_string.', None)
                if to_epoch:
                    if self.common.check_epoch_timestamp(to_epoch):
                        query_params['from_epoch'] = from_epoch
                        query_params['to_epoch'] = to_epoch
                    else:
                        return ('to_epoch {} is in the wrong format.'.format(
                            to_epoch), None)
                elif to_time_string:
                    if self.common.check_timestamp(to_time_string):
                        query_params['from_epoch'] = from_epoch
                        query_params['toTimeString'] = to_time_string
                    else:
                        return (
                            'to_time_string {} is in the wrong format.'.format(
                                to_time_string), None)
            else:
                return ('from_epoch {} is in the wrong format.'.format(
                    from_epoch), None)
        return None, query_params

    def verify_from_time_string(
            self, to_epoch, to_time_string, from_time_string):
        """Verify the the from_time_string param for compliance.

        :param to_epoch: timestamp since epoch -- str
                         e.g 1606820929 (seconds)
        :param from_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :param to_time_string: human readable date -- str
                                 e.g 2020-12-01 15:00
        :returns: msg or None -- str
                  query_params -- dict
        """
        query_params = dict()
        if from_time_string:
            if self.common.check_timestamp(from_time_string):
                if not to_time_string and not to_epoch:
                    return ('from_time_string must be accompanied with one of '
                            'to_time_string or to_epoch.', None)
                if to_time_string:
                    if self.common.check_timestamp(to_time_string):
                        query_params['fromTimeString'] = from_time_string
                        query_params['toTimeString'] = to_time_string
                    else:
                        return (
                            'to_time_string {} is in the wrong format.'.format(
                                to_time_string), None)
                elif to_epoch:
                    query_params['fromTimeString'] = from_time_string
                    query_params['to_epoch'] = to_epoch
            else:
                return ('from_time_string {} is in the wrong format.'.format(
                    from_time_string), None)
        return None, query_params
