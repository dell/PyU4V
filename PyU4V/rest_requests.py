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
"""rest_requests.py."""

import json
import logging

from PyU4V.utils import exception

import requests
from requests.auth import HTTPBasicAuth

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOG = logging.getLogger(__name__)


class RestRequests(object):
    """RestRequests."""

    def __init__(self, username, password, verify, base_url):
        """__init__."""
        self.username = username
        self.password = password
        self.verifySSL = verify
        self.base_url = base_url
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json'}
        self.timeout = 120
        self.session = self.establish_rest_session()

    def establish_rest_session(self):
        """establish_rest_session."""
        session = requests.session()
        session.headers = self.headers
        session.auth = HTTPBasicAuth(self.username, self.password)
        session.verify = self.verifySSL
        return session

    def rest_request(self, target_url, method,
                     params=None, request_object=None, timeout=None):
        """Send a request (GET, POST, PUT, DELETE) to the target api.

        :param target_url: target url (string)
        :param method: The method (GET, POST, PUT, or DELETE)
        :param params: Additional URL parameters
        :param request_object: request payload (dict)
        :param timeout: optional timeout override
        :return: server response object (dict), status code
        """
        if timeout:
            timeout_val = timeout
        else:
            timeout_val = self.timeout
        if not self.session:
            self.establish_rest_session()
        url = "%s%s" % (self.base_url, target_url)
        try:
            if request_object:
                response = self.session.request(
                    method=method, url=url, timeout=timeout_val,
                    data=json.dumps(request_object, sort_keys=True,
                                    indent=4))
            elif params:
                response = self.session.request(method=method, url=url,
                                                params=params,
                                                timeout=timeout_val)
            else:
                response = self.session.request(method=method, url=url,
                                                timeout=timeout_val)
            status_code = response.status_code
            try:
                response = response.json()
            except ValueError:
                LOG.debug("No response received from API. Status code "
                          "received is %(status_code)s.",
                          {'status_code': status_code})
                response = None
            LOG.debug("%(method)s request to %(url)s has returned "
                      "with a status code of: %(status_code)s.",
                      {'method': method,
                       'url': url,
                       'status_code': status_code})
            return response, status_code

        except (requests.Timeout, requests.ConnectionError) as e:
            LOG.error("The %(method)s request to URL %(url)s "
                      "timed-out, but may have been successful. Please check "
                      "the array. Exception received: %(e)s.",
                      {'method': method,
                       'url': url,
                       'e': e})
            return None, None
        except Exception as e:
            exp_message = ("The %(method)s request to URL %(url)s failed "
                           "with exception %(e)s.",
                           {'method': method,
                            'url': url,
                            'e': e})
            raise exception.VolumeBackendAPIException(data=exp_message)

    def close_session(self):
        """Close the current rest session."""
        return self.session.close()
