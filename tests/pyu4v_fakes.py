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

import ast
import os
import requests
import tempfile

from . import pyu4v_common_data as tpd  # noqa: H304


class FakeResponse(object):
    """Fake response."""

    def __init__(self, status_code, return_object):
        """__init__."""
        self.status_code = status_code
        self.return_object = return_object

    def json(self):
        """json."""
        if self.return_object:
            return self.return_object
        else:
            raise ValueError


class FakeRequestsSession(object):
    """Fake request session."""

    def __init__(self, *args, **kwargs):
        """__init__."""
        self.data = tpd.CommonData()

    def request(self, method, url, params=None, data=None, timeout=None):
        """request."""
        return_object = ''
        status_code = 200
        if method == 'GET':
            status_code, return_object = self._get_request(url, params)

        elif method == 'POST' or method == 'PUT':
            status_code, return_object = self._post_or_put(url, data)

        elif method == 'DELETE':
            status_code, return_object = self._delete(url)

        elif method == 'TIMEOUT':
            raise requests.Timeout

        elif method == 'EXCEPTION':
            raise Exception

        return FakeResponse(status_code, return_object)

    def _get_request(self, url, params):
        status_code = 200
        return_object = None
        if self.data.failed_resource in url:
            status_code = 500
            return_object = self.data.job_list[2]
        elif 'sloprovisioning' in url:
            if 'volume' in url:
                return_object = self._sloprovisioning_volume(url, params)
            elif 'storagegroup' in url:
                return_object = self._sloprovisioning_sg(url)
            elif 'srp' in url:
                return_object = self._sloprovisioning_srp(url)
            elif 'maskingview' in url:
                return_object = self._sloprovisioning_mv(url)
            elif 'portgroup' in url:
                return_object = self._sloprovisioning_pg(url)
            elif 'port' in url:
                return_object = self._sloprovisioning_port(url)
            elif 'director' in url:
                return_object = self._sloprovisioning_port(url)
            elif 'hostgroup' in url:
                return_object = self._sloprovisioning_hg(url)
            elif 'host' in url:
                return_object = self._sloprovisioning_ig(url)
            elif 'initiator' in url:
                return_object = self._sloprovisioning_initiator(url)
            elif 'workloadtype' in url:
                return_object = self.data.workloadtype
            elif 'compressionCapable' in url:
                return_object = self.data.compression_info
            elif '{}/slo'.format(self.data.array) in url:
                if self.data.slo in url:
                    return_object = self.data.slo_details
                else:
                    return_object = self.data.slo_list
            else:
                return_object = self.data.symm_list

        elif 'replication' in url:
            return_object = self._replication(url)

        elif 'migration' in url:
            return_object = self._migration(url)

        elif 'system' in url:
            return_object = self._system(url)

        elif 'headroom' in url:
            return_object = self.data.headroom

        elif 'Iterator' in url:
            return_object = self.data.iterator_page

        elif 'wlp' in url:
            return_object = self.data.wlp

        return status_code, return_object

    def _establish_rest_session(self):
        ref_headers = {'content-type': 'application/json',
                       'accept': 'application/json',
                       'application-type': 'pyu4v'}
        self.assertEqual(ref_headers, self.rest.session.headers)
        self.assertEqual('smc', self.rest.session.auth.username)
        self.assertEqual('smc', self.rest.session.auth.password)
        self.assertEqual(False, self.rest.session.verify)

    def _sloprovisioning_volume(self, url, params):
        return_object = self.data.volume_list[2]
        if params:
            if '1' in params.values():
                return_object = self.data.volume_list[0]
            elif '2' in params.values():
                return_object = self.data.volume_list[1]
        else:
            for vol in self.data.volume_details:
                if vol['volumeId'] in url:
                    return_object = vol
                    break
        return return_object

    def _sloprovisioning_sg(self, url):
        return_object = self.data.sg_list
        for sg in self.data.sg_details:
            if sg['storageGroupId'] in url:
                return_object = sg
                break
        return return_object

    def _sloprovisioning_mv(self, url):
        if self.data.masking_view_name_i in url:
            return_object = self.data.maskingview[1]
        elif self.data.masking_view_name_f in url:
            return_object = self.data.maskingview[0]
        else:
            return_object = self.data.maskingview[2]
        return return_object

    def _sloprovisioning_pg(self, url):
        return_object = self.data.pg_list
        for pg in self.data.portgroup:
            if pg['portGroupId'] in url:
                return_object = pg
                break
        return return_object

    def _sloprovisioning_port(self, url):
        return_object = None
        if 'port/' in url:
            for port in self.data.port_list:
                if (port['symmetrixPort']['symmetrixPortKey']['directorId']
                        in url):
                    return_object = port
                    break
        elif 'port' in url:
            return_object = self.data.port_key_list
        else:
            if self.data.director_id1 in url:
                return_object = self.data.director_info
            else:
                return_object = self.data.director_list
        return return_object

    def _sloprovisioning_ig(self, url):
        return_object = self.data.host_list
        for ig in self.data.initiatorgroup:
            if ig['hostId'] in url:
                return_object = ig
                break
        return return_object

    def _sloprovisioning_hg(self, url):
        if self.data.hostgroup_id in url:
            return_object = self.data.hostgroup
        else:
            return_object = self.data.hostgroup_list
        return return_object

    def _sloprovisioning_initiator(self, url):
        return_object = self.data.initiator_list[2]
        if self.data.wwpn1 in url:
            return_object = self.data.initiator_list[0]
        elif self.data.initiator in url:
            return_object = self.data.initiator_list[1]
        return return_object

    def _sloprovisioning_srp(self, url):
        return_object = self.data.srp_list
        if self.data.srp in url:
            if 'compressibility' in url:
                return_object = self.data.compr_report
            else:
                return_object = self.data.srp_details
        return return_object

    def _replication(self, url):
        return_object = self.data.rep_info
        if 'storagegroup' in url:
            return_object = self._replication_sg(url)
        elif 'rdf_group' in url:
            if self.data.device_id in url:
                return_object = self.data.rdf_group_vol_details
            elif 'volume' in url:
                return_object = self.data.rdf_group_vol_list
            elif self.data.rdf_group_no in url:
                return_object = self.data.rdf_group_details
            else:
                return_object = self.data.rdf_group_list
        elif 'capabilities' in url:
            return_object = self.data.capabilities
        return return_object

    def _replication_sg(self, url):
        return_object = self.data.sg_list_rep
        if 'generation' in url:
            if self.data.group_snapshot_name in url:
                return_object = self.data.group_snap_vx
            else:
                return_object = self.data.sg_snap_gen_list
        elif 'snapshot' in url:
            return_object = self.data.sg_snap_list
        elif 'rdf_group' in url:
            return_object = self.data.sg_rdf_list
            if self.data.rdf_group_no in url:
                for sg in self.data.sg_rdf_details:
                    if sg['storageGroupName'] in url:
                        return_object = sg
                        break
        elif self.data.storagegroup_name in url:
            return_object = self.data.sg_details_rep[0]
        return return_object

    def _migration(self, url):
        return_object = self.data.migration_info
        if 'storagegroup' in url:
            return_object = self._migration_sg(url)
        elif 'environment' in url:
            env_name = self.data.migration_environment_list['arrayId'][0]
            if '/environment/' + env_name in url:
                return_object = self.data.migration_environment_details
            else:
                return_object = self.data.migration_environment_list
        elif 'capabilities' in url:
            return_object = self.data.migration_capabilities
        return return_object

    def _migration_sg(self, url):
        return_object = self.data.sg_list_migration
        if self.data.sg_list_migration['name'][0] in url:
            return_object = self.data.sg_details_migration[0]
        return return_object

    def _system(self, url):
        return_object = self.data.symm_list
        if 'job' in url:
            for job in self.data.job_list:
                if job['jobId'] in url:
                    return_object = job
                    break
        elif 'version' in url:
            return_object = self.data.server_version
        else:
            for symm in self.data.symmetrix:
                if symm['symmetrixId'] in url:
                    return_object = symm
                    break
        return return_object

    def _post_or_put(self, url, payload):
        return_object = self.data.job_list[0]
        status_code = 201
        if self.data.failed_resource in url:
            status_code = 500
            return_object = self.data.job_list[2]
        elif payload:
            payload = ast.literal_eval(payload)
            if self.data.failed_resource in payload.values():
                status_code = 500
                return_object = self.data.job_list[2]
            if payload.get('executionOption'):
                status_code = 202
        return status_code, return_object

    def _delete(self, url):
        if self.data.failed_resource in url:
            status_code = 500
            return_object = self.data.job_list[2]
        else:
            status_code = 204
            return_object = None
        return status_code, return_object

    def session(self):
        """session."""
        return FakeRequestsSession()


class FakeConfigFile(object):
    """Fake config file."""

    def __init__(self):
        """__init__."""

    @staticmethod
    def create_fake_config_file(
            user='smc', password='smc', ip='10.0.0.75',
            port='8443', array=tpd.CommonData.array, verify=False):
        """create_fake_config_file."""
        data = ('[setup] \nusername={user} \npassword={password} '
                '\nserver_ip={ip}'
                '\nport={port} \narray={array} \nverify={verify}'
                .format(user=user, password=password,
                        ip=ip, port=port, array=array, verify=verify))
        filename = 'PyU4V.conf'
        config_file_path = os.path.normpath(
            tempfile.mkdtemp() + '/' + filename)

        with open(config_file_path, 'w') as f:
            f.writelines(data)
        return config_file_path
