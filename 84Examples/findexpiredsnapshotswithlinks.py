from PyU4V.rest_univmax2 import RestFunctions
ru=RestFunctions(u4v_version=84)

#Script will find a list of storage groups with expired snapshots and print
# details.

sglist,rc = ru.get_sg()

for sg in sglist["storageGroupId"]:
    snaplist,rc = ru.get_snap_sg(sg)
    if len(snaplist["snapVXSnapshots"]) >0:
        #print(sg, snaplist["snapVXSnapshots"])
        for snapshot_name in snaplist["snapVXSnapshots"]:
            snapgen, rc=ru.get_snap_sg_generation(sg,snapshot_name)
            snapcount=snapgen["generationCount"]
            gen_num=0
            while snapcount >0:
                snapdetails, rc= ru.get_snapshot_generation_details(sg,
                                                               snapshot_name,
                                                       gen_num)
                snapcount=snapcount-1
                if snapdetails["isExpired"]:
                    #print (snapdetails)
                    snapcreation_time = snapdetails["timestamp"]
                    snapexpiration = snapdetails["timeToLiveExpiryDate"]
                    for linked_sg in snapdetails["linkedStorageGroup"]:
                        linked_sg_name=linked_sg["name"]
                        print ("Storage Group %s has expired snapshots "
                               "Snapshot name %s, Generation "
                               "Number %s snapshot expired on %s, linked "
                               "storage group name is %s" %(
                            sg,snapshot_name,gen_num,snapexpiration,linked_sg_name))
                gen_num = gen_num + 1


