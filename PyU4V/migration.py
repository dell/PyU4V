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
"""migration.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)

# Resource constants
ASYNC_UPDATE = constants.ASYNC_UPDATE
MIGRATION = constants.MIGRATION
SYMMETRIX = constants.SYMMETRIX
ENVIRONMENT = constants.ENVIRONMENT
CAPABILITIES = constants.CAPABILITIES
STORAGEGROUP = constants.STORAGEGROUP


class MigrationFunctions(object):
    """MigrationFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource

    def get_migration_info(self, array_id=None):
        """Return migration information for an array.

        :returns: migration info -- dict
        """
        array_id = array_id if array_id else self.array_id
        return self.get_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=array_id)

    def create_migration_environment(self, target_array_id):
        """Create a new migration environment between two arrays.

        Creates a new migration environment between two arrays for use
        with non disruptive migrations

        :param target_array_id: target array id -- str
        :returns: migration environment info -- dict
        """
        return self.create_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            payload={'otherArrayId': target_array_id})

    def delete_migration_environment(self, target_array_id):
        """Delete migration environment.

        Given a target array will delete migration environment, used once
        all migrations are complete

        :param target_array_id: target array id -- str
        """
        self.delete_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=ENVIRONMENT, resource_type_id=target_array_id)

    def get_array_migration_capabilities(self, array_id=None):
        """Check what migration facilities are available.

        :returns: array capabilities -- dict
        """
        array_id = array_id if array_id else self.array_id
        capabilities = self.get_resource(
            category=MIGRATION, resource_level=CAPABILITIES,
            resource_type=SYMMETRIX)
        symm_list = (
            capabilities.get(
                'storageArrayCapability', list()) if capabilities else list())
        array_capabilities = dict()
        for symm in symm_list:
            if symm['arrayId'] == array_id:
                array_capabilities = symm
                break
        return array_capabilities

    # Environment endpoints
    def get_environment_list(self):
        """Get list of all migration environments.

        :returns: environments -- list
        """
        response = self.get_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=ENVIRONMENT)
        return response.get('arrayId', list()) if response else list()

    def get_environment(self, target_array_id):
        """Given a name, return migration environment details.

        :param target_array_id: target array id -- str
        :returns: environment details -- dict
        """
        return self.get_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=ENVIRONMENT, resource_type_id=target_array_id)

    def get_storage_group_list(self, include_migrations=False):
        """Get list of all storage groups or migrating storage groups.

        :param include_migrations: return only SGs with migration
                                   sessions -- bool
        :returns: storage groups or migrating storage groups -- list
        """
        response = self.get_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP)
        return response.get('migratingName') if include_migrations else (
            response.get('name'))

    def get_storage_groups(self):
        """Get all storage groups and migrating storage groups.

        :returns: storage groups and migrating storage groups -- dict
        """
        response = self.get_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP)
        return response

    def get_storage_group(self, storage_group_name):
        """Given a name, return storage group migrations details.

        :param storage_group_name: storage group id -- str
        :returns: storage group details -- dict
        """
        return self.get_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_name)

    def create_storage_group_migration(
            self, storage_group_name, target_array_id, srp_id=None,
            port_group_id=None, no_compression=False, pre_copy=False,
            validate=False):
        """Create a migration session for a storage group.

        :param storage_group_name: storage group id -- str
        :param target_array_id: target array id -- str
        :param srp_id: storage resource pool id -- str
        :param port_group_id: port group id -- str
        :param no_compression: dont use compression -- bool
        :param pre_copy: use pre copy -- bool
        :param validate: validate -- bool
        :returns: new storage group -- dict
        """
        payload = {'otherArrayId': target_array_id}
        if srp_id:
            payload.update({'srpId': srp_id})
        if port_group_id:
            payload.update({'portGroupId': port_group_id})
        if no_compression:
            payload.update({'noCompression': no_compression})
        if pre_copy:
            payload.update({'preCopy': pre_copy})
        if validate:
            payload.update({'validate': validate})

        return self.create_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_name,
            payload=payload)

    def modify_storage_group_migration(
            self, storage_group_name, action, options=None, _async=False):
        """Modify the state of a storage group's migration session.

        Valid migrations options are 'Cutover', 'Sync', 'Commit', 'Recover',
        and 'ReadyTgt'.

        :param storage_group_name: storage group id -- str
        :param action: migration action -- str
        :param options: migration options, example:
                        {cutover': {'force': True}} -- dict
        :param _async: if call should be async -- bool
        :returns: modified storage group info -- dict
        """
        payload = {'action': action}
        if options:
            payload.update(options)
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_name,
            payload=payload)

    def delete_storage_group_migration(self, storage_group_name):
        """Given a name, delete the storage group migration session.

        :param storage_group_name: storage group id -- str
        """
        self.delete_resource(
            category=MIGRATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_name)
