# Example to show how you can manage multiple arrays using PyU4V.
# This simple example returns the total count of hosts from the VMAX3 arrays in the environment.
# This example does not account for more than one Unisphere instance managing each array.

import PyU4V

# Create connections to Unisphere servers - create rest_functions instances for each Unisphere server
rf1 = PyU4V.rest_functions(username='smc', password='smc', server_ip='10.0.0.1')
rf2 = PyU4V.rest_functions(username='smc', password='smc', server_ip='10.0.0.2')


def get_host_count_from_all_arrays(rf):
    total_num_hosts = 0
    array_count = 0
    array_list, __ = rf.get_vmax3_array_list()
    if array_list and array_list.get('symmetrixId'):
        for array in array_list['symmetrixId']:
            rf.set_array(array)
            host_list, sc = rf.get_hosts()
            number_host = 0
            if host_list and host_list.get('hostId'):
                number_host = len(host_list["hostId"])
            total_num_hosts = total_num_hosts + number_host
            array_count += 1
    print("There are %d hosts associated with this Unisphere instance "
          "from a total of %d arrays " % (total_num_hosts, array_count))
    return total_num_hosts, array_count


def multiple_unispheres(rf_list):
    total_num_hosts = 0
    total_array_count = 1
    for rf in rf_list:
        hosts, array_count = get_host_count_from_all_arrays(rf)
        total_num_hosts = total_num_hosts + hosts
        total_array_count = total_array_count + array_count
    print("There are %d hosts in the given environment from a total "
          "of %d arrays and %d Unisphere hosts."
          % (total_num_hosts, total_array_count, len(rf_list)))

multiple_unispheres(rf_list=[rf1, rf2])
