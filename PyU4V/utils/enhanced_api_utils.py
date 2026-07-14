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
"""Private helpers shared by enhanced REST API wrappers."""


def _build_select_clause(metadata, select, exclude):
    """Build a selection clause without changing caller-owned lists."""
    excluded = ['rdf_infos', 'snapshots'] if exclude is None else exclude
    selected = list(select) if select else []

    if not selected:
        selected = [
            attribute['name'] for attribute in metadata
            if attribute['name'] not in excluded
        ]

    return ','.join(selected)
