# PyU4V Contributor Guide (AGENTS.md)

## Overview

PyU4V wraps the Unisphere for PowerMax REST API in simple Python abstractions.
Current release: **10.5** · Minimum Unisphere: **10.5.0** · Python: **3.9–3.13**

---

## Dev Setup

```bash
git clone https://github.com/dell/PyU4V
cd PyU4V
pip install -e .
pip install tox pytest testtools flake8 pylint
cp PyU4V/PyU4V.conf.sample ~/.PyU4V/PyU4V.conf   # edit with your array details
```

---

## Verification — run before every PR

### Unit tests
```bash
# All unit tests
pytest PyU4V/tests/unit_tests/

# Or via tox (tests every supported Python)
tox
```

### Linting
```bash
tox -e pep8     # flake8 (PEP 8 + naming + docstyle)
tox -e pylint   # pylint with project .pylintrc
```

All linting and unit tests **must pass cleanly** before submitting.
CI tests (`PyU4V/tests/ci_tests/`) require a live array and are run by maintainers.

---

## Code Standards

- Follow **PEP 8**; `flake8` is the enforcing tool.
- Public functions must have a **docstring** with `:param:` / `:returns:` / `:raises:`.
- Use keyword arguments for all new REST call wrappers to stay consistent with the existing API surface.
- Prefer `/v1/` Unisphere REST endpoints; use `enhanced_api` / `performance_enhanced` module helpers where available.

### Line Endings

- Before editing, inspect every target with `git ls-files --eol -- <paths>` and
  preserve its existing worktree line-ending style (`w/crlf` or `w/lf`).
- Follow `.gitattributes` when it defines an explicit policy. Do not change a
  file's line-ending style as part of an unrelated change.
- Patch tools can insert LF lines into CRLF files. After editing, normalize the
  entire touched file back to its original worktree style.
- Before handoff, run `git ls-files --eol -- <touched-paths>` and confirm that no
  touched file reports `w/mixed`; also run `git diff --check`.

---

## API Compatibility Rules

### Adding functionality ✅
New public methods, parameters (with defaults), and modules are welcome. Existing
call-sites must continue to work without change.

### Removing or moving functionality ⚠️
Deletions and relocations **require a deprecation decorator** targeting a release
**at least 2 minor versions after the current release (10.5)**, i.e. target ≥ **10.7**.

**Use `deprecation_notice` for straight removal:**

```python
from PyU4V.utils.decorators import deprecation_notice

@deprecation_notice('ClassName', start_version=10.5, end_version=10.7)
def old_method(self, ...):
    ...
```

**Use `refactoring_notice` when moving a function to a new location:**

```python
from PyU4V.utils.decorators import refactoring_notice

@refactoring_notice('ClassName', 'new_module.ClassName.{func}',
                    start_version='10.5', end_version='10.7')
def old_method(self, ...):
    return self._new_location.old_method(...)
```

Also add `.. deprecated:: <version>` to the docstring pointing to the new location.

### Breaking changes ❌
Changes that alter or remove existing public method signatures without a
deprecation notice will not be merged.

---

## Documentation & Changelog

- Update `README.rst` if the public API surface, supported versions, or key
  behaviour changes.
- Add an entry to `CHANGELOG.md` for every meaningful change.
- Sphinx docs live in `docs/source/`; run `make html` from `docs/` to verify
  no build warnings before submitting.

---

## Pull Request Process

1. Fork → feature branch → PR against `master`.
2. Ensure `pytest` (unit tests) and `tox -e pep8` pass locally.
3. Two approvals from core reviewers are required before merge.
4. Link any related GitHub issue in the PR description.

Full contribution guidelines: https://pyu4v.readthedocs.io/en/latest/
