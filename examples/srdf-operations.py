# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
"""docs/source/programmers_guide_src/code/srdf-operations.py"""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()
REMOTE_ARRAY = '000297900111'

# --- RDF Director & Port Discovery ---

# List all RDF directors on the local array
directors = conn.srdf.get_rdf_director_list()
print(f'RDF Directors: {directors}')

# Get details for a specific RDF director
if directors:
    director_detail = conn.srdf.get_rdf_director_detail(directors[0])
    print(f'Director {directors[0]}: {director_detail}')

    # List ports on the director
    ports = conn.srdf.get_rdf_director_port_list(directors[0])
    print(f'Ports on {directors[0]}: {ports}')

    # Get port details
    if ports:
        port_detail = conn.srdf.get_rdf_director_port_details(
            directors[0], ports[0])
        print(f'Port detail: {port_detail}')

        # Scan for remote connections (run after zoning is configured)
        remote = conn.srdf.get_rdf_port_remote_connections(
            directors[0], ports[0])
        print(f'Remote connections: {remote}')

# --- RDF Group Management ---

# List all RDF groups
rdf_groups = conn.srdf.get_rdf_group_list()
print(f'RDF Groups: {rdf_groups}')

# List RDF groups filtered by remote array
rdf_groups_filtered = conn.srdf.get_rdf_group_list(
    remote_symmetrix_id=REMOTE_ARRAY)
print(f'RDF Groups to {REMOTE_ARRAY}: {rdf_groups_filtered}')

# Get details for a specific RDF group
if rdf_groups:
    rdf_detail = conn.srdf.get_rdf_group(rdf_groups[0]['rdfgNumber'])
    print(f'RDF Group detail: {rdf_detail}')

# Look up an RDF group number by its label
rdfg_number = conn.srdf.get_rdf_group_number('my_rdfg_label')
print(f'RDFG number for label: {rdfg_number}')

# List volumes in an RDF group
if rdf_groups:
    vol_list = conn.srdf.get_rdf_group_volume_list(
        rdf_groups[0]['rdfgNumber'])
    print(f'Volumes in RDFG: {vol_list}')

# --- Storage Group SRDF Protection ---

# Create a storage group with volumes
storage_group = conn.provisioning.create_non_empty_storage_group(
    srp_id='SRP_1', storage_group_id='PyU4V_SRDF_SG',
    service_level='Diamond', workload=None, num_vols=2,
    vol_size=1, cap_unit='GB')
sg_id = storage_group['storageGroupId']

# Protect the storage group with SRDF Synchronous replication
conn.srdf.create_storage_group_srdf_pairings(
    storage_group_id=sg_id, remote_sid=REMOTE_ARRAY,
    srdf_mode='Synchronous', establish=True, _async=True)
print(f'SRDF pairing created for {sg_id}')

# List SRDF groups for the storage group
srdf_groups = conn.srdf.get_storage_group_srdf_group_list(sg_id)
print(f'SRDF groups for {sg_id}: {srdf_groups}')

# Get SRDF details for the storage group
if srdf_groups:
    srdf_detail = conn.srdf.get_storage_group_srdf_details(
        sg_id, srdf_groups[0])
    print(f'SRDF state: {srdf_detail}')

# --- SRDF State Management ---

if srdf_groups:
    rdfg = srdf_groups[0]

    # Suspend SRDF replication
    conn.srdf.suspend_storage_group_srdf(sg_id, rdfg)
    print('SRDF suspended')

    # Resume/Establish SRDF replication
    conn.srdf.establish_storage_group_srdf(sg_id, rdfg)
    print('SRDF re-established')

    # Failover to the remote array
    conn.srdf.failover_storage_group_srdf(sg_id, rdfg)
    print('SRDF failover complete')

    # Failback to the local array
    conn.srdf.failback_storage_group_srdf(sg_id, rdfg)
    print('SRDF failback complete')

    # Change SRDF mode to Asynchronous
    conn.srdf.modify_storage_group_srdf(
        sg_id, 'SetMode', rdfg,
        options={'setMode': {'mode': 'Asynchronous'}})
    print('SRDF mode changed to Asynchronous')

    # Delete SRDF pairings
    conn.srdf.delete_storage_group_srdf(sg_id, rdfg)
    print('SRDF pairings deleted')

# Check if two volumes are RDF paired
paired, local_state, pair_state = conn.srdf.are_volumes_rdf_paired(
    remote_array=REMOTE_ARRAY, device_id='00001',
    target_device='00001', rdf_group=1)
print(f'Paired: {paired}, State: {local_state}, Pair: {pair_state}')

# Close the session
conn.close_session()
