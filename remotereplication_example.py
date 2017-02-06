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

# This Script can be used to protect a storage group with SRDF Metro, Syncronous or Asyncronous, or Adaptive copy.


import argparse
from PyU4V.rest_univmax import rest_functions

####################################
# Define and Parse CLI arguments   #
# and instantiate session for REST #
####################################

PARSER = argparse.ArgumentParser(description='Example implementation of a Python REST client for EMC Unisphere for VMAX Protect Storage Group with SRDF. Note the source storage group must already exist.')
RFLAGS = PARSER.add_argument_group('Required arguments')
RFLAGS.add_argument('-sg', required=True, help='Storage group name, typically the application name e.g. oraclefinace')
RFLAGS.add_argument('-remote_sid', required=True, help='Please Supply symmetrix ID e.g. 000197000008')
RFLAGS.add_argument('-mode', required=True, help='Valid inputs are Active, AdaptiveCopyDisk,Synchronous,Asynchronous This is CASE sensitive')
ARGS = PARSER.parse_args()

SGNAME = ARGS.sg
remote_sid=ARGS.remote_sid
srdfmode=ARGS.mode
ru = rest_functions()
sg_id=SGNAME

#Call to protect Storage Group and Protect with SRDF, default action is not to start the copy, see full function
#srdf_protect_sg in rest_univmax.py, call can also be made adding optional parameter establish=True

ru.srdf_protect_sg(sg_id,remote_sid,srdfmode)
