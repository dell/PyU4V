# The MIT License (MIT)
# Copyright (c) 2016 Dell Inc. or its subsidiaries.

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

import json
import logging

import requests
from requests.auth import HTTPBasicAuth
import urllib3

from PyU4V.utils import exception

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOG = logging.getLogger(__name__)


class RestRequests(object):

    def __init__(self, username, password, verify, base_url):
        self.username = username
        self.password = password
        self.verifySSL = verify
        self.base_url = base_url
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json'}
        self.timeout = 120
        self.session = self.establish_rest_session()

    def establish_rest_session(self):
        session = requests.session()
        session.headers = self.headers
        session.auth = HTTPBasicAuth(self.username, self.password)
        session.verify = self.verifySSL
        return session

    def rest_request(self, target_url, method,
                     params=None, request_object=None, timeout=None):
        """Sends a request (GET, POST, PUT, DELETE) to the target api.

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
        url = ("{}{}".format(self.base_url, target_url))
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
                          "received is: {}".format(status_code))
                response = None
            LOG.debug("{} request to {} has returned with a status "
                      "code of: {}".format(method, url, status_code))
            return response, status_code

        except (requests.Timeout, requests.ConnectionError) as e:
            LOG.error("The {} request to URL {} timed-out, but may have been "
                      "successful. Please check the array. Exception "
                      "received: {}.".format(method, url, e))
            return None, None
        except Exception as e:
                exp_message = ("The {} request to URL: {} failed with "
                               "exception {}".format(method, url, e))
                raise exception.VolumeBackendAPIException(data=exp_message)

    def close_session(self):
        """
        Close the current rest session
        """
        return self.session.close()
