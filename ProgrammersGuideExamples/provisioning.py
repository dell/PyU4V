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

from PyU4V import RestFunctions
ru=RestFunctions(u4v_version='84')
import argparse

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

#Assign parameters to command line arguments
ARGS = PARSER.parse_args()
sgname = ARGS.sg
hba_file = ARGS.ig
port_file = ARGS.pg
appname = "REST_" + sgname
sg_id = appname + "_SG"
ig_id = appname + "_IG"
pg_id = appname + "_PG"
mv_id = appname + "_MV"
requested_capacity=ARGS.cap
initiator_list = ru.create_list_from_file(hba_file)


def provision_storage():
    if headroom_check():
        sg_job,sg_rc = ru.create_non_empty_storagegroup("SRP_1",sg_id,"Diamond",
                                                        "OLTP",1,
                                                        requested_capacity, "GB"
                                                        , True)
        if sg_rc < 300:
            #showing how async functions can be worked in.
            ru.wait_for_job("", sg_rc, sg_job)
            print("Storage Group Created Return Code %s" % sg_rc)
            host_job, host_rc = ru.create_host(ig_id, initiator_list)
            if host_rc < 300:
                print("Host Created Return Code %s" % host_rc)
                pg_job, pg_rc = ru.create_portgroup_from_file(port_file, pg_id)
                if pg_rc < 300:
                    print("Port Group Created Return Code %s" % pg_rc)
                    mv_job, mv_rc = ru.create_masking_view_existing_components(
                         pg_id, mv_id, sg_id, ig_id)
                    if mv_rc < 300:
                        print("Masking View Created Return Code %s" % mv_rc)
                    else:
                        print ('Error Creating Masking view %s' % mv_job[
                            'message'])
                else:
                    print("Error Creating Port Group %s" % pg_job['message'])
            else:
                print("Error Creating Host %s" % host_job['message'])

        else:
            print("Error Creating %s" % sg_job['message'])
    else:
        print("Headroom Check Failed, Check array Capacity Usage")

def headroom_check():
    headroom_cp = ru.get_headroom("OLTP")[0]["headroom"][0]["headroomCapacity"]
    if int(requested_capacity) <= int(headroom_cp):
        return True
    else:
        return False



def main():
    provision_storage()

main()









