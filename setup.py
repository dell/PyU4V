# Copyright (c) 2019 Dell Inc. or its subsidiaries.
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
import setuptools

setuptools.setup(
    name='PyU4V',
    version='9.1.5.0',
    url='https://github.com/dell/PyU4V/',
    author='Dell Inc. or its subsidiaries',
    author_email='Michael.Mcaleer@dell.com',
    description=("A Python library for use with Dell EMC's Unisphere for "
                 "PowerMax REST API."),
    license='Apache 2.0',
    packages=setuptools.find_packages(),
    install_requires=['requests', 'six', 'urllib3', 'prettytable'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    tests_require=['mock', 'testtools'],
    test_suite='tests')
