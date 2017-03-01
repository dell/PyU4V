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

# This Script can be used to change the state of an existing SRDF protected storage group
#Please ensure you are familar with the actions.  Restore, Failover, Failback and Swap will change the state of Source (R1)
#Devices.  DO Not Run this script on Production volumes unless you are 100% sure of the Action and resulting state.
#Please refer to https://support.emc.com/docu78908_Solutions_Enabler_SRDF_Family_8.3.0_CLI_User_Guide.pdf?language=en_US&language=en_US for details of state requirements.



import argparse
from PyU4V.rest_univmax import rest_functions

####################################
# Define and Parse CLI arguments   #
# and instantiate session for REST #
####################################

PARSER = argparse.ArgumentParser(description='Example implementation '
                                             'of a Python REST client '
                                             'for EMC Unisphere for VMAX '
                                             'Protect Storage Group with SRDF. '
                                             'Note the source storage group must '
                                             'already exist.')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument('-sg', required=True, help='Storage group name, '
                                               'typically the application '
                                               'name e.g. oraclefinace')
RFLAGS.add_argument('-action', required=True, help='Valid inputs are Establish, '
                                                   'Split, Suspend, Restore, Resume, '
                                                   'Failover, Failback, Swap')
ARGS = PARSER.parse_args()

sg_id = ARGS.sg
action=ARGS.action
ru = rest_functions()

currentstate=ru.get_srdf_state(sg_id)[0]["states"] # Gets the Current SRDF State
print(currentstate)
# Note this call may run for a long time depending on the size of the group,
# change RDF stat will by updated to async call when supported in 8.4
ru.change_srdf_state(sg_id, action)


# newstate=ru.get_srdf_state(sg_id)[0]["states"]
# print(newstate)  #Note NewState will return failed over if volumes are not in masking group on Remote Side


