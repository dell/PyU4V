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
"""system.py."""

from datetime import datetime
import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)

ARRAY_ID = constants.ARRAY_ID
ARRAY_NUM = constants.ARRAY_NUM
DESCRIPTION = constants.DESCRIPTION
DISK = constants.DISK
FAILED = constants.FAILED
HEALTH = constants.HEALTH
HEALTH_CHECK = constants.HEALTH_CHECK
SG_ID = constants.SG_ID
SG_NUM = constants.SG_NUM
SYMMETRIX = constants.SYMMETRIX
SYSTEM = constants.SYSTEM
TAG = constants.TAG
TAG_NAME = constants.TAG_NAME


class SystemFunctions(object):
    """SystemFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id

    def get_system_health(self, array_id=None):
        """Query for system health information.

        :param array_id: array id -- str
        :returns: system health -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=array_id, object_type=HEALTH)

    def list_system_health_check(self, array_id=None):
        """List previously run system health checks.

        :param array_id: array id -- str
        :returns: system health checks -- list
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            object_type=HEALTH, object_type_id=HEALTH_CHECK)

    def get_health_check_details(self, health_check_id, array_id=None):
        """Gets details of individual health check.

        :param health_check_id: health check id -- str
        :param array_id: array id -- str
        :returns: health check details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=HEALTH, resource_type_id=HEALTH_CHECK,
            object_type=health_check_id)

    def perform_health_check(self, array_id=None, description=None):
        """Initiate a environmental health check.

        :param array_id: array id -- str
        :param description: description for health check, if not set this will
                            default to 'PyU4V-array_id-date-time'
        :returns: health check property details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        now = datetime.now()
        date_now, time_now = now.strftime('%d%m%Y'), now.strftime('%H%M%S')
        if not description:
            description = 'PyU4V-{arr}-{date}-{time}'.format(
                arr=array_id, date=date_now, time=time_now)
        return self.common.create_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            object_type=HEALTH, object_type_id=HEALTH_CHECK,
            payload={DESCRIPTION: description})

    def delete_health_check(self, health_check_id, array_id=None):
        """Delete a health check record.

        :param health_check_id: health check id -- str
        :param array_id: array id -- str
        """
        array_id = self.array_id if not array_id else array_id
        self.common.delete_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=HEALTH, resource_type_id=HEALTH_CHECK,
            object_type=health_check_id)

    def get_disk_id_list(self, array_id=None, failed=False):
        """Get a list of disks ids installed.

        :param array_id: array id -- str
        :param failed: if only failed disks should be returned -- bool
        :returns: disk ids -- list
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DISK, params={FAILED: failed})

    def get_disk_details(self, disk_id, array_id=None):
        """Get details for specified disk id.

        :param disk_id: disk id -- str
        :param array_id: array id -- str
        :returns: disk details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DISK, resource_type_id=disk_id)

    def get_tags(self, array_id=None, tag_name=None, storage_group_id=None,
                 num_of_storage_groups=None, num_of_arrays=None):
        """Query for a list of tag names.

        The input parameters represent optional filters for the tag query,
        including any filters will apply that filter to the list of returned
        tags.

        :param array_id: filter by array id -- str
        :param tag_name: filter by tag name -- str
        :param storage_group_id: filter by storage group id -- str
        :param num_of_storage_groups: filter by tags that are in x or greater
                                      amount of storage groups -- int
        :param num_of_arrays: filter by tags that in y or greater amount of
                              arrays -- int
        :returns: tags -- list
        """
        filters = dict()
        if array_id:
            filters[ARRAY_ID] = array_id
        if tag_name:
            filters[TAG_NAME] = tag_name
        if storage_group_id:
            filters[SG_ID] = storage_group_id
        if num_of_storage_groups:
            filters[SG_NUM] = str(num_of_storage_groups)
        if num_of_arrays:
            filters[ARRAY_NUM] = str(num_of_arrays)

        return self.common.get_resource(
            category=SYSTEM, resource_level=TAG, params=filters)

    def get_tagged_objects(self, tag_name):
        """Get a list of objects with specified tag.

        :param tag_name: tag name -- str
        :returns: tags -- list
        """
        return self.common.get_resource(
            category=SYSTEM, resource_level=TAG, resource_level_id=tag_name)
