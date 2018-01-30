import time

import PyU4V


rf = PyU4V.U4VConn(
        username='smc', password='smc', server_ip='10.0.0.1',
        port='8443', array_id='000197111111')


def expand_srdf_storagegroup(
        production_sg_name, srp, slo, workload, vol_size,
        num_vols, cap_unit, rdfg_no, remote_symm_id, establish,
        rdf_mode, version='84'):
    """Expand an SRDF protected storage group.

    Please note that if you are expanding an Asynchronous group,
    the group will have to be suspended first (no consistency exempt
    option available). This must be done using storage group APIs when
    using REST, so there must be a 1-to-1 relationship between the
    volumes in the RDFG and the volumes in the production SG.
    :param production_sg_name: the name of the production sg
    :param srp: the srp
    :param slo: the service level
    :param workload: the workload
    :param vol_size: volume size
    :param num_vols: the number of required volumes
    :param cap_unit: the capacity unit
    :param rdfg_no: the rdfg number
    :param remote_symm_id: the remote symm id
    :param establish: flag to indicate establish -- bool
    :param rdf_mode: the rdf mode required
    :param version: the unisphere version required - '84' or '83' only
    """
    rf.U4V_VERSION = version
    rf.rest_client.timeout = 600
    sg_name = 'temp-sg-%d' % time.time()
    rf.provisioning.create_non_empty_storagegroup(
        srp, sg_name, slo, workload, num_vols, vol_size, cap_unit)

    # Create SRDF relationship
    if rdf_mode.lower() == "asynchronous":
        # The group needs to be in a suspended state before new volumes
        # can be added. Check state, suspend group if required.
        sg_rdf_details = rf.replication.get_storagegroup_srdf_details(
            production_sg_name, rdfg_no)
        if 'Suspended' not in sg_rdf_details['states']:
            rf.replication.modify_storagegroup_srdf(
                production_sg_name, 'Suspend', rdfg=rdfg_no,
                options={'immediate': 'true'})
        rf.replication.create_storagegroup_srdf_pairings(
            sg_name, remote_symm_id, rdf_mode,
            establish=None, rdfg_number=rdfg_no)
    else:
        rf.replication.create_storagegroup_srdf_pairings(
            sg_name, remote_symm_id, rdf_mode,
            establish=establish, rdfg_number=rdfg_no)

    # Get the device ids and move the volumes from the temp sg
    # to the production sg
    vol_list = rf.provisioning.get_vols_from_storagegroup(sg_name)
    # In 8.4, use 'move_volume' functionality
    rf.provisioning.move_volumes_between_storage_groups(
        sg_name, production_sg_name, vol_list)
    # Delete the temporary sg
    rf.provisioning.delete_storagegroup(sg_name)

    # Repeat on remote side
    local_array = rf.array_id
    rf.set_array_id(remote_symm_id)
    remote_vol_list = rf.provisioning.get_vols_from_storagegroup(sg_name)
    rf.provisioning.move_vol_between_storagegroup(
        sg_name, production_sg_name, remote_vol_list)
    rf.provisioning.delete_storagegroup(sg_name)
    # Set array back to local
    rf.set_array_id(local_array)
    # If async, re-establish the replication relationship if required
    if rdf_mode.lower() == "asynchronous" and establish is True:
        rf.replication.modify_storagegroup_srdf(
            production_sg_name, 'Establish', rdfg=rdfg_no)


expand_srdf_storagegroup(
        'test-expand-async1', 'SRP_1', 'Diamond', 'None', 1,
        3, 'GB', 30, '000197222222', True, 'Asynchronous', version='83')
