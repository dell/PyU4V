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
"""Constants.py."""

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# U4V constants
UNIVMAX_VERSION = '84'
REPLICATION = 'replication'
SLOPROVISIONING = 'sloprovisioning'
WLP = 'wlp'
MIGRATION = 'migration'
DSA = 'dsa'
SYSTEM = 'system'
VVOL = 'vvol'
PROVISIONING = 'provisioning'
STATUS_200 = 200
STATUS_201 = 201
STATUS_202 = 202
STATUS_204 = 204
STATUS_401 = 401
STATUS_404 = 404
# Job constants
INCOMPLETE_LIST = ['created', 'scheduled', 'running',
                   'validating', 'validated']
CREATED = 'created'
SUCCEEDED = 'succeeded'
ASYNCHRONOUS = "ASYNCHRONOUS"
ASYNC_UPDATE = {'executionOption': ASYNCHRONOUS}
CREATE_VOL_STRING = "Creating new Volumes"
