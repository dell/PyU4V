from PyU4V import RestFunctions

ru = RestFunctions(u4v_version=84)

# Script will find a list of storage groups with expired snapshots and return
# details.


def expired_snap_list():
    sglist = ru.replication.get_storage_group_rep_list(hasSnapshots=True)
    expired_list = []
    for sg in sglist:
        snaplist = ru.replication.get_storage_group_rep(sg)
        for snapshot_name in snaplist["snapVXSnapshots"]:
            snapgen_list = ru.replication.get_storagegroup_snapshot_generation_list(
                sg, snapshot_name)
            for i in snapgen_list:
                snapdetails = ru.replication.get_snapshot_generation_details(
                    sg, snapshot_name, i)
                if snapdetails["isExpired"]:
                    snapcreation_time = snapdetails["timestamp"]
                    snapexpiration = snapdetails["timeToLiveExpiryDate"]
                    expired_details = {'storagegroup_name': sg,
                                       'snapshot_name': snapshot_name,
                                       'generation_number': i,
                                       'linked_sg_names': snapdetails["linkedStorageGroup"],
                                       'created_at': snapcreation_time,
                                       'expired_at': snapexpiration}
                    expired_list.append(expired_details)
    return expired_list

expired_snap_list()
