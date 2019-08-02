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
"""migration.py."""
import logging

from PyU4V.utils import constants

LOG = logging.getLogger(__name__)

MIGRATION = constants.MIGRATION
ASYNC_UPDATE = constants.ASYNC_UPDATE


class MigrationFunctions(object):
    """MigrationFunctions."""

    def __init__(self, array_id, request, common, u4v_version):
        """__init__."""
        self.array_id = array_id
        self.common = common
        self.request = request
        self.U4V_VERSION = u4v_version
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource

    def get_migration_info(self):
        """Return migration information for an array.

        :returns: dict
        """
        target_uri = '/{}/migration/symmetrix/{}'.format(
            self.U4V_VERSION, self.array_id)
        return self.common.get_request(target_uri, 'migration info')

    def get_array_migration_capabilities(self):
        """Check what migration facilities are available.

        :returns: array_capabilities dict
        """
        array_capabilities = {}
        target_uri = ("/{}/migration/capabilities/symmetrix".format(
            self.U4V_VERSION))
        capabilities = self.common.get_request(
            target_uri, 'migration capabilities')
        symm_list = (
            capabilities.get(
                'storageArrayCapability', []) if capabilities else [])
        for symm in symm_list:
            if symm['arrayId'] == self.array_id:
                array_capabilities = symm
                break
        return array_capabilities

    # Environment endpoints
    def get_environment_list(self):
        """Get list of all environments.

        :returns: list of all environments
        """
        response = self.get_resource(self.array_id, MIGRATION, 'environment')
        environment_list = response.get('arrayId', []) if response else []
        return environment_list

    def get_environment(self, environment_name):
        """Given a name, return migration environment details.

        :param environment_name: the name of the migration environment
        returns: environment dict
        """
        return self.get_resource(
            self.array_id, MIGRATION, 'environment',
            resource_name=environment_name)

    def delete_environment(self, environment_name):
        """Given a name, delete the migration environment.

        :param environment_name: the name of the environment
        """
        return self.delete_resource(
            self.array_id, MIGRATION, 'environment',
            resource_name=environment_name)

    # Storage group endpoints
    def get_storage_group_list(self, include_migrations=False):
        """Get list of all storage groups.

        :param include_migrations: return only SGs with migration sessions
        :returns: list of storage groups or migrating storage groups
        """
        filters = {}
        if include_migrations:
            filters.update({'includeMigrations': True})
        response = self.get_resource(
            self.array_id, MIGRATION, 'storagegroup', params=filters)
        key = 'migratingName' if include_migrations else 'name'
        storage_group_list = response.get(key, []) if response else []
        return storage_group_list

    def get_storage_group(self, storage_group_name):
        """Given a name, return storage group details wrt migration.

        :param storage_group_name: the name of the storage group
        :returns: storage group dict
        """
        return self.get_resource(
            self.array_id, MIGRATION, 'storagegroup',
            resource_name=storage_group_name)

    def create_storage_group_migration(
            self, storage_group_name, target_array_id, srp_id=None,
            port_group_id=None, no_compression=None, pre_copy=None,
            validate=None):
        """Create a migration session for a storage group.

        :param storage_group_name: the name of the new SG migration session
        :param target_array_id: the id of the target array
        :param srp_id: the id of the storage resource pool to use
        :param port_group_id: the id of the port group to use
        :param no_compression: boolean, whether or not to use compression
        :param pre_copy: boolean, whether or not to pre copy
        :param validate: boolean, whether or not to validate
        :returns: the new storage group dict
        """
        payload = {"otherArrayId": target_array_id}
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
            self.array_id, MIGRATION, 'storagegroup',
            resource_name=storage_group_name, payload=payload)

    def modify_storage_group_migration(
            self, storage_group_name, action, options=None, _async=False):
        """Modify the state of a storage group's migration session.

        :param storage_group_name: name of the storage group
        :param action: the migration action e.g. Cutover, Sync, Commit,
                       Recover, ReadyTgt
        :param options: a dict of possible options - depends on action type.
                        example options={'cutover': {'force': True}}
        :param _async: flag to indicate if call should be async
        """
        payload = {'action': action}
        if options and action:
            payload.update(options)
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_resource(
            self.array_id, MIGRATION, 'storagegroup',
            resource_name=storage_group_name, payload=payload)

    def delete_storage_group_migration(self, storage_group_name):
        """Given a name, delete the storage group migration session.

        :param storage_group_name: the name of the migrating storage group
        """
        self.delete_resource(
            self.array_id, MIGRATION, 'storagegroup',
            resource_name=storage_group_name)
