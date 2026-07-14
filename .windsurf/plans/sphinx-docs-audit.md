# Sphinx Documentation Audit & Fix Plan

## Critical (Build-Breaking)
1. **Toctree mismatch** - `programmers_guide.rst` references `enhanced_bulk-api_calls` (hyphen) but file is `enhanced_bulk_api_calls.rst` (underscore)
2. **Missing blank line** - `quick_start.rst:52` code-block missing blank line before content
3. **Broken RST table** - `index.rst:40` has `**Minimum Unisphere Version*` (missing closing `**`)

## Version/Content
4. Python version notes say 3.6-3.10 but table says 3.6-3.12 (index.rst, installation.rst)
5. Outdated Unisphere version refs (quick_start.rst, configuration.rst, installation.rst)
6. Copyright 2022 -> 2025 in conf.py
7. enhanced_api.py docstring references wrong filename
8. restoreclone.py missing license header; clone.rst line range wrong
9. Outdated GitHub links (MichaelMcAleer -> Dell)
10. Typo: "Unipshere" in index.rst and quick_start.rst
11. Invalid Python syntax in contribute.rst example
12. Missing utils modules in PyU4V.utils.rst (performance_category_map, performance_constants, utils)
13. Missing programmers guide for: migration, snapshot_policy, serviceability, settings, workload_planner, volumes, storage_groups
14. contribute.rst skips convention #4
15. Update CHANGELOG and README
