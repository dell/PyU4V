import logging
import six

# register configuration file
from PyU4V.utils import config_handler

LOG = logging.getLogger(__name__)
CFG = config_handler.set_logger_and_config()


class PyU4VException(Exception):
    message = "An unknown exception occurred."
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
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
        return self.msg


class VolumeBackendAPIException(PyU4VException):
    message = ("Bad or unexpected response from the storage volume "
               "backend API: %(data)s")


class ResourceNotFoundException(PyU4VException):
    message = "The requested resource was not found: %(data)s"


class InvalidInputException(PyU4VException):
    message = "Invalid input received: %(data)s"


class UnauthorizedRequestException(PyU4VException):
    meesage = "Unauthorized request - please check credentials"
