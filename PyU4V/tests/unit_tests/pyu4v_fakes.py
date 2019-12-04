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
"""pyu4v_fakes.py."""

import ast
import os
import requests
import tempfile

from PyU4V.tests.unit_tests.pyu4v_common_data import CommonData
from PyU4V.tests.unit_tests.pyu4v_performance_data import PerformanceData
from PyU4V.utils import performance_constants as pc


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

    def __init__(self):
        """__init__."""
        self.data = CommonData()
        self.p_data = PerformanceData()

    def request(self, method, url, params=None, data=None, timeout=None):
        """request."""
        return_object = ''
        status_code = 200
        if 'performance' in url:
            status_code, return_object = self._performance_call(url)

        elif method == 'GET':
            status_code, return_object = self._get_request(url, params)

        elif method == 'POST' or method == 'PUT':
            if 'system' in url and 'health' in url:
                status_code = 200
                return_object = self.data.perform_health_check_response
            else:
                status_code, return_object = self._post_or_put(url, data)

        elif method == 'DELETE':
            status_code, return_object = self._delete(url)

        elif method == 'TIMEOUT':
            raise requests.exceptions.Timeout

        elif method == 'HTTPERROR':
            raise requests.exceptions.HTTPError

        elif method == 'SSLERROR':
            raise requests.exceptions.SSLError

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
            if 'director' in url:
                return_object = self._system_port(url)
            elif 'health' in url:
                return_object = self._system_health(url)
            elif 'disk' in url:
                return_object = self._system_disk(url)
            elif 'tag' in url:
                return_object = self._system_tag(url)
            else:
                return_object = self._system(url)

        elif 'headroom' in url:
            return_object = self.data.headroom_array

        elif 'Iterator' in url:
            if 'page' in url:
                return_object = self.data.iterator_page
            else:
                return_object = self.data.vol_with_pages

        elif 'wlp' in url:
            return_object = self.data.wlp_info

        elif 'version' in url:
            return_object = self.data.server_version

        return status_code, return_object

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
        else:
            for symm in self.data.symmetrix:
                if symm['symmetrixId'] in url:
                    return_object = symm
                    break
        return return_object

    def _system_disk(self, url):
        uri_components = url.split('/')
        return_object = list()
        if 'disk' == uri_components[-1]:
            return_object = self.data.disk_list
        if 'disk' == uri_components[-2]:
            return_object = self.data.disk_info
        return return_object

    def _system_health(self, url):
        uri_components = url.split('/')
        return_object = list()

        if 'health' == uri_components[-1]:
            return_object = self.data.array_health
        if 'health_check' in uri_components[-1]:
            return_object = self.data.array_health_check_list
        if 'health_check' in uri_components[-2]:
            return_object = self.data.health_check_response
        return return_object

    def _system_tag(self, url):
        uri_components = url.split('/')
        return_object = list()
        if 'tag' == uri_components[-1]:
            return_object = self.data.tag_list
        if 'tag' == uri_components[-2]:
            return_object = self.data.tagged_objects
        return return_object

    def _system_port(self, url):

        uri_components = url.split('/')
        return_object = list()

        if 'director' in uri_components[-1]:
            return_object = self.data.director_list
        elif 'director' in uri_components[-2]:
            if self.data.director_id1 in url:
                return_object = self.data.director_info

        if 'port' in uri_components[-1]:
            return_object = self.data.port_key_list
        elif 'port' in uri_components[-2]:
            for port in self.data.port_list:
                if (port['symmetrixPort']['symmetrixPortKey']['directorId']
                        in url):
                    return_object = port

        return return_object

    def _performance_call(self, url):
        uri_components = list(filter(None, url.split('/')))
        performance_section = uri_components[-1]
        category = uri_components[-2]
        return_object = list()
        status_code = 200

        if pc.METRICS == performance_section:
            return_object = self.p_data.perf_metrics_resp
        elif pc.KEYS == performance_section:
            if pc.ARRAY == category:
                return_object = self.p_data.array_keys
            elif pc.BE_DIR == category:
                return_object = self.p_data.be_dir_keys
            elif pc.BE_EMU == category:
                return_object = self.p_data.be_emu_keys
            elif pc.BE_PORT == category:
                return_object = self.p_data.be_port_keys
            elif pc.BOARD == category:
                return_object = self.p_data.board_keys
            elif pc.CACHE_PART == category:
                return_object = self.p_data.cache_partition_keys
            elif pc.CORE == category:
                return_object = self.p_data.core_keys
            elif pc.DB == category:
                return_object = self.p_data.database_keys
            elif pc.DEV_GRP == category:
                return_object = self.p_data.device_group_keys
            elif pc.DISK == category:
                return_object = self.p_data.disk_keys
            elif pc.DISK_GRP == category:
                return_object = self.p_data.disk_group_keys
            elif pc.DISK_TECH_POOL == category:
                return_object = self.p_data.disk_tech_pool_keys
            elif pc.EDS_DIR == category:
                return_object = self.p_data.eds_dir_keys
            elif pc.EDS_EMU == category:
                return_object = self.p_data.eds_emu_keys
            elif pc.EXT_DIR == category:
                return_object = self.p_data.ext_dir_keys
            elif pc.EXT_DISK == category:
                return_object = self.p_data.external_disk_id
            elif pc.EXT_DISK_GRP == category:
                return_object = self.p_data.ext_disk_group_keys
            elif pc.FE_DIR == category:
                return_object = self.p_data.fe_dir_keys
            elif pc.FE_EMU == category:
                return_object = self.p_data.fe_emu_keys
            elif pc.FE_PORT == category:
                return_object = self.p_data.fe_port_keys
            elif pc.FICON_EMU == category:
                return_object = self.p_data.ficon_emu_keys
            elif pc.FICON_EMU_THR == category:
                return_object = self.p_data.ficon_emu_thread_keys
            elif pc.FICON_PORT_THR == category:
                return_object = self.p_data.ficon_port_thread_keys
            elif pc.HOST == category:
                return_object = self.p_data.host_keys
            elif pc.IM_DIR == category:
                return_object = self.p_data.im_dir_keys
            elif pc.IM_EMU == category:
                return_object = self.p_data.im_emu_keys
            elif pc.INIT == category:
                return_object = self.p_data.init_keys
            elif pc.INIT_BY_PORT == category:
                return_object = self.p_data.init_by_port_keys
            elif pc.IP_INT == category:
                return_object = self.p_data.ip_interface_keys
            elif pc.ISCSI_TGT == category:
                return_object = self.p_data.iscsi_target_keys
            elif pc.PG == category:
                return_object = self.p_data.port_group_keys
            elif pc.RDFA == category:
                return_object = self.p_data.rdfa_keys
            elif pc.RDFS == category:
                return_object = self.p_data.rdfs_keys
            elif pc.RDF_DIR == category:
                return_object = self.p_data.rdf_dir_keys
            elif pc.RDF_EMU == category:
                return_object = self.p_data.rdf_emu_keys
            elif pc.RDF_PORT == category:
                return_object = self.p_data.rdf_port_keys
            elif pc.STORAGE_CONT == category:
                return_object = self.p_data.storage_container_keys
            elif pc.SG == category:
                return_object = self.p_data.storage_group_keys
            elif pc.SG_BY_POOL == category:
                return_object = self.p_data.storage_group_by_pool_keys
            elif pc.SRP == category:
                return_object = self.p_data.srp_keys
            elif pc.STORAGE_RES == category:
                return_object = self.p_data.storage_resource_keys
            elif pc.STORAGE_RES_BY_POOL == category:
                return_object = self.p_data.storage_resource_by_pool_keys
            elif pc.THIN_POOL == category:
                return_object = self.p_data.thin_pool_keys
        else:
            # Days to full settings
            if pc.DAYS_TO_FULL in uri_components:
                return_object = self.p_data.days_to_full_resp
            # Threshold Settings
            elif pc.THRESHOLD in uri_components:
                if pc.CATEGORIES in uri_components:
                    return_object = self.p_data.threshold_cat_resp
                elif pc.LIST in uri_components:
                    return_object = self.p_data.threshold_settings_resp
                    return_object[pc.CATEGORY] = uri_components[-1]
            elif pc.REG_DETAILS in uri_components:
                return_object = self.p_data.array_reg_details_enabled

        return status_code, return_object

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

    @staticmethod
    def session():
        """session."""
        return FakeRequestsSession()


class FakeConfigFile(object):
    """Fake config file."""

    def __init__(self):
        """__init__."""

    @staticmethod
    def create_fake_config_file(
            user='smc', password='smc', ip='10.0.0.75', port='8443',
            array=CommonData.array, verify=False, verify_key=True,
            write_log_config=False, remote_array=CommonData.remote_array):
        """create_fake_config_file."""
        data = '[setup]'

        if user:
            data += '\nusername={user}'.format(user=user)
        if password:
            data += '\npassword={password}'.format(password=password)
        if ip:
            data += '\nserver_ip={ip}'.format(ip=ip)
        if port:
            data += '\nport={port}'.format(port=port)
        if array:
            data += '\narray={array}'.format(array=array)
        if verify_key:
            data += '\nverify={verify}'.format(verify=verify)
        if remote_array:
            data += '\nremote_array={remote_array}'.format(
                remote_array=remote_array)

        if write_log_config:
            data += (
                '\n[loggers]\nkeys=root,PyU4V'
                '\n[logger_root]\nhandlers=consoleHandler'
                '\n[logger_PyU4V]\nlevel=INFO\nqualname=PyU4V\npropagate=0'
                '\nhandlers=consoleHandler'
                '\n[handlers]\nkeys=consoleHandler'
                '\n[handler_consoleHandler]\nclass=StreamHandler'
                '\nformatter=simpleFormatter\nargs=(sys.stdout,)'
                '\n[formatters]\nkeys=simpleFormatter'
                '\n[formatter_simpleFormatter]'
                '\nformat='
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        os.umask(0o77)
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'PyU4V.conf')
        try:
            with open(path, 'w') as tmp:
                tmp.writelines(data)
        except IOError as e:
            print('Error writing file: {msg}'.format(msg=e))

        return path, tmpdir

    @staticmethod
    def delete_fake_config_file(file_path, dir_path):
        """Delete fake config file and directory."""
        try:
            os.remove(file_path)
        except IOError:
            pass
        finally:
            os.umask(0o77)
            os.rmdir(dir_path)
