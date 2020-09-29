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
"""
OpenStack migrate_utils.py.

Migrate utilities for OpenStack
"""

from __future__ import print_function

from builtins import input
import logging
import re
import sys
import uuid

from PyU4V.utils import exception

import prettytable

LOG = logging.getLogger(__name__)

YES_CONSTANTS = ['y', 'yes']
NO_CONSTANTS = ['n', 'no']
EXIT_CONSTANTS = ['x', 'exit']

VERSION = '2.0.0'

DEBUG = 'DEBUG'
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'


class MigrateUtils(object):
    """OpenStack migrate utils."""

    def __init__(self, conn):
        """Initialize class.

        :param conn: the request connection -- obj
        """
        self.conn = conn

    @staticmethod
    def check_input(txt_str, option):
        """Check the input against the expected option.

        :param txt_str: text string -- str
        :param option: 'Y', 'N' or 'X' -- str
        :returns: boolean
        """
        if option == 'Y':
            return txt_str.lower() in YES_CONSTANTS
        elif option == 'N':
            return txt_str.lower() in NO_CONSTANTS
        elif option == 'X':
            LOG.debug('I am exiting')
            return txt_str.lower() in EXIT_CONSTANTS
        else:
            return False

    @staticmethod
    def print_to_log(print_str, level=DEBUG):
        """Print to the logs

        :param print_str: string to print -- str
        :param level: the debug level -- str
        """
        if level == ERROR:
            LOG.error(print_str)
        elif level == WARNING:
            LOG.warning(print_str)
        elif level == INFO:
            LOG.info(print_str)
        else:
            LOG.debug(print_str)

    @staticmethod
    def print_pretty_table(datadict):
        """Print the data in the dict.

        :param datadict: the data dictionary -- dict
        """
        t = prettytable.PrettyTable(['Key', 'Value'])
        for k, v in datadict.items():
            if v is not None:
                t.add_row([k, v])
        print(t)
        LOG.debug(t)
        print('\n')

    def smart_print(self, print_str, level, *args):
        """Print with variable arguments.

        :param print_str: the print string -- str
        :param level: the debug level -- str
        :param args: one or more arguments
        """
        print_str = print_str % args
        self.print_to_log(print_str, level)
        print(print_str)

    def get_elements_from_masking_view(self, masking_view_name):
        """Get components from masking view.

        :param masking_view_name: masking view name -- str
        :returns: portgroup -- str, storagegroup -- str, host -- str
        """
        masking_view_components = dict()
        try:
            masking_view_components['portgroup'] = (
                self.conn.provisioning.get_element_from_masking_view(
                    masking_view_name, portgroup=True))
            masking_view_components['storagegroup'] = (
                self.conn.provisioning.get_element_from_masking_view(
                    masking_view_name, storagegroup=True))
            masking_view_components['initiatorgroup'] = (
                self.conn.provisioning.get_element_from_masking_view(
                    masking_view_name, host=True))
        except exception.ResourceNotFoundException as error:
            exception_message = (
                'Cannot find one of the components of %s' % masking_view_name)
            self.smart_print(exception_message, ERROR)
            raise exception.ResourceNotFoundException(
                data=exception_message) from error

        self.print_pretty_table(masking_view_components)
        return masking_view_components

    @staticmethod
    def verify_protocol(protocol):
        """Verify the protocol.

        :param protocol: 'I' or 'F' -- str
        :returns: boolean
        """
        return bool(
            len(protocol) == 1 and ('I' in protocol or 'F' in protocol))

    @staticmethod
    def get_object_components(regex_str, input_str):
        """Get components from input string.

        :param regex_str: the regex -- str
        :param input_str: the input string -- str
        :returns: dict
        """
        full_str = re.compile(regex_str)
        match = full_str.match(input_str)
        return match.groupdict() if match else None

    def get_object_components_and_correct_host(self, regex_str, input_str):
        """Get components from input string.

        :param regex_str: the regex -- str
        :param input_str: the input string -- str
        :returns: object components -- dict
        """
        object_dict = self.get_object_components(regex_str, input_str)
        if object_dict and 'host' in object_dict:
            if object_dict['host'].endswith('-'):
                object_dict['host'] = object_dict['host'][:-1]
        return object_dict

    def get_masking_view_component_dict(
            self, masking_view_name, revert=False):
        """Get components from input string.

        :param masking_view_name: the masking view name -- str
        :param revert: is it a revert back -- boolean
        :returns: object components -- dict
        """
        if revert:
            regex_str = (r'^(?P<prefix>OS)-(?P<host>.+?)(?P<protocol>I|F)-'
                         r'(?P<portgroup>(?!CD|RE|CD-RE).+)-(?P<postfix>MV)$')
        else:
            regex_str = (r'^(?P<prefix>OS)-(?P<host>.+?)((?P<srp>SRP.+?)-'
                         r'(?P<slo>.+?)-(?P<workload>.+?)|(?P<no_slo>No_SLO))-'
                         r'(?P<protocol>I|F)(?P<CD>-CD|s*)(?P<RE>-RE|s*)-'
                         r'(?P<postfix>MV)$')
        return self.get_object_components_and_correct_host(
            regex_str, masking_view_name)

    @staticmethod
    def truncate_string(str_to_truncate, max_num):
        """Truncate a string by taking first and last characters.

        :param str_to_truncate: the string to be truncated -- str
        :param max_num: the maximum number of characters -- int
        :returns: truncated string or original string -- str
        """
        if len(str_to_truncate) > max_num:
            new_num = len(str_to_truncate) - max_num // 2
            first_chars = str_to_truncate[:max_num // 2]
            last_chars = str_to_truncate[new_num:]
            str_to_truncate = first_chars + last_chars
        return str_to_truncate

    def print_component_dict(self, masking_view_name, revert=False):
        """Print the components to the screen.

        :param masking_view_name: the masking view name -- str
        :param revert: is it a revert back -- boolean
        :returns: component details -- dict
        """
        if revert:
            self.smart_print('\n', DEBUG)
            self.smart_print(
                'Checking if masking view is in the following format: ',
                DEBUG)
            self.smart_print(
                '\tOS-[shortHostName]-[protocol]-[portgroup_name]-MV',
                DEBUG)
            component_dict = self.get_masking_view_component_dict(
                masking_view_name, revert)
            print('\n')
        else:
            self.smart_print('\n', DEBUG)
            self.smart_print(
                'Checking if masking view is in the following 2 formats: ',
                DEBUG)
            self.smart_print(
                '\tOS-[shortHostName]-[SRP]-[SLO]-[workload]-[protocol]-MV',
                DEBUG)
            self.smart_print('\t\tOR', DEBUG)
            self.smart_print('\tOS-[shortHostName]-No_SLO-[protocol]-MV',
                             DEBUG)
            self.smart_print('\n', DEBUG)
            component_dict = self.get_masking_view_component_dict(
                masking_view_name)
            self.smart_print('COMPONENTS OF %s', DEBUG, masking_view_name)
        if component_dict:
            self.print_pretty_table(component_dict)

        return component_dict

    def check_masking_view_for_migration(
            self, masking_view_name, revert=False):
        """Check if the masking view can be migrated.

        :param masking_view_name: the masking view name -- str
        :param revert: is it a revert case -- boolean
        :returns: flag -- boolean
        """
        if revert:
            component_dict = self.print_component_dict(
                masking_view_name, revert)
            if component_dict and self.verify_protocol(
                    component_dict['protocol']):
                print_str = '%s HAS BEEN VERIFIED TO BEING IN THE NEW FORMAT.'
                self.smart_print(print_str, DEBUG, masking_view_name)
                return True
            else:
                print_str = (
                    '%s IS NOT IN THE NEW FORMAT, MIGRATION WILL NOT '
                    'PROCEED.')
                self.smart_print(print_str, WARNING, masking_view_name)
                return False
        else:
            component_dict = self.print_component_dict(masking_view_name)
            if component_dict and self.verify_protocol(
                    component_dict['protocol']):
                print_str = '%s HAS BEEN VERIFIED TO BEING IN THE OLD FORMAT.'
                self.smart_print(print_str, DEBUG, masking_view_name)
                return True
            else:
                print_str = ('%s IS NOT IN THE OLD FORMAT, MIGRATION WILL NOT '
                             'PROCEED.')
                self.smart_print(print_str, WARNING, masking_view_name)
                return False

    def get_storage_group_component_dict(self, storage_group_name):
        """Parse the storage group string.

        :param storage_group_name: the storage group name -- str
        :returns: object components -- dict
        """
        regex_str = (r'^(?P<prefix>OS)-(?P<host>.+?)'
                     r'((?P<no_slo>No_SLO)|((?P<srp>SRP.+?)-'
                     r'(?P<sloworkload>.+?)))-(?P<portgroup>.+?)'
                     r'(?P<after_pg>$|-CD|-RE)')
        return self.get_object_components_and_correct_host(
            regex_str, storage_group_name)

    def get_element_dict_revert(
            self, component_dict, storage_group_name, cd_str, re_str,
            port_group_name, host_name):
        """Compile elements from mv, sg, host etc.

        :param component_dict: masking view dict -- dict
        :param storage_group_name: storage group name -- str
        :param cd_str: compression disabled -- str
        :param re_str: replication enabled -- str
        :param port_group_name: port group name -- str
        :param host_name: host name -- str
        :returns: element details -- dict
        """
        element_dict = dict()

        sg_component_dict = self.get_storage_group_component_dict(
            storage_group_name)
        if sg_component_dict:
            if sg_component_dict['sloworkload']:
                storagegroup = self.get_storage_group(storage_group_name)
                if storagegroup:
                    prefix = (component_dict['prefix']
                              + '-' + component_dict['host']
                              + '-' + sg_component_dict['srp']
                              + '-' + storagegroup['slo']
                              + '-' + self.get_workload(storagegroup)
                              + '-' + component_dict['protocol']
                              + cd_str + re_str)
                    element_dict['new_mv_name'] = prefix + '-MV'
                    element_dict['new_sg_name'] = prefix + '-SG'

                    element_dict['srp'] = sg_component_dict['srp']
                    element_dict['service_level'] = storagegroup['slo']
                    element_dict['workload'] = self.get_workload(storagegroup)
                else:
                    return element_dict
            else:
                prefix = (component_dict['prefix'] + '-'
                          + component_dict['host'] + '-'
                          + 'No_SLO' + '-'
                          + component_dict['protocol']
                          + cd_str + re_str)
                element_dict['new_mv_name'] = prefix + '-MV'
                element_dict['new_sg_name'] = prefix + '-SG'

            element_dict['port_group'] = port_group_name
            element_dict['initiator_group'] = host_name
        return element_dict

    @staticmethod
    def get_workload(storage_group):
        """Get the workload from the storagegroup object.

        :param storage_group: storagegroup -- object
        :returns: workload -- str
        """
        try:
            workload = storage_group['workload']
        except KeyError:
            workload = 'NONE'
        return workload

    def get_element_dict(self, component_dict, cd_str, re_str,
                         port_group_name, host_name):
        """Compile elements from mv, sg, host etc.

        :param component_dict: masking view dict -- dict
        :param cd_str: compression disabled -- str
        :param re_str: replication enabled -- str
        :param port_group_name: port group name -- str
        :param host_name: host name -- str
        :returns: element details -- dict
        """
        element_dict = dict()
        element_dict['new_mv_name'] = (component_dict['prefix'] + '-'
                                       + component_dict['host'] + '-'
                                       + component_dict['protocol'] + '-'
                                       + port_group_name + '-MV')
        element_dict['new_sg_parent_name'] = (component_dict['prefix'] + '-'
                                              + component_dict['host'] + '-'
                                              + component_dict['protocol']
                                              + '-' + port_group_name + '-SG')

        if component_dict['srp']:
            slo_wl_combo = self.truncate_string(
                component_dict['slo'] + component_dict['workload'], 10)
            element_dict['new_sg_name'] = (component_dict['prefix'] + '-'
                                           + component_dict['host'] + '-'
                                           + component_dict['srp'] + '-'
                                           + slo_wl_combo
                                           + '-' + port_group_name + cd_str
                                           + re_str)
            element_dict['srp'] = component_dict['srp']
            element_dict['service_level'] = component_dict['slo']
            element_dict['workload'] = component_dict['workload']
        else:
            element_dict['new_sg_name'] = (component_dict['prefix'] + '-'
                                           + component_dict['host'] + '-'
                                           + 'No_SLO' + '-'
                                           + port_group_name + cd_str
                                           + re_str)
        element_dict['port_group'] = port_group_name
        element_dict['initiator_group'] = host_name
        return element_dict

    def compile_new_element_names(
            self, masking_view_name, port_group_name, host_name,
            storage_group_name, revert=False):
        """Compile elements from mv, sg, host etc.

        :param masking_view_name: masking view name -- str
        :param port_group_name: port group name -- str
        :param host_name: host name -- str
        :param storage_group_name: storage group name -- str
        :param revert: is it a revert case -- boolean
        :returns: element details -- dict
        """
        element_dict = dict()
        cd_str = ''
        re_str = ''
        regex_all = '\\S+'
        if re.search('^OS-' + regex_all + '-CD', storage_group_name):
            cd_str = '-CD'
            element_dict['CD'] = 'CD'
        if re.search('^OS-' + regex_all + '-RE', storage_group_name):
            re_str = '-RE'
            element_dict['RE'] = 'RE'
        component_dict = self.get_masking_view_component_dict(
            masking_view_name, revert)
        if component_dict:
            if revert:
                element_dict = self.get_element_dict_revert(
                    component_dict, storage_group_name, cd_str, re_str,
                    port_group_name, host_name)
            else:
                element_dict = self.get_element_dict(
                    component_dict, cd_str, re_str,
                    port_group_name, host_name)
        else:
            print_str = 'UNABLE TO PARSE %s, MIGRATION WILL NOT ' \
                        'PROCEED.'
            self.smart_print(print_str, WARNING, masking_view_name)

        return element_dict

    def validate_existing_masking_view(
            self, masking_view_details, old_port_group, old_host,
            element_dict, revert=False):
        """Validate the masking view.

        :param masking_view_details: masking view details -- dict
        :param old_port_group: port group name -- str
        :param old_host: host name -- str
        :param element_dict: the element dictionary -- dict
        :param revert: is it a revert back -- boolean
        :returns: flag -- boolean
        """
        self.smart_print(
            'NEW MASKING VIEW %s', DEBUG,
            masking_view_details['maskingViewId'])
        masking_view_components = self.get_elements_from_masking_view(
            masking_view_details['maskingViewId'])
        if old_port_group != masking_view_components['portgroup']:
            self.smart_print(
                'Portgroups are not equal, please assess', DEBUG)
            return False
        if old_host != masking_view_components['initiatorgroup']:
            print_str = 'Hosts are not equal, please assess'
            self.smart_print(print_str, WARNING)
            return False
        if revert:
            if element_dict['new_sg_name'] != (
                    masking_view_components['storagegroup']):
                print_str = 'Storage group is not equal, please assess'
                self.smart_print(print_str, WARNING)
                return False
        else:
            if element_dict['new_sg_parent_name'] != (
                    masking_view_components['storagegroup']):
                print_str = (
                    'Parent storage group is not equal, please assess')
                self.smart_print(print_str, WARNING)
                return False
            # Check if child storage group exists
            child_storage_group = self.get_storage_group(
                element_dict['new_sg_name'])
            if child_storage_group:
                # Check if the child SG is part of the parent
                self._existing_child_storage_group_check(
                    element_dict['new_sg_name'],
                    element_dict['new_sg_parent_name'])
            else:
                self.create_child_storage_group_and_add_to_parent(
                    element_dict)
        return True

    def get_storage_group(self, storage_group_name):
        """Get the storage group object from the name.

        :param storage_group_name: storage group name -- str
        :returns: storage group -- dict
        """
        storage_group = None
        try:
            storage_group = self.conn.provisioning.get_storage_group(
                storage_group_name)
        except exception.ResourceNotFoundException:
            print_str = 'Storage group %s not found'
            self.smart_print(print_str, WARNING, storage_group_name)
        return storage_group

    def create_child_storage_group_and_add_to_parent(self, element_dict):
        """Create child storage group.

        :param element_dict: element details -- dict
        """
        print_str = '%s child storage group does not exist so creating it.'
        self.smart_print(print_str, DEBUG, element_dict['new_sg_name'])
        # Create a new child storage group with one volume in it
        disable_compression = False
        if 'CD' in element_dict:
            disable_compression = True
        if 'srp' in element_dict:
            message = self.conn.provisioning.create_non_empty_storage_group(
                element_dict['srp'],
                element_dict['new_sg_name'],
                element_dict['service_level'],
                element_dict['workload'], '1', '1', 'GB',
                disable_compression)
        else:
            message = self.conn.provisioning.create_empty_storage_group(
                None, element_dict['new_sg_name'], None, None)
            # Add a volume to it
            self.conn.provisioning.create_volume_from_storage_group_return_id(
                'first_vol', element_dict['new_sg_name'], '1')

        print_str = 'CREATED CHILD STORAGE GROUP %s.'
        self.smart_print(print_str, DEBUG, element_dict['new_sg_name'])
        self.print_pretty_table(message)
        # Add the child to the parent storage group
        self._add_child_to_parent(element_dict['new_sg_name'],
                                  element_dict['new_sg_parent_name'])

    def _existing_child_storage_group_check(
            self, storage_group_child, storage_group_parent):
        """Check that child is part of parent, if not, add it

        :param storage_group_child: child storage group name -- str
        :param storage_group_parent: parent storage group name -- str
        """
        prov = self.conn.provisioning
        if not prov.is_child_storage_group_in_parent_storage_group(
                storage_group_child, storage_group_parent):
            print_str = (
                'The child sg is not part of the parent sg: %s')
            self.smart_print(
                print_str, DEBUG, storage_group_child)
            self._add_child_to_parent(
                storage_group_child, storage_group_parent)

    def _add_child_to_parent(self, child_storage_group, parent_storage_group):
        """Add child storage group to parent storage group

        :param child_storage_group: child storage group name -- str
        :param parent_storage_group: parent storage group name -- str
        """
        message = (
            self.conn.provisioning.add_child_storage_group_to_parent_group(
                child_storage_group, parent_storage_group))
        print_str = 'ADDED CHILD STORAGE GROUP %s TO PARENT STORAGE GROUP %s.'
        self.smart_print(print_str, DEBUG, child_storage_group,
                         parent_storage_group)
        self.print_pretty_table(message)

    def get_or_create_cascaded_storage_group(self, element_dict):
        """Get or create cascaded storage group.

        :param element_dict: element dictionary -- dict
        :returns: parent storage group -- dict
        """
        storage_group_parent = self.get_storage_group(
            element_dict['new_sg_parent_name'])
        if not storage_group_parent:
            print_str = (
                '%s parent storage group does not exist so '
                'creating it.')
            self.smart_print(
                print_str, DEBUG, element_dict['new_sg_parent_name'])
            # Create a new empty parent storage group
            message = self.conn.provisioning.create_empty_storage_group(
                element_dict['srp'], element_dict['new_sg_parent_name'],
                None, None)
            self.print_pretty_table(message)
            storage_group_parent = self.get_storage_group(
                element_dict['new_sg_parent_name'])
        storage_group_child = self.get_storage_group(
            element_dict['new_sg_name'])
        if not storage_group_child:
            self.create_child_storage_group_and_add_to_parent(element_dict)
        else:
            self._existing_child_storage_group_check(
                element_dict['new_sg_name'],
                element_dict['new_sg_parent_name'])

        return storage_group_parent

    def get_or_create_elements(self, element_dict, revert=False):
        """Get or create component elements.

        :param element_dict: element details -- dict
        :param revert: is it a revert back -- boolean
        """
        if revert:
            storage_group = self.get_storage_group(
                element_dict['new_sg_name'])
            if not storage_group:
                # Create a new storage group with one volume in it
                prov = self.conn.provisioning
                message = prov.create_non_empty_storage_group(
                    element_dict['srp'],
                    element_dict['new_sg_name'],
                    element_dict['service_level'],
                    element_dict['workload'], '1', '1', 'GB')
                self.print_pretty_table(message)
            storage_group = self.get_storage_group(
                element_dict['new_sg_name'])
        else:
            storage_group = self.get_or_create_cascaded_storage_group(
                element_dict)
        if storage_group:
            port_group = element_dict['port_group']
            initiator_group = element_dict['initiator_group']
            self.conn.provisioning.create_masking_view_existing_components(
                port_group, element_dict['new_mv_name'],
                storage_group['storageGroupId'],
                host_name=initiator_group)
        else:
            exception_message = (
                'Cannot create or find the storagegroup.')
            self.smart_print(exception_message, ERROR)
            raise exception.ResourceNotFoundException(
                data=exception_message)

    def get_masking_view(self, masking_view_name):
        """Get the masking view object from the name.

        :param masking_view_name: masking view name -- str
        :returns: masking view -- dict
        """
        masking_view = None
        try:
            masking_view = self.conn.provisioning.get_masking_view(
                masking_view_name)
        except exception.ResourceNotFoundException:
            print_str = 'Masking view %s not found.'
            self.smart_print(print_str, WARNING, masking_view_name)
        return masking_view

    def get_or_create_masking_view(
            self, element_dict, port_group, host, revert=False):
        """Get or create masking view from component elements.

        :param element_dict: element details -- dict
        :param port_group: port group name -- str
        :param host: host name -- str
        :param revert: is it a revert case -- boolean
        :returns: masking view -- dict
        """
        new_masking_view_details = self.get_masking_view(
            element_dict['new_mv_name'])
        if new_masking_view_details:
            if self.validate_existing_masking_view(
                    new_masking_view_details, port_group, host,
                    element_dict, revert):
                print_str = (
                    'The existing masking view %s will be used.')
                self.smart_print(
                    print_str, DEBUG, element_dict['new_mv_name'])
                self.smart_print('\n', DEBUG)
            else:
                print_str = (
                    'Something is wrong with the existing masking view %s.')
                self.smart_print(
                    print_str, WARNING, element_dict['new_mv_name'])
        else:
            print_str = 'Creating masking view %s.'
            self.smart_print(print_str, DEBUG, element_dict['new_mv_name'])
            self.get_or_create_elements(element_dict, revert)
            new_masking_view_details = self.get_masking_view(
                element_dict['new_mv_name'])
        return new_masking_view_details

    def move_volumes_from_source_to_target(
            self, device_ids, source_storage_group, target_storage_group,
            create_volume_flag):
        """Get or create masking view from component elements.

        :param device_ids: list of device ids -- str
        :param source_storage_group: the source sg -- str
        :param target_storage_group: the target sg -- str
        :param create_volume_flag: create volume flag -- boolean
        :returns: message -- str
        """
        print_str = '\nMoving %d volume(s) from %s to %s.'
        self.smart_print(
            print_str, DEBUG, len(device_ids), source_storage_group,
            target_storage_group)
        self.smart_print(
            '\nPlease be patient, this may take several minutes...',
            DEBUG)
        # Create a small volume
        if create_volume_flag:
            last_volume = 'last_vol' + str(uuid.uuid1())[-10:]
            self.conn.provisioning.create_volume_from_storage_group_return_id(
                last_volume, source_storage_group, '1')
        # Move the volume from the old storage group to the
        # new storage group
        message = self.conn.provisioning.move_volumes_between_storage_groups(
            device_ids, source_storage_group, target_storage_group,
            force=False)
        return message

    @staticmethod
    def validate_list(full_list, sub_list):
        """Validate the sub list is within the full list.

        :param full_list: full list -- list
        :param sub_list: sub list -- list
        :returns: flag -- boolean
        """
        return bool(all(elem in full_list for elem in sub_list))

    def choose_subset_volumes(self, storage_group_name, volume_list):
        """Validate the sub list is within the full list.

        :param storage_group_name: storage group name -- str
        :param volume_list: sub list -- list
        :returns: volume_list -- list
        """
        create_volume_flag = False
        self.smart_print('Here is the full list of volumes in SG %s: %s',
                         DEBUG, storage_group_name, volume_list)
        txt = ('Which do you want to migrate (comma separated list): ',
               volume_list)
        txt_out = self.input(txt)
        if txt_out:
            sub_volume_list = txt_out.split(',')
            sub_volume_list = [x.strip(' \'') for x in sub_volume_list]
            if self.validate_list(volume_list, sub_volume_list):
                if len(volume_list) == len(sub_volume_list):
                    create_volume_flag = True
                volume_list = sub_volume_list
            else:
                print_str = ('Unable to validate your list, '
                             'no volumes will be migrated.')
                self.smart_print(print_str, WARNING)
                volume_list = list()
        else:
            self.smart_print('You cannot input an empty list', DEBUG)
            txt = 'Do you want to choose again Y/N or X:'
            txt_out = self.input(txt)
            if self.check_input(txt_out, 'Y'):
                volume_list, create_vol = self.choose_subset_volumes(
                    storage_group_name, volume_list)
            else:
                sys.exit()
        return volume_list, create_volume_flag

    def get_volume_list(self, storage_group_name):
        """Get the list of volumes from the storage group.

        :param storage_group_name: the storage group name -- str
        :returns: volume list -- list, create volume -- boolean
        """
        volume_list = self.conn.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        print_str = 'There are %d volume in storage group %s.'
        self.smart_print(print_str, DEBUG, len(volume_list),
                         storage_group_name)
        txt = ('Do you want to migrate all %s volumes: Y/N or X(ignore): '
               % len(volume_list))
        txt_out = self.input(txt)
        if self.check_input(txt_out, 'Y'):
            # Move list of devices from old to new masking view
            print_str = ('Moving all volumes between source '
                         'and target storage groups.')
            self.smart_print(print_str, DEBUG)
            create_volume_flag = True
        elif self.check_input(txt_out, 'N'):
            volume_list, create_volume_flag = self.choose_subset_volumes(
                storage_group_name, volume_list)
        else:
            return list(), False

        return volume_list, create_volume_flag

    def choose_storage_group(
            self, masking_view_name, child_storage_group_list, port_group,
            initiator_group, revert=False):
        """Choose a child storage group from the list.

        :param masking_view_name: the masking view name -- str
        :param child_storage_group_list: the storage group list -- list
        :param port_group: The port group name -- str
        :param initiator_group: the initiator group name -- str
        :param revert: revert back -- boolean
        :returns: element details -- dict, child storage group name -- str
        """
        element_dict = dict()
        child_storage_group_name = None
        for child_storage_group_name in child_storage_group_list:
            txt = ('Which storage group do you want to migrate:\n\t '
                   '%s. Y/N: ' % child_storage_group_name)
            txt_out = self.input(txt)
            if 'Y' in txt_out:
                # Compile the new names of the SGs and MV
                element_dict = self.compile_new_element_names(
                    masking_view_name, port_group, initiator_group,
                    child_storage_group_name, revert)
                return element_dict, child_storage_group_name
        return element_dict, child_storage_group_name

    def validate_masking_view(self, masking_view_name, revert=False):
        """Validate the masking view string.

        :param masking_view_name: masking view name -- str
        :param revert: revert back -- boolean
        :returns: validate flag -- boolean
        """
        if re.search('^OS-', masking_view_name):
            try:
                if revert:
                    return bool(self.get_masking_view_component_dict(
                        masking_view_name, True))
                else:
                    return bool(self.get_masking_view_component_dict(
                        masking_view_name))
            except Exception:
                return False
        else:
            return False

    def input(self, txt):
        """Handle input.

        :param txt: text in -- str
        :returns: txt_out -- str
        """
        txt_out = ''
        try:
            txt_out = input(txt)
        except EOFError:
            self.smart_print('Problem with input stream', ERROR)
        return txt_out

    def get_storage_group_qos_details(self, storage_group_details):
        """Get the storage group QoS details.

        :param: storage_group_details -- dict
        :returns: QoS details -- dict
        """
        qos_dict = dict()
        try:
            storage_group_qos_details = storage_group_details['hostIOLimit']
            qos_dict['sg_maxiops'] = (
                storage_group_qos_details['host_io_limit_io_sec'])
            qos_dict['sg_maxmbps'] = (
                storage_group_qos_details['host_io_limit_mb_sec'])
            qos_dict['sg_distribution_type'] = (
                storage_group_qos_details['dynamicDistribution'])
        except KeyError:
            self.smart_print(
                'hostIOLimit(QoS details) not set storage group %s.',
                DEBUG, storage_group_details['storageGroupId'])
        return qos_dict

    def set_qos(self, source_storage_group_name, target_storage_group_name):
        """Check and set QoS.

        :param source_storage_group_name: source SG name -- str
        :param target_storage_group_name: target SG name -- str
        """
        property_dict = dict()
        source_qos_dict = dict()
        target_qos_dict = dict()
        source_storage_group_details = self.get_storage_group(
            source_storage_group_name)
        target_storage_group_details = self.get_storage_group(
            target_storage_group_name)

        if source_storage_group_details:
            source_qos_dict = self.get_storage_group_qos_details(
                source_storage_group_details)
        if target_storage_group_details:
            target_qos_dict = self.get_storage_group_qos_details(
                target_storage_group_details)
        if source_qos_dict and target_qos_dict:
            if source_qos_dict['sg_maxiops'] != target_qos_dict['sg_maxiops']:
                property_dict['host_io_limit_io_sec'] = (
                    source_qos_dict['sg_maxiops'])
            if source_qos_dict['sg_maxmbps'] != target_qos_dict['sg_maxmbps']:
                property_dict['host_io_limit_mb_sec'] = (
                    source_qos_dict['sg_maxmbps'])
            if source_qos_dict['sg_distribution_type'] != (
                    target_qos_dict['sg_distribution_type']):
                property_dict['dynamicDistribution'] = (
                    source_qos_dict['sg_distribution_type'])
        elif source_qos_dict:
            property_dict['host_io_limit_io_sec'] = (
                source_qos_dict['sg_maxiops'])
            property_dict['host_io_limit_mb_sec'] = (
                source_qos_dict['sg_maxmbps'])
            property_dict['dynamicDistribution'] = (
                source_qos_dict['sg_distribution_type'])
        elif target_qos_dict:
            self.smart_print('Resetting target HostIO limits', DEBUG)
        if property_dict:
            payload = {'editStorageGroupActionParam': {
                'setHostIOLimitsParam': property_dict}}
            message = self.conn.provisioning.modify_storage_group(
                target_storage_group_name, payload)
            print_str = '%s Host IO details have changed:'
            self.smart_print(print_str, DEBUG, target_storage_group_name)
            self.print_pretty_table(message['hostIOLimit'])
