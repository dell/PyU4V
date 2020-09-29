# Copyright (c) 2020 Dell Inc. or its subsidiaries.
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
"""exception.py"""

import logging
import six

LOG = logging.getLogger(__name__)


class PyU4VException(Exception):
    """PyU4VException."""

    message = 'An unknown exception occurred.'
    code = 500
    headers = dict()
    safe = False

    def __init__(self, message=None, **kwargs):
        """__init__."""
        self.kwargs = kwargs
        self.kwargs['message'] = message

        if 'code' not in self.kwargs:
            self.kwargs['code'] = self.code

        for k, v in self.kwargs.items():
            if isinstance(v, Exception):
                self.kwargs[k] = six.text_type(v)

        if self._should_format():
            try:
                message = self.message % kwargs
            except Exception:
                self._log_exception()
                message = self.message
        elif isinstance(message, Exception):
            message = six.text_type(message)

        self.msg = message
        super().__init__(message)

    def _should_format(self):
        return self.kwargs['message'] is None or '%(message)' in self.message

    def _log_exception(self):
        LOG.exception('Exception in string format operation:')
        for name, value in self.kwargs.items():
            LOG.error("%(name)s: %(value)s",
                      {'name': name, 'value': value})

    def __unicode__(self):
        return self.msg


class VolumeBackendAPIException(PyU4VException):
    """VolumeBackendAPIException."""

    message = ('Bad or unexpected response from the storage volume '
               'backend API: %(data)s')


class ResourceNotFoundException(PyU4VException):
    """ResourceNotFoundException."""

    message = 'The requested resource was not found: %(data)s'


class InvalidInputException(PyU4VException):
    """InvalidInputException."""

    message = 'Invalid input received: %(data)s'


class UnauthorizedRequestException(PyU4VException):
    """UnauthorizedRequestException."""

    message = 'Unauthorized request - please check credentials'


class MissingConfigurationException(PyU4VException):
    """MissingConfigurationFileException"""

    message = ('PyU4V settings not be loaded, please check file location or '
               'univmax_conn input parameters.')
