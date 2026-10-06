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
"""Configure OpenTelemetry metrics export from Unisphere."""

import PyU4V

# Initialise a PyU4V connection to Unisphere.
conn = PyU4V.U4VConn()

# Inspect the current endpoint and per-array registration settings.
endpoint = conn.system.get_otel_endpoint_settings()
registration = conn.system.get_otel_registration()
print(endpoint)
print(registration)

# Register a gRPC collector endpoint. Port 4317 is the standard OTLP/gRPC
# port; use the address and port configured for your collector.
conn.system.register_otel_endpoint(
    address='otel-collector.example.com',
    port=4317,
    protocol='gRPC',
    enable_compression=False)

# Update the endpoint, in this case enabling gzip payload compression.
conn.system.update_otel_endpoint(
    address='otel-collector.example.com',
    port=4317,
    protocol='gRPC',
    enable_compression=True)

# Enable metrics export for the connection's primary array. Include another
# entry for each additional array whose export setting must be updated.
conn.system.update_otel_registration(registration_details=[
    {'system_id': conn.array_id, 'export_metrics': True},
    {'system_id': '000111222333', 'export_metrics': False}
])

# Confirm the applied settings.
print(conn.system.get_otel_endpoint_settings())
print(conn.system.get_otel_registration())

# Delete the collector endpoint when metrics export is no longer required.
conn.system.delete_otel_endpoint()

conn.close_session()
