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
"""pyu4v_performance_data.py."""


class PerformanceData(object):
    """Performance data."""

    first_date = 1555777200000
    last_date = 1587399600000

    perf_metrics_resp = {'resultList': {
        'result': [{'PercentBusy': 0.025403459, 'timestamp': first_date},
                   {'PercentBusy': 0.027849833, 'timestamp': last_date}],
        'from': 1, 'to': 2}, 'count': 2, 'expirationTime': last_date,
        'id': 'c2c3a5bd-5bed-41b2-be7c-24376496bc73_0', 'maxPageSize': 1000}

    director_info = {'directorId': 'test'}

    array = '000197800123'
    remote_array = '000197800124'
    array_keys_empty = {'arrayInfo': []}
    array_keys = {'arrayInfo': [{'symmetrixId': array,
                                 'firstAvailableDate': first_date,
                                 'lastAvailableDate': last_date}]}
    array_reg_details_enabled = {'registrationDetailsInfo': [{
        'symmetrixId': array, 'realtime': True, 'collectionintervalmins': 5,
        'diagnostic': True, 'message': 'Success'}]}
    array_reg_details_disabled = {'registrationDetailsInfo': [{
        'symmetrixId': array, 'realtime': False, 'collectionintervalmins': 0,
        'diagnostic': False, 'message': 'Success'}]}

    be_dir_id = 'DF-1C'
    be_dir_keys = {'beDirectorInfo': [{'directorId': be_dir_id,
                                       'firstAvailableDate': first_date,
                                       'lastAvailableDate': last_date}]}

    be_emu_id = 'DF-2C:2:11'
    be_emu_keys = {'beEmulationInfo': [{'beEmulationId': be_emu_id,
                                        'firstAvailableDate': first_date,
                                        'lastAvailableDate': last_date}]}

    be_port_id = '12'
    be_port_keys = {'bePortInfo': [{'portId': be_port_id,
                                    'firstAvailableDate': first_date,
                                    'lastAvailableDate': last_date}]}

    board_id = '1'
    board_keys = {'boardInfo': [{'boardId': board_id,
                                 'firstAvailableDate': first_date,
                                 'lastAvailableDate': last_date}]}

    cache_part_id = 'test_partition'
    cache_partition_keys = {
        'cachePartitionInfo': [{'cachePartitionId': cache_part_id,
                                'firstAvailableDate': first_date,
                                'lastAvailableDate': last_date}]}

    core_id = '1:0'
    core_keys = {'coreInfo': [{'coreId': core_id,
                               'firstAvailableDate': first_date,
                               'lastAvailableDate': last_date}]}

    database_id = 'my_test_db'
    database_keys = {'databaseInfo': [{'databaseId': database_id,
                                       'firstAvailableDate': first_date,
                                       'lastAvailableDate': last_date}]}

    db_pool_id = 'DG1_F_F'
    database_by_pool_keys = {'databaseByPoolInfo': [{
        'poolId': db_pool_id, 'firstAvailableDate': first_date,
        'lastAvailableDate': last_date}]}

    device_group_id = '526'
    device_group_keys = {'deviceGroupInfo': [{'deviceGroupId': device_group_id,
                                              'firstAvailableDate': first_date,
                                              'lastAvailableDate': last_date}]}

    disk_id = '0'
    disk_keys = {'diskInfo': [{'diskId': disk_id,
                               'firstAvailableDate': first_date,
                               'lastAvailableDate': last_date}]}

    disk_group_id = '0'
    disk_group_keys = {'diskGroupInfo': [{'diskGroupId': disk_group_id,
                                          'firstAvailableDate': first_date,
                                          'lastAvailableDate': last_date}]}
    disk_technology = 'EFD'
    disk_tech_pool_keys = {'diskTechPoolInfo': [{
        'diskTechnology': disk_technology, 'firstAvailableDate': first_date,
        'lastAvailableDate': last_date}]}

    eds_dir_id = 'ED-1B'
    eds_dir_keys = {'edsDirectorInfo': [{'directorId': eds_dir_id,
                                         'firstAvailableDate': first_date,
                                         'lastAvailableDate': last_date}]}

    eds_emu_id = 'ED-1B:1:29'
    eds_emu_keys = {'edsEmulationInfo': [{'edsEmulationId': eds_emu_id,
                                          'firstAvailableDate': first_date,
                                          'lastAvailableDate': last_date}]}
    ext_dir_id = 'ED-1G'
    ext_dir_keys = {'externalDirectorInfo': [{'directorId': ext_dir_id,
                                              'firstAvailableDate': first_date,
                                              'lastAvailableDate': last_date}]}

    ext_disk_id = '5'
    external_disk_id = {'externalDiskInfo': [{'diskId': ext_disk_id,
                                              'firstAvailableDate': first_date,
                                              'lastAvailableDate': last_date}]}

    ext_disk_group_id = '512'
    ext_disk_group_keys = {'externalDiskGroupInfo': [{
        'diskGroupId': ext_disk_group_id, 'firstAvailableDate': first_date,
        'lastAvailableDate': last_date}]}

    fe_dir_id = 'FA-1D'
    se_dir_id = 'SE-4E'
    fe_dir_keys = {'feDirectorInfo': [{'directorId': fe_dir_id,
                                       'firstAvailableDate': first_date,
                                       'lastAvailableDate': last_date}]}

    fe_emu_id = 'FA-4D:4:66'
    fe_emu_keys = {'feEmulationInfo': [{'feEmulationId': fe_emu_id,
                                        'firstAvailableDate': first_date,
                                        'lastAvailableDate': last_date}]}

    fe_port_id = '4'
    fe_port_keys = {'fePortInfo': [{'portId': fe_port_id,
                                    'firstAvailableDate': first_date,
                                    'lastAvailableDate': last_date}]}

    ficon_emu_id = 'EF-2E:2'
    ficon_emu_keys = {'ficonEmulationInfo': [{'ficonEmulationId': ficon_emu_id,
                                              'firstAvailableDate': first_date,
                                              'lastAvailableDate': last_date}]}

    ficon_emu_thread_id = 'EF-2E:2:0'
    ficon_emu_thread_keys = {'ficonEmulationThreadInfo': [{
        'ficonEmulationThreadId': ficon_emu_thread_id,
        'firstAvailableDate': first_date, 'lastAvailableDate': last_date}]}

    ficon_port_thread_id = 'EF-2E:2:10'
    ficon_port_thread_keys = {'ficonPortThreadInfo': [{
        'ficonPortThreadId': ficon_port_thread_id,
        'firstAvailableDate': first_date, 'lastAvailableDate': last_date}]}

    host_id = 'test_host'
    host_keys = {'hostInfo': [{'hostId': host_id,
                               'firstAvailableDate': first_date,
                               'lastAvailableDate': last_date}]}

    im_dir_id = 'IM-1A'
    im_dir_keys = {'imDirectorInfo': [{'directorId': im_dir_id,
                                       'firstAvailableDate': first_date,
                                       'lastAvailableDate': last_date}]}

    im_emu_id = 'IM-2A:2:0'
    im_emu_keys = {'iMEmulationInfo': [{'imEmulationId': im_emu_id,
                                        'firstAvailableDate': first_date,
                                        'lastAvailableDate': last_date}]}

    init_id = '10000090fa141c10'
    init_keys = {'initiatorInfo': [{'initiatorId': init_id,
                                    'firstAvailableDate': first_date,
                                    'lastAvailableDate': last_date}]}

    init_by_port_id = 'FA-1D:5:100000109b1b8ede'
    init_by_port_keys = {'initiatorByPortInfo': [{
        'initiatorByPortId': init_by_port_id, 'firstAvailableDate': first_date,
        'lastAvailableDate': last_date}]}

    ip_interface_id = 'SE-3E:8:17:192.168.0.70'
    ip_interface_keys = {'iSCSIClientInfo': [{'ipInterfaceId': ip_interface_id,
                                              'firstAvailableDate': first_date,
                                              'lastAvailableDate': last_date}]}

    iscsi_target_id = 'iqn.1992-04.com.emc:60000'
    iscsi_target_keys = {'iSCSITargetInfo': [{'iSCSITargetId': iscsi_target_id,
                                              'firstAvailableDate': first_date,
                                              'lastAvailableDate': last_date}]}

    port_group_id = 'test-pg'
    port_group_keys = {'portGroupInfo': [{'portGroupId': port_group_id,
                                          'firstAvailableDate': first_date,
                                          'lastAvailableDate': last_date}]}

    rdfa_group_id = '11'
    rdfa_keys = {'rdfaInfo': [{'raGroupId': rdfa_group_id,
                               'firstAvailableDate': first_date,
                               'lastAvailableDate': last_date}]}

    rdfs_group_id = '11'
    rdfs_keys = {'rdfsInfo': [{'raGroupId': rdfs_group_id,
                               'firstAvailableDate': first_date,
                               'lastAvailableDate': last_date}]}

    rdf_dir_id = 'RF-1F'
    rdf_dir_keys = {'rdfDirectorInfo': [{'directorId': rdf_dir_id,
                                         'firstAvailableDate': first_date,
                                         'lastAvailableDate': last_date}]}

    rdf_emu_id = 'RF-3F:3:68'
    rdf_emu_keys = {'rdfEmulationInfo': [{'rdfEmulationId': rdf_emu_id,
                                          'firstAvailableDate': first_date,
                                          'lastAvailableDate': last_date}]}

    rdf_port_id = '7'
    rdf_port_keys = {'rdfPortInfo': [{'portId': rdf_port_id,
                                      'firstAvailableDate': first_date,
                                      'lastAvailableDate': last_date}]}

    storage_container_id = 'test_container_1'
    storage_container_keys = {'storageContainerInfo': [{
        'storageContainerId': storage_container_id,
        'firstAvailableDate': first_date, 'lastAvailableDate': last_date}]}

    storage_group_id = 'test_sg'
    storage_group_keys = {'storageGroupInfo': [{
        'storageGroupId': storage_group_id, 'firstAvailableDate': first_date,
        'lastAvailableDate': last_date}]}

    storage_group_by_pool_id = 'test-pool'
    storage_group_by_pool_keys = {'poolInfo': [{
        'poolId': 'test-pool', 'firstAvailableDate': first_date,
        'lastAvailableDate': last_date}]}

    srp_id = 'SRP_1'
    srp_keys = {'srpInfo': [{'srpId': srp_id,
                             'firstAvailableDate': first_date,
                             'lastAvailableDate': last_date}]}

    storage_resource_id = 'storage_resource_1'
    storage_resource_keys = {'storageResourceInfo': [{
        'storageResourceId': storage_resource_id,
        'firstAvailableDate': first_date, 'lastAvailableDate': last_date}]}

    storage_resource_by_pool_id = 'DG1_F_7'
    storage_resource_by_pool_keys = {'poolInfo': [{
        'poolId': storage_resource_by_pool_id,
        'firstAvailableDate': first_date, 'lastAvailableDate': last_date}]}

    thin_pool_id = 'test_thin_pool'
    thin_pool_keys = {'poolInfo': [{'poolId': thin_pool_id,
                                    'firstAvailableDate': first_date,
                                    'lastAvailableDate': last_date}]}

    # Threshold
    threshold_cat_resp = {'endpoint': ['Array']}
    threshold_settings_resp = {
        'category': 'Array', 'num_of_metric_performance_thresholds': 2,
        'success': 'False', 'performanceThreshold': [
            {'metric': 'ResponseTime', 'kpi': 'True', 'alertError': 'False',
             'firstThreshold': 20, 'secondThreshold': 30},
            {'metric': 'HostMBWritten', 'kpi': 'False', 'alertError': 'False',
             'firstThreshold': 0, 'secondThreshold': 0}]}

    # Days to full
    days_to_full_resp = {'daysToFullObjectResultType': [{
        'ProjectionDaysToFull': 181.0, 'PercentUsedCapacity': 0.17,
        'TotalPoolCapacityGB': 62590.0, 'instanceId': array}]}
