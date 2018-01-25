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
Sample Performance Script to gather an hour of data at Given a Storage group
will collect Array, Storage Groupm, Port Group, and Host
or Cluster level Metrics.
"""
from PyU4V import RestFunctions

ru = RestFunctions(u4v_version='84',server_ip=112.456.23.12, )
import time

end_date = int(round(time.time()) * 1000)
start_date = (end_date - 3600000)
sg_id = "YOURSG"


def get_my_kpi():
    array_metrics = ru.get_array_metrics(start_date, end_date)
    sg_metrics = ru.get_storage_group_metrics(sg_id=sg_id,
                                              start_date=start_date,
                                              end_date=end_date)
    masking_view = ru.get_mv_from_sg(sg_id)[0]
    portgroup = ru.get_pg_from_mv(masking_view_id=masking_view)
    host = ru.get_host_from_mv(masking_view)
    pg_metrics = ru.get_port_group_metrics(pg_id=portgroup,
                                           start_date=start_date,
                                           end_date=end_date)
    host_metrics = ru.get_host_metrics(host=host, start_date=start_date,
                                       end_date=end_date)
    print(sg_metrics)
    print(array_metrics)
    print(pg_metrics)
    print(host_metrics)


def main():
    get_my_kpi()


main()
