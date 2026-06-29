#!/usr/bin/env python
# Copyright (c) 2026 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""update_version.py - Update version strings in documentation files.

This script reads the version from PyU4V/version.py and updates version strings
in README.rst and docs/source/installation.rst to match.

Usage:
    python update_version.py
"""

import os
import re


def read_version():
    """Read version from PyU4V/version.py."""
    version_file = os.path.join(os.path.dirname(__file__), 'PyU4V', 'version.py')
    with open(version_file, 'r') as f:
        content = f.read()
    
    version_match = re.search(r"^VERSION\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)
    major_match = re.search(r"^MAJOR_VERSION\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)

    if not version_match or not major_match:
        raise RuntimeError("Unable to find version strings in PyU4V/version.py")

    major = major_match.group(1)
    return {
        'VERSION': version_match.group(1),
        'MAJOR_VERSION': major,
        'UNI_VERSION': major + '.0',  # derived: '10.5' -> '10.5.0'
    }


def update_file(filepath, replacements):
    """Update file with version replacements."""
    with open(filepath, 'r') as f:
        content = f.read()

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Updated {filepath}")


def main():
    """Main function."""
    versions = read_version()
    print(f"Read versions from PyU4V/version.py:")
    print(f"  VERSION: {versions['VERSION']}")
    print(f"  MAJOR_VERSION: {versions['MAJOR_VERSION']}")
    print(f"  UNI_VERSION (derived): {versions['UNI_VERSION']}")
    print()
    
    # Extract old versions from the files to replace
    # For simplicity, we'll use patterns that match the current format
    
    ver = versions['VERSION']
    major = versions['MAJOR_VERSION']
    uni = versions['UNI_VERSION']

    # README.rst replacements
    readme_replacements = [
        (r'Welcome to PyU4V [\d.]+',
         f'Welcome to PyU4V {major}'),
        (r'PyU4V Version [\d.]+\n',
         f'PyU4V Version {major}\n'),
        (r'\| \*\*PyU4V Version\*\*\s+\| [\d.]+ +\|',
         f'| **PyU4V Version**             | {ver}                   |'),
        (r'\| \*\*Minimum Unisphere Version\*\*\s+\| [\d.]+ +\|',
         f'| **Minimum Unisphere Version** | {uni}                     |'),
    ]

    # docs/source/installation.rst replacements
    installation_replacements = [
        (r'\| \*\*PyU4V Version\*\*\s+\| [\d.]+ +\|',
         f'| **PyU4V Version**             | {ver}                               |'),
        (r'\| \*\*Minimum Unisphere Version\*\*\s+\| [\d.]+ +\|',
         f'| **Minimum Unisphere Version** | {uni}                                 |'),
    ]

    # root index.rst replacements (mirrors docs/source/index.rst patterns)
    root_index_replacements = [
        (r'\| \*\*PyU4V Version\*\*\s+\| [\d.]+ +\|',
         f'| **PyU4V Version**             | {ver}                               |'),
        (r'\| \*\*Minimum Unisphere Version\*\*\s+\| [\d.]+ +\|',
         f'| **Minimum Unisphere Version** | {uni}                                 |'),
        (r'PyU4V version [\d.]+ is compatible',
         f'PyU4V version {major} is compatible'),
        (r'PyU4V [\d.]+\.\d+\.\d+ with',
         f'PyU4V {ver} with'),
        (r'older than [\d.]+\n',
         f'older than {uni}\n'),
        (r'PyU4V [\d.]+\.\d+\.\d+ will',
         f'PyU4V {ver} will'),
        (r'PyU4V [\d.]+ is distributed under the Apache',
         f'PyU4V {major} is distributed under the Apache'),
    ]

    # docs/source/index.rst replacements
    index_replacements = [
        (r'\| \*\*PyU4V Version\*\*\s+\| [\d.]+ +\|',
         f'| **PyU4V Version**             | {ver}                               |'),
        (r'\| \*\*Minimum Unisphere Version\*[\*\s]+\| [\d.]+ +\|',
         f'| **Minimum Unisphere Version*  | {uni}                                 |'),
        (r'PyU4V version [\d.]+ is compatible',
         f'PyU4V version {ver} is compatible'),
        (r'PyU4V [\d.]+ is distributed under the Apache',
         f'PyU4V {major} is distributed under the Apache'),
    ]
    
    # Update files
    readme_path = os.path.join(os.path.dirname(__file__), 'README.rst')
    root_index_path = os.path.join(os.path.dirname(__file__), 'index.rst')
    installation_path = os.path.join(os.path.dirname(__file__), 'docs', 'source', 'installation.rst')
    index_path = os.path.join(os.path.dirname(__file__), 'docs', 'source', 'index.rst')

    update_file(readme_path, readme_replacements)
    update_file(root_index_path, root_index_replacements)
    update_file(installation_path, installation_replacements)
    update_file(index_path, index_replacements)
    
    print()
    print("Version update complete!")
    print("Please review the changes before committing.")


if __name__ == '__main__':
    main()
