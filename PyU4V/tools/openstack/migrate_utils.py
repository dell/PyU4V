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

"""
OpenStack migrate_utils.py.

Migrate utilities for OpenStack
"""

from __future__ import print_function

from builtins import input
import logging
import re
import sys

from PyU4V.utils import exception

import prettytable

LOG = logging.getLogger(__name__)

YES_CONSTANTS = ['y', 'yes']
NO_CONSTANTS = ['n', 'no']
EXIT_CONSTANTS = ['x', 'exit']

VERSION = '1.0.6'

DEBUG = 'DEBUG'
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'


class MigrateUtils(object):
    """OpenStack migrate utils."""

    def __init__(self, conn):
        """Initialize class.

        :param conn: the request connection
        """
        self.conn = conn

    def check_input(self, txt_str, option):
        """Check the input against the expected option.

        :param txt_str: text string
        :param option: 'Y', 'N' or 'X'
        :returns: boolean
        """
        if option == 'Y':
            return True if txt_str.lower() in YES_CONSTANTS else False
        elif option == 'N':
            return True if txt_str.lower() in NO_CONSTANTS else False
        elif option == 'X':
            LOG.debug('I am exiting')
            return True if txt_str.lower() in EXIT_CONSTANTS else False
        else:
            return False

    def print_to_log(self, print_str, level=DEBUG):
        """Print to the logs

        :param print_str: string to print
        :param level: the debug level
        """
        if level == ERROR:
            LOG.error(print_str)
        elif level == WARNING:
            LOG.warning(print_str)
        elif level == INFO:
            LOG.info(print_str)
        else:
            LOG.debug(print_str)

    def print_pretty_table(self, datadict):
        """Print the data in the dict.

        :param datadict: the data dictionary
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

        :param print_str: the print string
        :param level: the debug level
        :param args: one or more arguments
        """
        print_str = print_str % (args)
        self.print_to_log(print_str, level)
        print(print_str)

    def get_elements_from_masking_view(self, mv_name):
        """Get components from masking view.

        :param mv_name: masking view name
        :returns: strings - portgroup, storagegroup, host
        """
        mv_components = {}
        try:
            mv_components['portgroup'] = (
                self.conn.provisioning.get_element_from_masking_view(
                    mv_name, portgroup=True))
            mv_components['storagegroup'] = (
                self.conn.provisioning.get_element_from_masking_view(
                    mv_name, storagegroup=True))
            mv_components['initiatorgroup'] = (
                self.conn.provisioning.get_element_from_masking_view(
                    mv_name, host=True))
        except exception.ResourceNotFoundException:
            exception_message = (
                'Cannot find one of the components of %s' % mv_name)
            self.smart_print(exception_message, ERROR)
            raise exception.ResourceNotFoundException(
                data=exception_message)

        self.print_pretty_table(mv_components)
        return mv_components

    def verify_protocol(self, protocol):
        """Verify the protocol.

        :param protocol: 'I' or 'F'
        :returns: boolean
        """
        return (True if len(protocol) == 1 and (
                'I' in protocol or 'F' in protocol) else False)

    def get_object_components(self, regex_str, input_str):
        """Get components from input string.

        :param regex_str: the regex
        :param input_str: the input string
        :returns: dict
        """
        full_str = re.compile(regex_str)
        match = full_str.match(input_str)
        return match.groupdict() if match else None

    def get_object_components_and_correct_host(self, regex_str, input_str):
        """Get components from input string.

        :param regex_str: the regex
        :param input_str: the input string
        :returns: dict
        """
        object_dict = self.get_object_components(regex_str, input_str)
        if object_dict and 'host' in object_dict:
            if object_dict['host'].endswith('-'):
                object_dict['host'] = object_dict['host'][:-1]
        return object_dict

    def get_mv_component_dict(self, mv_name, revert=False):
        """Get components from input string.

        :param mv_name: the masking view name
        :param revert: is it a revert back
        :returns: dict
        """
        if revert:
            regex_str = '^(?P<prefix>OS)-(?P<host>.+?)(?P<protocol>I|F)-' \
                        '(?P<portgroup>(?!CD|RE|CD-RE).+)-(?P<postfix>MV)$'
        else:
            regex_str = '^(?P<prefix>OS)-(?P<host>.+?)((?P<srp>SRP.+?)-' \
                        '(?P<slo>.+?)-(?P<workload>.+?)|(?P<no_slo>No_SLO))-' \
                        '(?P<protocol>I|F)(?P<CD>-CD|s*)(?P<RE>-RE|s*)-' \
                        '(?P<postfix>MV)$'
        return self.get_object_components_and_correct_host(regex_str, mv_name)

    def truncate_string(self, str_to_truncate, max_num):
        """Truncate a string by taking first and last characters.

        :param str_to_truncate: the string to be truncated
        :param max_num: the maximum number of characters
        :returns: string -- truncated string or original string
        """
        if len(str_to_truncate) > max_num:
            new_num = len(str_to_truncate) - max_num // 2
            first_chars = str_to_truncate[:max_num // 2]
            last_chars = str_to_truncate[new_num:]
            str_to_truncate = first_chars + last_chars
        return str_to_truncate

    def print_component_dict(self, mv_name, revert=False):
        """Print the components to the screen.

        :param mv_name: the masking view name
        :param revert: is it a revert back
        :returns: dict
        """
        if revert:
            self.smart_print('\n', DEBUG)
            self.smart_print(
                'Checking if masking view is in the following format: ',
                DEBUG)
            self.smart_print(
                '    OS-[shortHostName]-[protocol]-[portgroup_name]-MV',
                DEBUG)
            component_dict = self.get_mv_component_dict(mv_name, revert)
            print('\n')
        else:
            self.smart_print('\n', DEBUG)
            self.smart_print(
                'Checking if masking view is in the following 2 formats: ',
                DEBUG)
            self.smart_print(
                '    OS-[shortHostName]-[SRP]-[SLO]-[workload]-[protocol]-MV',
                DEBUG)
            self.smart_print('        OR', DEBUG)
            self.smart_print('    OS-[shortHostName]-No_SLO-[protocol]-MV',
                             DEBUG)
            self.smart_print('\n', DEBUG)
            component_dict = self.get_mv_component_dict(mv_name)
            self.smart_print('COMPONENTS OF %s', DEBUG, mv_name)
        if component_dict:
            self.print_pretty_table(component_dict)

        return component_dict

    def check_mv_for_migration(self, mv_name, revert=False):
        """Check if the masking view can be migrated.

        :param mv_name: the masking view name
        :param test: is it a test case
        :returns: boolean
        """
        if revert:
            component_dict = self.print_component_dict(mv_name, revert)
            if component_dict and self.verify_protocol(
                    component_dict['protocol']):
                print_str = '%s HAS BEEN VERIFIED TO BEING IN THE NEW FORMAT.'
                self.smart_print(print_str, DEBUG, mv_name)
                return True
            else:
                print_str = (
                    '%s IS NOT IN THE NEW FORMAT, MIGRATION WILL NOT '
                    'PROCEED.')
                self.smart_print(print_str, WARNING, mv_name)
                return False
        else:
            component_dict = self.print_component_dict(mv_name)
            if component_dict and self.verify_protocol(
                    component_dict['protocol']):
                print_str = '%s HAS BEEN VERIFIED TO BEING IN THE OLD FORMAT.'
                self.smart_print(print_str, DEBUG, mv_name)
                return True
            else:
                print_str = ('%s IS NOT IN THE OLD FORMAT, MIGRATION WILL NOT '
                             'PROCEED.')
                self.smart_print(print_str, WARNING, mv_name)
                return False

    def get_sg_component_dict(self, sg_name):
        """Parse the storage group string.

        :param sg_name: the storage group name
        :param test: is it a test case
        :returns: dict
        """
        regex_str = '^(?P<prefix>OS)-(?P<host>.+?)' \
                    '((?P<no_slo>No_SLO)|((?P<srp>SRP.+?)-' \
                    '(?P<sloworkload>.+?)))-(?P<portgroup>.+?)' \
                    '(?P<after_pg>$|-CD|-RE)'
        return self.get_object_components_and_correct_host(regex_str, sg_name)

    def get_element_dict_test(self, component_dict, sg_name, cd_str, re_str,
                              pg_name, host_name):
        """Compile elements from mv, sg, host etc.

        :param component_dict: masking view dict
        :param sg_name: storage group name
        :param cd_str: compression disabled
        :param re_str: replication enabled
        :param pg_name: port group name
        :param host_name: host name
        :returns: dict
        """
        element_dict = {}

        sg_component_dict = self.get_sg_component_dict(sg_name)
        if sg_component_dict:
            if sg_component_dict['sloworkload']:
                storagegroup = self.get_storage_group(sg_name)
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

            element_dict['port_group'] = pg_name
            element_dict['initiator_group'] = host_name
        return element_dict

    def get_workload(self, storagegroup):
        """Get the workload from the storagegroup object.

        :param storagegroup: storagegroup object
        :returns: workload
        """
        try:
            workload = storagegroup['workload']
        except KeyError:
            workload = 'NONE'
        return workload

    def get_element_dict(self, component_dict, cd_str, re_str,
                         pg_name, host_name):
        """Compile elements from mv, sg, host etc.

        :param component_dict: masking view dict
        :param cd_str: compression disabled
        :param re_str: replication enabled
        :param pg_name: port group name
        :param host_name: host name
        :returns: dict
        """
        element_dict = {}
        element_dict['new_mv_name'] = (component_dict['prefix'] + '-'
                                       + component_dict['host'] + '-'
                                       + component_dict['protocol'] + '-'
                                       + pg_name + '-MV')
        element_dict['new_sg_parent_name'] = (component_dict['prefix'] + '-'
                                              + component_dict['host'] + '-'
                                              + component_dict['protocol']
                                              + '-' + pg_name + '-SG')

        if component_dict['srp']:
            slo_wl_combo = self.truncate_string(
                component_dict['slo'] + component_dict['workload'], 10)
            element_dict['new_sg_name'] = (component_dict['prefix'] + '-'
                                           + component_dict['host'] + '-'
                                           + component_dict['srp'] + '-'
                                           + slo_wl_combo
                                           + '-' + pg_name + cd_str + re_str)
            element_dict['srp'] = component_dict['srp']
            element_dict['service_level'] = component_dict['slo']
            element_dict['workload'] = component_dict['workload']
        else:
            element_dict['new_sg_name'] = (component_dict['prefix'] + '-'
                                           + component_dict['host'] + '-'
                                           + 'No_SLO' + '-'
                                           + pg_name + cd_str + re_str)
        element_dict['port_group'] = pg_name
        element_dict['initiator_group'] = host_name
        return element_dict

    def compile_new_element_names(
            self, mv_name, pg_name, host_name, sg_name, revert=False):
        """Compile elements from mv, sg, host etc.

        :param mv_name: masking view name
        :param pg_name: port group name
        :param host_name: host name
        :param sg_name: storage group name
        :param test: is it a test case
        :returns: dict
        """
        element_dict = {}
        cd_str = ''
        re_str = ''
        regex_all = '\\S+'
        if re.search('^OS-' + regex_all + '-CD', sg_name):
            cd_str = '-CD'
            element_dict['CD'] = 'CD'
        if re.search('^OS-' + regex_all + '-RE', sg_name):
            re_str = '-RE'
            element_dict['RE'] = 'RE'
        component_dict = self.get_mv_component_dict(mv_name, revert)
        if component_dict:
            if revert:
                element_dict = self.get_element_dict_test(
                    component_dict, sg_name, cd_str, re_str,
                    pg_name, host_name)
            else:
                element_dict = self.get_element_dict(
                    component_dict, cd_str, re_str,
                    pg_name, host_name)
        else:
            print_str = 'UNABLE TO PARSE %s, MIGRATION WILL NOT ' \
                        'PROCEED.'
            self.smart_print(print_str, WARNING, mv_name)

        return element_dict

    def validate_existing_masking_view(
            self, mv_details, old_port_group, old_host, element_dict,
            revert=False):
        """Validate the masking view.

        :param mv_details: masking view details
        :param old_port_group: port group name
        :param old_host: host name
        :param element_dict: the element dictionary
        :param revert: is it a revert back
        :returns: Boolean
        """
        self.smart_print(
            'NEW MASKING VIEW %s', DEBUG, mv_details['maskingViewId'])
        mv_components = self.get_elements_from_masking_view(
            mv_details['maskingViewId'])
        if old_port_group != mv_components['portgroup']:
            self.smart_print(
                'Portgroups are not equal, please assess', DEBUG)
            return False
        if old_host != mv_components['initiatorgroup']:
            print_str = 'Hosts are not equal, please assess'
            self.smart_print(print_str, WARNING)
            return False
        if revert:
            if element_dict['new_sg_name'] != mv_components['storagegroup']:
                print_str = 'Storage group is not equal, please assess'
                self.smart_print(print_str, WARNING)
                return False
        else:
            if element_dict['new_sg_parent_name'] != (
                    mv_components['storagegroup']):
                print_str = (
                    'Parent storage group is not equal, please assess')
                self.smart_print(print_str, WARNING)
                return False
            # Check if child storage group exists
            child_storagegroup = self.get_storage_group(
                element_dict['new_sg_name'])
            if child_storagegroup:
                # Check if the child SG is part of the parent
                if not self.conn.provisioning.is_child_sg_in_parent_sg(
                        element_dict['new_sg_name'],
                        element_dict['new_sg_parent_name']):
                    print_str = (
                        'The child sg is not part of the parent sg: %s')
                    self.smart_print(
                        print_str, DEBUG, element_dict['new_sg_name'])
                    # Now add the new storage group to the parent
                    message = (
                        self.conn.provisioning.add_child_sg_to_parent_sg(
                            element_dict['new_sg_name'],
                            element_dict['new_sg_parent_name']))
                    self.get_storage_group(message, DEBUG)
            else:
                self.create_child_storage_group_and_add_to_parent(
                    element_dict)

        return True

    def get_storage_group(self, storage_group_name):
        """Get the storage group object from the name.

        :param storage_group_name: storage group name
        :returns: dict
        """
        storagegroup = None
        try:
            storagegroup = self.conn.provisioning.get_storage_group(
                storage_group_name)
        except exception.ResourceNotFoundException:
            print_str = 'Storage group %s not found'
            self.smart_print(print_str, WARNING, storage_group_name)
        return storagegroup

    def create_child_storage_group_and_add_to_parent(self, element_dict):
        """Create child storage group.

        :param element_dict: element dictionary
        :returns: parent storage group
        """
        print_str = '%s child storage group does not exist so creating it.'
        self.smart_print(print_str, DEBUG, element_dict['new_sg_name'])
        # Create a new child storage group with one volume in it
        disable_compression = False
        if 'CD' in element_dict:
            disable_compression = True
        if 'srp' in element_dict:
            message = self.conn.provisioning.create_non_empty_storagegroup(
                element_dict['srp'],
                element_dict['new_sg_name'],
                element_dict['service_level'],
                element_dict['workload'], '1', '1', 'GB',
                disable_compression)
        else:
            message = self.conn.provisioning.create_empty_sg(
                None,
                element_dict['new_sg_name'],
                None,
                None)
            # Add a volume to it
            self.conn.provisioning.create_volume_from_sg_return_dev_id(
                'first_vol', element_dict['new_sg_name'], '1')

        print_str = 'CREATED CHILD STORAGE GROUP %s.'
        self.smart_print(print_str, DEBUG, element_dict['new_sg_name'])
        self.print_pretty_table(message)
        # Add the child to the parent storage group
        message = self.conn.provisioning.add_child_sg_to_parent_sg(
            element_dict['new_sg_name'], element_dict['new_sg_parent_name'])
        print_str = 'ADDED CHILD STORAGE GROUP %s TO PARENT STORAGE GROUP %s.'
        self.smart_print(print_str, DEBUG, element_dict['new_sg_name'],
                         element_dict['new_sg_parent_name'])
        self.print_pretty_table(message)

    def get_or_create_cascaded_storage_group(self, element_dict):
        """Get or create cascaded storage group.

        :param element_dict: element dictionary
        :returns: parent storage group
        """
        storagegroup_parent = self.get_storage_group(
            element_dict['new_sg_parent_name'])
        if not storagegroup_parent:
            print_str = (
                '%s parent storage group does not exist so'
                'creating it.')
            self.smart_print(
                print_str, DEBUG, element_dict['new_sg_parent_name'])
            # Create a new empty parent storage group
            message = self.conn.provisioning.create_empty_sg(
                element_dict['srp'],
                element_dict['new_sg_parent_name'],
                None,
                None)
            self.print_pretty_table(message)
            storagegroup_parent = self.get_storage_group(
                element_dict['new_sg_parent_name'])
        storagegroup_child = self.get_storage_group(
            element_dict['new_sg_name'])
        if not storagegroup_child:
            self.create_child_storage_group_and_add_to_parent(element_dict)
        return storagegroup_parent

    def get_or_create_elements(self, element_dict, revert=False):
        """Get or create component elements.

        :param element_dict: element dictionary
        :param revert: is it a revert back
        """
        if revert:
            storagegroup = self.get_storage_group(
                element_dict['new_sg_name'])
            if not storagegroup:
                # Create a new storage group with one volume in it
                message = self.conn.provisioning.create_non_empty_storagegroup(
                    element_dict['srp'],
                    element_dict['new_sg_name'],
                    element_dict['service_level'],
                    element_dict['workload'], '1', '1', 'GB')
                self.print_pretty_table(message)
            storagegroup = self.get_storage_group(
                element_dict['new_sg_name'])
        else:
            storagegroup = self.get_or_create_cascaded_storage_group(
                element_dict)
        if storagegroup:
            port_group = element_dict['port_group']
            initiator_group = element_dict['initiator_group']
            self.conn.provisioning.create_masking_view_existing_components(
                port_group, element_dict['new_mv_name'],
                storagegroup['storageGroupId'],
                host_name=initiator_group)
        else:
            exception_message = (
                'Cannot create or find the storagegroup.')
            self.smart_print(exception_message, ERROR)
            raise exception.ResourceNotFoundException(
                data=exception_message)

    def get_masking_view(self, mv_name):
        """Get the masking view object from the name.

        :param mv_name: masking view name
        :returns: dict
        """
        masking_view = None
        try:
            masking_view = self.conn.provisioning.get_masking_view(
                mv_name)
        except exception.ResourceNotFoundException:
            print_str = 'Masking view %s not found.'
            self.smart_print(print_str, WARNING, mv_name)
        return masking_view

    def get_or_create_masking_view(
            self, element_dict, portgroup, host, revert=False):
        """Get or create masking view from component elements.

        :param element_dict: element dictionary
        :param portgroup: port group name
        :param host: host name
        :param test: is it a test case
        :returns: dict
        """
        new_masking_view_details = self.get_masking_view(
            element_dict['new_mv_name'])
        if new_masking_view_details:
            if self.validate_existing_masking_view(
                    new_masking_view_details, portgroup, host,
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

    def move_vols_from_source_to_target(
            self, device_ids, source_sg, target_sg, create_vol_f):
        """Get or create masking view from component elements.

        :param device_ids: list of device ids
        :param source_sg: the source sg
        :param target_sg: the target sg
        :param create_vol_f: create volume flag
        :returns: string
        """
        print_str = '\nMoving %d volume(s) from %s to %s.'
        self.smart_print(
            print_str, DEBUG, len(device_ids), source_sg, target_sg)
        self.smart_print(
            '\nPlease be patient, this may take several minutes...',
            DEBUG)
        # Create a small volume
        if create_vol_f:
            self.conn.provisioning.create_volume_from_sg_return_dev_id(
                'last_vol', source_sg, '1')
        # Move the volume from the old storage group to the
        # new storage group
        message = self.conn.provisioning.move_volumes_between_storage_groups(
            device_ids, source_sg, target_sg,
            force=False
        )
        return message

    def validate_list(self, full_list, sub_list):
        """Validate the sub list is within the full list.

        :param full_list: full list
        :param sub_list: sub list
        :returns: Boolean
        """
        return True if all(elem in full_list for elem in sub_list) else False

    def choose_subset_volumes(self, storagegroup, volume_list):
        """Validate the sub list is within the full list.

        :param storagegroup: full list
        :param volume_list: sub list
        :returns: volume_list
        """
        create_vol = False
        self.smart_print('Here is the full list of volumes in SG %s: %s',
                         DEBUG, storagegroup, volume_list)
        txt = ('Which do you want to migrate (comma separated list): ',
               volume_list)
        txt_out = self.input(txt)
        if txt_out:
            sub_volume_list = txt_out.split(',')
            sub_volume_list = [x.strip(' \'') for x in sub_volume_list]
            if self.validate_list(volume_list, sub_volume_list):
                if len(volume_list) == len(sub_volume_list):
                    create_vol = True
                volume_list = sub_volume_list
            else:
                print_str = ('Unable to validate your list, '
                             'no volumes will be migrated.')
                self.smart_print(print_str, WARNING)
                volume_list = []
        else:
            self.smart_print('You cannot input an empty list', DEBUG)
            txt = 'Do you want to choose again Y/N or X:'
            txt_out = self.input(txt)
            if self.check_input(txt_out, 'Y'):
                volume_list, create_vol = self.choose_subset_volumes(
                    storagegroup, volume_list)
            else:
                sys.exit()
        return volume_list, create_vol

    def get_volume_list(self, storagegroup):
        """Get the list of volumes from the storagegroup.

        :param storagegroup: the storage group name
        :returns: List, Boolean
        """
        create_vol = False
        volume_list = self.conn.provisioning.get_vols_from_storagegroup(
            storagegroup)
        print_str = 'There are %d volume in storage group %s.'
        self.smart_print(print_str, DEBUG, len(volume_list), storagegroup)
        txt = ('Do you want to migrate all %s volumes: Y/N: '
               % len(volume_list))
        txt_out = self.input(txt)
        if self.check_input(txt_out, 'Y'):
            # Move list of devices from old to new masking view
            print_str = ('Moving all volumes between source '
                         'and target storage groups.')
            self.smart_print(print_str, DEBUG)
            create_vol = True
        else:
            volume_list, create_vol = self.choose_subset_volumes(
                storagegroup, volume_list)

        return volume_list, create_vol

    def choose_sg(
            self, masking_view, child_sg_list, portgroup, initiatorgroup,
            revert=False):
        """Choose a child storage group from the list.

        :param masking_view: the masking view
        :param child_sg_list: the storage group list
        :param portgroup: The port group name
        :param initiatorgoup: the initiator group name
        :param revert: revert back
        :returns: dict, string
        """
        element_dict = {}
        child_sg = None
        for child_sg in child_sg_list:
            txt = ('Which storage group do you want to migrate:\n\t '
                   '%s. Y/N: ' % child_sg)
            txt_out = self.input(txt)
            if 'Y' in txt_out:
                # Compile the new names of the SGs and MV
                element_dict = self.compile_new_element_names(
                    masking_view, portgroup, initiatorgroup, child_sg,
                    revert)
                return element_dict, child_sg
        return element_dict, child_sg

    def validate_masking_view(self, masking_view, revert=False):
        """Validate the masking view string.

        :param masking_view: masking view name
        :param revert: revert back
        :returns: boolean
        """
        if re.search('^OS-', masking_view):
            try:
                if revert:
                    return True if self.get_mv_component_dict(
                        masking_view, sys.argv[1]) else False
                else:
                    return True if self.get_mv_component_dict(
                        masking_view) else False
            except Exception:
                return False
        else:
            return False

    def input(self, txt):
        """Handle input.

        :param txt: text in
        :returns: txt_out
        """
        txt_out = ''
        try:
            txt_out = input(txt)
        except EOFError:
            self.smart_print('Problem with input stream', ERROR)
        return txt_out

    def get_sg_qos_details(self, sg_details):
        """Get the storage group QoS details.

        :param sg_details:
        :returns: dict
        """
        qos_dict = {}
        try:
            sg_qos_details = sg_details['hostIOLimit']
            qos_dict['sg_maxiops'] = sg_qos_details['host_io_limit_io_sec']
            qos_dict['sg_maxmbps'] = sg_qos_details['host_io_limit_mb_sec']
            qos_dict['sg_distribution_type'] = (
                sg_qos_details['dynamicDistribution'])
        except KeyError:
            self.smart_print(
                'hostIOLimit(QoS details) not set storage group %s.',
                DEBUG, sg_details['storageGroupId'])
        return qos_dict

    def set_qos(self, source_sg_name, target_sg_name):
        """Check and set QoS.

        :param source sg: source SG name
        :param target_sg: target SG name
        """
        property_dict = {}
        source_qos_dict = {}
        target_qos_dict = {}
        source_sg_details = self.get_storage_group(source_sg_name)
        target_sg_details = self.get_storage_group(target_sg_name)

        if source_sg_details:
            source_qos_dict = self.get_sg_qos_details(source_sg_details)
        if target_sg_details:
            target_qos_dict = self.get_sg_qos_details(target_sg_details)
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
                target_sg_name, payload)
            print_str = '%s Host IO details have changed:'
            self.smart_print(print_str, DEBUG, target_sg_name)
            self.print_pretty_table(message['hostIOLimit'])
