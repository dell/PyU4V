# -*- coding: utf-8 -*-
# __________         ____ ___  _________   ____
# \______   \___.__.|    |   \/  |  \   \ /   /
#  |     ___<   |  ||    |   /   |  |\   Y   /
#  |    |    \___  ||    |  /    ^   /\     /
#  |____|    / ____||______/\____   |  \___/
#            \/                  |__|
# Copyright (c) 2021 Dell Inc. or its subsidiaries.
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
"""__init__.py."""

from .univmax_conn import U4VConn  # noqa: F401
from . import version
__title__ = 'pyu4v'
__version__ = version.VERSION
__author__ = 'Dell EMC or its subsidiaries'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2023 Dell EMC Inc'
