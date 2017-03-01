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

PARSER = argparse.ArgumentParser(
    description='This python script is a basic VMAX REST recipe used for '
                'creating and provisioning storage for an Oracle Database.')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument(
    '-sg', required=True, help='Storage group name, typically the application'
                               ' name e.g. REST_TEST_SG')
ARGS = PARSER.parse_args()

# Variables are initiated to append REST to the Storage Group and Initiator
# - this can all be customized to match your individual
# requirements

sg_id = ARGS.sg
ln_sg_id = sg_id + "_LNK"
ru = rest_functions()
mvname = ln_sg_id + "_MV"


def main():
    mysnap = ru.set_snapshot_id(sg_id)
    print("You Chose Snap %s" % mysnap)
    ru.link_gen_snapsthot_83(sg_id, mysnap, generation=0,
                             link_sg_name=ln_sg_id)
    ru.create_masking_view_existing_components(
        port_group_name="cse_pg", masking_view_name=mvname,
        storage_group_name=ln_sg_id, host_name="esx144_IG")

main()
