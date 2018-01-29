# The MIT License (MIT)
# Copyright (c) 2016 Dell Inc. or its subsidiaries.

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

This python scrtipt will create a snapvx snapshot on the specified
storage group and timestamp the name.  Each snapshot is preserved
for 24 hours.

REST call create_new_snap for a storage group.
"""
import argparse
from time import strftime

from PyU4V import RestFunctions

ru = RestFunctions(u4v_version='84')

######################################################################
# Define and Parse CLI arguments and instantiate session for REST #
######################################################################

PARSER = argparse.ArgumentParser(
    description='Example implementation of a Python REST client '
                'for EMC Unisphere Taking SnapVX Snapshots.')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument(
    '-sg', required=True, help='Storage group name, typically '
                               'the application name e.g. oraclefinace')
ARGS = PARSER.parse_args()

# Variables are initiated to appent REST to the Storage Group and Initiator
# SG and IG will append _SG or _IG to the name passed by the user.  e.g.
# REST_Oracle_IG and REST_ORACLE_IG
sg_id = ARGS.sg


def main():
    # assign name to snap with date and time appended to name
    snap_name = "REST_Snap_" + strftime("%d%m%Y%H%M%S")
    ru.replication.create_storagegroup_snap(sg_id, snap_name)
    print ("Check the Gui now or REST Client to see if snapshot %s "
           "was created for Storage Group %s" % (snap_name, sg_id))


main()
