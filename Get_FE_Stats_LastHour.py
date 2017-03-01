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
import time
# This script will gather all performance statistics for all
# Front End directors and print them.  For use in real world
# output would be writen to a file.

####################################
# Declare Variables                #
# and instantiate session for REST #
# calls                            #
####################################
# end_date = int(round(time.time() * 1000)) #Set end Date to current time EPOCH in Milliseconds
# start_date = (end_date - 3600000)  #Set start date to EPOCH Time 1 hours Earlier
ru = rest_functions()
end_date = int(round(time.time() * 1000))
start_date = (end_date - 3600000)

#No Arguments are Required to run this script running with -h will provide a description.

PARSER = argparse.ArgumentParser(description='This python scrtipt is a basic VMAX REST recipe used Gathering Some Performance Statistics from VMAX and VMAX3 Arrays.')
ARGS = PARSER.parse_args()

dir_list=ru.get_fe_director_list()


def get_last_hour_fe_metrics():
    # First Get a list of all Directors
    # Calculate start and End Dates for Gathering Performance Stats Last 1 Hour
    director_results_combined = dict()
    director_results_list=[]
    # print("this is the director list %s" % dir_list)
    director_results_combined['reporting_level'] = "FEDirector"
    for fe_director in dir_list:
        director_metrics = ru.get_fe_director_metrics(director=fe_director, start_date=start_date, end_date=end_date,dataformat='Average')
        director_results=({
            "symmetrixID":ru.array_id,
            "directorID":fe_director,
            "perfdata":director_metrics[0]['resultList']['result']
        })
        director_results_list.append(director_results)
    director_results_combined['hourlyPerf']=director_results_list

    return director_results_combined


def main():
    feperfdata=get_last_hour_fe_metrics()
    print (feperfdata)



main()












