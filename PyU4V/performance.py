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
"""performance.py."""
import csv
import logging
import time

from PyU4V.utils import constants

LOG = logging.getLogger(__name__)

GET = constants.GET
POST = constants.POST
PUT = constants.PUT


class PerformanceFunctions(object):
    """PerformanceFunctions."""

    def __init__(self, array_id, request, common, provisioning, u4v_version):
        """__init__."""
        self.end_date = int(round(time.time() * 1000))
        self.start_date = (self.end_date - 3600000)
        self.array_id = array_id
        self.request = request
        self.common = common
        self.provisioning = provisioning
        self.U4V_VERSION = u4v_version

    def get_fe_director_list(self):
        """Get list of all FE Directors.

        :returns: director list
        """
        target_uri = "/performance/FEDirector/keys"
        dir_payload = ({"symmetrixId": self.array_id})

        dir_response = self.request(
            target_uri, POST, request_object=dir_payload)
        dir_list = []
        for director in dir_response[0]['feDirectorInfo']:
            dir_list.append(director['directorId'])
        return dir_list

    def get_fe_port_list(self):
        """Get a list of all front end ports in the array.

        :returns: List of Directors and Ports
        """
        target_uri = "/performance/FEPort/keys"
        port_list = []
        dir_list = self.get_fe_director_list()
        for director in dir_list:
            port_payload = ({
                "symmetrixId": self.array_id,
                "directorId": director
            })
            port_details = {}
            port_response = self.request(
                target_uri, POST, request_object=port_payload)
            for port in port_response[0]['fePortInfo']:
                port_details[port['portId']] = director
            port_list.append(port_details)
        return port_list

    def get_days_to_full(self, category, array_id=None,):
        """Get days to full.

        Requests Days to Full Metrics from performance stats
        requires at least 10 Days of Performance data

        :returns: Requested stats
        """
        if not array_id:
            array_id = self.array_id

        target_uri = '/performance/daystofull'
        port_perf_payload = ({"symmetrixId": array_id, "category": category})
        return self.request(
            target_uri, POST, request_object=port_perf_payload)

    def get_fe_port_util_last4hrs(self, dir_id, port_id):
        """Get stats for last 4 hours.

        Currently only coded for one metric - can be adapted for multiple.

        :returns: Requested stats
        """
        end_date = int(round(time.time() * 1000))
        start_date = (end_date - 14400000)

        target_uri = '/performance/FEPort/metrics'
        port_perf_payload = ({"startDate": start_date,
                              "endDate": end_date,
                              "symmetrixId": self.array_id,
                              "directorId": dir_id,
                              "portId": port_id,
                              "dataFormat": "Average",
                              "metrics": ["PercentBusy"]})
        return self.request(
            target_uri, POST, request_object=port_perf_payload)

    def get_fe_director_metrics(self, start_date, end_date,
                                director, dataformat):
        """Get one or more metrics for front end directors.

        :param start_date: Date EPOCH Time in Milliseconds
        :param end_date: Date EPOCH Time in Milliseconds
        :param director: List of FE Directors
        :param dataformat: Average or Maximum
        :returns: JSON Payload, and RETURN CODE 200 for success
        """
        target_uri = "/performance/FEDirector/metrics"
        fe_director_param = ({
            "symmetrixId": self.array_id,
            "directorId": director,
            "endDate": end_date,
            "dataFormat": dataformat,
            "metrics": ['AvgRDFSWriteResponseTime', 'AvgReadMissResponseTime',
                        'AvgWPDiscTime', 'AvgTimePerSyscall', 'DeviceWPEvents',
                        'HostMBs', 'HitReqs', 'HostIOs', 'MissReqs',
                        'AvgOptimizedReadMissSize', 'OptimizedMBReadMisses',
                        'OptimizedReadMisses', 'PercentBusy', 'PercentHitReqs',
                        'PercentReadReqs', 'PercentReadReqHit',
                        'PercentWriteReqs', 'PercentWriteReqHit',
                        'QueueDepthUtilization', 'HostIOLimitIOs',
                        'HostIOLimitMBs', 'ReadReqs', 'ReadHitReqs',
                        'ReadMissReqs', 'Reqs', 'ReadResponseTime',
                        'WriteResponseTime', 'SlotCollisions', 'SyscallCount',
                        'Syscall_RDF_DirCounts', 'SyscallRemoteDirCounts',
                        'SystemWPEvents', 'TotalReadCount', 'TotalWriteCount',
                        'WriteReqs', 'WriteHitReqs', 'WriteMissReqs'],
            "startDate": start_date})

        return self.request(target_uri, POST, request_object=fe_director_param)

    def get_fe_port_metrics(self, start_date, end_date, director_id,
                            port_id, dataformat, metriclist):
        """Get one or more Metrics for Front end Director ports.

        The metric list can contain a list of one or more of PercentBusy,
        IOs, MBRead, MBWritten, MBs, AvgIOSize, SpeedGBs, MaxSpeedGBs,
        HostIOLimitIOs, HostIOLimitMBs.

        :param start_date: Date EPOCH Time in Milliseconds
        :param end_date: Date EPOCH Time in Milliseconds
        :param director_id: Director id
        :param port_id: port id
        :param dataformat: Average or Maximum
        :param metriclist: list of one or more metrics
        :return: JSON Payload, and RETURN CODE 200 for success
        """
        target_uri = "/performance/FEPort/metrics"
        fe_director_param = ({"symmetrixId": self.array_id,
                              "directorId": director_id,
                              "endDate": end_date,
                              "dataFormat": dataformat,
                              "metrics": [metriclist],
                              "portId": port_id,
                              "startDate": start_date})

        return self.request(
            target_uri, POST, request_object=fe_director_param)

    def get_array_metrics(self, start_date, end_date):
        """Get array metrics.

        Get all avaliable performance statistics for specified time
        period return in JSON.

        :param start_date: EPOCH Time
        :param end_date: Epoch Time
        :return: array_results_combined
        """
        target_uri = "/performance/Array/metrics"
        array_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'metrics': [
                'OverallCompressionRatio', 'OverallEfficiencyRatio',
                'PercentVPSaved', 'VPSharedRatio', 'VPCompressionRatio',
                'VPEfficiencyRatio', 'PercentSnapshotSaved',
                'SnapshotSharedRatio', 'SnapshotCompressionRatio',
                'SnapshotEfficiencyRatio', 'CopySlotCount', 'HostIOs',
                'HostReads', 'HostWrites', 'PercentReads', 'PercentWrites',
                'PercentHit', 'HostMBs', 'HostMBReads', 'HostMBWritten',
                'HostMBWritten', 'FEReqs', 'FEReadReqs', 'FEWriteReqs',
                'BEIOs', 'BEReqs', 'BEReadReqs', 'BEWriteReqs',
                'SystemWPEvents', 'DeviceWPEvents', 'WPCount',
                'SystemMaxWPLimit', 'PercentCacheWP', 'AvgFallThruTime',
                'FEHitReqs', 'FEReadHitReqs', 'FEWriteHitReqs',
                'PrefetchedTracks', 'FEReadMissReqs', 'FEWriteMissReqs',
                'ReadResponseTime', 'WriteResponseTime',
                'OptimizedReadMisses', 'OptimizedMBReadMisses',
                'AvgOptimizedReadMissSize', 'QueueDepthUtilization',
                'InfoAlertCount', 'WarningAlertCount', 'CriticalAlertCount',
                'RDFA_WPCount', 'AllocatedCapacity', 'FE_Balance',
                'DA_Balance', 'DX_Balance', 'RDF_Balance', 'Cache_Balance',
                'SATA_Balance', 'FC_Balance', 'EFD_Balance'
            ],
            'startDate': start_date
        }
        array_perf_data = self.request(
            target_uri, POST, request_object=array_perf_payload)
        array_results_combined = dict()
        array_results_combined['symmetrixID'] = self.array_id
        array_results_combined['reporting_level'] = "array"
        array_results_combined['perf_data'] = (
            array_perf_data[0]['resultList']['result'])
        return array_results_combined

    def get_storage_group_metrics(self, sg_id, start_date, end_date):
        """Get storage group metrics.

        :param sg_id: the storage group id
        :param start_date: the start date
        :param end_date: the end date
        :return: sg_results_combined
        """
        target_uri = '/performance/StorageGroup/metrics'
        sg_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'storageGroupId': sg_id,
            'metrics': [
                'CriticalAlertCount', 'InfoAlertCount', 'WarningAlertCount',
                'AllocatedCapacity', 'TotalTracks', 'BEDiskReadResponseTime',
                'BEReadRequestTime', 'BEReadTaskTime', 'AvgIOSize',
                'AvgReadResponseTime6', 'AvgReadResponseTime7',
                'AvgReadSize', 'AvgWritePacedDelay', 'AvgWriteResponseTime6',
                'AvgWriteResponseTime7', 'AvgWriteSize', 'BEMBReads',
                'BEMBTransferred', 'BEMBWritten', 'BEPercentReads',
                'BEPercentWrites', 'BEPrefetchedTrackss', 'BEReadReqs',
                'BEPrefetchedTrackUsed', 'BEWriteReqs', 'CompressedTracks',
                'CompressionRatio', 'BlockSize', 'HostMBs', 'IODensity',
                'HostIOs', 'MaxWPThreshold', 'HostMBReads', 'HostMBWritten',
                'AvgOptimizedReadMissSize', 'OptimizedMBReadMisss',
                'OptimizedReadMisses', 'PercentCompressedTracks',
                'PercentHit', 'PercentMisses', 'PercentRandomIO',
                'PercentRandomReads', 'PercentRandomReadHit', 'PercentRead',
                'PercentRandomReadMiss', 'PercentRandomWrites',
                'PercentRandomWriteHit', 'PercentRandomWriteMiss',
                'PercentReadMiss', 'PercentReadHit', 'PercentSeqIO',
                'PercentSeqRead', 'PercentSeqReadHit', 'PercentSeqReadMiss',
                'PercentSeqWrites', 'PercentSeqWriteHit', 'PercentWrite',
                'PercentVPSpaceSaved', 'PercentWriteHit', 'RandomIOs',
                'PercentSeqWriteMiss', 'PercentWriteMiss', 'BEPrefetchedMBs',
                'HostIOLimitPercentTimeExceeded', 'RandomReadHits',
                'RandomReadMisses', 'RandomReads', 'RandomWriteHits',
                'RandomWriteMisses', 'RandomWrites', 'RdfMBRead',
                'RdfMBWritten', 'RdfReads', 'RdfReadHits', 'RdfResponseTime',
                'RDFRewrites', 'RdfWrites', 'HostReads', 'HostReadHits',
                'HostReadMisses', 'ReadResponseTimeCount1',
                'ReadResponseTimeCount2', 'ReadResponseTimeCount3',
                'ReadResponseTimeCount4', 'ReadResponseTimeCount5',
                'ReadResponseTimeCount6', 'ReadResponseTimeCount7',
                'RDFS_WriteResponseTime', 'ReadMissResponseTime',
                'ResponseTime', 'ReadResponseTime', 'WriteMissResponseTime',
                'WriteResponseTime', 'SeqReadHits', 'SeqReadMisses',
                'SeqReads', 'SeqWriteHits', 'SeqWriteMisses', 'SeqWrites',
                'Skew', 'SRDFA_MBSent', 'SRDFA_WriteReqs', 'SRDFS_MBSent',
                'SRDFS_WriteReqs', 'BEReqs', 'HostHits', 'HostMisses',
                'SeqIOs', 'WPCount', 'HostWrites', 'HostWriteHits',
                'HostWriteMisses', 'WritePacedDelay',
                'WriteResponseTimeCount1', 'WriteResponseTimeCount2',
                'WriteResponseTimeCount3', 'WriteResponseTimeCount4',
                'WriteResponseTimeCount5', 'WriteResponseTimeCount6',
                'WriteResponseTimeCount7'
            ],
            'startDate': start_date
        }
        sg_perf_data = self.request(
            target_uri, POST, request_object=sg_perf_payload)
        sg_results_combined = dict()
        sg_results_combined['symmetrixID'] = self.array_id
        sg_results_combined['reporting_level'] = "StorageGroup"
        sg_results_combined['sgname'] = sg_id
        sg_results_combined['perf_data'] = (
            sg_perf_data[0]['resultList']['result'])
        return sg_results_combined

    def get_all_fe_director_metrics(self, start_date, end_date):
        """Get a list of all Directors.

        Calculate start and End Dates for Gathering Performance Stats
        Last 1 Hour.

        :param start_date: start date
        :param end_date: end date
        :return: director_results_combined
        """
        dir_list = self.get_fe_director_list()
        director_results_combined = dict()
        director_results_list = []
        # print("this is the director list %s" % dir_list)
        for fe_director in dir_list:
            director_metrics = self.get_fe_director_metrics(
                director=fe_director, start_date=start_date,
                end_date=end_date, dataformat='Average')
            director_results = ({
                "directorID": fe_director,
                "perfdata": director_metrics[0]['resultList']['result']})
            director_results_list.append(director_results)
        director_results_combined['symmetrixID'] = self.array_id
        director_results_combined['reporting_level'] = "FEDirector"
        director_results_combined['perf_data'] = director_results_list
        return director_results_combined

    def get_director_info(self, director_id, start_date, end_date):
        """Get director performance information.

        Get Director level information and performance metrics for
        specified time frame, hard coded to average numbers.

        :param director_id: Director ID
        :param start_date: start date
        :param end_date: end date
        :return: Combined payload
        """
        # Create Director level target URIs
        director_info = self.provisioning.get_director(director_id)
        be_director_uri = '/performance/BEDirector/metrics'
        fe_director_uri = '/performance/FEDirector/metrics'
        rdf_director_uri = '/performance/RDFDirector/metrics'
        im_director_uri = '/performance/IMDirector/metrics'
        eds_director_uri = '/performance/EDSDirector/metrics'

        # Set BE Director performance metrics payload
        be_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'metrics': [
                'AvgTimePerSyscall', 'CompressedMBs', 'CompressedReadMBs',
                'CompressedWriteMBs', 'CompressedReadReqs', 'CompressedReqs',
                'CompressedWriteReqs', 'IOs', 'MBs', 'MBRead', 'MBWritten',
                'PercentBusy', 'PercentBusyLogicalCore_0',
                'PercentBusyLogicalCore_1', 'PercentNonIOBusyLogicalCore_1',
                'PercentNonIOBusyLogicalCore_0', 'PercentNonIOBusy',
                'PrefetchedTracks', 'ReadReqs', 'Reqs', 'SyscallCount',
                'Syscall_RDF_DirCount', 'SyscallRemoteDirCount', 'WriteReqs'
            ],
            'startDate': self.start_date
        }

        # Set FE Director performance metrics payload
        fe_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'metrics': [
                'AvgRDFSWriteResponseTime', 'AvgReadMissResponseTime',
                'AvgWPDiscTime', 'AvgTimePerSyscall', 'DeviceWPEvents',
                'HostMBs', 'HitReqs', 'HostIOs', 'MissReqs',
                'AvgOptimizedReadMissSize', 'OptimizedMBReadMisses',
                'OptimizedReadMisses', 'WriteMissReqs', 'PercentHitReqs',
                'PercentReadReqs', 'PercentReadReqHit', 'PercentWriteReqs',
                'PercentWriteReqHit', 'QueueDepthUtilization', 'ReadMissReqs',
                'HostIOLimitMBs', 'ReadReqs', 'ReadHitReqs', 'Reqs',
                'ReadResponseTime', 'HostIOLimitIOs', 'WriteResponseTime',
                'SlotCollisions', 'SyscallCount', 'Syscall_RDF_DirCounts',
                'SyscallRemoteDirCounts', 'SystemWPEvents', 'TotalReadCount',
                'TotalWriteCount', 'WriteReqs', 'WriteHitReqs', 'PercentBusy',
            ],
            'startDate': start_date
        }

        # Set RDF Director performance metrics payload
        rdf_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'metrics': [
                'AvgIOServiceTime', 'AvgIOSizeReceived', 'AvgIOSizeSent',
                'AvgTimePerSyscall', 'CopyIOs', 'CopyMBs', 'IOs', 'Reqs',
                'MBSentAndReceived', 'MBRead', 'MBWritten', 'PercentBusy',
                'Rewrites', 'AsyncMBSent', 'AsyncWriteReqs', 'SyncMBSent',
                'SyncWrites', 'SyscallCount', 'Syscall_RDF_DirCounts',
                'SyscallRemoteDirCount', 'SyscallTime', 'WriteReqs',
                'TracksSentPerSec', 'TracksReceivedPerSec'
            ],
            'startDate': start_date
        }

        # Set IM Director performance metrics payload
        im_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.end_date,
            'dataFormat': 'Average',
            'metrics': ['PercentBusy'],
            'startDate': self.start_date
        }

        # Set EDS Director performance metrics payload
        eds_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.end_date,
            'dataFormat': 'Average',
            'metrics': [
                'PercentBusy', 'RandomReadMissMBs', 'RandomReadMisses',
                'RandomWriteMissMBs', 'RandomWriteMisses'
            ],
            'startDate': self.start_date
        }

        # Perform Director level performance REST call dependent on Dir type
        if 'DF' in director_id or 'DX' in director_id:
            perf_metrics_payload = self.request(
                be_director_uri, POST, request_object=be_director_payload)
            director_type = 'BE'
        elif ('EF' in director_id or 'FA' in director_id or (
                'FE' in director_id or 'SE' in director_id)):
            perf_metrics_payload = self.request(
                fe_director_uri, POST, request_object=fe_director_payload)
            director_type = 'FE'
        elif 'RF' in director_id or 'RE' in director_id:
            perf_metrics_payload = self.request(
                rdf_director_uri, POST, request_object=rdf_director_payload)
            director_type = 'RDF'
        elif 'IM' in director_id:
            perf_metrics_payload = self.request(
                im_director_uri, POST, request_object=im_director_payload)
            director_type = 'IM'
        elif 'ED' in director_id:
            perf_metrics_payload = self.request(
                eds_director_uri, POST, request_object=eds_director_payload)
            director_type = 'EDS'
        else:
            # Unable to determine Director type, set to N/A
            perf_metrics_payload = []
            director_type = 'N/A'

        # Set combined payload values not present in returned REST metrics
        combined_payload = dict()
        combined_payload['reporting_level'] = "Director"
        combined_payload['symmetrixId'] = self.array_id
        combined_payload['director_id'] = director_id
        combined_payload['directorType'] = director_type

        # If no Director level information is retrieved...
        if not director_info:
            combined_payload['info_data'] = None
            combined_payload['info_msg'] = 'No Director info data available'

        else:
            # Director level information retrieved...
            for k, v in director_info.items():
                combined_payload[k] = v

        # If no Director level performance information is retrieved...
        if not perf_metrics_payload:
            combined_payload['perf_data'] = False
            combined_payload['perf_msg'] = ("No active Director "
                                            "performance data available")
        else:
            # Performance metrics returned...
            combined_payload['perf_data'] = (
                perf_metrics_payload[0]['resultList']['result'])

        return combined_payload

    def get_port_group_metrics(self, pg_id, start_date, end_date):
        """Get Port Group Performance Metrics.

        :param pg_id: port group id
        :param start_date: the start date
        :param end_date: the end date
        :return: pg_results_combined
        """
        target_uri = '/performance/PortGroup/metrics'
        pg_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'portGroupId': pg_id,
            'metrics': [
                'Reads', 'Writes', 'IOs', 'MBRead', 'MBWritten', 'MBs',
                'AvgIOSize', 'PercentBusy'],
            'startDate': start_date
        }
        pg_perf_data = self.request(
            target_uri, POST, request_object=pg_perf_payload)
        pg_results_combined = dict()
        pg_results_combined['symmetrixID'] = self.array_id
        pg_results_combined['reporting_level'] = "PortGroup"
        pg_results_combined['pgname'] = pg_id
        pg_results_combined['perf_data'] = (
            pg_perf_data[0]['resultList']['result'])
        return pg_results_combined

    def get_host_metrics(self, host, start_date, end_date):
        """Get host metrics.

        Get all avaliable host performance statiscics for specified
        time period return in JSON.

        :param host: the host name
        :param start_date: EPOCH Time
        :param end_date: Epoch Time
        :return: Formatted results
        """
        target_uri = "/performance/Host/metrics"
        host_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'hostId': host,
            'dataFormat': 'Average',
            'metrics': ['HostIOs', 'HostMBReads', 'HostMBWrites', 'Reads',
                        'ResponseTime', 'ReadResponseTime', 'Writes',
                        'WriteResponseTime', 'SyscallCount', 'MBs'],
            'startDate': start_date}
        host_perf_data = self.request(
            target_uri, POST, request_object=host_perf_payload)
        host_results = dict()
        host_results['symmetrixID'] = self.array_id
        host_results['reporting_level'] = "Host"
        host_results['HostID'] = host
        host_results['perf_data'] = host_perf_data[0]['resultList']['result']
        if 'resultList' in host_perf_data[0]:
            host_results['perf_data'] = host_perf_data[0]['resultList'][
                'result']
        else:
            host_results['perf_data'] = []

        return host_results

    def get_perf_threshold_categories(self):
        """Get performance threshold categories.

        :return: category_list
        """
        target_uri = "/performance/threshold/categories"
        categories = self.request(target_uri, GET)
        category_list = categories[0]["endpoint"]
        return category_list

    def get_perf_category_threshold_settings(self, category):
        """Get performance threshold category settings.

        Will accept valid category (categories listed from
        get_threshold_categories).

        :param category:
        :return: dict, sc
        """
        target_uri = "/performance/threshold/list/%s" % category
        return self.request(target_uri, GET)

    def set_perf_threshold_and_alert(self, category, metric, firstthreshold,
                                     secondthreshold, notify):
        """Set performance thresholds and alerts.

        Function to set performance alerts, suggested use with CSV file to
        get parameter settings from user template.
        Default is to check for 3 out of 5 samples before returning alert,
        users may want to modify as potentially 3 of 5 could mean could
        take 25 minutes for an alert to be seen as samples are at 5 minute
        intervals.

        :param category: the category name
        :param metric: the required metric
        :param firstthreshold: the first threshold
        :param secondthreshold: the second threshold
        :param notify: Notify user with Alert Boolean
        """
        payload = ({"secondThresholdSamples": 5,
                    "firstThreshold": firstthreshold,
                    "firstThresholdSamples": 5,
                    "metric": metric, "alert": notify,
                    "firstThresholdOccurrrences": 3,
                    "firstThresholdSeverity": "WARNING",
                    "secondThresholdSeverity": "CRITICAL",
                    "secondThreshold": secondthreshold,
                    "secondThresholdOccurrrences": 3})
        target_uri = "/performance/threshold/update/%s" % category

        return self.request(target_uri, PUT, request_object=payload)

    def generate_threshold_settings_csv(self, outputcsvname):
        """Generate a csv file with threshold settings.

        Creates a CSV file with the following headers format containing current
        alert configuration for the given unisphere instance
        category,metric,firstthreshold,secondthreshold,notify,kpi
        array,HostReads,100000,300000,true,true
        array,HostWrites,100000,300000,true,false

        :param outputcsvname: filename for CSV to be generated
        """
        category_list = self.get_perf_threshold_categories()
        with open(bytes(outputcsvname, 'UTF-8'), 'w', newline='') as csvfile:
            eventwriter = csv.writer(csvfile,
                                     delimiter=',',
                                     quotechar='|',
                                     quoting=csv.QUOTE_MINIMAL)

            eventwriter.writerow(["category", "metric", "firstthreshold",
                                  "secondthreshold", "notify", "kpi"])
            for category in category_list:
                metric_setting = (
                    self.get_perf_category_threshold_settings(category)[0][
                        'performanceThreshold'])
                for metric in metric_setting:
                    eventwriter.writerow(
                        [category, metric.get('metric'),
                         metric.get('firstThreshold'), metric.get(
                            'secondThreshold'), metric.get('alertError'),
                         metric.get('kpi')])

    def set_perfthresholds_csv(self, csvfilename):
        """Set performance thresholds using a CSV file.

        reads CSV file, and sets perforamnce threshold metrics, should be
        used with generate_threshold_settings_csv to produce CSV file that
        can be edited and uploaded. The CSV file should have the following
        headers format category,metric,firstthreshold,secondthreshold,
        notify,kpi,array,HostReads,100000,300000,True,True
        array,HostWrites,100000,300000,True,False
        Boolean values are case sensitive ensure that when editing file that
        they are True or False.  KPI setting can not be changed with REST
        API in current implementation, if you change this value it will not
        be updated in the UI. Only notify alert Boolean can be changed with
        REST. Only KPI Metrics should be alterted on, note if you are changing
        default threshold values for metrics used for dashboard views these
        will also update the numbers used for your dashboards.  It's not
        recommended to alert on every value as this will just create noise.

        :param csvfilename: the path to the csv file
        """
        data = self.common.read_csv_values(csvfilename)
        firstthreshold_list = data.get("firstthreshold")
        secondthreshold_list = data.get("secondthreshold")
        notify_list = data.get("notify")
        categrory_list = data.get("category")
        metric_list = data.get("metric")
        kpimetric_list = data.get("kpi")

        for c, m, f, s, n, k in zip(categrory_list, metric_list,
                                    firstthreshold_list,
                                    secondthreshold_list, notify_list,
                                    kpimetric_list):
            if k:
                self.set_perf_threshold_and_alert(c, m, f, s, n)
