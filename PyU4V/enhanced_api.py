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
"""enhanced_api.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)


class EnhancedAPIFunctions(object):
    """Enhanced Functions for retrieving data about provisioned storage
    objects."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.array_id = array_id
        self.enhanced_api_version = constants.ENHANCED_API_VERSION

    def get_storage_object_meta_data(self, storage_object):
        """Get details on available metadata for storage objects of the
        specified type.

        :param: storage_object, the storage object to get metadata for,
                valid values are directors, hosts, initiators,
                ip-interfaces, ip-routes, masking-views, port-groups, ports,
                rdf-groups, storage-groups, volumes -- string
        :returns: dictionary with list of attributes and descriptions of
                 attribute types used for filtering and selection -- dict
        """
        response = self.common.get_request(
            target_uri=f"/{self.enhanced_api_version}/systems"
                       f"/{storage_object}/metadata",
                       resource_type=None)
        return response

    def get_storage_object_details(
            self, storage_object, array_id=None, filters=None, select=None,
            exclude=None):
        """Get list of volumes from array with selected parameters.

        :param: storage_object, the storage object to get metadata for,
                valid values are directors, hosts, initiators,
                ip-interfaces, ip-routes, masking-views, port-groups, ports,
                rdf-groups, storage-groups, volumes -- string
        :param array_id: The storage array ID -- string
        :param filters: filter parameters, used to narrow down the result
                        list, filters can be any of the volume attributes,
                        and operators vary depending on type,
                        'eq','ne','gt','ge','lt','le', equal, not equal,
                        greater than, greater than or equal, less than,
                        less than or equal, additional operators are
                        'like','ilike' for string match, or case in-sensitive
                        string match, example
                        filters=['num_of_storage_groups eq 1',
                        'identifier ilike findme'] -- list
        :param select: selection of attributes to be in return, attributes
                       can be listed using get_volumes_meta_data function
                       If none selected base set of top level attributes are
                       returned, by default API will only return id,
                       to achieve this pass a list with empty string [''],
                       to extend the list of attributes returned to include
                       second level attributes you can pass along with list
                       from get_volumes_meta_data() e.g.
                       select=api.volumes.get_volumes_meta_data() +
                       ['snapshots.name'] -- list
        :param exclude: list of attributes to exclude, by default rdf_infos
                        and snapshot details have been excluded as these can
                        extend the running of the API call, to override
                        simply pass an empty list or specify a list of
                        attribute names that you want to exclude from the
                        return, if values are passed in by select exclude is
                        ignored -- list
        :returns: dict
        """
        array_id = array_id if array_id else self.array_id
        if not exclude:
            exclude = ['rdf_infos', 'snapshots']
        if not select:
            select = []
            volume_metadata = self.get_storage_object_meta_data(
                storage_object=storage_object)
            for attribute in volume_metadata:
                if attribute['name'] not in exclude:
                    select.append(attribute['name'])
                select.append(attribute['name'])
        select = ','.join(select)
        if filters:
            filters = '&filter=' + ','.join(filters)
        else:
            filters = ''
        response = self.common.get_request(
            target_uri=f"/{self.enhanced_api_version}/systems"
                       f"/{array_id}/{storage_object}"
                       f"?select={select}{filters}",
                       resource_type=None)
        return response
