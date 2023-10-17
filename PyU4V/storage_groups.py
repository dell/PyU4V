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
"""storage_groups.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)


class StorageGroupsFunctions(object):
    """Enhanced Functions for retrieving Array Configuration Data."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.array_id = array_id
        self.enhanced_api_version = constants.ENHANCED_API_VERSION

    def get_storage_groups_meta_data(self):
        """Get details on available meta data for storage group objects.

        returns: dictionary with list of attributes and descriptions of
                 attribute types -- dict
        """
        response = constants.STORAGEGROUP_META_DATA
        return response

    def get_storage_groups_details(
            self, array_id=None, filters=None, select=None,
            exclude=None):
        """Get list of storage_groups from array with selected parameters.

        :param array_id: The storage array ID -- string
        :param filters: filter parameters, used to narrow down the result
                        list, filters can be any of the storage_groups
                        attributes and operators vary depending on type,
                        'eq','ne','gt','ge','lt','le', equal, not equal,
                        greater than, greater than or equal, less than,
                        less than or equal, additional operators are
                        'like','ilike' for string match, or case in-sensitive
                        string match, example
                        filters=['id ilike gk', 'num_of_volumes eq 32'] -- list
        :param select: selection of attributes to be in return, attributes
                       can be listed using get_storage_groups_meta_data
                       function e.g. ['volumes.wwn','volumes.effective_wwn',
                       'type', 'effective_used_capacity_gb'] If none
                       selected base set of top level attributes are
                       returned, by default API will only return id,
                       to achieve this pass a list with empty string ['']
                       -- list
        :param exclude: list of attributes to exclude, by default rdf_infos
                        and snapshot details have been excluded as these can
                        extend the running of the API call, to override
                        simply pass an empty list or specify a list of
                        attribute names that you want to exclude from the
                        return, , if values are passed in by select exclude is
                        ignored -- list
        """
        array_id = array_id if array_id else self.array_id
        if not exclude:
            exclude = ['rdf_infos', 'snapshots']
        if not select:
            select = []
            storage_groups_metadata = (self.get_storage_groups_meta_data())
            for attribute in storage_groups_metadata:
                if attribute['name'] not in exclude:
                    select.append(attribute['name'])
        select = ','.join(select)
        if filters:
            filters = '&filter=' + ','.join(filters)
        else:
            filters = ''
        response = self.common.get_request(
            target_uri=f"/{self.enhanced_api_version}/systems"
                       f"/{array_id}/storage-groups?select={select}{filters}",
            resource_type=None)
        return response
