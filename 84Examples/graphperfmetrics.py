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
Sample Script to show graphing of performanc metrics using matplotlib

"""
from PyU4V import RestFunctions
import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime as dt
import time
import numpy as np


ru = RestFunctions(u4v_version='84')


end_date = int(round(time.time()) * 1000)
start_date = (end_date - 3600000)

def get_array_kpi():
    array_metrics = ru.get_array_metrics(start_date, end_date)
    return array_metrics


def main():
    array_metrics=get_array_kpi()
    perfdatalist=array_metrics.get('perf_data')
    hostiolist = []
    dtstimelist = []
    readresponselist =[]
    print (perfdatalist)
    for perf_host in perfdatalist:
        hostiolist.append(perf_host.get('HostIOs'))
        readresponselist.append(perf_host.get('ReadResponseTime'))
        epochtime=(perf_host.get ('timestamp'))
        dtstime = round(epochtime/1000)
        dtstimelist.append(dtstime)

    dateconv=np.vectorize(dt.datetime.fromtimestamp)
    convtimelist =(dateconv(dtstimelist))
    # print(convtimelist)
    fig, ax = plt.subplots(1)
    fig.autofmt_xdate()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot_date(convtimelist,hostiolist,'-')
    plt.plot_date(convtimelist, readresponselist, '-')
    plt.legend(['HostIOs', 'ReadResponseTime'], loc='upper left')
    plt.subplots_adjust(bottom=0.1)
    plt.xticks(rotation=25)
    plt.ylabel('Host IOs')
    plt.xlabel('Time')
    plt.title('Host IOs and Read Response times over the last Hour')
    plt.show()


main()
