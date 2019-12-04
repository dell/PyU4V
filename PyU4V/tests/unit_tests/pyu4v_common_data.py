# Copyright (c) 2019 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""pyu4v_common_data.py."""


class CommonData(object):
    """Common array data."""
    U4P_VERSION = '91'

    array = '000197800123'
    remote_array = '000197800124'
    srp = 'SRP_1'
    slo = 'Diamond'
    workload = 'DSS'
    port_group_name_f = 'PU-fibre-PG'
    port_group_name_i = 'PU-iscsi-PG'
    masking_view_name_f = 'PU-HostX-F-MV'
    masking_view_name_i = 'PU-HostX-I-MV'
    initiatorgroup_name_f = 'PU-HostX-F-IG'
    initiatorgroup_name_i = 'PU-HostX-I-IG'
    hostgroup_id = 'PU-HostGroup-F-HG'
    storagegroup_name = 'PU-mystoragegroup-SG'
    failed_resource = 'PU-failed-resource'
    volume_wwn = '600000345'
    device_id = '00001'
    device_id2 = '00002'
    device_id3 = '00003'
    device_id4 = '00004'
    rdf_group_name = 'Group1'
    rdf_group_name_91 = 'Group1'
    rdf_group_num_91 = 1
    rdf_group_no = '70'
    u4v_version = '91'
    parent_sg = 'PU-HostX-SG'
    storagegroup_name_1 = 'PU-mystoragegroup1-SG'
    storagegroup_name_2 = 'PU-mystoragegroup2-SG'
    group_snapshot_name = 'Grp_snapshot'
    target_group_name = 'Grp_target'
    qos_storagegroup = 'PU-QOS-SG'
    snapshot_name = 'snap_01234'

    # director port info
    director_id1 = 'FA-1D'
    port_id1 = '4'
    director_id2 = 'SE-4E'
    port_id2 = '0'
    port_key1 = {'directorId': director_id1, 'portId': port_id1}
    port_key2 = {'directorId': director_id2, 'portId': port_id2}

    # Connector info
    wwpn1 = '123456789012345'
    wwpn2 = '123456789054321'
    wwnn1 = '223456789012345'
    initiator = 'iqn.1993-08.org.debian: 01: 222'
    initiator2 = 'iqn.1993-08.com.emc: 01: 222'
    ip, ip2 = u'123.4.56.78', u'123.45.67.89'
    ipv6 = u'2001:1:22:333:4444:dbfa:a7f7:8000'
    iqn = u'iqn.1992-04.com.emc:600009700bca30c01e3e012e00000001,t,0x0001'
    iqn2 = u'iqn.1992-04.com.emc:600009700bca30c01e3e012e00000002,t,0x0001'

    # PowerMax data
    # SLO provisioning
    compression_info = {'symmetrixId': ['000197800128']}
    director_info = {'directorId': director_id1,
                     'director_slot_number': 1,
                     'availability': 'Online',
                     'num_of_ports': 5}
    director_list = {'directorId': [director_id1, director_id2]}
    host_list = {'hostId': [initiatorgroup_name_f, initiatorgroup_name_i]}
    initiatorgroup = [{'initiator': [wwpn1],
                       'hostId': initiatorgroup_name_f,
                       'maskingview': [masking_view_name_f]},
                      {'initiator': [initiator],
                       'hostId': initiatorgroup_name_i,
                       'maskingview': [masking_view_name_i]}]

    hostgroup = {'num_of_hosts': 1,
                 'num_of_initiators': 4,
                 'num_of_masking_views': 1,
                 'host': [initiatorgroup[0]],
                 'type': 'Fibre',
                 'hostGroupId': hostgroup_id,
                 'maskingview': [masking_view_name_f]}

    hostgroup_list = {'hostGroupId': [hostgroup_id]}

    initiator_list = [{'host': initiatorgroup_name_f,
                       'initiatorId': wwpn1,
                       'maskingview': [masking_view_name_f]},
                      {'host': initiatorgroup_name_i,
                       'initiatorId': initiator,
                       'maskingview': [masking_view_name_i]},
                      {'initiatorId': [
                          'FA-1D:4:' + wwpn1,
                          'SE-4E:0:' + initiator]}]

    maskingview = [{'maskingViewId': masking_view_name_f,
                    'portGroupId': port_group_name_f,
                    'storageGroupId': storagegroup_name,
                    'hostId': initiatorgroup_name_f,
                    'maskingViewConnection': [
                        {'host_lun_address': '0003'}]},
                   {'maskingViewId': masking_view_name_i,
                    'portGroupId': port_group_name_i,
                    'storageGroupId': storagegroup_name_1,
                    'hostId': initiatorgroup_name_i,
                    'maskingViewConnection': [
                        {'host_lun_address': '0003'}]},
                   {'maskingViewId': [masking_view_name_f,
                                      masking_view_name_i]}]

    portgroup = [{'portGroupId': port_group_name_f,
                  'symmetrixPortKey': [
                      {'directorId': director_id1,
                       'portId': 'FA-1D:4'}],
                  'maskingview': [masking_view_name_f]},
                 {'portGroupId': port_group_name_i,
                  'symmetrixPortKey': [
                      {'directorId': director_id2,
                       'portId': 'SE-4E:0'}],
                  'maskingview': [masking_view_name_i]}]

    pg_list = {'portGroupId': [port_group_name_i, port_group_name_f]}

    port_key_list = {'symmetrixPortKey': [port_key1, port_key2]}

    port_list = [
        {'symmetrixPort': {'num_of_masking_views': 1,
                           'maskingview': [masking_view_name_f],
                           'identifier': wwnn1,
                           'symmetrixPortKey': port_key1,
                           'portgroup': [port_group_name_f]}},
        {'symmetrixPort': {'identifier': initiator,
                           'symmetrixPortKey': port_key2,
                           'ip_addresses': [ip],
                           'num_of_masking_views': 1,
                           'maskingview': [masking_view_name_i],
                           'portgroup': [port_group_name_i]}}]

    sg_details = [{'srp': srp,
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': storagegroup_name,
                   'slo': slo,
                   'workload': workload},
                  {'srp': srp,
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': storagegroup_name_1,
                   'slo': slo,
                   'workload': workload,
                   'maskingview': [masking_view_name_f],
                   'parent_storage_group': [parent_sg]},
                  {'srp': srp,
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': storagegroup_name_2,
                   'slo': slo,
                   'workload': workload,
                   'maskingview': [masking_view_name_i]},
                  {'srp': 'None',
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': parent_sg,
                   'child_storage_group': [storagegroup_name_1],
                   'maskingview': [masking_view_name_f]},
                  {'srp': srp, 'num_of_vols': 2, 'cap_gb': 2,
                   'storageGroupId': qos_storagegroup,
                   'slo': slo, 'workload': workload,
                   'hostIOLimit': {'host_io_limit_io_sec': '4000',
                                   'dynamicDistribution': 'Always',
                                   'host_io_limit_mb_sec': '4000'}}]

    sg_details_rep = [{'childNames': [],
                       'numDevicesNonGk': 2,
                       'isLinkTarget': False,
                       'rdf': True,
                       'capacityGB': 2.0,
                       'name': storagegroup_name,
                       'snapVXSnapshots': [group_snapshot_name],
                       'symmetrixId': array,
                       'numSnapVXSnapshots': 1}]

    sg_details_migration = [{'targetArray': remote_array,
                             'sourceArray': array,
                             'totalCapacity': 8.0,
                             'targetMaskingView': [masking_view_name_f],
                             'state': 'Synchronized',
                             'sourceMaskingView': [masking_view_name_i],
                             'remainingCapacity': 0.0,
                             'devicePairs': [{
                                 'invalidSrc': False,
                                 'srcVolumeName': 'my-vol',
                                 'invalidTgt': False,
                                 'tgtVolumeName': 'my-vol2',
                                 'missingSrc': False,
                                 'missingTgt': False}],
                             'storageGroup': storagegroup_name}]

    sg_rdf_details = [{'storageGroupName': storagegroup_name,
                       'symmetrixId': array,
                       'modes': ['Synchronous'],
                       'rdfGroupNumber': rdf_group_no,
                       'states': ['Synchronized']}]

    sg_list = {'storageGroupId': [storagegroup_name,
                                  storagegroup_name_1,
                                  storagegroup_name_2]}

    sg_list_rep = {'name': [storagegroup_name]}
    sg_rdf_list = {'rdfgs': [rdf_group_no]}

    sg_list_migration = {'name': sg_list['storageGroupId'],
                         'migratingName': [storagegroup_name]}

    srp_details = {'srpSloDemandId': ['Bronze', 'Diamond', 'Gold',
                                      'None', 'Optimized', 'Silver'],
                   'srpId': srp,
                   'total_used_cap_gb': 5244.7,
                   'total_usable_cap_gb': 20514.4,
                   'total_subscribed_cap_gb': 84970.1,
                   'fba_used_capacity': 5244.7,
                   'reserved_cap_percent': 10}

    srp_list = {'srpId': [srp, 'SRP_2']}

    compr_report = {'storageGroupCompressibility': [
        {'num_of_volumes': 6, 'storageGroupId': storagegroup_name,
         'allocated_cap_gb': 0.0, 'used_cap_gb': 0.0,
         'compression_enabled': 'false'}, ]}

    volume_details = [{'cap_gb': 2,
                       'num_of_storage_groups': 1,
                       'volumeId': device_id,
                       'volume_identifier': 'my-vol',
                       'wwn': volume_wwn,
                       'snapvx_target': 'false',
                       'snapvx_source': 'false',
                       'storageGroupId': [storagegroup_name],
                       'allocated_percent': 5,
                       'rdfGroupId': 1},
                      {'cap_gb': 1,
                       'num_of_storage_groups': 1,
                       'volumeId': device_id2,
                       'wwn': '600012345',
                       'storageGroupId': [storagegroup_name_1],
                       'allocated_percent': 5},
                      {'cap_gb': 1,
                       'num_of_storage_groups': 0,
                       'volumeId': device_id3,
                       'volume_identifier': 'my-vol3',
                       'wwn': '600012345',
                       'allocated_percent': 50}]

    volume_list = [
        {'resultList': {'result': [{'volumeId': device_id}]}},
        {'resultList': {'result': [{'volumeId': device_id2}]}},
        {'expirationTime': 1517830955979, 'count': 2, 'maxPageSize': 1000,
         'id': '123', 'resultList': {'result': [{'volumeId': device_id},
                                                {'volumeId': device_id2}]}}]

    workloadtype = {'workloadId': ['OLTP', 'OLTP_REP', 'DSS', 'DSS_REP']}
    slo_list = {'sloId': ['Bronze', 'Diamond', 'Gold',
                          'Optimized', 'Platinum', 'Silver']}
    slo_details = {'sloBaseId': slo, 'num_of_workloads': 5, 'sloId': slo,
                   'num_of_storage_groups': 1230,
                   'workloadId': workloadtype['workloadId'],
                   'storageGroupId': [storagegroup_name,
                                      storagegroup_name_1,
                                      storagegroup_name_2]}

    # replication
    capabilities = {'symmetrixCapability': [{'rdfCapable': True,
                                             'snapVxCapable': True,
                                             'symmetrixId': '0001111111'},
                                            {'symmetrixId': array,
                                             'snapVxCapable': True,
                                             'rdfCapable': True}]}

    no_capabilities = {'symmetrixCapability': [{'rdfCapable': False,
                                                'snapVxCapable': False,
                                                'symmetrixId': '0001111111'},
                                               {'symmetrixId': array,
                                                'snapVxCapable': False,
                                                'rdfCapable': False}]}

    snap_restore_payload = {'action': 'Restore'}

    group_snap_vx = {'generation': 0,
                     'isLinked': False,
                     'numUniqueTracks': 0,
                     'isRestored': False,
                     'name': group_snapshot_name,
                     'numStorageGroupVolumes': 1,
                     'state': ['Established'],
                     'timeToLiveExpiryDate': 'N/A',
                     'isExpired': False,
                     'numSharedTracks': 0,
                     'timestamp': '00:30:50 Fri, 02 Jun 2017 IST +0100',
                     'numSourceVolumes': 1}
    expired_snap = {'generation': 0,
                    'isLinked': True,
                    'name': group_snapshot_name,
                    'numStorageGroupVolumes': 1,
                    'state': ['Established'],
                    'timeToLiveExpiryDate': '01:30:50 Fri, 02 Jun 2017 IST ',
                    'isExpired': True,
                    'linkedStorageGroup': [{'name': target_group_name}],
                    'timestamp': '00:30:50 Fri, 02 Jun 2017 IST +0100',
                    'numSourceVolumes': 1}
    sg_snap_list = {'name': [group_snapshot_name]}
    sg_snap_gen_list = {'generations': [0]}

    rdf_group_list_91 = [{'rdfgNumber': 1, 'label': 'Group1'},
                         {'rdfgNumber': 2, 'label': 'Group2'},
                         {'rdfgNumber': 3, 'label': 'Group3'},
                         {'rdfgNumber': 4, 'label': 'Group4'}]

    rdf_group_list = {'rdfGroupID': [{'rdfgNumber': rdf_group_no,
                                      'label': rdf_group_name}]}

    rdf_group_details = {'modes': ['Synchronous'],
                         'remoteSymmetrix': remote_array,
                         'label': rdf_group_name,
                         'type': 'Dynamic',
                         'numDevices': 1,
                         'remoteRdfgNumber': rdf_group_no,
                         'rdfgNumber': rdf_group_no}
    rdf_group_vol_details = {'remoteRdfGroupNumber': rdf_group_no,
                             'localSymmetrixId': array,
                             'volumeConfig': 'RDF1+TDEV',
                             'localRdfGroupNumber': rdf_group_no,
                             'localVolumeName': device_id,
                             'rdfpairState': 'Synchronized',
                             'remoteVolumeName': device_id2,
                             'localVolumeState': 'Ready',
                             'rdfMode': 'Synchronous',
                             'remoteVolumeState': 'Write Disabled',
                             'remoteSymmetrixId': remote_array}
    rdf_group_vol_list = {'name': [device_id, device_id2]}

    rep_info = {'symmetrixId': array, 'storageGroupCount': 1486,
                'replicationCacheUsage': 0, 'rdfGroupCount': 7}

    # migration
    migration_info = {'symmetrixId': array, 'storageGroupCount': 1486,
                      'local': True, 'migrationSessionCount': 10}
    migration_capabilities = {'storageArrayCapability': [{
        'srdfsTarget': True,
        'dmSource': True,
        'srdfsSource': True,
        'dmTarget': True,
        'compression': True,
        'arrayId': array}]}
    migration_environment_list = {'arrayId': [array]}
    migration_environment_details = {'symmetrixId': array,
                                     'otherSymmetrixId': remote_array,
                                     'invalid': False,
                                     'state': 'OK'}

    # system
    job_list = [{'status': 'SUCCEEDED',
                 'jobId': '12345',
                 'result': 'created',
                 'resourceLink': 'storagegroup/%s' % storagegroup_name},
                {'status': 'RUNNING', 'jobId': '55555'},
                {'status': 'FAILED', 'jobId': '09999'}]
    symmetrix = [{'symmetrixId': array,
                  'model': 'VMAX250F',
                  'ucode': '5977.1091.1092'}]
    symm_list = {'symmetrixId': [array, remote_array]}
    server_version = {'version': 'V9.1.0.0'}

    # wlp
    wlp_info = {'symmetrixId': array, 'lastProcessed': 1569417000000,
                'nextUpdate': 795}
    headroom_array = {'gbHeadroom': [{'srpId': 'SRP_TEST', 'emulation': 'FBA',
                                      'capacity': 58555.9}]}

    # iterator
    iterator_page = {'result': [{'volumeId': '00002'}], 'from': 2, 'to': 2}

    vol_with_pages = {'expirationTime': 1572358809878, 'count': 6,
                      'maxPageSize': 5, 'from': 1, 'to': 1,
                      'id': '0edbcf48-65f0-4271-999b-22412c457cd5_0',
                      'resultList': {'result': [{'volumeId': '00001'}]}}

    # Health
    array_health = {
        'num_failed_disks': 0, 'health_score_metric': [{
            'cached_date': 1573660846922, 'expired': False,
            'metric': 'SERVICE_LEVEL_COMPLIANCE',
            'instance_metrics': [{
                'health_score': 95.0, 'data_date': 1573660846922,
                'health_score_instance_metric': [{
                    'severity': 'Critical',
                    'instance_name': 'Storage Group Py1 is out of compliance',
                    'metric_name': 'Service Level Health Score',
                    'health_score_reduction': 5.0,
                    'metric_category': 'SG'}]}]}]}

    array_health_check_list = {'health_check_id': ['1573664112128']}

    perform_health_check_response = {
        'jobId': '1573664112132', 'name': 'CI-Test', 'status': 'RUNNING',
        'username': 'test', 'last_modified_date': 'Nov-13-2019 16:55:12.133',
        'last_modified_date_milliseconds': 1573664112133,
        'completed_date_milliseconds': 0, 'task': [{
            'execution_order': 1, 'description': 'CI-Test'}],
        'resourceLink': 'test', 'result': 'Started'}

    health_check_response = {'testResult': [
        {'item_name': 'Vault State Test ', 'result': True},
        {'item_name': 'Spare Drives Test ', 'result': True},
        {'item_name': 'Memory Test ', 'result': True},
        {'item_name': 'Locks Test ', 'result': True},
        {'item_name': 'Emulations Test ', 'result': True},
        {'item_name': 'Environmentals Test ', 'result': False},
        {'item_name': 'Battery Test ', 'result': True},
        {'item_name': 'General Test ', 'result': True},
        {'item_name': 'Compression And Dedup Test ', 'result': True}],
        'execution_status': 'FAILED', 'symmetrixId': array,
        'description': 'CI-Test', 'date': 1573728472714}

    disk_list = {'disk_ids': [
        '0', '1', '10', '11', '12', '13', '2', '3', '4', '5', '6', '7', '8',
        '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8A', '8B',
        '8C', '8D', '9', 'A', 'B', 'C', 'D', 'E', 'F']}

    disk_info = {'spindle_id': '0', 'type': 'INCSTRM_0', 'vendor': 'Intel',
                 'capacity': 354.78}

    tag_list = {'tag_name': ['CLBCK', 'Payroll']}

    tagged_objects = {'array_ids': ['000297600111']}
