# PyU4V Compatibility-Safe Improvement Plan

## Compatibility invariant

All work must preserve existing customer import paths, constructors, method
signatures, parameter ordering/defaults, public attributes, return shapes,
exceptions, warnings, and side effects unless a change follows the documented
deprecation process. Internal helpers and regression tests should be preferred
over public API changes.

## Completed in the current worktree

1. **P1-1 — API-key authentication:** explicit tokens now take precedence over
   configuration-file credentials and configure both the primary and enhanced
   REST clients.
2. **P1-2 — Array state propagation:** `set_array_id()` now updates every
   top-level and nested array-scoped component, including enhanced clients,
   settings, Metro DR, real-time performance, and nested provisioning helpers.
3. **P1-3 — Enhanced selection:** shared internal selection construction now
   prevents duplicate fields, honors default exclusions, supports `exclude=[]`,
   and leaves caller-owned selection lists unchanged.
4. **P1-4 — Alert notification updates:** partial payloads are copied, omitted
   settings remain unchanged, explicit `False` values disable targets, and
   integer or string SNMPv3 versions retain their target details.
5. **P2-6 — Connection lifecycle parity:** timeout changes and session closure
   now apply to both primary and enhanced REST clients.
6. **P2-7 — Serviceability correctness:** explicit array overrides are honored,
   nethost actions are validated before REST calls, certificate paths are
   checked without assertions, and all certificate handles close after upload
   success or failure.
7. **Original P2-10 — Performance decorator metadata:** the performance
   recommendation decorator now preserves public method names, docstrings,
   modules, and signatures with `functools.wraps` while retaining identical
   call forwarding, logging, return values, and exception propagation.

Original issue 5 (`PyU4V.tools` removal) is excluded from the compatibility
queue because it was an internal tool and was not part of the supported
customer SDK interface.

## Reprioritized remaining work

### Priority 1 — deterministic reliability and resource safety

1. **Original P2-8 — File-transfer failures and cleanup:** close temporary
   sessions and upload handles in `finally` paths and prevent timeout responses
   from being dereferenced as objects. Decide and test the compatibility-safe
   exception contract before changing the current error type.
2. **Original P2-11 — Runtime assertions:** replace input-validation assertions
   with explicit checks while retaining normal-mode exception classes and
   messages; verify behavior under `python -O`.

### Priority 2 — regression strength and release reproducibility

3. Add a committed public-interface manifest covering imports, classes,
   constructors, signatures, defaults, namespaces, and decorated-method
   metadata.
4. Replace tests that mock the method under test with REST-boundary mocks and
   exact URI, payload, response, and exception assertions.
5. Make linting reproducible by resolving the Pylint 4 configuration mismatch
   and pinning or constraining developer-tool versions.
6. Correct the configuration sample path, version/minimum-support statements,
   Read the Docs dependency file, and stale changelog/deprecation text; enable
   warning-failing Sphinx builds after cleanup.
7. Align `requires-python` and development extras with the tested Python
   3.9–3.13 matrix and required contributor checks.

### Priority 3 — compatibility-sensitive decisions

8. **Original P2-12 — Error semantics:** retain current return and exception
    contracts unless an opt-in path or deprecation cycle is approved for broad
    exception handling in provisioning and real-time performance methods.
9. **Original P2-9 — Workload Planner example:** either document a supported
    replacement or explicitly approve restoration of legacy delegating methods;
    do not silently expand or contract the public surface.
10. Review process-wide TLS warning suppression, empty-dictionary request
    bodies, mutable defaults, and large wrapper modules after compatibility
    snapshots are in place.

## Verification gate for future work

- Run all unit tests on Python 3.9–3.13.
- Run `tox -e pep8` and `tox -e pylint` cleanly.
- Build Sphinx documentation without warnings.
- Add focused negative-path and compatibility regression tests for each fix.
- Inspect live-array tests but do not execute them without an approved array.
- Confirm the public-interface manifest is unchanged unless an approved
  deprecation or additive change explicitly permits a difference.
