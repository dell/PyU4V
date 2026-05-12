# PyU4V Change Log

## Version 10.5

### Sphinx Documentation Audit & Fixes

#### Build-Breaking Fixes
- Fixed toctree filename mismatch in `programmers_guide.rst` — reference used hyphen (`enhanced_bulk-api_calls`) but file uses underscore (`enhanced_bulk_api_calls`)
- Fixed missing blank line after `.. code-block:: python` directive in `quick_start.rst` causing content to not render as code
- Fixed broken RST bold markup in `index.rst` version table (`**Minimum Unisphere Version*` → `**Minimum Unisphere Version**`)
- Fixed title underline too short for `PyU4V.settings` section in `PyU4V.rst`
- Fixed multiple `literalinclude` line ranges that exceeded file length in `clone.rst`, `enhanced_bulk_api_calls.rst`, `serviceability.rst`, `settings.rst`, `volumes_storage_groups.rst`

#### Docstring Fixes (Sphinx Warning Elimination)
- Fixed docstring formatting in `settings.py` — added blank lines after summaries, fixed `:param` syntax, corrected sample payload formatting for `update_performance_thresholds_and_alerts`, `update_alert_notifications`, `update_alert_policies`, `update_performance_registration_settings`
- Fixed docstring in `system.py` `configure_ldap_authentication` — added blank line after summary, fixed missing colons in `:param` directives
- Fixed docstring in `rest_requests.py` `file_transfer_request` — added blank lines, fixed `:raises:` continuation indentation
- Fixed `get_alert_policies` indentation misalignment in `syslog_notifications` param

#### Version & Content Updates
- Updated copyright year from 2022 to 2025 in `conf.py`
- Updated Python version notes to include 3.11 & 3.12 in `index.rst` and `installation.rst`
- Updated outdated Unisphere version references (`V9.1.0.5` → `V10.5.0.0`, `V10.2.0.0` → `V10.5.0.0`) in `quick_start.rst`, `configuration.rst`
- Updated `pip install` version from `10.4.0.0` to `10.5.0.0` in `installation.rst`
- Updated compatibility statement from `10.4.0.0` to `10.5.0.0` in `installation.rst`
- Updated API docs URL from `10.2` to `10.5` in `quick_start.rst`
- Fixed typo `Unipshere` → `Unisphere` in `index.rst` and `quick_start.rst`
- Fixed outdated GitHub links (`MichaelMcAleer/PyU4V` → `Dell/PyU4V`) in `tools.rst` and `recommendations.rst`
- Fixed invalid Python syntax in `contribute.rst` example (`raise Exception` in ternary → `False`)
- Added missing convention #4 (import ordering) in `contribute.rst`

#### New Programmer's Guide Examples
- Added migration operations example (`migration-operations.py`) with full migration lifecycle
- Added serviceability operations example (`serviceability-operations.py`) with NTP and GRAB log operations
- Added settings operations example (`settings-operations.py`) with performance registration, SCG, and CloudIQ
- Added volumes & storage groups example (`volumes-storage_groups.py`) with metadata queries, filtering, and selection
- Created corresponding RST guide pages: `migration.rst`, `serviceability.rst`, `settings.rst`, `volumes_storage_groups.rst`
- Added new sections to `programmers_guide.rst` toctree
- Copied example files to top-level `examples/` directory

#### API Documentation Completeness
- Added missing `PyU4V.utils.utils`, `PyU4V.utils.performance_constants`, and `PyU4V.utils.performance_category_map` modules to `PyU4V.utils.rst`
- Fixed `enhanced_api.py` docstring referencing wrong filename
- Added license header and fixed comments in `restoreclone.py`

#### Copyright Year Update
- Updated all copyright headers from 2019-2025 to 2026 across all project source files (~120 `.py` files), `conf.py`, `__init__.py`, and `setup.py`

#### Result
- Sphinx build now completes with **zero warnings** (`-W` flag passes)

### Dependency Cleanup

#### Removed Unnecessary Packages
- Removed standalone `mock` package from `tox.ini` (`[testenv]` and `[testenv:ci]`) and `setup.py` `tests_require` — all test files already use `unittest.mock` (Python stdlib since 3.3)
- Removed unused `pytest` from `tox.ini` test deps — test runner is `stestr`; `pytest` was listed but never invoked
- Moved `prettytable` from `install_requires` to `extras_require={'tools': ['prettytable']}` in `setup.py` — only used by the OpenStack migration utility in `tools/`, not by the core library; install via `pip install pyu4v[tools]`
- Updated `Requirements` table in `README.rst`, `index.rst`, `docs/source/index.rst`, and `docs/source/installation.rst` to reflect core deps only (`requests`, `urllib3`)

### Dependency Removal: `six`

#### Python 3 Native Compatibility
- Removed `six` package dependency from the codebase — PyU4V targets Python 3.6+ exclusively and has no need for the Python 2/3 compatibility shim
- Replaced `six.text_type(x)` with `str(x)` in `PyU4V/common.py`, `PyU4V/utils/exception.py`, and `PyU4V/tests/unit_tests/test_pyu4v_utils.py`
- Removed `import six` from all three affected modules
- Removed `six` from `install_requires` in `setup.py`
- Removed `six` from `requirements.txt`
- Removed `Six_` reference and link from `README.rst`, `index.rst`, `docs/source/index.rst`, and `docs/source/installation.rst`

### Unit Test Updates

#### Test Suite Refactoring
- Updated unit test assertions in provisioning, replication, migration, metro_dr, and snapshot_policy test suites to use `target_uri` parameter instead of legacy `category`, `resource_level`, `resource_type` parameters
- Updated mock patch targets from module-level aliases (e.g., `self.provisioning`) to direct common method calls (e.g., `self.provisioning.common`)
- Fixed missed alias in replication.py: `self.delete_resource` → `self.common.delete_resource`
- All 318 modified unit tests pass successfully

### Version Management Consolidation

#### Single Source of Truth
- Made `PyU4V/version.py` the single source of truth for version information
- Deleted duplicate `pyu4v_version.py` file from root directory
- Updated `setup.py` to read version dynamically from `PyU4V/version.py` using a helper function
- Deleted `setup_template.py` as it's no longer needed
- Updated `docs/source/conf.py` to import `MAJOR_VERSION` and `VERSION` from `PyU4V.version` instead of hardcoding

#### Template and Script Removal
- Deleted template files: `README_template.rst`, `index_template.rst`, `docs/source/installation_template.rst`, `docs/source/index_template.rst`
- Deleted `PyU4V/scripts/replace_version.py` script as template-based version replacement is no longer needed
- Generated output files (`README.rst`, `index.rst`, `docs/source/installation.rst`, `docs/source/index.rst`) now maintained directly

#### API Version Validation
- Enhanced `validate_unisphere()` in `univmax_conn.py` to validate user-specified `u4v_version` against server's `supported_api_versions`
- When `custom_api_version` is True, PyU4V now calls `common.get_uni_version_info()` and checks if the specified version is supported
- If the specified version is not supported, PyU4V exits with a clear error message listing supported versions
- This ensures backward compatibility while preventing connection failures due to unsupported API versions

#### Configuration and Documentation
- Updated `PyU4V.conf.example` to document the `u4v_version` configuration option with usage examples
- Added "API Version Configuration" section to `README.rst` explaining how to use `u4v_version` for backward compatibility
- Documented usage examples: `conn = PyU4V.U4VConn(u4v_version='100')` and `conn.set_u4v_version('101')`

#### Version Bump Workflow
- To bump versions, now edit only `PyU4V/version.py` and manually update version strings in `README.rst` and doc `.rst` files
- No script or template workflow required

---

## Version 10.4

### Performance Enhanced Module Improvements

#### performance_enhanced.py
- Extracted `_build_filter_query()` static helper to remove duplicated filter-building logic (DRY)
- Extracted `_perf_uri()` private helper to centralise URI construction across all methods
- Replaced misplaced triple-quoted block comments with idiomatic `#` comments
- Removed unused shortcut attributes (`get_resource`, `create_resource`, `modify_resource`, `delete_resource`) from `__init__`
- Removed legacy `(object)` from class definition (Python 3 style)
- All public method signatures and return values remain unchanged for backward compatibility

### Authentication Enhancements

#### rest_requests.py
- Added Bearer token support for authentication (api_key parameter), requires 
  Microsoft Entra ID or OKTA to be configured, API key is passed as a Bearer 
  token and obtained from Entra ID or OKTA
- Added `_apply_auth_to_headers()` helper method to manage Authorization 
  headers
- Modified `establish_rest_session()` to support both Basic auth and Bearer 
  token auth
- Improved error handling for authentication scenarios

#### replication.py
- Added `remote_storage_group` parameter to `create_storage_group_srdf_pairings`, this allows for different naming of remote storage group

#### univmax_conn.py
- Added API key authentication support as alternative to username/password
- Added `set_u4v_version()` method to dynamically update Unisphere API version
- Added `u4v_version` configuration option from config file
- Modified `validate_unisphere()` to skip minimum version check when custom version is specified
- Improved version propagation across all REST clients and CommonFunctions

### Version Management Improvements
- Changed from `self.version` to `self.common.UNI_VERSION` throughout codebase for consistent version handling
- Updated `settings.py`, `serviceability.py`, and `system.py` to use `self.common.UNI_VERSION`
- Improved version handling in URI construction across all modules

### Deprecated Functions Removed

#### performance.py
- Removed `generate_threshold_settings_csv()` function (deprecated in favor of settings module)
- Removed `set_thresholds_from_csv()` function (deprecated in favor of settings module)
- Users should explore API calls in the new settings module for threshold management

### Code Cleanup
- Removed blank lines in docstrings throughout common.py for cleaner code
- Improved code formatting and consistency across modules
- Minor refactoring for better code maintainability

---

## Version 10.3
- setup.py changed name to normalized pyu4v per PEP 625
- Added enhanced_api functions
- Updated performance_enhanced.py to accept filters new in 10.3
- Added keepR1 and KeepR2 parameters to `modify_rdf_group` function in replication.py

---

## Version 10.2.0.3
- replication.py: `create_storage_group_srdf_pairings` `force_new_rdfg` parameter made defunct as was removed from API, will be ignored if specified and warning logged

---

## Version 10.2.0.1
- metro_dr.py: Added support to specify r2_rdfg on convert
- Updated versioning to be more automatic, version only needs to be updated in version.py

---

## Version 10.2.0.0

#### metro_dr.py
- Added Reverse flag to PUT payload
- Added WLP Flags to storage group create and modify functions
- IP Storage configuration Library

#### replication.py
- Added bothsides option to `create_storage_group_snapshot` function

#### system.py
- Added `configure_ldap_authentication`
- Added `get_ldap_configuration`

#### provisioning.py
- Added `reset_volume_wwn` function and tests

#### performance.py
- BugFix: Added `includeRealTimeTraceOnCritical` Key to update performance thresholds payload and parameters

---

### Deprecated functions removed in v10.2

Please ensure if you are using any of these functions please ensure you have updated your code to use the replacement function. These functions have been marked for depreciation for previous 2 releases and will have provided a warning error during that time to update.

- **Removed** `PyU4V.performance.get_cloud_provider_keys` and `get_cloud_provider_stats`

- **Old:** `PyU4V.performance.is_array_performance_registered`  
  **New:** `PyU4V.performance.is_array_diagnostic_performance_registered`

- **Old:** `PyU4V.performance.get_iscsi_target_keys`  
  **New:** `PyU4V.performance.get_endpoint_keys`

- **Old:** `PyU4V.performance.get_iscsi_target_stats`  
  **New:** `PyU4V.performance.get_endpoint_stats`

- **Old:** `PyU4V.performance.PerformanceFunctions.get_iscsi_target_stats`  
  **New:** `PyU4V.performance.PerformanceFunctions.get_endpoint_stats`

- **Old:** `PyU4V.performance.PerformanceFunctions.get_iscsi_target_keys`  
  **New:** `PyU4V.performance.PerformanceFunctions.get_endpoint_keys`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director`  
  **New:** `PyU4V.system.SystemFunctions.get_director`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director_list`  
  **New:** `PyU4V.system.SystemFunctions.get_director_list`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director_port`  
  **New:** `PyU4V.system.SystemFunctions.get_director_port`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director_port_list`  
  **New:** `PyU4V.system.SystemFunctions.get_director_port_list`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_port_identifier`  
  **New:** `PyU4V.system.SystemFunctions.get_port_identifier`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_fa_directors`  
  **New:** `PyU4V.system.SystemFunctions.get_fa_directors`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_iscsi_ip_address_and_iqn`  
  **New:** `PyU4V.system.SystemFunctions.get_iscsi_ip_address_and_iqn`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_any_director_port`  
  **New:** `PyU4V.system.SystemFunctions.get_any_director_port`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.create_multiport_port_group`  
  **New:** `PyU4V.provisioning.ProvisioningFunctions.create_new_port_group`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.create_port_group`  
  **New:** `PyU4V.provisioning.ProvisioningFunctions.create_new_port_group`

---

## Version 10.1.0.2 and backport to Version 10.0.0.20
- Added timeout parameter to connection to make configurable. PyU4V.conf also can take new setup value for timeout to override 120s value

---

## Version 10.1.0.1
- Bug fix for Github Issue #174: `restart_unisphere_application` has wrong payload

---

## Version 10.1.0.0

### Documentation updates
- Changed constants file to reflect migration resource changed to mobility
- Added volumes.py
- Added storage
- Added performance_enhanced

### system.py
New functions added:
- `get_management_server_resources`
- `refresh_array_details`
- `set_server_logging_level`
- `get_server_logging_level`
- `update_snmp_trap_destination`
- `delete_snmp_trap_destination`
- `set_snmp_trap_destination`
- `get_snmp_trap_configuration`

### replication.py
- Added force options to delete snapshot functions
- New function `bulk_terminate_snapshots`
- Added new query filters to `get_replication_enabled_storage_groups`, now returns cloud snapshots or linked sg in list if specified

### provisioning.py
- Added `starting_lun_address` param to specify the LUN address to use as a starting point for volumes in a SG when creating a Masking View
- Added to functions:
  - `add_new_volume_to_storage_group`
  - `add_existing_volume_to_storage_group`
  - `create_masking_view_existing_components`
- Added terminate snapshots option to `remove_volume_from_storage_group`

### serviceability.py
Added functions:
- `get_local_symmetrix`
- `get_symmetrix_ntp_server`
- `modify_ntp_server`
- `download_serviceability_log`
- `get_ip_configuration`
- `update_ip_configuration`
- `get_application`
- `get_unisphere_application`
- `modify_unisphere_application`
- `restart_unisphere_application`
- `get_unisphere_configuration`
- `modify_unisphere_configuration`
- `get_symavoid_settings`
- `update_symavoid_settings`
- `get_solutions_enabler_application`
- `get_solutions_enabler_configuration`
- `get_solutions_enabler_system`
- `import_custom_certificate`
- `replace_self_signed_certificate`

### Performance
- Added to `enable_real_time_data_collection` to be able to register for file, and storage groups for realtime collection

---

## Version 10.0.0.19
- Documentation update to include additional examples
- system.py: Added `set_port_protocol`

---

## Version 10.0.0.19 (continued)
- Added clone functions
- Added proxy Support
- Removed test `test_format_time_input_no_end`

---

## Version 10.0.0.17

### performance.py
- Added `get_volume_stats` - ability to get performance stats from volume level with PyU4V

---

## Version 10.0.0.0 (released 10/19/2022)

### Added Functionality 10.0

#### Provisioning.py
- Allow for a different Emulation Type for storage group and volume creation
- Added `create_empty_port_group` function

#### Download audit log record
- Download audit log record and take longer than the default 120 seconds
- Now timeout is configurable so this can be increase or decreased at will

#### Replication.py
- `get_rdf_group_list` updated to add new search params to simplify workflows for RDFG operations
- `modify_storage_group_snapshot_by_snapid` added force and remote options
- `get_storage_group_replication_details` updated with new filter options to simplify workflows

---

### Deprecated functions to be removed in 10.2

These functions will been removed entirely from the PyU4V code-base after the required two release notification period.

- **Old:** `PyU4V.performance.PerformanceFunctions.get_iscsi_target_stats`  
  **New:** `PyU4V.performance.PerformanceFunctions.get_endpoint_stats`

- **Old:** `PyU4V.performance.PerformanceFunctions.get_iscsi_target_keys`  
  **New:** `PyU4V.performance.PerformanceFunctions.get_endpoint_keys`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director`  
  **New:** `PyU4V.system.SystemFunctions.get_director`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director_list`  
  **New:** `PyU4V.system.SystemFunctions.get_director_list`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director_port`  
  **New:** `PyU4V.system.SystemFunctions.get_director_port`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_director_port_list`  
  **New:** `PyU4V.system.SystemFunctions.get_director_port_list`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_port_identifier`  
  **New:** `PyU4V.system.SystemFunctions.get_port_identifier`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_fa_directors`  
  **New:** `PyU4V.system.SystemFunctions.get_fa_directors`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_iscsi_ip_address_and_iqn`  
  **New:** `PyU4V.system.SystemFunctions.get_iscsi_ip_address_and_iqn`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.get_any_director_port`  
  **New:** `PyU4V.system.SystemFunctions.get_any_director_port`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.create_multiport_port_group`  
  **New:** `PyU4V.provisioning.ProvisioningFunctions.create_new_port_group`

- **Old:** `PyU4V.provisioning.ProvisioningFunctions.create_port_group`  
  **New:** `PyU4V.provisioning.ProvisioningFunctions.create_new_port_group`

---

### Create port group
- `port_group_protocol` required in request payload for a create port group operation. Values are one of SCSI_FC, iSCSI, NVMe_TCP

---

### Real-Time Performance
- The following functions have been updated to accept an array_id to accommodate differences between V3/V4 systems:
  - `PyU4V.real_time.RealTimeFunctions.get_categories()`
  - `PyU4V.real_time.RealTimeFunctions.get_category_metrics()`

---

### Diagnostic Performance

#### Cloud Provider
- `PyU4V.performance.PerformanceFunctions.get_cloud_provider_keys()`
- `PyU4V.performance.PerformanceFunctions.get_cloud_provider_stats()`

#### EM Directors
- `PyU4V.performance.PerformanceFunctions.get_em_director_keys()`
- `PyU4V.performance.PerformanceFunctions.get_em_director_stats()`

#### SDNAS
- `PyU4V.performance.PerformanceFunctions.get_sdnas_filesystem_keys()`
- `PyU4V.performance.PerformanceFunctions.get_sdnas_filesystem_stats()`
- `PyU4V.performance.PerformanceFunctions.get_sdnas_interface_keys()`
- `PyU4V.performance.PerformanceFunctions.get_sdnas_interface_stats()`
- `PyU4V.performance.PerformanceFunctions.get_sdnas_node_keys()`
- `PyU4V.performance.PerformanceFunctions.get_sdnas_node_stats()`
- `PyU4V.performance.PerformanceFunctions.get_sdnas_server_keys()`
- `PyU4V.performance.PerformanceFunctions.get_sdnas_server_stats()`

#### zHyperLinkPorts
- `PyU4V.performance.PerformanceFunctions.get_zhyperlink_port_keys()`
- `PyU4V.performance.PerformanceFunctions.get_zhyperlink_port_stats()`

#### Performance Updates
- Attribute added to PerformanceFunctions() for is_v4 array
- `PerformanceFunctions.get_performance_categories_list()` has been changed to retrieve categories via Unisphere REST endpoint instead of hard coded category map
- `PerformanceFunctions.get_performance_metrics_list()` has been changed to retrieve metrics via Unisphere REST endpoint instead of hard coded metric map
- Performance category/metric map for diagnostic performance endpoints has been removed entirely in favour of REST endpoints. Categories and metrics are still obtained through the same functions, the underlying data retrieval is the only thing to change
- `PerformanceFunctions.get_threshold_categories()` now accepts an array_id to accommodated difference in categories between V3/V4 systems
- `PerformanceFunctions.get_threshold_category_settings()` now accepts an array_id to accommodated difference in categories between V3/V4 systems
- When generating threshold CSV files from `PerformanceFunctions.generate_threshold_settings_csv` it is now possible to set category as an input value to limit the CSV threshold to only that category
- CI tests for thresholds have been updated to target a default threshold marked as KPI to ensure it has both first and second threshold values populated before the test runs
- Removed trailing white space from performance metrics in the metric map

---

### System Changes
- `SystemFunctions.get_audit_log_record()` has been updated to extract audit log record details after changes were made to Unisphere REST responses. What is returned to the user from PyU4V will not change
- Added `set_director_port_online` function

---

### CI Test Improvements
- Performance CI tests will output dead metrics to screen when encountered instead of just failing and moving on
- Array performance CI tests have been improved to provide better coverage of all metrics and reporting of dead metrics
- Certain tests are skipped if they are version specific and CI array does not meet required version (V3/V4)

---

### Building URI with args deprecated
This functionality as provided by `PyU4V.common.CommonFunctions._build_uri_args` has been marked for deprecation since PyU4V 9.1 and has been fully removed in the 10.0 release. The impact of this is such that the following methods must be called with kwargs or specify target uri to form target URIs if you are using them for access to custom REST endpoints:
- `PyU4V.common.CommonFunctions.get_resource`
- `PyU4V.common.CommonFunctions.create_resource`
- `PyU4V.common.CommonFunctions.modify_resource`
- `PyU4V.common.CommonFunctions.delete_resource`

---

### Deprecated functions removed from code-base

These functions have been removed entirely from the PyU4V code-base after the required two release notification period.

#### common.py
- `PyU4V.common.CommonFunctions._build_uri_args`

#### performance.py
- `PyU4V.performance.PerformanceFunctions.get_fe_port_util_last4hrs`
- `PyU4V.performance.PerformanceFunctions.get_all_fe_director_metrics`
- `PyU4V.performance.PerformanceFunctions.get_director_info`

#### replication.py
- `PyU4V.replication.ReplicationFunctions.choose_snapshot_from_list_in_console`

#### utils/console.py
- Entire file removed, PyU4V will not provide console level functionality moving forward. Please handle this outside of PyU4V if it is required

---

### Refactored functions removed from code-base in favour of other functions

These refactored functions take the format of:
- Refactored (removed) function → New function to target

#### common.py
- `PyU4V.common.CommonFunctions.create_list_from_file` → `PyU4V.utils.file_handler.create_list_from_file`
- `PyU4V.common.CommonFunctions.read_csv_values` → `PyU4V.utils.file_handler.read_csv_values`
- `PyU4V.common.CommonFunctions.get_wlp_information` → `PyU4V.workload_planner.WLPFunctions.get_wlp_information`
- `PyU4V.common.CommonFunctions.get_headroom` → `PyU4V.workload_planner.WLPFunctions.get_headroom`

#### performance.py
- `PyU4V.performance.PerformanceFunctions.get_perf_threshold_categories` → `PyU4V.performance.PerformanceFunctions.get_threshold_categories`
- `PyU4V.performance.PerformanceFunctions.get_perf_category_threshold_settings` → `PyU4V.performance.PerformanceFunctions.get_threshold_category_settings`
- `PyU4V.performance.PerformanceFunctions.set_perf_threshold_and_alert` → `PyU4V.performance.PerformanceFunctions.update_threshold`
- `PyU4V.performance.PerformanceFunctions.set_perfthresholds_csv` → `PyU4V.performance.PerformanceFunctions.set_thresholds_from_csv`
- `PyU4V.performance.PerformanceFunctions.get_fe_director_list` → `PyU4V.performance.PerformanceFunctions.get_frontend_director_keys`
- `PyU4V.performance.PerformanceFunctions.get_fe_port_list` → `PyU4V.performance.PerformanceFunctions.get_frontend_port_keys`
- `PyU4V.performance.PerformanceFunctions.get_fe_director_metrics` → `PyU4V.performance.PerformanceFunctions.get_frontend_director_stats`
- `PyU4V.performance.PerformanceFunctions.get_fe_port_metrics` → `PyU4V.performance.PerformanceFunctions.get_frontend_port_stats`
- `PyU4V.performance.PerformanceFunctions.get_array_metrics` → `PyU4V.performance.PerformanceFunctions.get_array_stats`
- `PyU4V.performance.PerformanceFunctions.get_storage_group_metrics` → `PyU4V.performance.PerformanceFunctions.get_storage_group_stats`
- `PyU4V.performance.PerformanceFunctions.get_port_group_metrics` → `PyU4V.performance.PerformanceFunctions.get_port_group_stats`
- `PyU4V.performance.PerformanceFunctions.get_host_metrics` → `PyU4V.performance.PerformanceFunctions.get_host_stats`

#### provisioning.py
- `PyU4V.provisioning.ProvisioningFunctions.get_mvs_from_host` → `PyU4V.provisioning.ProvisioningFunctions.get_masking_views_from_host`
- `PyU4V.provisioning.ProvisioningFunctions.get_hostgroup` → `PyU4V.provisioning.ProvisioningFunctions.get_host_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_hostgroup_list` → `PyU4V.provisioning.ProvisioningFunctions.get_host_group_list`
- `PyU4V.provisioning.ProvisioningFunctions.create_hostgroup` → `PyU4V.provisioning.ProvisioningFunctions.create_host_group`
- `PyU4V.provisioning.ProvisioningFunctions.modify_hostgroup` → `PyU4V.provisioning.ProvisioningFunctions.modify_host_group`
- `PyU4V.provisioning.ProvisioningFunctions.delete_hostgroup` → `PyU4V.provisioning.ProvisioningFunctions.delete_host_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_masking_views_by_host` → `PyU4V.provisioning.ProvisioningFunctions.get_masking_views_by_initiator_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_common_masking_views` → `PyU4V.provisioning.ProvisioningFunctions.get_port_group_common_masking_views`
- `PyU4V.provisioning.ProvisioningFunctions.get_host_from_maskingview` → `PyU4V.provisioning.ProvisioningFunctions.get_host_from_masking_view`
- `PyU4V.provisioning.ProvisioningFunctions.get_storagegroup_from_maskingview` → `PyU4V.provisioning.ProvisioningFunctions.get_storage_group_from_masking_view`
- `PyU4V.provisioning.ProvisioningFunctions.get_portgroup_from_maskingview` → `PyU4V.provisioning.ProvisioningFunctions.get_port_group_from_masking_view`
- `PyU4V.provisioning.ProvisioningFunctions.get_maskingview_connections` → `PyU4V.provisioning.ProvisioningFunctions.get_masking_view_connections`
- `PyU4V.provisioning.ProvisioningFunctions.find_host_lun_id_for_vol` → `PyU4V.provisioning.ProvisioningFunctions.find_host_lun_id_for_volume`
- `PyU4V.provisioning.ProvisioningFunctions.get_portgroup` → `PyU4V.provisioning.ProvisioningFunctions.get_port_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_portgroup_list` → `PyU4V.provisioning.ProvisioningFunctions.get_port_group_list`
- `PyU4V.provisioning.ProvisioningFunctions.get_ports_from_pg` → `PyU4V.provisioning.ProvisioningFunctions.get_ports_from_port_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_target_wwns_from_pg` → `PyU4V.provisioning.ProvisioningFunctions.get_target_wwns_from_port_group`
- `PyU4V.provisioning.ProvisioningFunctions.create_portgroup` → `PyU4V.provisioning.ProvisioningFunctions.create_port_group`
- `PyU4V.provisioning.ProvisioningFunctions.create_multiport_portgroup` → `PyU4V.provisioning.ProvisioningFunctions.create_multiport_port_group`
- `PyU4V.provisioning.ProvisioningFunctions.create_portgroup_from_file` → `PyU4V.provisioning.ProvisioningFunctions.create_port_group_from_file`
- `PyU4V.provisioning.ProvisioningFunctions.modify_portgroup` → `PyU4V.provisioning.ProvisioningFunctions.modify_port_group`
- `PyU4V.provisioning.ProvisioningFunctions.delete_portgroup` → `PyU4V.provisioning.ProvisioningFunctions.delete_port_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_slo_list` → `PyU4V.provisioning.ProvisioningFunctions.get_service_level_list`
- `PyU4V.provisioning.ProvisioningFunctions.get_slo` → `PyU4V.provisioning.ProvisioningFunctions.get_service_level`
- `PyU4V.provisioning.ProvisioningFunctions.modify_slo` → `PyU4V.provisioning.ProvisioningFunctions.modify_service_level`
- `PyU4V.provisioning.ProvisioningFunctions.get_mv_from_sg` → `PyU4V.provisioning.ProvisioningFunctions.get_masking_view_from_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_num_vols_in_sg` → `PyU4V.provisioning.ProvisioningFunctions.get_num_vols_in_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.is_child_sg_in_parent_sg` → `PyU4V.provisioning.ProvisioningFunctions.is_child_storage_group_in_parent_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_child_sg_from_parent` → `PyU4V.provisioning.ProvisioningFunctions.get_child_storage_groups_from_parent`
- `PyU4V.provisioning.ProvisioningFunctions.create_non_empty_storagegroup` → `PyU4V.provisioning.ProvisioningFunctions.create_non_empty_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.create_empty_sg` → `PyU4V.provisioning.ProvisioningFunctions.create_empty_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.add_existing_vol_to_sg` → `PyU4V.provisioning.ProvisioningFunctions.add_existing_volume_to_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.add_new_vol_to_storagegroup` → `PyU4V.provisioning.ProvisioningFunctions.add_new_volume_to_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.remove_vol_from_storagegroup` → `PyU4V.provisioning.ProvisioningFunctions.remove_volume_from_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.create_volume_from_sg_return_dev_id` → `PyU4V.provisioning.ProvisioningFunctions.create_volume_from_storage_group_return_id`
- `PyU4V.provisioning.ProvisioningFunctions.add_child_sg_to_parent_sg` → `PyU4V.provisioning.ProvisioningFunctions.add_child_storage_group_to_parent_group`
- `PyU4V.provisioning.ProvisioningFunctions.remove_child_sg_from_parent_sg` → `PyU4V.provisioning.ProvisioningFunctions.remove_child_storage_group_from_parent_group`
- `PyU4V.provisioning.ProvisioningFunctions.update_storagegroup_qos` → `PyU4V.provisioning.ProvisioningFunctions.update_storage_group_qos`
- `PyU4V.provisioning.ProvisioningFunctions.delete_storagegroup` → `PyU4V.provisioning.ProvisioningFunctions.delete_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_vol_effective_wwn_details_84` → `PyU4V.provisioning.ProvisioningFunctions.get_volume_effective_wwn_details`
- `PyU4V.provisioning.ProvisioningFunctions.get_vols_from_storagegroup` → `PyU4V.provisioning.ProvisioningFunctions.get_volumes_from_storage_group`
- `PyU4V.provisioning.ProvisioningFunctions.get_storagegroup_from_vol` → `PyU4V.provisioning.ProvisioningFunctions.get_storage_group_from_volume`
- `PyU4V.provisioning.ProvisioningFunctions.is_volume_in_storagegroup` → `PyU4V.provisioning.ProvisioningFunctions.is_volume_in_storage_group`

#### replication.py
- `PyU4V.replication.ReplicationFunctions.get_storage_group_rep` → `PyU4V.replication.ReplicationFunctions.get_storage_group_replication_details`
- `PyU4V.replication.ReplicationFunctions.get_storage_group_rep_list` → `PyU4V.replication.ReplicationFunctions.get_replication_enabled_storage_groups`
- `PyU4V.replication.ReplicationFunctions.get_storagegroup_snapshot_list` → `PyU4V.replication.ReplicationFunctions.get_storage_group_snapshot_list`
- `PyU4V.replication.ReplicationFunctions.create_storagegroup_snap` → `PyU4V.replication.ReplicationFunctions.create_storage_group_snapshot`
- `PyU4V.replication.ReplicationFunctions.get_storagegroup_snapshot_generation_list` → `PyU4V.replication.ReplicationFunctions.get_storage_group_snapshot_generation_list`
- `PyU4V.replication.ReplicationFunctions.modify_storagegroup_snap` → `PyU4V.replication.ReplicationFunctions.modify_storage_group_snapshot`
- `PyU4V.replication.ReplicationFunctions.delete_storagegroup_snapshot` → `PyU4V.replication.ReplicationFunctions.delete_storage_group_snapshot`
- `PyU4V.replication.ReplicationFunctions.is_vol_in_rep_session` → `PyU4V.replication.ReplicationFunctions.is_volume_in_replication_session`
- `PyU4V.replication.ReplicationFunctions.are_vols_rdf_paired` → `PyU4V.replication.ReplicationFunctions.are_volumes_rdf_paired`
- `PyU4V.replication.ReplicationFunctions.get_storagegroup_srdfg_list` → `PyU4V.replication.ReplicationFunctions.get_storage_group_srdf_group_list`
- `PyU4V.replication.ReplicationFunctions.get_storagegroup_srdf_details` → `PyU4V.replication.ReplicationFunctions.get_storage_group_srdf_details`
- `PyU4V.replication.ReplicationFunctions.create_storagegroup_srdf_pairings` → `PyU4V.replication.ReplicationFunctions.create_storage_group_srdf_pairings`
- `PyU4V.replication.ReplicationFunctions.modify_storagegroup_srdf` → `PyU4V.replication.ReplicationFunctions.modify_storage_group_srdf`
- `PyU4V.replication.ReplicationFunctions.suspend_storagegroup_srdf` → `PyU4V.replication.ReplicationFunctions.suspend_storage_group_srdf`
- `PyU4V.replication.ReplicationFunctions.establish_storagegroup_srdf` → `PyU4V.replication.ReplicationFunctions.establish_storage_group_srdf`
- `PyU4V.replication.ReplicationFunctions.failover_storagegroup_srdf` → `PyU4V.replication.ReplicationFunctions.failover_storage_group_srdf`
- `PyU4V.replication.ReplicationFunctions.failback_storagegroup_srdf` → `PyU4V.replication.ReplicationFunctions.failback_storage_group_srdf`
- `PyU4V.replication.ReplicationFunctions.delete_storagegroup_srdf` → `PyU4V.replication.ReplicationFunctions.delete_storage_group_srdf`

---

## Version 9.2.1.4
- Added enable/disable consistency feature to `modify_storage_group_srdf` function in replication
- Updated `add_existing_volume_to_storage_group` to create RDF pairings
- Made srdfg number mandatory in `delete_storage_group_srdf`, added filters options, removed unit test `test_delete_storagegroup_srdf_no_number`
- Updated constants file `ISCSI_IQN_SEARCH_PATTERN = ('^iqn.\\d{1,4}-\\d{2}.(?:com|org).\\w{1,}:(?:\\d{2}:)*'[0-9a-fA-F]{1,32}$||.[0-9A-Fa-f]{16}')` added test to ci_utils.py `test_iscsi_regex`
- Added relink to `modify_storage_group_snapshot` and `modify_storage_group_snapshot_snapsetid`

---

## Version 9.2.1.3
- Added enable_mobility id to provisioning functions `create_storage_group`, `add_new_volume_to_storage_group`, `create_volume_from_storage_group_return_id`
- Added `get_snapshot_policy_storage_group_list` to snapshot policy functions

---

## Version 9.2.1.2 (released 08/03/21)
- Support for changing local users passwords via REST, requires Unisphere 9.2.1
- Added `change_local_user_password` function

---

## Version 9.2.1.1 (released 15/02/21)
- Support for Snapshot Policy compliance
- Refactoring of snapshot policy modification by operation

---

## Version 9.2.0.8 (released 05/02/21)
- Update `__init__.py` to reflect the correct version
- Update the docs to reflect new version

---

## Version 9.2.0.7 (released 03/02/21)
- Fix for Python 3.9.1
- Fix for exception in `get_storage_group_snapshot_list` if no snapshot exists
- CI fix of `test_is_volume_in_replication_session`
- Upgrade of pep8
- Addition of .gitattributes for unix LF checkin only
- New default parameter for get metro DR details

---

## Version 9.2.0.5 (released 18/12/20)
- Fix for system CI test to select only FE/SE/BE/RDF director:
  - `PyU4V.tests.ci_tests.test_pyu4v_ci_system.CITestSystem.test_get_director_port_list`
  - New optional parameter `snapshot_policy_ids` in `create_non_empty_storage_group` and `create_empty_storage_group`

---

## Version 9.2.0.4 (released 9/12/20)
- Fix for metro_dr delete function
- Fix for metro_dr added recover option
- Fix for CI tests:
  - `PyU4V.tests.ci_tests.test_pyu4v_ci_system.CITestSystem._test_get_health_check_details`
  - `PyU4V.tests.ci_tests.test_pyu4v_ci_system.CITestSystem.test_get_ip_interface_list`
  - `PyU4V.tests.ci_tests.test_pyu4v_ci_system.CITestSystem.test_get_ip_interface`
- Added Force Option to metro dr restore
- Application-Type header is now set by default to 'PyU4V-{version}'

---

## Version 9.2.0.3 (released 7/12/20)

### Masking View performance support has been added to performance.py
- `PyU4V.performance.PerformanceFunctions.get_masking_view_keys`
- `PyU4V.performance.PerformanceFunctions.get_masking_view_stats`

### Director list, Port list, IP interface list, and get IP interface details have been added to system.py
- `PyU4V.system.SystemFunctions.get_director_list`
- `PyU4V.system.SystemFunctions.get_director_port_list`
- `PyU4V.system.SystemFunctions.get_ip_interface_list`
- `PyU4V.system.SystemFunctions.get_ip_interface`

### Array storage level details are now available via provisioning.py
- `PyU4V.provisioning.ProvisioningFunctions.get_array`

### Array level WLP capabilities are now accessible in workload_planner.py
- `PyU4V.workload_planner.WLPFunctions.get_capabilities`

### array_id is now an optional parameter for the following functions
- `PyU4V.replication.ReplicationFunctions.get_array_replication_capabilities`
- `PyU4V.migration.MigrationFunctions.get_migration_info`
- `PyU4V.migration.MigrationFunctions.get_array_migration_capabilities`

---

## Version 9.2.0.2 (released 14/10/20)
- When generating threshold CSV files from `PerformanceFunctions.generate_threshold_settings_csv` it is now possible to set category as an input value to limit the CSV threshold file to only that performance category
- CI tests for thresholds have been updated to target a default threshold marked as KPI to ensure it has both first and second threshold values populated before the test runs
- Removed trailing white space from two performance metrics in the metric map, 'BEDisk ReadResponseTime ' is now 'BEDiskReadResponseTime' in diagnostic category 'DeviceGroup', and, 'BEReadRequestTime ' is now 'BEReadRequestTime' in category 'StorageContainer'

---

## Version 9.2.0.1 (released 12/10/20)
- Tighten base CI tests around RDF group creation and deletion
- Update Unisphere minimum version to reflect 9.2 GA Unisphere version

---

## Version 9.2.0.0 (released 29/09/20)

### Snap id Support
Functions added:
- `get_storage_group_snapshot_snap_id_list`
- `get_snapshot_snap_id_details`
- `find_expired_snapvx_snapshots_by_snap_ids`
- `modify_storage_group_snapshot_by_snap_id`
- `restore_snapshot_by_snap_id`
- `rename_snapshot_by_snap_id`
- `link_snapshot_by_snap_id`
- `unlink_snapshot_by_snap_id`
- `delete_storage_group_snapshot_by_snap_id`

### Snapshot Policy Functions
Functions added:
- `get_snapshot_policy_list`
- `get_snapshot_policy`
- `create_snapshot_policy`
- `modify_snapshot_policy`
- `delete_snapshot_policy`

Functions modified:
- `create_storage_group`

### System Enhancements
- Users can now export (download) and import (upload) both Unisphere and array system settings combined or individually using system calls. Settings can be written to a zip file or returned to the caller function as binary data so file writing can be handled outside of PyU4V or uploaded directly to Unisphere without the need for file handling. Users can call the following system functions for settings download/upload:
  - `download_all_settings()`
  - `download_unisphere_settings()`
  - `download_system_settings()`
  - `upload_settings()`
- Users can retrieve array audit logs from PyU4V for specified time ranges, obtain information about specific audit logs, or export an audit log to .pdf document locally
- Support for alerts has now been included, users can get alert summary, detailed info, acknowledge and delete alerts

### Replication
Functions modified:
- `get_rdf_group()` now has the ability to take array_id as an input param

### Metro DR
Functions added:
- `create_metrodr_environment`
- `delete_metrodr_environment`
- `modify_metrodr_environment`
- `convert_to_metrodr_environment`

### Performance (Diagnostic)
Functions added:
- `is_array_diagnostic_performance_registered`
- `is_array_real_time_performance_registered`
- `get_array_registration_details`
- `enable_diagnostic_data_collection`
- `disable_diagnostic_data_collection`
- `enable_real_time_data_collection`
- `disable_real_time_data_collection`
- `backup_performance_database`

Functions marked for deprecation:
- `is_array_performance_registered` in favour of `is_array_diagnostic_performance_registered`

### Removed Categories
- Core
- Disk
- Disk Technology Pool
- External Director
- External Disk Group
- Initiator by Port
- Storage Group by Pool
- Storage Resource by Pool

### Performance (Real-time)
- Users now have access to Unisphere real-time performance functions. These calls are accessed through PyU4V.performance.real_time. All Unisphere for PowerMax real-time categories and metrics are supported

### Documentation
- Code examples have been moved to docs/source/programmers_guide_src/code for ease of reference in main documentation
- Programmers Guide Examples section has been re-structured for ease of navigation

### Miscellaneous
- PyLint has been updated to 2.6.0 in test suite
- Deprecation/refactoring notices have been updated from 9.3 to 10.0 where applicable
- Add long description to setup.py for PyPi
- Fix short description in setup.py for PyPi
- Change url to reflect move to dell GitHub repo in setup.py for PyPi
- Add supported Python versions 3.8 & 3.9
- Docstring kwargs have been updated with ":key [param]:" where applicable
- Minimum Unisphere version has been updated to v9.2.0.0

---

## Version 9.1.5.0 (released 21/09/20)

### Bug fixes
- Fixed a bug in performance CI tests where tests would fail if there was no provisioned assets in certain performance categories. The tests will skip now instead of failing

---

## Version 9.1.4.0 (released 09/09/20)

### Bug Fixes
- GitHub Issue #93 (https://github.com/dell/PyU4V/issues/93) has been resolved. Users can now create storage groups with volumes in the same request where no service level has been specified as an input parameter or service level is set to None. In addition, another bug found whilst fixing #93 whereby storage groups with no service level set were created with no storage resource pool regardless of user input parameter value
- GitHub Issue #92 (https://github.com/dell/PyU4V/issues/92) has been resolved. User documentation has been updated to correct the error in the path to set a custom PyU4V.conf location

### Version Control
- Pep8 test suite flake8 package version has been upgraded to 3.8.3
- Pylint test suite package version has been upgraded to 2.5.3

### Quality Control
- The change to Pylint version resulted in more stringent code analysis, as such a number of changes were made in the following files to bring the code rating back up to 10.0/10.0:
  - PyU4V/common.py
  - PyU4V/performance.py
  - PyU4V/provisioning.py
  - PyU4V/tools/openstack/migrate_utils.py

---

## Version 9.1.3.0 (released 19/01/20)

### Replication Enhancements

#### RDF functions added
- `create_rdf_group`
- `modify_rdf_group`
- `delete_rdf_group`
- `get_rdf_port_connections`
- `get_rdf_director_port_details`
- `get_rdf_director_ports`
- `get_rdf_director`
- `get_rdf_director_list`
- `create_storage_group_from_rdfg`

### BugFix
- Update to rest_requests header parameter corrected to application-type line 54

---

## Version 9.1.2.0 (released 19/12/19)

### Provisioning Enhancements
- `add_new_volume_to_storage_group`: Added functionality to be able to add volumes to SRDF protected storage groups, new volumes will automatically be protected with SRDF, volumes are added to the remote storage group to fully automate the provisioning and simplify operations. Storage group must be local to the unisphere instance and only works with storage groups that contain R1 or R11 devices
- `remove_volume_from_storage_group`: Enhanced to be able to automatically remove volumes from local and remote storage groups deleting srdf pairs as part of the process, no need to suspend, the automation takes care of everything, storage group must be local to the unisphere instance and only works with storage groups that contain R1 or R11 devices

### Replication Enhancements
- `create_storage_group_snapshot`: Added secure option to enable creation of secure snapshot

---

## Version 9.1.1.0 (released 12/12/19)

### Fixes
- During Provisioning CI tests, only check storage groups for compression related values if compression is present and enabled
- OpenStack migrate tool and corresponding documentation

---

## Version 9.1.0.0 (released 4/12/19)

### Enhancements
- Changed from MIT License to Apache 2.0 License
- Python 2.7 has been removed as a supported Python version in advance of discontinued community support
- Doc strings have been standardised through out PyU4V
- Snake case has been implemented across method names and old methods set for deprecation (see refactoring/deprecation list below)
- Unisphere version has been moved from a user-set variable to a constant set by PyU4V
- If the user does not supply environment settings or they cannot be loaded from the config file an exception is raised during initialisation of U4VConn()
- Imports have been correctly implemented so class instances are not passed around except for the rest_client
- List/Dict comprehension have been cleaned up
- Decorators have been created for deprecating/refactoring methods, see section 'Refactoring & Deprecation' below
- Methods have been changed from old build_uri method to new build_uri method so there are zero hard coded endpoints
- Workload Planner functions have been moved out of common.py and into their own file workload_planner.py
- File handling functions have been moved to utils.file_handler.py
- Added .gitignore file to prevent any unwanted files merging with upstream repo
- Logger log level now only set in one place in PyU4V.conf
- Logger rotating file handler set up to create log files no bigger than 10MB and rotate through 10 of them with the most recent always being PyU4V.log
- Separate handling of SSLError, Timeout, HTTPError, and ConnectionError REST exceptions, allows for more granularity when diagnosing problems
- PyU4V will run a Unisphere validation check in U4VConn() __init__, if the version does not meet the required minimum set the driver gracefully exits
- A new REST header has been added called user-agent which specifies the current version of PyU4V in use, the platform running it and release information, and the Python version in use
- System endpoints have been added to PyU4V, enhancements feature system health checks, disk, and tag information
- Users can write dictionary to CSV from utils.file_handler
- CSV reader can convert string representations of boolean and float values to the correct type for processing
- Page list iterator now can iterate through all pages automatically, merge all results into one list and return to the user
- Performance section had a complete overhaul, from top to bottom it is an entirely new section. Old methods have been fixed but all marked for deprecation. For more information see 'Refactoring & Deprecation' section below
- Performance constants have been moved out of the package wide constants file into their own performance_constants file
- PyU4V README and ReadTheDocs had a complete overhaul from their previous state and can be considered complete revisions
- Retry decorator added to decorators.py to allow functions to be attempted multiple times before failing
- Check if a given string is a valid ipv4 or ipv6 address
- Functions now expect integer numbers instead of string representations of numbers expected by the Unisphere REST API, the intention is to make the use of PyU4V as simple as possible and let us take care of casting required types
- Online Device Expansion is included presenting users with the ability to extend R2 devices in the same operation as extending R1 devices

### Provisioning Enhancements
- `get_available_initiator_wwn_as_list()`: Get a list of available initiator WWNs
- `get_in_use_initiator()`: Get an initiator that is in use filterable by director type
- `get_available_initiator()`: Get an available initiator filterable by director type
- `get_fa_directors()`: Get all FA directors on the array
- `get_active_masking_view_connections()`: Get list of active connections from any masking view
- `format_director_port`: Format separate director port into single string
- `get_any_director_port`: Get a non-GuestOS port from a director

### Fixes
- When searching for volumes by volume name, if more than one volume matches the input volume name a list of volume device IDs will be returned, if only one volume is matched just that device ID is returned as a string
- Fix for establishing a session when none exists during rest requests
- PyU4V.conf loading on Windows from user home directory now working as intended from default location of ~/.PyU4V
- Removed CFG from header of univmax_conn.py and set it in __init__ so users file_path is now read as intended
- Removed CFG from header of utils files, it was unnecessary to have it included there, it only needs set once in U4VConn()
- The function migration.get_storage_group_list() set includeMigrations to False incorrectly returns all SGs in the migratingNames list, a new function migration.get_storage_groups() has been added which returns the default response of a dict containing all SG names and those SGs which are part of a migration session
- The function migration.delete_environment() was deleted as it is a duplicate of function migration.delete_migration_environment()
- CSV writer has been changed to use correct file writing modes and practices
- Pull #30 Modify initiator reverses alias name during a rename operation
- Pull #34 Get target wwn fails to split director:port return value
- Pull #38 Incorrect type in docstring of get_size_of_device_on_array
- Split returned port ids correctly during port group create/modify operations

### Tests
- 100% unit test coverage with all tests running cleanly across both unit and CI
- All suitable functions now have a respective Continuous Integration (CI) test
- Extensive CI test coverage
- Requests session establish is tested instead of mocking behaviour
- Fake request session mock has been changed so it does not adversely affect other tests when full suite of tests is run

### Refactoring & Deprecations
The following methods have either been refactored and marked for deprecation after PyU4V 9.3 or just marked for deprecation with no refactoring. To reduce the impact on end-users which may use these methods in their scripts an n+2 deprecation policy has been adopted.

For any methods marked for deprecation in the current release, they will need to remain in PyU4V for two full releases before being completely removed. As this policy has only just been implemented for PyU4V 9.1, all methods below marked for deprecation after PyU4V 9.3 will be removed entirely in PyU4V 9.4 or whatever the equivalent version is for n+2.

It is assumed that after two full releases users will have had enough time and notice to make the required changes in their code. Any methods which have been refactored in favour of other methods will be clearly marked in the associated logs generated when a refactored function is in use.

#### PyU4V/common.py
- `_build_uri_args()` has been marked for deprecation, please use new format `_build_uri()`
- `create_list_from_file()` has been refactored and marked for deprecation, please use alternative function `utils.file_handler.create_list_from_file()`
- `read_csv_values()` has been refactored and marked for deprecation, please use alternative function `utils.file_handler.read_csv_values()`
- `get_wlp_information()` has been refactored and marked for deprecation, please use alternative function `WLPFunctions.get_wlp_information()`
- `get_headroom()` has been refactored and marked for deprecation, please use alternative function `WLPFunctions.get_headroom()`

#### PyU4V/performance.py
- `get_perf_threshold_categories()` has been refactored and marked for deprecation, please use alternative function `get_threshold_categories()`
- `get_perf_category_threshold_settings()` has been refactored and marked for deprecation, please use alternative function `get_category_threshold_settings()`
- `set_perf_threshold_and_alert()` has been refactored and marked for deprecation, please use alternative function `update_threshold()`
- `set_perfthresholds_csv()` has been refactored and marked for deprecation, please use alternative function `update_threshold()`
- `get_fe_director_list()` has been refactored and marked for deprecation, please use alternative function `get_frontend_director_keys()`
- `get_fe_port_list()` has been refactored and marked for deprecation, please use alternative function `get_frontend_port_keys()`
- `get_fe_port_util_last4hrs()` has been marked for deprecation, use standard get FE Director performance stats call and specify the start and end time manually
- `get_fe_director_metrics()` has been refactored and marked for deprecation, please use alternative function `get_frontend_director_stats()`
- `get_fe_port_metrics()` has been refactored and marked for deprecation, please use alternative function `get_frontend_port_stats()`
- `get_array_metrics()` has been refactored and marked for deprecation, please use alternative function `get_array_stats()`
- `get_storage_group_metrics()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_stats()`
- `get_all_fe_director_metrics()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_stats()`
- `get_all_fe_director_metrics()` has been refactored and marked for deprecation, use standard get FE Director performance stats call and specify all required array IDs
- `get_director_info()` has been marked for deprecation, use standard get Director performance stats call and specify all required array IDs and type
- `get_port_group_metrics()` has been refactored and marked for deprecation, please use alternative function `get_port_group_stats()`
- `get_host_metrics()` has been refactored and marked for deprecation, please use alternative function `get_host_stats()`

#### PyU4V/provisioning.py
- `get_mvs_from_host()` has been refactored and marked for deprecation, please use alternative function `get_masking_views_from_host()`
- `get_hostgroup()` has been refactored and marked for deprecation, please use alternative function `get_host_group()`
- `get_hostgroup_list()` has been refactored and marked for deprecation, please use alternative function `get_host_group_list()`
- `create_hostgroup()` has been refactored and marked for deprecation, please use alternative function `create_host_group()`
- `modify_hostgroup()` has been refactored and marked for deprecation, please use alternative function `modify_host_group()`
- `delete_hostgroup()` has been refactored and marked for deprecation, please use alternative function `delete_host_group()`
- `get_masking_views_by_host()` has been refactored and marked for deprecation, please use alternative function `get_masking_views_by_initiator_group()`
- `get_common_masking_views()` has been refactored and marked for deprecation, please use alternative function `get_port_group_common_masking_views()`
- `get_host_from_maskingview()` has been refactored and marked for deprecation, please use alternative function `get_host_from_masking_view()`
- `get_storagegroup_from_maskingview()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_from_masking_view()`
- `get_portgroup_from_maskingview()` has been refactored and marked for deprecation, please use alternative function `get_port_group_from_masking_view()`
- `get_maskingview_connections()` has been refactored and marked for deprecation, please use alternative function `get_masking_view_connections()`
- `find_host_lun_id_for_vol()` has been refactored and marked for deprecation, please use alternative function `find_host_lun_id_for_volume()`
- `get_portgroup()` has been refactored and marked for deprecation, please use alternative function `get_port_group()`
- `get_portgroup_list()` has been refactored and marked for deprecation, please use alternative function `get_port_group_list()`
- `get_ports_from_pg()` has been refactored and marked for deprecation, please use alternative function `get_ports_from_port_group()`
- `get_target_wwns_from_pg()` has been refactored and marked for deprecation, please use alternative function `get_target_wwns_from_port_group()`
- `create_portgroup()` has been refactored and marked for deprecation, please use alternative function `create_port_group()`
- `create_multiport_portgroup()` has been refactored and marked for deprecation, please use alternative function `create_multiport_port_group()`
- `create_portgroup_from_file()` has been refactored and marked for deprecation, please use alternative function `create_port_group_from_file()`
- `modify_portgroup()` has been refactored and marked for deprecation, please use alternative function `modify_port_group()`
- `delete_portgroup()` has been refactored and marked for deprecation, please use alternative function `delete_port_group()`
- `get_slo_list()` has been refactored and marked for deprecation, please use alternative function `get_service_level_list()`
- `get_slo()` has been refactored and marked for deprecation, please use alternative function `get_service_level()`
- `modify_slo()` has been refactored and marked for deprecation, please use alternative function `modify_service_level()`
- `get_mv_from_sg()` has been refactored and marked for deprecation, please use alternative function `get_masking_view_from_storage_group()`
- `get_num_vols_in_sg()` has been refactored and marked for deprecation, please use alternative function `get_num_vols_in_storage_group()`
- `is_child_sg_in_parent_sg()` has been refactored and marked for deprecation, please use alternative function `is_child_storage_group_in_parent_storage_group()`
- `get_child_sg_from_parent()` has been refactored and marked for deprecation, please use alternative function `get_child_storage_groups_from_parent()`
- `create_non_empty_storagegroup()` has been refactored and marked for deprecation, please use alternative function `create_non_empty_storage_group()`
- `create_empty_sg()` has been refactored and marked for deprecation, please use alternative function `create_empty_storage_group()`
- `add_existing_vol_to_sg()` has been refactored and marked for deprecation, please use alternative function `add_existing_volume_to_storage_group()`
- `add_new_vol_to_storagegroup()` has been refactored and marked for deprecation, please use alternative function `add_new_volume_to_storage_group()`
- `remove_vol_from_storagegroup()` has been refactored and marked for deprecation, please use alternative function `remove_volume_from_storage_group()`
- `create_volume_from_sg_return_dev_id()` has been refactored and marked for deprecation, please use alternative function `create_volume_from_storage_group_return_id()`
- `add_child_sg_to_parent_sg()` has been refactored and marked for deprecation, please use alternative function `add_child_storage_group_to_parent_group()`
- `remove_child_sg_from_parent_sg()` has been refactored and marked for deprecation, please use alternative function `remove_child_storage_group_from_parent_group()`
- `update_storagegroup_qos()` has been refactored and marked for deprecation, please use alternative function `update_storage_group_qos()`
- `delete_storagegroup()` has been refactored and marked for deprecation, please use alternative function `delete_storage_group()`
- `get_vol_effective_wwn_details_84()` has been refactored and marked for deprecation, please use alternative function `get_volume_effective_wwn_details()`
- `get_vols_from_storagegroup()` has been refactored and marked for deprecation, please use alternative function `get_volumes_from_storage_group()`
- `get_storagegroup_from_vol()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_from_volume()`
- `is_volume_in_storagegroup()` has been refactored and marked for deprecation, please use alternative function `is_volume_in_storage_group()`

#### PyU4V/replication.py
- `get_storage_group_rep()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_srdf_details()`
- `get_storage_group_rep_list()` has been refactored and marked for deprecation, please use alternative function `get_replication_enabled_storage_groups()`
- `get_storagegroup_snapshot_list()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_snapshot_list()`
- `create_storagegroup_snap()` has been refactored and marked for deprecation, please use alternative function `create_storage_group_snap()`
- `get_storagegroup_snapshot_generation_list()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_snapshot_generation_list()`
- `modify_storagegroup_snap()` has been refactored and marked for deprecation, please use alternative function `modify_storage_group_snapshot()`
- `delete_storagegroup_snapshot()` has been refactored and marked for deprecation, please use alternative function `delete_storage_group_snapshot()`
- `choose_snapshot_from_list_in_console()` has marked for deprecation
- `is_vol_in_rep_session()` has been refactored and marked for deprecation, please use alternative function `is_volume_in_replication_session()`
- `are_vols_rdf_paired()` has been refactored and marked for deprecation, please use alternative function `are_volumes_rdf_paired()`
- `get_storagegroup_srdfg_list()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_srdf_group_list()`
- `get_storagegroup_srdf_details()` has been refactored and marked for deprecation, please use alternative function `get_storage_group_rdf_details()`
- `create_storagegroup_srdf_pairings()` has been refactored and marked for deprecation, please use alternative function `create_storage_group_srdf_pairings()`
- `modify_storagegroup_srdf()` has been refactored and marked for deprecation, please use alternative function `modify_storage_group_srdf()`
- `suspend_storagegroup_srdf()` has been refactored and marked for deprecation, please use alternative function `suspend_storage_group_srdf()`
- `establish_storagegroup_srdf()` has been refactored and marked for deprecation, please use alternative function `establish_storage_group_srdf()`
- `failover_storagegroup_srdf()` has been refactored and marked for deprecation, please use alternative function `failover_storage_group_srdf()`
- `failback_storagegroup_srdf()` has been refactored and marked for deprecation, please use alternative function `failback_storage_group_srdf()`
- `delete_storagegroup_srdf()` has been refactored and marked for deprecation, please use alternative function `delete_storage_group_srdf()`

#### PyU4V/utils/console.py
- `choose_from_list()` has been marked for deprecation, please implement any console driven commands from your own scripts and not from PyU4V
