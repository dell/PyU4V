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
"""rest_requests.py."""

import json
import logging
import platform
import requests
import requests.exceptions as r_exc
import sys
import urllib3

from PyU4V.utils import constants
from PyU4V.utils import exception
from requests.auth import HTTPBasicAuth

__pyu4v_version__ = constants.PYU4V_VERSION
__python_version__ = platform.python_version()
__platform__ = platform.system()
__platform_release__ = platform.release()
ua_details = (
    'PyU4V/{pv} ({platform}; version {release}) Python {python}'.format(
        pv=__pyu4v_version__, platform=__platform__,
        release=__platform_release__, python=__python_version__))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
LOG = logging.getLogger(__name__)


class RestRequests(object):
    """RestRequests."""

    def __init__(self, username, password, verify, base_url, interval, retries,
                 application_type=None):
        """__init__."""
        self.username = username
        self.password = password
        self.verify_ssl = verify
        self.base_url = base_url
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json',
                        'user-agent': ua_details,
                        'application-type': application_type}
        self.timeout = 120
        self.interval = interval
        self.retries = retries
        self.session = self.establish_rest_session()

    def establish_rest_session(self):
        """Establish a REST session.

        :returns: session -- object
        """
        session = requests.session()
        session.headers = self.headers
        session.auth = HTTPBasicAuth(self.username, self.password)
        session.verify = self.verify_ssl
        return session

    def rest_request(self, target_url, method,
                     params=None, request_object=None, timeout=None):
        """Send a request to the target api.

        Valid methods are 'GET', 'POST', 'PUT', 'DELETE'.

        :param target_url: target url --str
        :param method: method -- str
        :param params: Additional URL parameters -- dict
        :param request_object: request payload -- dict
        :param timeout: optional timeout override -- int
        :returns: server response, status code -- dict, int
        """
        if timeout:
            timeout_val = timeout
        else:
            timeout_val = self.timeout
        if not self.session:
            self.session = self.establish_rest_session()
        url = '{base_url}{target_url}'.format(
            base_url=self.base_url, target_url=target_url)
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
                response = None
                if not status_code:
                    status_code = None
                LOG.debug('No response received from API. Status code '
                          'received is: {sc}.'.format(sc=status_code))

            LOG.debug('{method} request to {url} has returned with a status '
                      'code of: {sc}.'.format(method=method, url=url,
                                              sc=status_code))
            return response, status_code

        except requests.Timeout as error:
            LOG.error(
                'The {method} request to URL {url} timed-out, but may have '
                'been successful. Please check the array. Exception received: '
                '{exc}.'.format(method=method, url=url, exc=error))
            return None, None

        except r_exc.SSLError as error:
            msg = (
                'The connection to {base} has encountered an SSL error. '
                'Please check your SSL config or supplied SSL cert in Cinder '
                'configuration. SSL Exception message: {m}'.format(
                    base=self.base_url, m=error))
            raise r_exc.SSLError(msg)

        except (r_exc.ConnectionError, r_exc.HTTPError) as error:
            exc_class, __, __ = sys.exc_info()
            msg = (
                'The {met} to Unisphere server {base} has experienced a {exc} '
                'error. Please check your Unisphere server connection and '
                'availability. Exception message: {msg}'.format(
                    met=method, base=self.base_url,
                    exc=error.__class__.__name__, msg=error))
            raise exc_class(msg)

        except Exception as error:
            exp_message = (
                'The {method} request to URL {url} failed with exception: '
                '{e}.'.format(method=method, url=url, e=error))
            raise exception.VolumeBackendAPIException(data=exp_message)

    def close_session(self):
        """Close the current session."""
        self.session.close()
