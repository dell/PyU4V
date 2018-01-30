from PyU4V import U4VConn

ru = U4VConn()

"""
Sample script to set specific performance metrics and enable alerting for 
these metrics.

Reads a CSV file with the following format

category,metric,firstthreshold,secondthreshold,notify
array,HostReads,100000,300000,true
array,HostWrites,100000,300000,true


"""
data = ru.common.read_csv_values("metricalerts.csv")


firstthreshold_list = data["firstthreshold"]
secondthreshold_list = data["secondthreshold"]
notify_list = data["notify"]
categrory_list = data["category"]
metric_list = data["metric"]

for c, m, f, s, n in zip(categrory_list, metric_list, firstthreshold_list,
                         secondthreshold_list, notify_list,):
    ru.performance.set_perf_threshold_and_alert(c, m, f, s, n)
