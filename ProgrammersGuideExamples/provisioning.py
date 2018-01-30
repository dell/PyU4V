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

from PyU4V import U4VConn

ru = U4VConn(u4v_version='84')

PARSER = argparse.ArgumentParser(description='This python scrtipt is a basic '
                                             'VMAX REST recipe provisioning '
                                             'multiple sized volume for an '
                                             'application.\n'
                                             'python provisioning.py -sg TEST '
                                             '-ig initiators.txt -pg ports.txt'
                                             ' -cap 1')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument('-sg', required=True, help='Storage group name, typically '
                                               'the application name '
                                               'e.g. oraclefinace')
RFLAGS.add_argument('-ig', required=True, help='Filename containing initiators'
                                               ',one per line '
                                               'e.g. 10000000c9873cae')
RFLAGS.add_argument('-pg', required=True, help='Filename containing list of '
                                               'ports one per line, '
                                               'e.g. FA-1D:25')
RFLAGS.add_argument('-cap', required=True, help='Capacity in GB')

# Assign parameters to command line arguments
ARGS = PARSER.parse_args()
sgname = ARGS.sg
hba_file = ARGS.ig
port_file = ARGS.pg
appname = "REST_" + sgname
sg_id = appname + "_SG"
ig_id = appname + "_IG"
pg_id = appname + "_PG"
mv_id = appname + "_MV"
requested_capacity = ARGS.cap
initiator_list = ru.common.create_list_from_file(hba_file)


def provision_storage():
    if headroom_check():
        sg_job = ru.provisioning.create_non_empty_storagegroup(
            "SRP_1", sg_id, "Diamond", "OLTP", 1, requested_capacity, "GB", True)
        # showing how async functions can be worked in.
        ru.common.wait_for_job("", sg_job)
        print("Storage Group Created.")
        ru.provisioning.create_host(ig_id, initiator_list)
        print("Host Created.")
        ru.provisioning.create_portgroup_from_file(port_file, pg_id)
        print("Port Group Created.")
        ru.provisioning.create_masking_view_existing_components(
             pg_id, mv_id, sg_id, ig_id)
        print("Masking View Created.")
    else:
        print("Headroom Check Failed, Check array Capacity Usage")


def headroom_check():
    headroom_cp = ru.common.get_headroom("OLTP")[0]["headroom"][0]["headroomCapacity"]
    if int(requested_capacity) <= int(headroom_cp):
        return True
    else:
        return False


provision_storage()
