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

"""
This script is a very simple example to get a list of storage groups in the system, it will also get a count.
Also introduced here is a way to parse the returned JSON payload from the get SG.
"""

from rest_unimax import rest_functions
ru = rest_functions() #Sets up Session with Unisphere Server


sglist=ru.get_sg()


print("This is the full json dictionary returned from the REST Call %s  " %(sglist))
print()
print()
print ("This line parses the JSON to list only the storage group ids from the returned JSON %s" %(sglist["storageGroupId"]))
print()
print("This line parses the returned JSON Number for just the number of Storage groups=%s" %(sglist["num_of_storage_groups"]))
print()