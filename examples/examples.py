import PyU4V

ru = PyU4V.rest_functions(server_ip='10.60.141.75')

# define variables
array_id = '000197800128'
ru.set_array(array_id)

sg_id = "test-1"
sg_id2 = "test-2"
ig_id = "test-host"
vol_id = "00123"
snap_name = "new_snap"
gen_snap = "new_gen_snap"
initiator1 = "10000000c123456"
initiator2 = ""
SRP = "SRP_1"
SLO = "Diamond"
volume_identifier = "test"
workload = None
PG = "os-test-pg"
PG_iscsi = "os-fakeport-pg"
jobID = "1467022150377"
maskingviewId = "test_MV"
host_name = "test-host"
link_sg_name = "test_link_sg"


def main():

    ru.set_array(array_id)

    ''' sg function calls '''
    print(ru.get_sg())

    ru.create_empty_sg(SRP, sg_id, SLO, workload)
    ru.create_non_empty_storagegroup(
        srpID=SRP, sg_id=sg_id2, slo=SLO, workload="None",
        num_vols=2, capUnit="GB", vol_size="1")
    ru.add_new_vol_to_storagegroup(sg_id=sg_id2, num_vols=1,
                                   capUnit="GB", vol_size="1")
    ru.get_sg(sg_id)
    ru.delete_sg(sg_id)

    ''' host and masking view calls'''
    ru.get_mvs_from_host(ig_id)
    ru.create_host("new_host_name", initiator_list=[initiator1])
    ru.create_masking_view_existing_components(
        PG, maskingviewId, 'new_host_name', sg_id2)
    print(ru.get_mv_connections(maskingviewId))

# main()


# Example function where a given SLO and workload are checked on the array
def verify_slo_workload(slo, workload, array):
    """Check if SLO and workload values are valid.

    :param slo: Service Level Object e.g bronze
    :param workload: workload e.g DSS
    :param array: Symm array id e.g 1901876178
    :returns: boolean
    """
    ru.set_array(array)
    isValidSLO = False
    isValidWorkload = False
    validWorkloads, sc = ru.get_workload()['workloadId']
    validSLOs, sc = ru.get_SLO()['sloId']

    if (workload in validWorkloads) or (workload is None):
        isValidWorkload = True
    else:
        print(("Workload: %s is not valid. Valid values are "
               "%s") % (workload, validWorkloads))
    if (slo in validSLOs) or (slo is None):
        isValidSLO = True
    else:
        print(("SLO: %s is not valid. Valid values are "
               "%s" % (slo, validSLOs)))
    print(isValidSLO, isValidWorkload)

# verify_slo_workload(SLO, workload, array_id)

# print(ru.get_perf_threshold_categories())


# example function to get the physical port identifiers from a portgroup
def get_port_identifier(portgroup):
    """Given a portgroup, get the physical port identifiers,
    e.g. wwn or iqn

    :return: list of identifiers
    """
    identifier_list = []
    portkeylist = ru.extract_directorId_pg(portgroup)
    for portkey in portkeylist:
        try:
            director = portkey["directorId"]
            port = portkey["portId"]
            identifier = ru.get_port_identifier(director, port)
            identifier_list.append(identifier)
        except KeyError:
            pass
    return identifier_list

print(get_port_identifier('os-ciara-pg'))


def headroom_check():
    headroom_capacity_gb = ru.get_headroom("OLTP")[0]
    print(headroom_capacity_gb)

# headroom_check()
