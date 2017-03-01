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

# Lab1.py
"""
This python script is a basic recipe used for creating and provisioning storage with different device sizes. In this
case we provision 4 devices to the specified host 125 GB for DATA, 8 For TEMP, 8 for REDO and 40 for FRA,
This is just a sample configuration and can be modified to support the needs of your company.
The procedure is called by running the command as follows

python provisioning_example.py -sg test -igfile initiators.txt -ports ports.txt

sample format for the texts files used

Initiators.txt
10000000c9873cae
10000000c9873caf

ports.txt
FA-1D:24
FA-2D:24
FA-1D:25
FA-2D:25

This script will
1. Check available headroom
2. Create Storage Group if headroom is available to meet demand
3. Create the host
4. Create a Port Group
5. Create Masking view.

This lab assumes that Host, Storage and Port groups are new.  This is for adding single host only,  if you are adding a cluster then
it is necessary to create a hostgroup or use exising host group.  Please use the REST Java client to explore the REST endpoints

"""
import argparse
from PyU4V.rest_univmax import rest_functions
ru=rest_functions()



PARSER = argparse.ArgumentParser(description='This python scrtipt is a basic VMAX REST recipe provisioning multiple sized volume for an application.')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument('-sg', required=True, help='Storage group name, typically the application name e.g. oraclefinace')
RFLAGS.add_argument('-ig', required=True, help='Filename containing initiators,one per line e.g. 10000000c9873cae')
RFLAGS.add_argument('-pg', required=True, help='Filename containing list of ports one per line, e.g. FA-1D:25')
RFLAGS.add_argument('-cap', required=True, help='Capacity in GB')


ARGS = PARSER.parse_args()
sgname = ARGS.sg
hba_file = ARGS.ig
port_file = ARGS.pg
appname = ("REST_")+sgname
sg_id=appname+("_SG")
ig_id=appname+("_IG")
pg_id=appname+("_PG")
mv_id=appname+("_MV")
requested_capacity=ARGS.cap
initiator_list = ru.create_list_from_file(file_name=hba_file)

def headroom_check():
    headroom_capacity_GB = ru.get_headroom("OLTP")[0]["headroom"][0]["headroomCapacity"]
    if int(requested_capacity) <= int(headroom_capacity_GB):
        return True
    else:
        return False

def provision_storage ():
    if headroom_check():
        ru.create_non_empty_storagegroup(srpID="SRP_1",sg_id=sg_id,slo="Diamond",workload="OLTP",num_vols=1,vol_size=requested_capacity, capUnit="GB")
        ru.create_host(host_name=ig_id,initiator_list=initiator_list)
        ru.create_portgroup_from_file(file_name=port_file, portgroup_id=pg_id)
        ru.create_masking_view_existing_components(masking_view_name=mv_id, port_group_name=pg_id, storage_group_name=sg_id, host_name=ig_id)
        #ru.srdf_protect_sg(sg_id,remote_sid="000197000008",srdfmode="Active",establish=True)
    else:
        print ("Not Enough Headroom for requested capacity")

def main():
    provision_storage()

main()