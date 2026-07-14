# Versioning Refactor — Full Consistency (10.5)

## Goal
Single source of truth for the active Unisphere REST API version, with **no public
interface change**. `U4VConn(u4v_version=...)`, the `[setup] u4v_version` config key,
`conn.set_u4v_version()`, and `common.UNI_VERSION` all keep working.

## Background (current flow)
- `version.py` defines `MAJOR_VERSION`, `VERSION`, `UNI_VERSION` (unused), `API_VERSION`,
  `ENHANCED_API_VERSION`.
- `constants.UNISPHERE_VERSION = version.API_VERSION` ("105") drives REST URLs.
- `version.UNI_VERSION` ("10.5.0") is dead/misleading -> removed.
- Each module cached its own `common.UNI_VERSION`; `set_u4v_version()` updated them via a
  hand-maintained loop (omission bug risk).
- `provisioning/settings/serviceability/system/replication` cached `self.version` at init.

## Tasks
- [x] common.py: back `UNI_VERSION` by `rest_client.u4v_version` via a property
      (getter falls back to `constants.UNISPHERE_VERSION`; setter stamps the client).
- [x] univmax_conn.py: collapse `set_u4v_version()` manual loop to stamping both clients.
- [x] univmax_conn.py: cache `supported_api_versions` from `get_uni_version_info()`.
- [x] Convert per-module `self.version` (provisioning, settings, serviceability, system)
      to a read-only property reading `common.UNI_VERSION` (replication already done).
- [x] version.py: remove unused `UNI_VERSION`; add clarifying comments.
- [x] Tests: single-source version propagation assertions.
- [x] Docs: README "API Version" section + CHANGELOG.

## Backward-compat notes
- `common.UNI_VERSION` remains readable AND writable; writes now propagate globally
  (single source) instead of per-instance. Documented as intended.
- No constructor signatures changed.
- `PyU4V.version.UNI_VERSION` removed (was not imported anywhere internally).
