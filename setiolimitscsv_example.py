#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import csv
from PyU4V.rest_univmax import rest_functions

"""
IO Density for IOPS restricted service levels- Sample Values only
-	Highest: no limit - Diamond
-	High: 1.3 IOps/GB - Platinum
-	Medium: 0.8 IOps/GB - Gold
-	Low: 0.3 IOps/GB – Silver

"""
highIops = 1.3
mediumIops = 0.8
lowIops = 0.3


# open the file in universal line ending mode
with open('sgpolicy.csv', 'rU') as infile:
    # read the file as a dictionary for each row ({header : value})
    reader = csv.DictReader(infile)
    data = {}
    for row in reader:
        for header, value in row.items():
            try:
                data[header].append(value)
            except KeyError:
                data[header] = [value]

# extract the variables you want
sgnamelist = data['sgname']
policylist = data['policy']


def roundup(x):
    return x if x % 100 == 0 else x + 100 - x % 100


def calculate_io_density(sgname, policy):
    """after making changes to a storage group config or creating a new storage group, this method can be invoked to set
    IO Limit based on the Policy Specified get current IOLimits and Capacity for storage group
    Requires that existing
    """
    sg_current_attributes, sc = ru.get_sg(sg_id=sgname)
    sg_current_capacity = sg_current_attributes["storageGroup"][0]["cap_gb"]
    if policy == "Diamond":
        ru.set_hostIO_limit_IOPS(storageGroup=sgname, IOPS="NOLIMIT",
                                 dynamicDistribution="Never")
    elif policy == "Platinum":
        new_io_limit = int(round(sg_current_capacity) * highIops)
        if new_io_limit < 100:
            # Minimum IO limit that can be set is 100 IOPS
            new_io_limit = 100
        roundup_limit = roundup(new_io_limit)
        ru.set_hostIO_limit_IOPS(storageGroup=sgname, IOPS=roundup_limit,
                                 dynamicDistribution="Always")
    elif policy == "Gold":
        new_io_limit = int(round(sg_current_capacity) * mediumIops)
        if new_io_limit < 100:
            # Minimum IO limit that can be set is 100 IOPS,
            # IOLIMIT must be set in increments of 100 IOPS
            new_io_limit = 100
        roundup_limit = roundup(new_io_limit)
        ru.set_hostIO_limit_IOPS(storageGroup=sgname, IOPS=roundup_limit,
                                 dynamicDistribution="Always")
    elif policy == "Silver":
        new_io_limit = int(round(sg_current_capacity) * lowIops)
        if new_io_limit < 100:
            new_io_limit = 100  # Minimum IO limit that can be set is 100 IOPS
        roundup_limit = roundup(new_io_limit)
        ru.set_hostIO_limit_IOPS(storageGroup=sgname, IOPS=roundup_limit,
                                 dynamicDistribution="Always")

# Invoke RestClass with conf file

ru = rest_functions()

for sg_name, policy_name in zip(sgnamelist, policylist):
    calculate_io_density(sg_name, policy_name)
