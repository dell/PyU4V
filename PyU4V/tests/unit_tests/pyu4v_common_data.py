# Copyright (c) 2020 Dell Inc. or its subsidiaries.
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
    U4P_VERSION = '101'
    server_version = {'version': 'V10.1.0.0'}

    array = '000197800123'
    remote_array = '000197800124'
    remote_array2 = '000197800125'
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
    parent_sg = 'PU-HostX-SG'
    storagegroup_name_1 = 'PU-mystoragegroup1-SG'
    storagegroup_name_2 = 'PU-mystoragegroup2-SG'
    group_snapshot_name = 'Grp_snapshot'
    target_group_name = 'Grp_target'
    qos_storagegroup = 'PU-QOS-SG'
    snapshot_name = 'snap_01234'
    sg_snap_id = 118749976833

    # director port info
    director_id1 = 'FA-1D'
    port_id1 = '4'
    director_id2 = 'SE-4E'
    port_id2 = '0'
    port_key1 = {'directorId': director_id1, 'portId': port_id1}
    port_key2 = {'directorId': director_id2, 'portId': port_id2}

    # V4 director port info
    or_director_id = 'OR-1D'
    ef_director_id = 'EF-1D'
    em_director_id = 'EM-1D'

    v4_port_list = [{'directorId': 'OR-1D', 'portId': '4'},
                    {'directorId': 'OR-4E', 'portId': '0'}]

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
                     'num_of_cores': 7,
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
    port_details = {
        'symmetrixPort': {
            'director_status': 'Online',
            'no_participating': False,
            'num_of_cores': 7,
            'aclx': True,
            'environ_set': False,
            'num_of_mapped_vols': 0,
            'iscsi_target': False,
            'num_of_masking_views': 0,
            'wwn_node': '5000097398027004',
            'enable_auto_negotiate': True,
            'type': 'FibreChannel (563)',
            'avoid_reset_broadcast': False,
            'disable_q_reset_on_ua': False,
            'sunapee': False,
            'port_status': 'PendOn',
            'init_point_to_point': True,
            'volume_set_addressing': False,
            'vnx_attached': False,
            'scsi_support1': True,
            'hp_3000_mode': False,
            'identifier': '5000097398027005',
            'symmetrixPortKey': {
                'directorId': 'FA-1D',
                'portId': '5'
            },
            'max_speed': '16',
            'negotiate_reset': False,
            'spc2_protocol_version': True,
            'unique_wwn': True,
            'siemens': False,
            'num_of_port_groups': 0,
            'common_serial_number': True,
            'scsi_3': True,
            'soft_reset': False
        }
    }
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

    sg_details_rep = [{'childNames': list(),
                       'numDevicesNonGk': 2,
                       'isLinkTarget': False,
                       'rdf': True,
                       'capacityGB': 2.0,
                       'name': storagegroup_name,
                       'snapVXSnapshots': [group_snapshot_name],
                       'symmetrixId': array,
                       'numSnapVXSnapshots': 1}]

    sg_expand_payload_multi_site = {
        'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addSpecificVolumeParam': {
                    'volumeId': [
                        '00123'
                    ],
                    'remoteSymmSGInfoParam': {
                        'remote_symmetrix_2_id': remote_array2,
                        'remote_symmetrix_1_id': remote_array,
                        'remote_symmetrix_1_sgs': [
                            storagegroup_name
                        ],
                        'remote_symmetrix_2_sgs': [
                            storagegroup_name
                        ]}}}}}

    sg_expand_payload_basic_srdf = {
        'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addSpecificVolumeParam': {
                    'volumeId': [
                        '00123'
                    ],
                    'remoteSymmSGInfoParam': {
                        'remote_symmetrix_1_id': remote_array,
                        'remote_symmetrix_1_sgs': [
                            storagegroup_name
                        ]}}}}}

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

    array_slo_details = {
        'default_fba_srp': srp,
        'symmetrixId': array,
        'system_capacity': {
            'usable_total_tb': 61.12, 'subscribed_total_tb': 149.99,
            'subscribed_allocated_tb': 3.73, 'snapshot_total_tb': 1492.07,
            'subscribed_usable_capacity_percent': 246.0,
            'usable_used_tb': 6.24, 'snapshot_modified_tb': 0.0},
        'physicalCapacity': {
            'used_capacity_gb': 76290.38, 'total_capacity_gb': 76290.38},
        'host_visible_device_count': 6848,
        'system_efficiency': {
            'overall_efficiency_ratio_to_one': 445.1,
            'virtual_provisioning_savings_ratio_to_one': 40.6,
            'data_reduction_enabled_percent': 0.0,
            'pattern_detection_savings_tb': 0.0,
            'drr_on_reducible_only_to_one': 0.0,
            'snapshot_savings_ratio_to_one': 1.14096688E7,
            'deduplication_and_compression_savings_tb': 0.0,
            'unreducible_data_tb': 0.0, 'reducible_data_tb': 0.0},
        'sloCompliance': {
            'slo_marginal': 0, 'no_slo': 157, 'slo_stable': 251,
            'slo_critical': 9},
        'meta_data_usage': {
            'backend_meta_data_used_percent': 47.0,
            'replication_cache_used_percent': 0,
            'system_meta_data_used_percent': 34.0,
            'frontend_meta_data_used_percent': 13.0},
        'model': 'PowerMax_2000',
        'ucode': '5978.669.669',
        'device_count': 7168,
        'local': True}

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
                     'snapid': sg_snap_id,
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
    expired_snap = (
        {'generation': 0,
         'isLinked': True,
         'name': group_snapshot_name,
         'numStorageGroupVolumes': 1,
         'state': ['Established'],
         'timeToLiveExpiryDate': '01:30:50 Fri, 02 Jun 2017 IST ',
         'isExpired': True,
         'linkedStorageGroup': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2017 IST +0100',
         'numSourceVolumes': 1})
    non_expired_snap = (
        {'generation': 0,
         'isLinked': True,
         'name': group_snapshot_name,
         'numStorageGroupVolumes': 1,
         'state': ['Established'],
         'timeToLiveExpiryDate': '01:30:50 Fri, 02 Jun 2017 IST ',
         'isExpired': False,
         'linkedStorageGroup': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2017 IST +0100',
         'numSourceVolumes': 1})
    expired_snap_id = (
        {'generation': 0,
         'snapid': 118749976834,
         'linked': True,
         'name': group_snapshot_name,
         'num_storage_group_volumes': 1,
         'state': ['Established'],
         'time_to_live_expiry_date': '01:30:50 Fri, 02 Jun 2020 IST ',
         'expired': True,
         'linked_storage_group': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2020 IST +0100',
         'num_source_volumes': 1})
    non_expired_snap_id = (
        {'generation': 0,
         'snapid': 118749976834,
         'linked': True,
         'name': group_snapshot_name,
         'num_storage_group_volumes': 1,
         'state': ['Established'],
         'time_to_live_expiry_date': '01:30:50 Fri, 02 Jun 2020 IST ',
         'isExpired': False,
         'linked_storage_group': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2020 IST +0100',
         'num_source_volumes': 1})

    sg_snap_list = {'name': [group_snapshot_name]}
    sg_snap_gen_list = {'generations': [0]}
    sg_snap_id_list = {'snapids': [sg_snap_id]}

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

    local_rdf_ports = ['RF-1E:8', 'RF-2E:8']

    remote_rdf_ports = ['RF-1E:8', 'RF-2E:8']

    rdf_ports = [4, 5]

    rdf_director_list = ['RF-1F', 'RF-2F']

    rdf_dir_detail = {
        'gige': False,
        'symmetrixID': '000197600156',
        'fiber': True,
        'directorNumber': 81,
        'directorId': 'RF-1F',
        'hwCompressionSupported': True,
        'online': True
    }

    rdf_dir_port_detail = {
        'symmetrixID': '000197600156',
        'directorNumber': 81,
        'directorId': 'RF-1F',
        'online': True,
        'portNumber': 4,
        'wwn': '5000097398027004'
    }

    remote_port_details = {
        'remotePort': [
            {
                'symmetrixID': '000197900111',
                'directorNumber': 81,
                'directorId': 'RF-1F',
                'online': True,
                'portNumber': 4,
                'wwn': '50000973B001BC04'
            }
        ]
    }

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

    alert_list = {'alertId': ['15a15a58-26a0-4127-9e63-00ca162df789',
                              '2d9e481b-552a-4a33-a586-4bb1d11605c5']}
    alert_id = '15a15a58-26a0-4127-9e63-00ca162df789'
    alert_details = {'alertId': '15a15a58-26a0-4127-9e63-00ca162df789',
                     'state': 'NEW',
                     'severity': 'NORMAL',
                     'type': 'ARRAY',
                     'array': '000197900111',
                     'object': 'RF-1F:5',
                     'object_type': 'Port',
                     'created_date': 'Mar-19-2020 11:51:56.000',
                     'created_date_milliseconds': 1584618716000,
                     'description': 'Port state has changed to Online. '
                                    '- Object is: 000197900111:RF-1F:5',
                     'acknowledged': False}
    alert_summary = {'serverAlertSummary': {
        'alert_count': 0, 'all_unacknowledged_count': 0,
        'fatal_unacknowledged_count': 0,
        'critical_unacknowledged_count': 0,
        'warning_unacknowledged_count': 0,
        'info_unacknowledged_count': 0,
        'minor_unacknowledged_count': 0,
        'normal_unacknowledged_count': 0,
        'all_acknowledged_count': 0,
        'fatal_acknowledged_count': 0,
        'critical_acknowledged_count': 0,
        'warning_acknowledged_count': 0,
        'info_acknowledged_count': 0,
        'minor_acknowledged_count': 0,
        'normal_acknowledged_count': 0},
        'symmAlertSummary': list()}

    ip_interface_address = '192.168.0.3'
    ip_interface_address_network = '192.168.0.3-9'
    ip_interface_list = {'ipInterfaceId': [ip_interface_address_network]}
    ip_interface_details = {
        'ip_interface_id': ip_interface_address_network, 'network_id': 9,
        'ip_prefix_length': 24, 'vlan_id': 0, 'mtu': 1500,
        'iscsi_target_director': director_id2, 'iscsi_target_port': 0,
        'ip_address': ip_interface_address}

    # wlp
    wlp_info = {'symmetrixId': array, 'lastProcessed': 1569417000000,
                'nextUpdate': 795}
    headroom_array = {'gbHeadroom': [{'srpId': 'SRP_TEST', 'emulation': 'FBA',
                                      'capacity': 58555.9}]}
    wlp_capabilities = {'symmetrixCapability': [
        {'symmetrixId': array, 'workloadDetailCapable': True,
         'componentUtilizationCapable': True, 'characterizationCapable': True,
         'headroomGbCapable': True, 'suitabilityTestCapable': True,
         'provisioningTemplateCapable': True, 'slComplianceCapable': True,
         'headroomIopsCapable': True},
        {'symmetrixId': remote_array, 'workloadDetailCapable': True,
         'componentUtilizationCapable': True,
         'characterizationCapable': True,
         'headroomGbCapable': True, 'suitabilityTestCapable': True,
         'provisioningTemplateCapable': True, 'slComplianceCapable': True,
         'headroomIopsCapable': True}]}

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

    # migrate array info
    m_array = '000197800123'
    m_portgroup = 'myportgroup'
    m_initiatorgroup = 'myinitiatorgroup'
    m_sg_name = 'mystoragegroup'
    m_host_name = 'myhost'

    # Old masking views
    smis_mv_1 = 'OS-myhost-No_SLO-I-MV'
    smis_mv_2 = 'OS-myhost-SRP_1-Diamond-NONE-I-CD-MV'
    smis_mv_3 = 'OS-myhost-SRP_1-Diamond-DSS-I-MV'
    smis_mv_4 = 'OS-myhost-SRP_1-Silver-NONE-I-MV'
    smis_mv_5 = 'OS-myhost-SRP_1-Bronze-OLTP-I-CD-MV'
    smis_mv_6 = 'OS-myhost-SRP_1-Diamond-OLTP-I-RE-MV'
    smis_mv_7 = 'OS-host-with-dashes-No_SLO-I-MV'
    smis_mv_8 = 'OS-host-with-dashes-SRP_1-Diamond-NONE-I-MV'

    # New masking view
    rest_mv_1 = 'OS-myhost-I-myportgroup-MV'
    rest_mv_2 = 'OS-myhost-I-portgroup-with-dashes-MV'
    rest_mv_3 = 'OS-host-with-dash-I-myportgroup-MV'

    # Old storage groups
    smis_sg_1 = 'OS-myhost-No_SLO-I-SG'
    smis_sg_2 = 'OS-myhost-SRP_1-Diamond-NONE-I-SG'
    smis_sg_3 = 'OS-myhost-SRP_1-Diamond-DSS-I-SG'
    smis_sg_4 = 'OS-myhost-SRP_1-Silver-NONE-I-CD-SG'
    smis_sg_5 = 'OS-myhost-SRP_1-Diamond-OLTP-I-CD-SG'
    smis_sg_6 = 'OS-myhost-SRP_1-Bronze-OLTP-I-RE-SG'
    smis_sg_7 = 'OS-host-with_dashes-SRP_1-Diamond-OLTP-I-RE-SG'
    smis_sg_8 = 'OS-myhost-SRP_1-Diamond-NONE-I-CD-SG'

    # New parent storage groups
    rest_parent_sg = 'OS-myhost-I-myportgroup-SG'

    # New storage groups
    rest_sg_1 = 'OS-myhost-No_SLO-os-iscsi-pg'
    rest_sg_2 = 'OS-myhost-SRP_1-DiamodNONE-os-iscsi-pg-CD'
    rest_sg_3 = 'OS-myhost-SRP_1-DiamodNONE-os-iscsi-pg'
    rest_sg_4 = 'OS-myhost-SRP_1-DiamodOLTP-os-iscsi-pg-RE'
    rest_sg_5 = 'OS-host-with-dashes-SRP_1-DiamodOLTP-myportgroup-RE'
    rest_sg_6 = 'OS-myhost-SRP_1-DiamodOLTP-myportgroup-CD'

    m_storagegroup = {'slo': 'Diamond',
                      'workload': 'OLTP',
                      'storageGroupId': 'test'}

    m_maskingview = {'portGroupId': m_portgroup,
                     'hostId': m_host_name,
                     'storageGroupId': rest_parent_sg,
                     'maskingViewId': rest_mv_1}

    element_dict = {'new_mv_name': 'OS-myhost-I-myportgroup-MV',
                    'workload': 'NONE',
                    'new_sg_name': 'OS-myhost-SRP_1-DiamodNONE-myportgroup',
                    'srp': 'SRP_1', 'port_group': 'myportgroup',
                    'initiator_group': 'myinitiatorgroup',
                    'new_sg_parent_name': 'OS-myhost-I-myportgroup-SG',
                    'service_level': 'Diamond'}

    element_dict_revert = {
        'service_level': 'Diamond',
        'port_group': 'myportgroup',
        'initiator_group': 'myinitiatorgroup',
        'srp': 'SRP_1',
        'new_mv_name': 'OS-myhost-SRP_1-Diamond-NONE-I-CD-MV',
        'new_sg_name': 'OS-myhost-SRP_1-Diamond-NONE-I-CD-SG',
        'workload': 'NONE'}

    mv_components = {'portGroupId': m_portgroup,
                     'hostId': m_host_name,
                     'storageGroupId': rest_sg_1,
                     'maskingViewId': rest_mv_1}

    device_list = ['0064F', '0088E', '00890', '00891', '00DF2', '00DF3']

    host_io_limit_source = {'host_io_limit_mb_sec': '2000',
                            'host_io_limit_io_sec': '2000',
                            'dynamicDistribution': 'Always'}

    host_io_limit_target = {'host_io_limit_mb_sec': '4000',
                            'host_io_limit_io_sec': '4000',
                            'dynamicDistribution': 'Never'}

    source_sg_details = {'storageGroupId': smis_sg_2,
                         'slo': 'Diamond',
                         'srp': 'SRP_1',
                         'hostIOLimit': host_io_limit_source}

    target_sg_details = {'storageGroupId': rest_sg_3,
                         'slo': 'Diamond',
                         'srp': 'SRP_1',
                         'hostIOLimit': host_io_limit_target}

    snapshot_policy_list = {
        'name': [
            '10_minute',
            '10_min_7_past',
            '10_minute_policy_2',
            'HourlyDefault',
            'WeeklyDefault',
            '10_min_5_past',
            '10_min_on_hour',
            '10_min_3_past',
            'DailyDefault',
            'Hourly_16past']}

    snapshot_policy_name = '10_minute'
    snapshot_policy_info = {'symmetrixID': array,
                            'snapshot_count': 20,
                            'offset_minutes': 0,
                            'interval_minutes': 360,
                            'secure': False,
                            'suspended': False,
                            'snapshot_policy_name': snapshot_policy_name}

    snapshot_policy_sg_list = ['sg1', 'sg2']
    # Metro DR

    metro_dr_detail = {
        'metro_witness_state': 'Available',
        'metro_r2_connectivity_health': 'Degraded',
        'dr_state': 'Synchronized',
        'metro_remain_capacity_to_copy_mb': 0,
        'metro_r1_connectivity_health': 'Degraded',
        'dr_link_state': 'Online',
        'dr_exempt': False,
        'environment_exempt': False,
        'metro_link_state': 'Online',
        'dr_percent_complete': 100,
        'metro_r2_array_health': 'Normal',
        'metro_r1_array_health': 'Normal',
        'valid': True,
        'metro_exempt': False,
        'dr_service_state': 'Active',
        'environment_state': 'Degraded, Manual Recovery',
        'dr_remain_capacity_to_copy_mb': 0,
        'metro_state': 'ActiveActive',
        'name': 'PyU4V_Metro',
        'capacity_gb': 2.003,
        'metro_service_state': 'Active_HA',
        'metro_percent_complete': 100,
        'dr_rdf_mode': 'Adaptive Copy'}

    response_string_dict_success = {'success': True, 'message': 'OK'}
    response_string_dict_fail = {'success': False, 'message': 'FAIL'}

    audit_log_list = {
        'expirationTime': 1600159200802, 'count': 5, 'maxPageSize': 1000,
        'id': 'a2b42abe-977d-4858-bd18-0322d1eb3a43_0', 'from': 1, 'to': 5,
        'resultList': {'result': [
            {'record_id': 747855,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': ('STARTING on PyU4V-sg(Storage group) "CREATE" '
                         'operation. Symm=000111222333, '
                         'SERVICE_LEVEL_NAME=Diamond SRP_NAME=SRP_1 '),
             'entry_date': 1599519722,
             'username': 'C:10.10.10.10\\pyu4v_user'},
            {'record_id': 747856,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': ('Successfully created Storage Group PyU4V-sg '
                         '(index 0xD69) '),
             'entry_date': 1599519722, 'username': ''},
            {'record_id': 747857,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': 'Set SLO 0x1 and SRP 0x1 on devices from SG 0xD69 ',
             'entry_date': 1599519722, 'username': ''},
            {'record_id': 747858,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': ('On Storage group PyU4V-sg operation "CREATE" '
                         'SUCCESSFULLY COMPLETED'),
             'entry_date': 1599519722,
             'username': 'C:10.10.10.10\\pyu4v_user'},
            {'record_id': 747859,
             'entry_date_string': 'Tue Sep 8 2020 00:02:05',
             'message': ('STARTING a TDEV Create Device operation on Symm '
                         '000111222333.'),
             'entry_date': 1599519725,
             'username': 'C:10.10.10.10\\pyu4v_user'}]}}

    audit_record = {'objectList': [{
        'function_class': 'BaseCtrl', 'process_id': '5228',
        'api_library': 'SEK', 'action_code': 'Create', 'task_id': '4584',
        'api_version': 'V9.2.0.1', 'application_id': 'UNIVMAX',
        'entry_date': 1599519722, 'audit_class': 'Base', 'record_id': 747855,
        'entry_date_string': 'Tue Sep 8 2020 00:02:02',
        'records_in_sequence': '1', 'hostname': 'PyU4V-Client',
        'offset_in_sequence': '1', 'os_type': 'WinNT',
        'os_revision': '10.0.14393', 'vendor_id': 'EMC Corp',
        'activity_id': 'SE1e3b9f5c45', 'client_host': '',
        'username': 'C:10.10.10.10\\pyu4v_user',
        'application_version': '9.2.0.1',
        'message': (
            'STARTING on PyU4V-sg(Storage group) "CREATE" '
            'operation. Symm=000111222333, SERVICE_LEVEL_NAME=Diamond '
            'SRP_NAME=SRP_1 ')}]}

    compliance_details = {
        'storage_group_name': storagegroup_name,
        'compliance': 'GREEN', 'sl_count': 1,
        'sl_compliance': [
            {'sl_name': 'DailyDefault',
             'calculation_time': '2020-12-01T12:05',
             'compliance': 'GREEN'}
        ]
    }
    # Clone Functions

    clone_list = {
        'number_of_clone_target_sgs': 2,
        'clone_target_sg_names': [
            'sg_1',
            'sg_2'
        ]
    }

    clone_target_get = {
        'source_volume_id': '0017C',
        'wwn': '60000970000197900256533030313743',
        'state': 'Created',
        'capacity_gb': 8,
        'protected_percent': 0
    }

    clone_target_sg_list = {
        'number_of_clone_target_sgs': 1,
        'clone_target_sg_names': [
            'clonetgt'
        ]
    }

    clone_pairs_list = {
        'clone_count': 2,
        'clones': [
            {
                'source_volume_name': '00332',
                'target_volume_name': '00334',
                'state': 'Ready'
            },
            {
                'source_volume_name': '00365',
                'target_volume_name': '00646',
                'state': 'Ready'
            }
        ]
    }

    management_server_data = {
        "server_details": {
            "cpu_percent": 56,
            "used_heap_percent": 0,
            "total_heap_gb": 12,
            "total_host_memory_gb": 16,
            "used_host_memory_gb": 11,
            "free_host_disk_space_gb": 159,
            "unisphere_thread_count": 125,
            "unisphere_daemon_thread_count": 81,
            "device_count": 4647,
            "local_system_count": 2,
            "remote_system_count": 0,
            "server_start_time_ms": 1689081306887,
            "endpoint_execution_time_ms": 1689084370173
        },
        "clients": {
            "time_window_start_ms": 1689082868327,
            "time_window_end_ms": 1689083768289,
            "client_and_call_counts": [
                {
                    "client": "PyU4V-10.1.0.0/10.16.202.207",
                    "call_count": 12
                },
                {
                    "client": "UNKNOWN/10.16.202.207",
                    "call_count": 3
                }
            ]
        },
        "endpoints": {
            "time_window_start_ms": 1689082868327,
            "time_window_end_ms": 1689083768289,
            "endpoint_and_call_counts": [
                {
                    "endpoint": "/101/system/symmetrix/{symmetrixId} GET",
                    "call_count": 9
                },
                {
                    "endpoint": "/version GET",
                    "call_count": 6
                }
            ]
        },
        "call_frequency_windows": {
            "five_minute_count": 4,
            "one_hour_count": 31,
            "twenty_four_hour_count": 119
        },
        "call_frequency_timeline_one_day": {
            "call_frequency_points": [
                {
                    "time_ms": 1688997495125,
                    "call_count": 0,
                    "cpu_percent": 16
                },
                {
                    "time_ms": 1688997795118,
                    "call_count": 0,
                    "cpu_percent": 11
                },
                {
                    "time_ms": 1688998095120,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1688998395127,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1688998695126,
                    "call_count": 0,
                    "cpu_percent": 13
                },
                {
                    "time_ms": 1688998995118,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1688999295125,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689000105847,
                    "call_count": 0,
                    "cpu_percent": 75
                },
                {
                    "time_ms": 1689000405832,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689000705828,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689001005832,
                    "call_count": 0,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689001305827,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689001605826,
                    "call_count": 0,
                    "cpu_percent": 17
                },
                {
                    "time_ms": 1689001905826,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689002205825,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689002505825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689002805826,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689003105830,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689003405825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689003705824,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689004005825,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689004305825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689004605825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689004905826,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689005205824,
                    "call_count": 0,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689005505824,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689005805825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689006105825,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689006405825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689006705827,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689007005825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689007305824,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689007605824,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689007905824,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689008205824,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689008505826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689008805824,
                    "call_count": 0,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689009105826,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689009405824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689009705823,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689010005825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689010305835,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689010605825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689010905828,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689011205827,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689011505825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689011805823,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689012105825,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689012405825,
                    "call_count": 0,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689012705824,
                    "call_count": 0,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689013005825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689013305825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689013605827,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689013905825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689014205828,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689014505825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689014805914,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689015105825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689015405824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689015705824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689016005825,
                    "call_count": 0,
                    "cpu_percent": 17
                },
                {
                    "time_ms": 1689016305826,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689016605826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689016905826,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689017205826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689017505825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689017805825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689018105825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689018405825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689018705825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689019005825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689019305824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689019605824,
                    "call_count": 0,
                    "cpu_percent": 14
                },
                {
                    "time_ms": 1689019905825,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689020205825,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689020505825,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689020805825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689021105826,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689021405826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689021705826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689022005825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689022305828,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689022605824,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689022905826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689023205825,
                    "call_count": 0,
                    "cpu_percent": 17
                },
                {
                    "time_ms": 1689023505826,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689023805826,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689024105826,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689024405824,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689024705825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689025005825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689025305824,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689025605828,
                    "call_count": 0,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689025905826,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689026205824,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689026505826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689026805824,
                    "call_count": 0,
                    "cpu_percent": 19
                },
                {
                    "time_ms": 1689027105824,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689027405825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689027705826,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689028005825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689028305824,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689028605825,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689028905826,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689029205826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689029505827,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689029805827,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689030105825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689030405825,
                    "call_count": 0,
                    "cpu_percent": 22
                },
                {
                    "time_ms": 1689030705825,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689031005825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689031305825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689031605825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689031905828,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689032205825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689032505825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689032805825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689033105827,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689033405827,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689033705825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689034005825,
                    "call_count": 0,
                    "cpu_percent": 15
                },
                {
                    "time_ms": 1689034305825,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689034605825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689034905825,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689035205825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689035505832,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689035805825,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689036105826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689036405825,
                    "call_count": 0,
                    "cpu_percent": 11
                },
                {
                    "time_ms": 1689036705824,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689037005827,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689037305825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689037605826,
                    "call_count": 0,
                    "cpu_percent": 16
                },
                {
                    "time_ms": 1689037905825,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689038205828,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689038505826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689038805824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689039105826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689039405826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689039705825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689040005824,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689040305828,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689040605826,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689040905825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689041205824,
                    "call_count": 0,
                    "cpu_percent": 13
                },
                {
                    "time_ms": 1689041505826,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689041805827,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689042105826,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689042405826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689042705824,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689043005825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689043305825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689043605827,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689043905826,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689044205825,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689044505824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689044805826,
                    "call_count": 0,
                    "cpu_percent": 13
                },
                {
                    "time_ms": 1689045105826,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689045405826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689045705825,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689046005824,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689046305824,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689046605825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689046905825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689047205825,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689047505825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689047805825,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689048105825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689048405826,
                    "call_count": 0,
                    "cpu_percent": 14
                },
                {
                    "time_ms": 1689048705826,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689049005825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689049305825,
                    "call_count": 0,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689049605824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689049905830,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689050205825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689050505825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689050805825,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689051105827,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689051405825,
                    "call_count": 0,
                    "cpu_percent": 55
                },
                {
                    "time_ms": 1689051705827,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689052005827,
                    "call_count": 0,
                    "cpu_percent": 13
                },
                {
                    "time_ms": 1689052305827,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689052605824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689052905825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689053205825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689053505826,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689053805824,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689054105827,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689054405825,
                    "call_count": 0,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689054705825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689055005825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689055305824,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689055605824,
                    "call_count": 0,
                    "cpu_percent": 17
                },
                {
                    "time_ms": 1689055905825,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689056205824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689056505825,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689056805826,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689057105825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689057405825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689057705825,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689058005824,
                    "call_count": 0,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689058305824,
                    "call_count": 0,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689058605825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689058905826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689059205827,
                    "call_count": 0,
                    "cpu_percent": 20
                },
                {
                    "time_ms": 1689059505825,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689059805826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689060105826,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689060405827,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689060705828,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689061005827,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689061305825,
                    "call_count": 0,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689061605825,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689061905825,
                    "call_count": 0,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689062205825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689062505825,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689062805825,
                    "call_count": 0,
                    "cpu_percent": 17
                },
                {
                    "time_ms": 1689063105824,
                    "call_count": 0,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689063405824,
                    "call_count": 0,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689063705827,
                    "call_count": 3,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689064005829,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689064305828,
                    "call_count": 1,
                    "cpu_percent": 11
                },
                {
                    "time_ms": 1689064605827,
                    "call_count": 1,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689064905826,
                    "call_count": 1,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689065205826,
                    "call_count": 1,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689065505825,
                    "call_count": 9,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689065805825,
                    "call_count": 9,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689066105826,
                    "call_count": 4,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689066405827,
                    "call_count": 1,
                    "cpu_percent": 20
                },
                {
                    "time_ms": 1689066705827,
                    "call_count": 1,
                    "cpu_percent": 25
                },
                {
                    "time_ms": 1689067005825,
                    "call_count": 3,
                    "cpu_percent": 3
                },
                {
                    "time_ms": 1689067305826,
                    "call_count": 1,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689067605826,
                    "call_count": 2,
                    "cpu_percent": 31
                },
                {
                    "time_ms": 1689067905825,
                    "call_count": 7,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689068205825,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689068505825,
                    "call_count": 1,
                    "cpu_percent": 11
                },
                {
                    "time_ms": 1689068805825,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689069105826,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689069405826,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689069705825,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689070005825,
                    "call_count": 1,
                    "cpu_percent": 20
                },
                {
                    "time_ms": 1689070305825,
                    "call_count": 1,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689070605824,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689070905825,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689071205826,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689071505826,
                    "call_count": 1,
                    "cpu_percent": 11
                },
                {
                    "time_ms": 1689071805826,
                    "call_count": 2,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689072105828,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689072405826,
                    "call_count": 1,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689072705827,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689073005825,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689073305825,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689073605826,
                    "call_count": 1,
                    "cpu_percent": 22
                },
                {
                    "time_ms": 1689073905826,
                    "call_count": 1,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689074205826,
                    "call_count": 1,
                    "cpu_percent": 11
                },
                {
                    "time_ms": 1689074505826,
                    "call_count": 1,
                    "cpu_percent": 9
                },
                {
                    "time_ms": 1689074805825,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689075105826,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689075405826,
                    "call_count": 1,
                    "cpu_percent": 20
                },
                {
                    "time_ms": 1689075705825,
                    "call_count": 1,
                    "cpu_percent": 19
                },
                {
                    "time_ms": 1689076005828,
                    "call_count": 1,
                    "cpu_percent": 12
                },
                {
                    "time_ms": 1689076305825,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689076605827,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689076905825,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689077205826,
                    "call_count": 1,
                    "cpu_percent": 20
                },
                {
                    "time_ms": 1689077505826,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689077805825,
                    "call_count": 1,
                    "cpu_percent": 4
                },
                {
                    "time_ms": 1689078105826,
                    "call_count": 1,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689078405826,
                    "call_count": 1,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689078705826,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689079005827,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689079305826,
                    "call_count": 1,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689079605825,
                    "call_count": 1,
                    "cpu_percent": 24
                },
                {
                    "time_ms": 1689079905826,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689080205826,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689080505835,
                    "call_count": 1,
                    "cpu_percent": 5
                },
                {
                    "time_ms": 1689080805825,
                    "call_count": 1,
                    "cpu_percent": 23
                },
                {
                    "time_ms": 1689081366954,
                    "call_count": 0,
                    "cpu_percent": 75
                },
                {
                    "time_ms": 1689081666937,
                    "call_count": 1,
                    "cpu_percent": 18
                },
                {
                    "time_ms": 1689081966932,
                    "call_count": 1,
                    "cpu_percent": 17
                },
                {
                    "time_ms": 1689082266935,
                    "call_count": 5,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689082566932,
                    "call_count": 2,
                    "cpu_percent": 10
                },
                {
                    "time_ms": 1689082866930,
                    "call_count": 1,
                    "cpu_percent": 7
                },
                {
                    "time_ms": 1689083166930,
                    "call_count": 1,
                    "cpu_percent": 12
                },
                {
                    "time_ms": 1689083466931,
                    "call_count": 5,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689083766930,
                    "call_count": 9,
                    "cpu_percent": 6
                },
                {
                    "time_ms": 1689084066930,
                    "call_count": 1,
                    "cpu_percent": 8
                },
                {
                    "time_ms": 1689084366931,
                    "call_count": 4,
                    "cpu_percent": 10
                }
            ]
        },
        "call_frequency_timeline_one_week": {
            "call_frequency_points": [
                {
                    "time_ms": 1688598000012,
                    "call_count": 493
                },
                {
                    "time_ms": 1688641200007,
                    "call_count": 522
                },
                {
                    "time_ms": 1688684400015,
                    "call_count": 37
                },
                {
                    "time_ms": 1688727600000,
                    "call_count": 0
                },
                {
                    "time_ms": 1688770800007,
                    "call_count": 0
                },
                {
                    "time_ms": 1688814000013,
                    "call_count": 0
                },
                {
                    "time_ms": 1688857200001,
                    "call_count": 0
                },
                {
                    "time_ms": 1688900399999,
                    "call_count": 0
                },
                {
                    "time_ms": 1688943600000,
                    "call_count": 0
                },
                {
                    "time_ms": 1688986799999,
                    "call_count": 0
                },
                {
                    "time_ms": 1689029999999,
                    "call_count": 0
                },
                {
                    "time_ms": 1689073200000,
                    "call_count": 63
                }
            ]
        }
    }
    server_log_level = {
        "server_logging_level": "WARN",
        "restapi_logging_enabled": False}
    snmp = {
        "engine_id": "0x800004730193b22ab2000000",
        "snmp_traps": [
            {
                "id": "56910fe4-9c69-3100-a493-ff9455acc02d",
                "name": "10.60.1.1",
                "port": 162,
                "snmp_version": "v1"
            }]}
    # Serviceability Data
    serviceability_symmetrix = {'symmetrixId': ['000197800128']}
    ntp_server = {'ntp_server': '10.10.10.10'}
    ip_configuration = {'natone_ip_address_ipv4': '10.10.10.10',
                        'natone_netmask_ipv4': '255.255.255.0',
                        'natone_gateway_ipv4': '10.10.10.10',
                        'nattwo_ip_address_ipv4': '10.10.10.10',
                        'nattwo_netmask_ipv4': '255.255.255.0',
                        'nattwo_gateway_ipv4': '10.10.10.10',
                        'natone_ip_address_ipv6': '0:0:0:0:0:0:0:0',
                        'natone_prefix_ipv6': 0,
                        'natone_gateway_ipv6': '0:0:0:0:0:0:0:0',
                        'nattwo_ip_address_ipv6': '0:0:0:0:0:0:0:0',
                        'nattwo_prefix_ipv6': 0,
                        'nattwo_gateway_ipv6': '0:0:0:0:0:0:0:0'}
    applications = [{'application_id': 'solutions_enabler',
                     'application_name': 'Solutions Enabler'},
                    {'application_id': 'unisphere',
                     'application_name': 'Unisphere for PowerMax'},
                    {'application_id': 'vasa',
                     'application_name': 'VASA Provider'}]
    unisphere_application = {'access_id': ' 35000538-000000-34626637\n',
                             'guest_name': 'Unisphere-0',
                             'node_name': 'MGMT-0',
                             'server_access': 'allow',
                             'status': 'Running',
                             'version': '10.1.0623.5'}
    unisphere_configuration = {
        'se_base_configuration': {
            'general_symapi_options': {
                'symapi_gns_mirrored_group_control': 'Enable',
                'symapi_use_access_id': 'Client'},
            'se_base_configuration_errors': {
                'configuration_errors': ['2023-08-19T18:41:22.6495--NIL--NIL']
            }
        },
        'se_service_configuration': {
            'service_storevntd': {'log_level': 'Verbose',
                                  'logfile_retention': 50,
                                  'log_event_syslog_host': '',
                                  'log_event_syslog_port': 0},
            'service_storgnsd': {'gns_device_poll_interval': 201,
                                 'gns_ppath_poll_interval': 200,
                                 'gns_remote_mirror': 'Disable',
                                 'gns_rmtarr_update_interval': 200,
                                 'log_level': 'Verbose',
                                 'logfile_retention': 50},
            'se_service_configuration_errors': {
                'configuration_errors':
                    ['2023-08-19T18:41:22.624613--NIL--NIL']}}}
    available_symms_response = {'symm_avoid_list': ['000220200000'],
                                'symm_list': ['000297900000', '000297900000']}
    vasa_application = {
        'vasa_applications': [
            {'guest_name': 'VASA-0',
             'node_name': 'SERVICEA-0',
             'status': 'Running',
             'ecom_url': 'https://10.10.10.10:5989/config',
             'url': 'https://10.60.141.235:5989/vasa-providers.xml'},
            {'guest_name': 'VASA-1',
             'node_name': 'SERVICEA-1',
             'status': 'Running',
             'ecom_url': 'https://10.60.10.10:5989/ECOMConfig',
             'url': 'https://10.60.141.236:5989/vasa-providers.xml'},
            {'guest_name': 'VASA-DB-0',
             'node_name': 'SERVICEA-0',
             'status': 'Running'}],
        'version': '10.1.0.54 (Release, Build 54, 2023-06-23 11:44:38)',
        'access_id': '65333164-34633766-63366434'}
    vasa_provider = {'retain_vp_cert': 'FALSE',
                     'running_status': 'Running',
                     'symapi_debug_log': 'DISABLED',
                     'vp_log_file_size_mb': '64',
                     'vp_log_level': 'INFO',
                     'vp_max_connection_per_session': '8',
                     'vp_num_of_files_to_be_retained': '10'}
    vasa_0 = 'VASA-0'
    solutions_enabler_application = {
        'se_applications': [{'guest_name': 'SE-MGMT-0',
                             'node_name': 'MGMT-0',
                             'status': 'Running'},
                            {'guest_name': 'SE-MGMT-1',
                             'node_name': 'MGMT-1',
                             'status': 'Running'}],
        'version': '10.1.0.167 (Beta, Build 2751, 2023-06-28 23:50:07)',
        'access_id': '35343564-31656461-36373464',
        'se_nethost': [{'node_name': '', 'user': ''}]}
    solutions_enabler_configuration = {'se_base_configuration': {
        'general_symapi_options': {
            'SYMAPI_APPREG_EXPIRATION_PERIOD': 90,
            'SYMAPI_ALLOW_CG_ENABLE_FROM_R2': 'Enable',
            'SYMAPI_ALLOW_RDF_SYMFORCE': False,
            'SYMAPI_CG_TIMEOUT': 30,
            'SYMAPI_CLONE_COPY_ON_WRITE': 'Disable',
            'SYMAPI_COMMAND_SCOPE': 'Disable',
            'SYMAPI_DEFAULT_RDF_MODE': 'Acp',
            'SYMAPI_GNS_MIRRORED_GROUP_CONTROL': 'Disable',
            'SYMAPI_POOL_DRAIN_THRESHOLD': 90,
            'SYMAPI_RCOPY_GET_MODIFIED_TRACKS': False,
            'SYMAPI_RDF_CHECK_R2_NOT_WRITABLE': 'Disable',
            'SYMAPI_RDF_CREATEPAIR_LARGER_R2': 'Enable',
            'SYMAPI_RDF_RW_DISABLE_R2': 'Disable',
            'SYMAPI_SNAP_COUNT_MODIFIED_TRACKS': False,
            'SYMAPI_TF_COUNT_MODIFIED_TRACKS': False,
            'SYMAPI_USE_ACCESS_ID': 'Server'
        },
        'se_base_configuration_errors': {
            'configuration_errors': ['2023-08-19T20:18:03.387143--NIL--NIL']}},
        'se_service_configuration': {
            'service_storgnsd': {
                'gns_device_poll_interval': 15,
                'gns_ppath_poll_interval': 60,
                'gns_remote_mirror': 'Disable',
                'gns_rmtarr_update_interval': 60,
                'log_level': 'Warning',
                'logfile_retention': 3},
            'service_storsrvd': {
                'log_level': 'Info',
                'logfile_retention': 3,
                'log_filter': 'SESSION+APIREQ',
                'security_clt_secure_lvl': 'Noverify',
                'max_sessions': 100,
                'max_sessions_per_host': 0,
                'security_cert_allow_wildcards': 'Disable'},
            'se_service_configuration_errors': {
                'configuration_errors': [
                    '2023-08-19T20:18:03.387491--NIL--NIL']}}}
    self_signed_cert_response = {
        'message': 'Successfully generated selfsigned certificate '
                   'for Solutions Enabler in : Semgmt0 .',
        'node_displayname': 'SE-MGMT-0', 'success': True}
    import_certs_response = {
        'success': True,
        'message': 'Solutions Enabler custom certificate '
                   'successfully updated in node SE-MGMT-1!!'
    }

    seconfig_reference_payload = {'se_base_configuration': {
        'general_symapi_options': {'SYMAPI_USE_ACCESS_ID': 'CLIENT'}}}

    se_nethost_reference_empty = {'se_applications': [
        {'guest_name': 'SE-MGMT-0', 'node_name': 'MGMT-0',
         'status': 'Running'},
        {'guest_name': 'SE-MGMT-1', 'node_name': 'MGMT-1',
         'status': 'Running'}],
        'version': '10.1.0.148 (Beta, Build 2751, 2023-06-16 23:24:45)',
        'access_id': '63323335-37656265-36393334',
        'se_nethost': [
            {'node_name': '', 'user': ''}]}
