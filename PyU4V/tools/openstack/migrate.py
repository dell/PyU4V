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
OpenStack migrate script.

The script migrates volumes from the old SMI-S Masking view to the
new REST Masking view used from Pike onwards
"""

from __future__ import print_function

from builtins import input
import sys

from PyU4V.tools.openstack import migrate_utils
from PyU4V import univmax_conn

sys.path.append('../../..')
sys.path.append('.')


conn = univmax_conn.U4VConn()
utils = migrate_utils.MigrateUtils(conn)

utils.smart_print(
    '********************************************************************',
    migrate_utils.DEBUG)
utils.smart_print(
    '*** Welcome to the migration script for the VMAX/PowerMax driver ***',
    migrate_utils.DEBUG)
utils.smart_print(
    '*** to migrate from SMI-S masking view to REST masking view.     ***',
    migrate_utils.DEBUG)
utils.smart_print(
    '*** This is recommended if you intend using live migration to    ***',
    migrate_utils.DEBUG)
utils.smart_print(
    '*** move from one compute node to another.                       ***',
    migrate_utils.DEBUG)
utils.smart_print(
    '********************************************************************',
    migrate_utils.DEBUG)

utils.smart_print('version is %s', migrate_utils.DEBUG, migrate_utils.VERSION)
masking_view_list = conn.provisioning.get_masking_view_list()

is_revert = False
no_action = True
if len(sys.argv) == 2:
    if sys.argv[1] == 'revert':
        is_revert = True
    else:
        utils.smart_print('%s is not a valid argument.',
                          migrate_utils.DEBUG, sys.argv[1])
        sys.exit()


def revert_case(masking_view_name):
    """The revert case of the migrate process

    :param masking_view_name: masking view name -- str
    :returns: masking view details -- dict
              element details -- dict
              no action flag -- boolean
    """
    if utils.check_masking_view_for_migration(
            masking_view_name, True):
        utils.smart_print(
            'NEW MASKING VIEW IS %s',
            migrate_utils.DEBUG, masking_view_name)
        masking_view_details = (
            utils.get_elements_from_masking_view(masking_view_name))
        # The storage group is the parent SG
        # Get the list of child SGs
        child_storage_group_list = (
            conn.provisioning.get_child_storage_groups_from_parent(
                masking_view_details['storagegroup']))
        element_details, masking_view_details['storagegroup'] = (
            utils.choose_storage_group(
                masking_view_name, child_storage_group_list,
                masking_view_details['portgroup'],
                masking_view_details['initiatorgroup'],
                is_revert))
        # Check if masking view exists and if it does validate it
        if element_details:
            utils.get_or_create_masking_view(
                element_details,
                masking_view_details['portgroup'],
                masking_view_details['initiatorgroup'],
                is_revert)
        else:
            utils.smart_print(
                'NO MIGRATION', migrate_utils.WARNING)
            sys.exit()
        return masking_view_details, element_details, False
    else:
        return dict(), dict(), True


def migrate_case(masking_view_name):
    """The revert case of the migrate process

    :param masking_view_name: masking view name -- str
    :returns: masking view details -- dict
              element details -- dict
              no action flag -- boolean
    """
    if utils.check_masking_view_for_migration(masking_view_name):
        utils.smart_print(
            'OLD MASKING VIEW IS %s',
            migrate_utils.DEBUG, masking_view_name)
        masking_view_details = (
            utils.get_elements_from_masking_view(masking_view_name))
        # Compile the new names of the SGs and MV
        element_details = utils.compile_new_element_names(
            masking_view_name, masking_view_details['portgroup'],
            masking_view_details['initiatorgroup'],
            masking_view_details['storagegroup'])
        # Check if masking view exists and if it does validate it
        utils.get_or_create_masking_view(
            element_details, masking_view_details['portgroup'],
            masking_view_details['initiatorgroup'])

        return masking_view_details, element_details, False
    else:
        return dict(), dict(), True


def move_volumes(masking_view_details, element_details):
    """Move volumes from one masking view to another

    :param masking_view_details: masking view details -- dict
    :param element_details: element details -- dict
    """
    # Check the qos setting of source and target storage group
    utils.set_qos(
        masking_view_details['storagegroup'],
        element_details['new_sg_name'])
    volume_list, create_volume_flag = utils.get_volume_list(
        masking_view_details['storagegroup'])
    if volume_list:
        message = utils.move_volumes_from_source_to_target(
            volume_list, masking_view_details['storagegroup'],
            element_details['new_sg_name'], create_volume_flag)
        print_str = '%s SOURCE STORAGE GROUP REMAINS'
        utils.smart_print(
            print_str, migrate_utils.DEBUG,
            masking_view_details['storagegroup'])
        utils.print_pretty_table(message)
        new_storage_group = utils.get_storage_group(
            element_details['new_sg_name'])
        print_str = '%s TARGET STORAGE GROUP DETAILS:'
        utils.smart_print(
            print_str, migrate_utils.DEBUG,
            element_details['new_sg_name'])
        utils.print_pretty_table(new_storage_group)


for masking_view in masking_view_list:
    if utils.validate_masking_view(masking_view, is_revert):
        txt = 'Do you want to migrate %s. Y/N or X(exit): ' % masking_view
        txt_out = input(txt)
        if utils.check_input(txt_out, 'Y'):
            if is_revert:
                masking_view_components, element_dict, no_action = (
                    revert_case(masking_view))
            else:
                masking_view_components, element_dict, no_action = (
                    migrate_case(masking_view))
            # Get the volumes in the storage group
            if masking_view_components and (
                    'storagegroup' in masking_view_components):
                move_volumes(masking_view_components, element_dict)
            else:
                utils.smart_print('NO MIGRATION', migrate_utils.WARNING)
        elif utils.check_input(txt_out, 'X'):
            sys.exit()
if no_action:
    utils.smart_print(
        'No OpenStack masking views eligible for migration.',
        migrate_utils.DEBUG)
