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
import json
####################################
# Define and Parse CLI arguments   #
# and instantiate session for REST #
####################################

#No Arguments are Required to run this script

PARSER = argparse.ArgumentParser(description='This python scrtipt is a basic VMAX REST recipe used Gathering Some Performance Statistics from VMAX and VMAX3 Arrays.')
ARGS = PARSER.parse_args()

#This script will gather all performance statistics for all Front End directors and print them.  For use in real world
#output would be writen to a file.

ru=rest_functions()

#First Get a list of all Directors
#Calculate start and End Dates for Gathering Performance Stats Last 4 Hours
#end_date = int(round(time.time() * 1000)) #Set end Date to current time EPOCH in Milliseconds
#start_date = (end_date - 14400000)  #Set start date to EPOCH Time 4 hours Earlier
# Get timestamps
dir_list=ru.get_fe_director_list()

end_date = int(round(time.time() * 1000))
start_date = (end_date - 3600000)

director_performance_results=[]
director_results_combined=[]

for director in dir_list:
    director_metrics=ru.get_fe_director_metrics(director=director,start_date=start_date,end_date=end_date, dataformat='Average')
    director_results = ({
        "director": director,
        "Perfdata": director_metrics
    })
    director_results_combined.append(director_results)

print(director_results_combined)








