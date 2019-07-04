# The MIT License (MIT)
# Copyright (c) 2019 Dell Inc. or its subsidiaries.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""Exception package."""

import logging

# Register configuration file
from PyU4V.utils import config_handler

import six

LOG = logging.getLogger(__name__)
CFG = config_handler.set_logger_and_config()


class PyU4VException(Exception):
    """PyU4VException."""

    message = "An unknown exception occurred."
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        """__init__."""
        self.kwargs = kwargs
        self.kwargs['message'] = message

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        for k, v in self.kwargs.items():
            if isinstance(v, Exception):
                self.kwargs[k] = six.text_type(v)

        if self._should_format():
            try:
                message = self.message % kwargs

            except Exception:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception('Exception in string format operation')
                for name, value in kwargs.items():
                    LOG.error("%(name)s: %(value)s",
                              {'name': name, 'value': value})
                # at least get the core message out if something happened
                message = self.message
        elif isinstance(message, Exception):
            message = six.text_type(message)

        self.msg = message
        super(PyU4VException, self).__init__(message)

    def _should_format(self):
        return self.kwargs['message'] is None or '%(message)' in self.message

    def __unicode__(self):
        """__unicode__."""
        return self.msg


class VolumeBackendAPIException(PyU4VException):
    """VolumeBackendAPIException."""

    message = ("Bad or unexpected response from the storage volume "
               "backend API: %(data)s")


class ResourceNotFoundException(PyU4VException):
    """ResourceNotFoundException."""

    message = "The requested resource was not found: %(data)s"


class InvalidInputException(PyU4VException):
    """InvalidInputException."""

    message = "Invalid input received: %(data)s"


class UnauthorizedRequestException(PyU4VException):
    """UnauthorizedRequestException."""

    meesage = "Unauthorized request - please check credentials"
