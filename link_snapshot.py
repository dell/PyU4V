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

import argparse
from PyU4V.rest_univmax import rest_functions
####################################
# Define and Parse CLI arguments   #
# and instantiate session for REST #
####################################

PARSER = argparse.ArgumentParser(description='This python scrtipt is a basic VMAX REST recipe used for creating and provisioning storage for an Oracle Database.')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument('-sg', required=True, help='Storage group name, typically the application name e.g. REST_TEST_SG')
#RFLAGS.add_argument('-pg', required=True, help='Port group name, typically the application name e.g. REST_TEST_PG')
#RFLAGS.add_argument('-host', required=True, help='Port group name, typically the application name e.g. REST_TEST_PG')
ARGS = PARSER.parse_args()

#Variables are initiated to append REST to the Storage Group and Initiator this can all be customized to match your individual
#requirements
#SG and IG will append _SG or _IG to the name passed by the user.  e.g. REST_Oracle_IG and REST_ORACLE_IG

sgname = ARGS.sg
#mountHost = ARGS.ig
#portgroup = ARGS.pg

ru = rest_functions()

def set_snapshot_id():
    #simple function to parse a list of snaps for storage group and select from menu
    snaplist = ru.get_snap_sg(sgname)
    print(snaplist)
    i = 0
    for elem in snaplist[0]["name"]:
        print(i, " ", elem, "\n")
        i = int(i + 1)
    snapselection = input("Select the snapshot you want from the List \n")
    snapshot_id = (snaplist[0]["name"][int(snapselection)])

    return snapshot_id
mysnap=set_snapshot_id()
print("You Chose Snap %s" % mysnap)

#TODO link snapshot method, Call to create the Masking view, update arguments to accept host details, port and LinkSG group.





