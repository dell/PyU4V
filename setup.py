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
"""setup.py."""
import os
import re
import setuptools


def _read_version():
    """Read version from PyU4V/version.py without importing it."""
    version_file = os.path.join(os.path.dirname(__file__), 'PyU4V', 'version.py')
    with open(version_file, 'r') as f:
        version_content = f.read()
    # Match VERSION = '...'
    match = re.search(r"VERSION\s*=\s*['\"]([^'\"]+)['\"]", version_content)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find VERSION string in PyU4V/version.py")


with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyu4v',
    version=_read_version(),
    url='https://github.com/dell/PyU4V/',
    author='Dell Inc. or its subsidiaries',
    author_email='paule.martin@dell.com',
    description="A Python library for use with Dell EMC's Unisphere for "
                "PowerMax REST API.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license='Apache-2.0',
    packages=setuptools.find_packages(),
    install_requires=['requests>=2.28'],  # urllib3 is a transitive dep of requests
    extras_require={'tools': ['prettytable']},
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    python_requires='>=3.9, <4.0',
    tests_require=['testtools'],
    test_suite='tests')
