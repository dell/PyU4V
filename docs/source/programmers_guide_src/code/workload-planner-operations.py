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
"""docs/source/programmers_guide_src/code/workload-planner-operations.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# List workload planner eligible authorized systems
wlp_systems = conn.wlp.get_system_list()
print('WLP systems: {s}'.format(s=wlp_systems))

# Get workload planner processing details for the active array
wlp_system_details = conn.wlp.get_system(array_id=conn.array_id)
print('WLP system details: {d}'.format(d=wlp_system_details))

# List workload planner eligible storage groups
wlp_storage_groups = conn.wlp.get_storage_group_list(array_id=conn.array_id)
print('WLP storage groups: {sgs}'.format(sgs=wlp_storage_groups))

if wlp_storage_groups:
    # Get workload planner performance and planning details for a
    # storage group
    storage_group_details = conn.wlp.get_storage_group(
        storage_group_id=wlp_storage_groups[0], array_id=conn.array_id)
    print('WLP storage group details: {d}'.format(d=storage_group_details))

# Query headroom and utilization
headroom = conn.wlp.get_headroom(
    array_id=conn.array_id, srp='SRP_1', slo='Diamond', emulation='FBA')
print('Headroom: {h}'.format(h=headroom))

utilization = conn.wlp.get_utilization(
    array_id=conn.array_id, bucket='0', back_end_only=True)
print('Utilization: {u}'.format(u=utilization))

# Query compliance history
compliance = conn.wlp.get_compliance_history(array_id=conn.array_id)
print('Compliance history: {c}'.format(c=compliance))

# Provisioning template list, details, and creation
templates = conn.wlp.get_provisioning_template_list()
print('Provisioning templates: {t}'.format(t=templates))
if templates:
    template_details = conn.wlp.get_provisioning_template(
        template_id=templates[0])
    print('Template details: {d}'.format(d=template_details))

if wlp_storage_groups:
    new_template = conn.wlp.create_provisioning_template(
        symmetrix_id=conn.array_id, storage_group_id=wlp_storage_groups[0],
        template_id='example-template', response_time_target=0.8,
        volume_attribute={'capacityUnit': 'GB', 'volumeSize': 10})
    print('Created template: {t}'.format(t=new_template))

    # Update the template's response time target
    conn.wlp.update_provisioning_template(
        template_id='example-template', response_time_target=1.0)

    # Delete the template once it is no longer required
    conn.wlp.delete_provisioning_template(template_id='example-template')

# Test the performance impact of migrating a storage group to this array
impact_result = conn.wlp.test_performance_impact(
    migration_impact_param={
        'source_symmetrix_id': conn.array_id,
        'source_storage_group_id': 'example-sg'
    },
    auto_resolve_conflicts=False, details=True)
print('Performance impact: {i}'.format(i=impact_result))

# Close the session
conn.close_session()
