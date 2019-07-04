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
"""Hello Unisphere."""

from PyU4V import U4VConn

conn = U4VConn(u4v_version='90', server_ip='IPADDRESS', port=8443,
               verify=False, username='smc', password='smc')

# Make a get call to find the version
version = conn.common.get_uni_version()

# Get a list of managed arrays
array_list = conn.common.get_array_list()


print("Congratulations you have just connected to Unisphere for "
      "VMAX your Version is ", version[1])
print("This Unisphere instance manages the following arrays", array_list)

local_array_list = []

for i in array_list:
    check_local = conn.common.get_array(i)
    if check_local["local"]:
        local_array_list.append(i)


print("The following arrays are local to this Unisphere instance",
      local_array_list)
