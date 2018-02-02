# The MIT License (MIT)
# Copyright (c) 2018 Dell Inc. or its subsidiaries.

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
import tempfile

import mock
import requests
import testtools

from PyU4V import common
from PyU4V import performance
from PyU4V import provisioning
from PyU4V import replication
from PyU4V import rest_requests
from PyU4V import univmax_conn
from PyU4V.utils import exception


class CommonData(object):
    # array info
    array = '000197800123'
    remote_array = '000197800124'
    srp = 'SRP_1'
    slo = 'Diamond'
    workload = 'DSS'
    port_group_name_f = 'PU-fibre-PG'
    port_group_name_i = 'PU-iscsi-PG'
    masking_view_name_f = 'PU-HostX-F-MV'
    masking_view_name_i = 'PU-HostX-I-MV'
    initiatorgroup_name_f = 'PU-HostX-F-IG'
    initiatorgroup_name_i = 'PU-HostX-I-IG'
    hostgroup_id = 'PU-HostGroup-F-HG'
    storagegroup_name = 'PU-mystoragegroup-SG'
    storagegroup_list = [storagegroup_name]
    failed_resource = 'PU-failed-resource'
    volume_wwn = '600000345'
    device_id = '00001'
    device_id2 = '00002'
    device_id3 = '00003'
    rdf_group_name = '23_24_007'
    rdf_group_no = '70'
    u4v_version = '84'
    parent_sg = 'PU-HostX-SG'
    storagegroup_name_1 = 'PU-mystoragegroup1-SG'
    storagegroup_name_2 = 'PU-mystoragegroup2-SG'
    group_snapshot_name = 'Grp_snapshot'
    target_group_name = 'Grp_target'
    # director port info
    director_id1 = "FA-1D"
    port_id1 = "4"
    director_id2 = "SE-4E"
    port_id2 = "0"
    port_key1 = {"directorId": director_id1, "portId": port_id1}
    port_key2 = {"directorId": director_id2, "portId": port_id2}

    # connector info
    wwpn1 = "123456789012345"
    wwpn2 = "123456789054321"
    wwnn1 = "223456789012345"
    initiator = 'iqn.1993-08.org.debian: 01: 222'
    ip, ip2 = u'123.456.7.8', u'123.456.7.9'
    iqn = u'iqn.1992-04.com.emc:600009700bca30c01e3e012e00000001,t,0x0001'
    iqn2 = u'iqn.1992-04.com.emc:600009700bca30c01e3e012e00000002,t,0x0001'

    # vmax data
    # sloprovisioning
    compression_info = {"symmetrixId": ["000197800128"]}
    director_info = {"directorId": director_id1,
                     "director_slot_number": 1,
                     "availability": "Online",
                     "num_of_ports": 5}
    director_list = {"directorId": [director_id1, director_id2]}
    host_list = {"hostId": [initiatorgroup_name_f, initiatorgroup_name_i]}
    initiatorgroup = [{"initiator": [wwpn1],
                       "hostId": initiatorgroup_name_f,
                       "maskingview": [masking_view_name_f]},
                      {"initiator": [initiator],
                       "hostId": initiatorgroup_name_i,
                       "maskingview": [masking_view_name_i]}]

    hostgroup = {"num_of_hosts": 1,
                 "num_of_initiators": 4,
                 "num_of_masking_views": 1,
                 "host": [initiatorgroup[0]],
                 "type": "Fibre",
                 "hostGroupId": hostgroup_id,
                 "maskingview": [masking_view_name_f]}

    hostgroup_list = { "hostGroupId": [hostgroup_id]}

    initiator_list = [{"host": initiatorgroup_name_f,
                       "initiatorId": wwpn1,
                       "maskingview": [masking_view_name_f]},
                      {"host": initiatorgroup_name_i,
                       "initiatorId": initiator,
                       "maskingview": [masking_view_name_i]},
                      {"initiatorId": [
                          "FA-1D:4:" + wwpn1,
                          "SE-4E:0:" + initiator]}]

    maskingview = [{"maskingViewId": masking_view_name_f,
                    "portGroupId": port_group_name_f,
                    "storageGroupId": storagegroup_name,
                    "hostId": initiatorgroup_name_f,
                    "maskingViewConnection": [
                        {"host_lun_address": "0003"}]},
                   {"maskingViewId": masking_view_name_i,
                    "portGroupId": port_group_name_i,
                    "storageGroupId": storagegroup_name_1,
                    "hostId": initiatorgroup_name_i,
                    "maskingViewConnection": [
                        {"host_lun_address": "0003"}]},
                   {"maskingViewId": [masking_view_name_f,
                                      masking_view_name_i]}]

    portgroup = [{"portGroupId": port_group_name_f,
                  "symmetrixPortKey": [
                      {"directorId": director_id1,
                       "portId": "FA-1D:4"}],
                  "maskingview": [masking_view_name_f]},
                 {"portGroupId": port_group_name_i,
                  "symmetrixPortKey": [
                      {"directorId": director_id2,
                       "portId": "SE-4E:0"}],
                  "maskingview": [masking_view_name_i]}]

    port_key_list = {"symmetrixPortKey": [port_key1, port_key2]}

    port_list = [
        {"symmetrixPort": {"num_of_masking_views": 1,
                           "maskingview": [masking_view_name_f],
                           "identifier": wwnn1,
                           "symmetrixPortKey": port_key1,
                           "portgroup": [port_group_name_f]}},
        {"symmetrixPort": {"identifier": initiator,
                           "symmetrixPortKey": port_key2,
                           "ip_addresses": [ip],
                           "num_of_masking_views": 1,
                           "maskingview": [masking_view_name_i],
                           "portgroup": [port_group_name_i]}}]

    sg_details = [{"srp": srp,
                   "num_of_vols": 2,
                   "cap_gb": 2,
                   "storageGroupId": storagegroup_name,
                   "slo": slo,
                   "workload": workload},
                  {"srp": srp,
                   "num_of_vols": 2,
                   "cap_gb": 2,
                   "storageGroupId": storagegroup_name_1,
                   "slo": slo,
                   "workload": workload,
                   "maskingview": [masking_view_name_f],
                   "parent_storage_group": [parent_sg]},
                  {"srp": srp,
                   "num_of_vols": 2,
                   "cap_gb": 2,
                   "storageGroupId": storagegroup_name_2,
                   "slo": slo,
                   "workload": workload,
                   "maskingview": [masking_view_name_i]}]

    sg_details_rep = [{"childNames": [],
                       "numDevicesNonGk": 2,
                       "isLinkTarget": False,
                       "rdf": True,
                       "capacityGB": 2.0,
                       "name": storagegroup_name,
                       "snapVXSnapshots": ['6560405d-752f5a139'],
                       "symmetrixId": array,
                       "numSnapVXSnapshots": 1}]

    sg_rdf_details = [{"storageGroupName": storagegroup_name,
                       "symmetrixId": array,
                       "modes": ["Synchronous"],
                       "rdfGroupNumber": rdf_group_no,
                       "states": ["Synchronized"]}]

    sg_list = {"storageGroupId": [storagegroup_name,
                                  storagegroup_name_1,
                                  storagegroup_name_2]}

    sg_list_rep = [storagegroup_name]

    srp_details = {"srpSloDemandId": ["Bronze", "Diamond", "Gold",
                                      "None", "Optimized", "Silver"],
                   "srpId": srp,
                   "total_used_cap_gb": 5244.7,
                   "total_usable_cap_gb": 20514.4,
                   "total_subscribed_cap_gb": 84970.1,
                   "fba_used_capacity": 5244.7,
                   "reserved_cap_percent": 10}

    volume_details = [{"cap_gb": 2,
                       "num_of_storage_groups": 1,
                       "volumeId": device_id,
                       "volume_identifier": 'my-vol',
                       "wwn": volume_wwn,
                       "snapvx_target": 'false',
                       "snapvx_source": 'false',
                       "storageGroupId": [storagegroup_name]},
                      {"cap_gb": 1,
                       "num_of_storage_groups": 1,
                       "volumeId": device_id2,
                       "volume_identifier": "my-vol2",
                       "wwn": '600012345',
                       "storageGroupId": [storagegroup_name_1]},
                      {"cap_gb": 1,
                       "num_of_storage_groups": 0,
                       "volumeId": device_id3,
                       "volume_identifier": 'my-vol3',
                       "wwn": '600012345'}]

    volume_list = [
        {"resultList": {"result": [{"volumeId": device_id}]}},
        {"resultList": {"result": [{"volumeId": device_id2}]}},
        {"resultList": {"result": [{"volumeId": device_id},
                                   {"volumeId": device_id2}]}}]

    workloadtype = {"workloadId": ["OLTP", "OLTP_REP", "DSS", "DSS_REP"]}
    slo_details = {"sloId": ["Bronze", "Diamond", "Gold",
                             "Optimized", "Platinum", "Silver"]}

    # replication
    capabilities = {"symmetrixCapability": [{"rdfCapable": True,
                                             "snapVxCapable": True,
                                             "symmetrixId": "0001111111"},
                                            {"symmetrixId": array,
                                             "snapVxCapable": True,
                                             "rdfCapable": True}]}
    group_snap_vx = {"generation": 0,
                     "isLinked": False,
                     "numUniqueTracks": 0,
                     "isRestored": False,
                     "name": group_snapshot_name,
                     "numStorageGroupVolumes": 1,
                     "state": ["Established"],
                     "timeToLiveExpiryDate": "N/A",
                     "isExpired": False,
                     "numSharedTracks": 0,
                     "timestamp": "00:30:50 Fri, 02 Jun 2017 IST +0100",
                     "numSourceVolumes": 1
                     }
    group_snap_vx_1 = {"generation": 0,
                       "isLinked": False,
                       "numUniqueTracks": 0,
                       "isRestored": False,
                       "name": group_snapshot_name,
                       "numStorageGroupVolumes": 1,
                       "state": ["Copied"],
                       "timeToLiveExpiryDate": "N/A",
                       "isExpired": False,
                       "numSharedTracks": 0,
                       "timestamp": "00:30:50 Fri, 02 Jun 2017 IST +0100",
                       "numSourceVolumes": 1,
                       "linkedStorageGroup":
                           {"name": target_group_name,
                            "percentageCopied": 100},
                       }
    grp_snapvx_links = [{"name": target_group_name,
                         "percentageCopied": 100},
                        {"name": "another-target",
                         "percentageCopied": 90}]

    rdf_group_list = {"rdfGroupID": [{"rdfgNumber": rdf_group_no,
                                      "label": rdf_group_name}]}
    rdf_group_details = {"modes": ["Synchronous"],
                         "remoteSymmetrix": remote_array,
                         "label": rdf_group_name,
                         "type": "Dynamic",
                         "numDevices": 1,
                         "remoteRdfgNumber": rdf_group_no,
                         "rdfgNumber": rdf_group_no}
    rdf_group_vol_details = {"remoteRdfGroupNumber": rdf_group_no,
                             "localSymmetrixId": array,
                             "volumeConfig": "RDF1+TDEV",
                             "localRdfGroupNumber": rdf_group_no,
                             "localVolumeName": device_id,
                             "rdfpairState": "Synchronized",
                             "remoteVolumeName": device_id2,
                             "localVolumeState": "Ready",
                             "rdfMode": "Synchronous",
                             "remoteVolumeState": "Write Disabled",
                             "remoteSymmetrixId": remote_array}

    # system
    job_list = [{"status": "SUCCEEDED",
                 "jobId": "12345",
                 "result": "created",
                 "resourceLink": "storagegroup/%s" % storagegroup_name},
                {"status": "RUNNING", "jobId": "55555"},
                {"status": "FAILED", "jobId": "09999"}]
    symmetrix = [{"symmetrixId": array,
                  "model": "VMAX250F",
                  "ucode": "5977.1091.1092"}]
    symm_list = {"symmetrixId": [array, remote_array]}
    server_version = {"version": "V8.4.0.6"}

    # wlp
    headroom = {"headroom": [{"headroomCapacity": 20348.29}]}
    wlp = {"symmetrixDetails": {"processingDetails": {
        "lastProcessedSpaTimestamp": 1517408700000,
        "nextUpdate": 1038},
        "spaRegistered": 'true'}}

    iterator_page = {"result": [{}, {}]}


class FakeResponse(object):

    def __init__(self, status_code, return_object):
        self.status_code = status_code
        self.return_object = return_object

    def json(self):
        if self.return_object:
            return self.return_object
        else:
            raise ValueError


class FakeRequestsSession(object):

    def __init__(self, *args, **kwargs):
        self.data = CommonData()

    def request(self, method, url, params=None, data=None, timeout=None):
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
            elif 'srp' in url:
                return_object = self.data.srp_details
            elif 'workloadtype' in url:
                return_object = self.data.workloadtype
            elif 'compressionCapable' in url:
                return_object = self.data.compression_info
            elif '/slo/' in url:
                return_object = self.data.slo_details
            else:
                return_object = self.data.symm_list

        elif 'replication' in url:
            return_object = self._replication(url)

        elif 'system' in url:
            return_object = self._system(url)

        elif 'headroom' in url:
            return_object = self.data.headroom

        elif 'Iterator' in url:
            return_object = self.data.iterator_page

        elif 'wlp' in url:
            return_object = self.data.wlp

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
        return_object = None
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

    def _replication(self, url):
        return_object = None
        if 'storagegroup' in url:
            return_object = self._replication_sg(url)
        elif 'rdf_group' in url:
            if self.data.device_id in url:
                return_object = self.data.rdf_group_vol_details
            elif self.data.rdf_group_no in url:
                return_object = self.data.rdf_group_details
            else:
                return_object = self.data.rdf_group_list
        elif 'capabilities' in url:
            return_object = self.data.capabilities
        return return_object

    def _replication_sg(self, url):
        return_object = None
        if 'generation' in url:
            return_object = self.data.group_snap_vx
        elif 'rdf_group' in url:
            for sg in self.data.sg_rdf_details:
                if sg['storageGroupName'] in url:
                    return_object = sg
                    break
        elif 'storagegroup' in url:
            return_object = self.data.sg_details_rep[0]
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
        return FakeRequestsSession()


class FakeConfigFile(object):

    def __init__(self):
        """"""

    @staticmethod
    def create_fake_config_file(
            user='smc', password='smc', ip='10.0.0.75',
            port='8443', array=CommonData.array, verify=False):
        data = ("[setup] \nusername={} \npassword={} \nserver_ip={}"
                "\nport={} \narray={} \nverify={}".format(
                    user, password, ip, port, array, verify))
        filename = 'PyU4V.conf'
        config_file_path = os.path.normpath(
            tempfile.mkdtemp() + '/' + filename)

        with open(config_file_path, 'w') as f:
            f.writelines(data)
        return config_file_path


class PyU4VCommonTest(testtools.TestCase):

    def setUp(self):
        super(PyU4VCommonTest, self).setUp()
        self.data = CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=FakeRequestsSession())
        config_file = FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn(array_id=self.data.array)
        self.common = self.conn.common

    def test_wait_for_job_complete(self):
        _, _, status, _ = self.common.wait_for_job_complete(
            self.data.job_list[0])
        self.assertEqual('SUCCEEDED', status)

    def test_check_status_code_success(self):
        self.common.check_status_code_success(
            'test-success', 201, '')
        self.assertRaises(exception.ResourceNotFoundException,
                          self.common.check_status_code_success,
                          'test-404', 404, '')
        self.assertRaises(exception.UnauthorizedRequestException,
                          self.common.check_status_code_success,
                          'test-401', 401, '')
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.common.check_status_code_success,
                          'test-500', 500, '')

    @mock.patch.object(common.CommonFunctions, 'wait_for_job_complete',
                       side_effect=[(0, '', '', ''), (1, '', '', '')])
    def test_wait_for_job(self, mock_complete):
        # Not an async job
        self.common.wait_for_job('sync-job', 200, {})
        mock_complete.assert_not_called()
        # Async, completes successfully
        self.common.wait_for_job('sync-job', 202, {})
        mock_complete.assert_called_once()
        # Async, job fails
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.common.wait_for_job, 'sync-job', 202, {})

    def test_build_uri(self):
        resource_name_list = [None, self.data.device_id, self.data.device_id]
        version_list = [None, '', '90']
        for x in range(0, 3):
            self.common._build_uri(
                self.data.array, 'sloprovisioning', 'volume',
                resource_name=resource_name_list[x], version=version_list[x])

    def test_get_request(self):
        message = self.common.get_request(
            '/84/system/version', 'version', params=None)
        self.assertEqual(self.data.server_version, message)

    def test_get_resource(self):
        message = self.common.get_resource(
            self.data.array, 'sloprovisioning', 'volume',
            resource_name=None, params=None)
        self.assertEqual(self.data.volume_list[2], message)

    def test_create_resource(self):
        message = self.common.create_resource(
            self.data.array, 'sloprovisioning', 'storagegroup', {})
        self.assertEqual(self.data.job_list[0], message)

    def test_modify_resource(self):
        message = self.common.modify_resource(
            self.data.array, 'sloprovisioning', 'storagegroup', {})
        self.assertEqual(self.data.job_list[0], message)

    def test_delete_resource(self):
        self.common.delete_resource(
            self.data.array, 'sloprovisioning',
            'storagegroup', self.data.storagegroup_name)

    def test_get_uni_version(self):
        version, major_version = self.common.get_uni_version()
        self.assertEqual(self.data.server_version['version'], version)
        self.assertEqual(self.data.u4v_version, major_version)

    def test_get_array_list(self):
        array_list = self.common.get_array_list()
        self.assertEqual(self.data.symm_list['symmetrixId'], array_list)

    def test_get_v3_or_newer_array_list(self):
        array_list = self.common.get_v3_or_newer_array_list()
        self.assertEqual(self.data.symm_list['symmetrixId'], array_list)

    def test_get_array(self):
        array_details = self.common.get_array(self.data.array)
        self.assertEqual(self.data.symmetrix[0], array_details)

    def test_get_iterator_page_list(self):
        iterator_page = self.common.get_iterator_page_list('123', 1, 1000)
        self.assertEqual(self.data.iterator_page['result'], iterator_page)

    def test_get_wlp_timestamp(self):
        wlp_timestamp = self.common.get_wlp_information(self.data.array)
        self.assertEqual(self.data.wlp['symmetrixDetails'], wlp_timestamp)

    def test_get_headroom(self):
        headroom = self.common.get_headroom(self.data.array,
                                            self.data.workload)
        self.assertEqual(self.data.headroom['headroom'], headroom)


class PyU4VPerformanceTest(testtools.TestCase):
    pass


class PyU4VProvisioningTest(testtools.TestCase):

    def setUp(self):
        super(PyU4VProvisioningTest, self).setUp()
        self.data = CommonData()
        rest_requests.RestRequests.establish_rest_session = mock.Mock(
            return_value=FakeRequestsSession())
        config_file = FakeConfigFile.create_fake_config_file()
        univmax_conn.file_path = config_file
        self.conn = univmax_conn.U4VConn(array_id=self.data.array)
        self.common = self.conn.common
        self.provisioning = self.conn.provisioning

    def test_get_director(self):
        dir_details = self.provisioning.get_director(self.data.director_id1)
        self.assertEqual(self.data.director_info, dir_details)

    def test_get_director_list(self):
        dir_list = self.provisioning.get_director_list()
        self.assertEqual(self.data.director_list['directorId'], dir_list)

    def test_get_director_port(self):
        port_details = self.provisioning.get_director_port(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.port_list[0], port_details)

    def test_get_director_port_list(self):
        port_key_list = self.provisioning.get_director_port_list(
            self.data.director_id1)
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_port_identifier(self):
        wwn = self.provisioning.get_port_identifier(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.wwnn1, wwn)

    def test_get_host(self):
        host_details = self.provisioning.get_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual(self.data.initiatorgroup[0], host_details)

    def test_get_host_list(self):
        host_list = self.provisioning.get_host_list()
        self.assertEqual(self.data.host_list['hostId'], host_list)

    def test_create_host(self):
        host_flags = {"consistent_lun": 'true'}
        data = [self.data.wwnn1, self.data.wwpn2]
        with mock.patch.object(self.provisioning, 'create_resource') as \
                mock_create:
            self.provisioning.create_host(
                self.data.initiatorgroup_name_i, host_flags=host_flags,
                initiator_list=data, async=True)
            new_ig_data = {"hostId": self.data.initiatorgroup_name_i,
                           "initiatorId": data,
                           "hostFlags": host_flags,
                           "executionOption": "ASYNCHRONOUS"}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'host', new_ig_data)
            mock_create.reset_mock()
            self.provisioning.create_host(
                self.data.initiatorgroup_name_i)
            new_ig_data2 = {"hostId": self.data.initiatorgroup_name_i}
            mock_create.assert_called_once_with(
                self.data.array, 'sloprovisioning', 'host', new_ig_data2)

    def test_modify_host(self):
        host_name = self.data.initiatorgroup_name_i
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_host(
                host_name, host_flag_dict={"consistent_lun": 'true'})
            self.provisioning.modify_host(
                host_name, remove_init_list=[self.data.wwnn1])
            self.provisioning.modify_host(
                host_name, add_init_list=[self.data.wwnn1])
            self.provisioning.modify_host(host_name, new_name='my-new-name')
            self.assertEqual(4, mock_mod.call_count)
            self.assertRaises(exception.InvalidInputException,
                              self.provisioning.modify_host, host_name)

    def test_delete_host(self):
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_host(self.data.initiatorgroup_name_i)
            mock_delete.assert_called_once()

    def test_get_mvs_from_host(self):
        mv_list = self.provisioning.get_mvs_from_host(
            self.data.initiatorgroup_name_i)
        self.assertEqual([self.data.masking_view_name_i], mv_list)

    def test_get_initiator_ids_from_host(self):
        init_list = self.provisioning.get_initiator_ids_from_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual([self.data.wwpn1], init_list)

    def test_get_hostgroup(self):
        hg_details = self.provisioning.get_hostgroup(self.data.hostgroup_id)
        self.assertEqual(self.data.hostgroup, hg_details)

    def test_get_hostgroup_list(self):
        hg_list = self.provisioning.get_hostgroup_list()
        self.assertEqual(self.data.hostgroup_list['hostGroupId'], hg_list)
        with mock.patch.object(
                self.provisioning, 'get_resource',
                return_value={'some_key': 'some_value'}):
            hg_list = self.provisioning.get_hostgroup_list()
            self.assertEqual([], hg_list)

    def test_create_hostgroup(self):
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_hostgroup(
                self.data.hostgroup_id, [self.data.initiatorgroup_name_f],
                host_flags={'flag': 1}, async=True)
            self.provisioning.create_hostgroup(
                self.data.hostgroup_id, [self.data.initiatorgroup_name_f])
        self.assertEqual(2, mock_create.call_count)

    def test_modify_hostgroup(self):
        hostgroup_name = self.data.hostgroup_id
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_hostgroup(
                hostgroup_name, host_flag_dict={"consistent_lun": 'true'})
            self.provisioning.modify_hostgroup(
                hostgroup_name, remove_host_list=['host1'])
            self.provisioning.modify_hostgroup(
                hostgroup_name, add_host_list=['host2'])
            self.provisioning.modify_hostgroup(
                hostgroup_name, new_name='my-new-name')
            self.assertEqual(4, mock_mod.call_count)
            self.assertRaises(exception.InvalidInputException,
                              self.provisioning.modify_hostgroup,
                              hostgroup_name)

    def test_delete_hostgroup(self):
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_hostgroup(self.data.hostgroup_id)
            mock_delete.assert_called_once()

    def test_get_initiator(self):
        init_details = self.provisioning.get_initiator(self.data.wwpn1)
        self.assertEqual(self.data.initiator_list[0], init_details)

    def test_get_initiator_list(self):
        init_list = self.provisioning.get_initiator_list()
        self.assertEqual(
            self.data.initiator_list[2]['initiatorId'], init_list)

    def test_modify_initiator(self):
        initiator_name = self.data.wwpn1
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_initiator(
                initiator_name, remove_masking_entry='true')
            self.provisioning.modify_initiator(
                initiator_name, replace_init=self.data.wwpn2)
            self.provisioning.modify_initiator(
                initiator_name, rename_alias=(
                    'new node name', 'new port name'))
            self.provisioning.modify_initiator(
                initiator_name, set_fcid='my-new-name')
            self.provisioning.modify_initiator(
                initiator_name, initiator_flags={'my-flag': 'value'})
            self.assertEqual(5, mock_mod.call_count)
            self.assertRaises(
                exception.InvalidInputException,
                self.provisioning.modify_initiator, initiator_name)

    def test_is_initiator_in_host(self):
        check = self.provisioning.is_initiator_in_host(self.data.wwpn1)
        self.assertTrue(check)
        check = self.provisioning.is_initiator_in_host('fake-init')
        self.assertFalse(check)

    def test_get_initiator_group_from_initiator(self):
        found_ig_name = self.provisioning.get_initiator_group_from_initiator(
            self.data.wwpn1)
        self.assertEqual(self.data.initiatorgroup_name_f, found_ig_name)

    def test_get_masking_view_list(self):
        mv_list = self.provisioning.get_masking_view_list()
        self.assertEqual(self.data.maskingview[2]['maskingViewId'], mv_list)

    def test_get_masking_view(self):
        mv_details = self.provisioning.get_masking_view(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.maskingview[0], mv_details)

    def test_create_masking_view_existing_components(self):
        pg_name = self.data.port_group_name_f
        sg_name = self.data.storagegroup_name_2
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_masking_view_existing_components(
                pg_name, 'my_masking_view', sg_name,
                host_group_name=self.data.hostgroup_id, async=True)
            self.provisioning.create_masking_view_existing_components(
                pg_name, 'my_masking_view', sg_name, async=True,
                host_name=self.data.initiatorgroup_name_f)
        self.assertEqual(2, mock_create.call_count)
        self.assertRaises(
            exception.InvalidInputException,
            self.provisioning.create_masking_view_existing_components,
            pg_name, 'my_masking_view', sg_name)

    def test_get_masking_views_from_storage_group(self):
        mv_list = self.provisioning.get_masking_views_from_storage_group(
            self.data.storagegroup_name_1)
        self.assertEqual(self.data.sg_details[1]['maskingview'], mv_list)

    def test_get_masking_views_by_host(self):
        mv_list = self.provisioning.get_masking_views_by_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual(self.data.initiator_list[0]['maskingview'], mv_list)

    def test_get_element_from_masking_view_exception(self):
        with mock.patch.object(self.provisioning, 'get_masking_view',
                               return_value=None):
            self.assertRaises(exception.ResourceNotFoundException,
                              self.provisioning.get_element_from_masking_view,
                              self.data.masking_view_name_f)

    def test_get_common_masking_views(self):
        with mock.patch.object(
                self.provisioning, 'get_masking_view_list') as mock_list:
            self.provisioning.get_common_masking_views(
                self.data.port_group_name_f, self.data.initiatorgroup_name_f)
            mock_list.assert_called_once()

    def test_delete_masking_view(self):
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_masking_view(
                self.data.masking_view_name_f)
            mock_delete.assert_called_once()

    def test_rename_masking_view(self):
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.rename_masking_view(
                self.data.masking_view_name_f, 'new-name')
            mock_mod.assert_called_once()

    def test_get_host_from_maskingview(self):
        ig_id = self.provisioning.get_host_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.initiatorgroup_name_f, ig_id)

    def test_get_storagegroup_from_maskingview(self):
        sg_id = self.provisioning.get_storagegroup_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.storagegroup_name, sg_id)

    def test_get_portgroup_from_maskingview(self):
        pg_id = self.provisioning.get_portgroup_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.port_group_name_f, pg_id)

    def test_get_maskingview_connections(self):
        mv_conn_list = self.provisioning.get_maskingview_connections(
            self.data.masking_view_name_f)
        self.assertEqual(
            self.data.maskingview[0]['maskingViewConnection'], mv_conn_list)

    def test_find_host_lun_id_for_vol(self):
        host_lun_id = self.provisioning.find_host_lun_id_for_vol(
            self.data.masking_view_name_f, self.data.device_id)
        self.assertEqual(3, host_lun_id)
        with mock.patch.object(
                self.provisioning, 'get_maskingview_connections',
                side_effect=[[], [{'not_host_lun': 'value'}]]):
            for x in range(0, 2):
                host_lun_id2 = self.provisioning.find_host_lun_id_for_vol(
                    self.data.masking_view_name_f, self.data.device_id)
                self.assertIsNone(host_lun_id2)

    def test_get_port_list(self):
        port_key_list = self.provisioning.get_port_list()
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_portgroup(self):
        pass


class PyU4VReplicationTest(testtools.TestCase):
    pass


class PyU4VRestRequestsTest(testtools.TestCase):
    pass


class PyU4VUnivmaxConnTest(testtools.TestCase):
    pass
