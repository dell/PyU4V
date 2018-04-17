#Sample Script

from PyU4V import U4VConn

conn = U4VConn(u4v_version='90', server_ip='IPADDRESS',port=8443,
               verify=False,username='smc',password='smc')

#Make a get call to find the version
version=conn.common.get_uni_version()

#Get a list of managed arrays
array_list=conn.common.get_array_list()



print ("Congratulations you have just connected to Unisphere for "
       "VMax your Version is ", version[1])
print ("This Unisphere instance manages the following arrays", array_list)

local_array_list = []

for i in array_list:
    check_local = conn.common.get_array(i)
    if check_local["local"]:
        local_array_list.append(i)



print ("The following arrays are local to this Unisphere instance",
       local_array_list)