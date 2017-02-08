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

There are 5 Parts to this Script.
1.First create the host by adding the initiators.
2.Next Create the Port Group we will use for the application
3.Next the storage Group will be created and the first lot of volumes added.
4.Add volumes to the storage group of different sizes
5.Finally Create the Masking View with all pieces together

This lab assumes that Host, Storage and Port groups are new.  This is for adding single host only,  if you are adding a cluster then
it is necessary to create a hostgroup or use exising host group.  Please use the REST Java client to explore the REST endpoints

"""

import argparse
from PyU4V.rest_requests import rest_functions

####################################
# Define and Parse CLI arguments   #
# and instantiate session for REST #
####################################

PARSER = argparse.ArgumentParser(description='This python scrtipt is a basic VMAX REST recipe provisioning multiple sized volume for an application.')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument('-sg', required=True, help='Storage group name, typically the application name e.g. oraclefinace')
RFLAGS.add_argument('-ig', required=True, help='Filename containing initiators,one per line e.g. 10000000c9873cae')
RFLAGS.add_argument('-pg', required=True, help='Filename containing list of ports one per line, e.g. FA1d:25')
ARGS = PARSER.parse_args()

#Variables are initiated to append REST to the Storage Group and Initiator this can all be customized to match your individual
#requirements
#SG and IG will append _SG or _IG to the name passed by the user.  e.g. REST_Oracle_IG and REST_ORACLE_IG

SGNAME = ARGS.sg
host = ARGS.ig
PORTS = ARGS.pg
appname = ("REST_")+SGNAME
sg_id=appname+("_SG")
ig_id=appname+("_IG")
pg_id=appname+("_PG")
mv_id=appname+("_MV")
ru = rest_functions()

initiator_list=ru.create_list_from_file(file_name=host)

# Actual REST calls to build up the function, script is checking for Return code of 200 in each of the rest calls if that fails it will display error message and Roll Back.
#Return code of 200 indicates sucessful completion of REST call.   Note all calls are simply calling functions from rest_fucntions, the functions are imported as ru which
#saves some typing.

if 200 in ru.create_non_empty_storagegroup(srpID="SRP_1",sg_id=sg_id,slo="Diamond", workload="OLTP", num_vols="1",vol_size="1", capUnit="GB"):
    print ("Storage Group %s Created " %(sg_id))
    #add additional volumes of various sizes you could loop this
    if 200 in ru.add_new_vol_to_storagegroup(sg_id=sg_id, num_vols=2, capUnit="GB", vol_size="2"):
        print("Added first set of additional volumes")
    else:
        print("Problem adding additional volumes to %s please check logs" % sg_id)
        ru.delete_sg(sg_id)
        print("Deleting SG %s" % sg_id)
        exit()
    if 200 in ru.add_new_vol_to_storagegroup(sg_id=sg_id, num_vols=1, capUnit="GB", vol_size="3"):
        print("Added second set of additional volumes")
    else:
        print("Problem adding additional volumes to %s please check logs" % sg_id)
        ru.delete_sg(sg_id)
        print("Deleting SG %s" % sg_id)
        exit()
else:
    print("Problem Creating Storage Group %s, Possibly a storage group of the same name already exists, please check logs" % sg_id)
    exit()

if 200 in ru.create_host(ig_id,initiator_list):
    print ("Host Created")
else:
    print("Something went wrong, deleting storage group and empty initiator group, Please check the symapi log file on the Unisphere Server for more details" )
    # REST calls to delete structures already created
    ru.delete_host(ig_id)
    ru.delete_sg(sg_id)
    exit()

if 200 in ru.create_portgroup_from_file(file_name=PORTS,portgroup_id=pg_id):
    print("PortGroup Created")
else:
    print("Something went wrong creating portgroup, deleting storage group and empty initiator group, Please check the symapi log file on the Unisphere Server for more details")
    # REST calls to delete structures already created
    ru.delete_host(ig_id)
    ru.delete_sg(sg_id)
    ru.delete_portgroup(pg_id)
    exit()

if 200 in ru.create_masking_view_existing_components(masking_view_name=mv_id,port_group_name=pg_id,storage_group_name=sg_id,host_name=ig_id):
    print("Masking view created Sucessfully ", mv_id)
else:
    print("Something went wrong creating the masking view, deleting storage group and empty initiator group, Please check the symapi log file on the Unisphere Server for more details")
    # REST calls to delete structures already created
    ru.delete_host(ig_id)
    ru.delete_sg(sg_id)
    ru.delete_portgroup(pg_id)
    exit()
