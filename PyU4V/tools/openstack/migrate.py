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
OpenStack migrate script.

The script migrates volumes from the old SMI-S Masking view to the
new REST Masking view used from Pike onwards
"""
from __future__ import print_function

from builtins import input
import sys
sys.path.append('../../..')
sys.path.append('.')

from PyU4V import univmax_conn

from PyU4V.tools.openstack import migrate_utils

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

for masking_view in masking_view_list:
    if utils.validate_masking_view(masking_view, is_revert):
        txt = 'Do you want to migrate %s. Y/N or X(exit): ' % masking_view
        txt_out = input(txt)
        if utils.check_input(txt_out, 'Y'):
            if is_revert:
                if utils.check_mv_for_migration(masking_view, is_revert):
                    no_action = False
                    utils.smart_print(
                        'NEW MASKING VIEW IS %s',
                        migrate_utils.DEBUG, masking_view)
                    mv_components = (
                        utils.get_elements_from_masking_view(masking_view))
                    # The storage group is the parent SG
                    # Get the list of child SGs
                    child_sg_list = (
                        conn.provisioning.get_child_sg_from_parent(
                            mv_components['storagegroup']))
                    element_dict, mv_components['storagegroup'] = (
                        utils.choose_sg(masking_view, child_sg_list,
                                        mv_components['portgroup'],
                                        mv_components['initiatorgroup'],
                                        is_revert))
                    # Check if masking view exists and if it does validate it
                    if element_dict:
                        new_masking_view_details = (
                            utils.get_or_create_masking_view(
                                element_dict, mv_components['portgroup'],
                                mv_components['initiatorgroup'], is_revert))
                    else:
                        utils.smart_print(
                            'NO MIGRATION', migrate_utils.WARNING)
                        sys.exit()

            else:
                if utils.check_mv_for_migration(masking_view):
                    no_action = False
                    utils.smart_print(
                        'OLD MASKING VIEW IS %s',
                        migrate_utils.DEBUG, masking_view)
                    mv_components = (
                        utils.get_elements_from_masking_view(masking_view))
                    # Compile the new names of the SGs and MV
                    element_dict = utils.compile_new_element_names(
                        masking_view, mv_components['portgroup'],
                        mv_components['initiatorgroup'],
                        mv_components['storagegroup'])
                    # Check if masking view exists and if it does validate it
                    new_masking_view_details = (
                        utils.get_or_create_masking_view(
                            element_dict, mv_components['portgroup'],
                            mv_components['initiatorgroup']))
            # Get the volumes in the storage group
            if 'storagegroup' in mv_components:
                # Check the qos setting of source and target storage group
                utils.set_qos(mv_components['storagegroup'],
                              element_dict['new_sg_name'])
                volume_list, create_vol_f = utils.get_volume_list(
                    mv_components['storagegroup'])
                if volume_list:
                    message = utils.move_vols_from_source_to_target(
                        volume_list, mv_components['storagegroup'],
                        element_dict['new_sg_name'], create_vol_f)
                    print_str = '%s SOURCE STORAGE GROUP REMAINS'
                    utils.smart_print(
                        print_str, migrate_utils.DEBUG,
                        mv_components['storagegroup'])
                    utils.print_pretty_table(message)
                    new_storage_group = utils.get_storage_group(
                        element_dict['new_sg_name'])
                    print_str = '%s TARGET STORAGE GROUP DETAILS:'
                    utils.smart_print(
                        print_str, migrate_utils.DEBUG,
                        element_dict['new_sg_name'])
                    utils.print_pretty_table(new_storage_group)
            else:
                utils.smart_print('NO MIGRATION', migrate_utils.WARNING)
        elif utils.check_input(txt_out, 'X'):
            sys.exit()
if no_action:
    utils.smart_print(
        'No OpenStack masking views eligible for migration.',
        migrate_utils.DEBUG)
