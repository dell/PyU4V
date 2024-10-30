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
"""constants.py."""

import version

# Configuration constants
SETUP = 'setup'
ARRAY = 'array'
R_ARRAY = 'remote_array'
R_ARRAY_2 = 'remote_array_2'
USERNAME = 'username'
PASSWORD = 'password'
SERVER_IP = 'server_ip'
PORT = 'port'
VERIFY = 'verify'

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'
CONTENT_TYPE = 'content-type'
ACCEPT = 'accept'
ACCEPT_ENC = 'Accept-Encoding'
USER_AGENT = 'user-agent'
APP_TYPE = 'application-type'
APP_JSON = 'application/json'
APP_OCT = 'application/octet-stream'
APP_MPART = 'multipart/form-data'

# Unisphere REST URI constants
PYU4V_VERSION = version.VERSION
UNISPHERE_VERSION = version.API_VERSION
ENHANCED_API_VERSION = version.ENHANCED_API_VERSION
UCODE_6079 = '6079'
VERSION = 'version'
ITERATOR = 'Iterator'
PAGE = 'page'
JOB = 'job'
SYMMETRIX = 'symmetrix'
SLOPROVISIONING = 'sloprovisioning'
PROVISIONING = 'provisioning'
STORAGEGROUP = 'storagegroup'
REPLICATION = 'replication'
MAINFRAME = 'mainframe'
METRO_DR = 'metrodr'
WLP = 'wlp'
MIGRATION = 'mobility'
DSA = 'dsa'
SYSTEM = 'system'
LOCAL_USER = 'local_user'
VOLUME = 'volume'
VVOL = 'vvol'
COMMON = 'common'
HEADROOM = 'headroom'
ENVIRONMENT = 'environment'
CAPABILITIES = 'capabilities'
DIRECTOR = 'director'
PORTGROUP = 'portgroup'
HOST = 'host'
HOSTGROUP = 'hostgroup'
INITIATOR = 'initiator'
MASKINGVIEW = 'maskingview'
CONNECTIONS = 'connections'
SLO = 'slo'
WORKLOADTYPE = 'workloadtype'
SRP = 'srp'
COMPRESSIBILITY_REPORT = 'compressibility_report'
SG_DEMAND_REPORT = 'storage_group_demand_report'
SNAPSHOT = 'snapshot'
GENERATION = 'generation'
SNAP_ID = 'snapid'
RDFG = 'rdf_group'
RDF_GROUP = 'rdf_group'
GB_HEADROOM = 'gbHeadroom'
RDF_DIRECTOR = 'rdf_director'
REMOTE_PORT = 'remote_port'
ALERT = 'alert'
ALERT_SUMMARY = 'alert_summary'
COMPLIANCE = 'compliance'
FICON_SPLIT = 'split'
CU_IMAGE = 'cuimage'
SERVICEABILITY = 'serviceability'
NTP_SERVER = "ntp_server"
SYMMETRIX_ID = "symmetrix_id"

# Status Codes
STATUS_200 = 200
STATUS_201 = 201
STATUS_202 = 202
STATUS_204 = 204
STATUS_401 = 401
STATUS_404 = 404

# Job constants
INCOMPLETE_LIST = ['created', 'scheduled', 'running',
                   'validating', 'validated']
CREATED = 'created'
SUCCEEDED = 'succeeded'
ASYNCHRONOUS = 'ASYNCHRONOUS'
ASYNC_UPDATE = {'executionOption': ASYNCHRONOUS}
CREATE_VOL_STRING = 'Creating new Volumes'

# Replication Modes
ASYNCHRONOUS_CC = 'Asynchronous'
ADAPTIVE_COPY = 'AdaptiveCopyDisk'
DISABLECONSISTENCY = 'DisableConsistency'
ENABLECONSISTENCY = 'EnableConsistency'
ESTABLISH = 'Establish'
FAILBACK = 'Failback'
FAILOVER = 'Failover'
RECOVER = 'Recover'
RESTORE = 'Restore'
RESUME = 'Resume'
SETBIAS = 'SetBias'
SETMODE = 'SetMode'
SPLIT = 'Split'
SUSPEND = 'Suspend'
SWAP = 'Swap'
UPDATE_R1 = 'UpdateR1'
# RDFG Constants

RDFG_ACTIONS = {
    'MOVE': 'Move', 'ADD_PORTS': 'add_ports',
    'REMOVE_PORTS': 'remove_ports', 'SET_LABEL': 'set_label'}
METRO_DR_ACTIONS = {
    'ESTABLISH': ESTABLISH, 'SPLIT': SPLIT, 'SUSPEND': SUSPEND,
    'RECOVER': RECOVER, 'RESTORE': RESTORE, 'FAILOVER': FAILOVER,
    'FAILBACK': FAILBACK, 'SETMODE': SETMODE, 'UPDATER1': UPDATE_R1
}
METRO_DR_ACTION_PARAMS = {
    'ESTABLISH': 'establish', 'SPLIT': 'split', 'SUSPEND': 'suspend',
    'RESTORE': 'restore', 'FAILOVER': 'failover',
    'FAILBACK': 'failback', 'SETMODE': 'set_mode', 'UPDATER1': 'update_r1'
}

METRO_DR_REPLICATION_MODE = {'ADAPTIVECOPYDISK': 'AdaptiveCopyDisk',
                             'ASYNCHRONOUS': 'Asynchronous'}

# Director constants
DIRECTOR_ID = 'directorId'
PORT_ID = 'portId'
SYMMETRIX_PORT_KEY = 'symmetrixPortKey'
NUM_OF_PORTS = 'num_of_ports'
NUM_OF_CORES = 'num_of_cores'
IP_INTERFACE = 'ipinterface'
IP_INTERFACE_ID = 'ipInterfaceId'

# Host constants
HOST_ID = 'hostId'
ENABLED_FLAGS = 'enabled_flags'
CONSISTENT_LUN = 'consistent_lun'
NUM_OF_INITIATORS = 'num_of_initiators'
HOST_LUN_ADDRESS = 'host_lun_address'
OVERRIDE = 'override'
ENABLED = 'enabled'
TRUE = 'True'
FALSE = 'False'
SPC2_PROTOCOL_VERSION = 'spc2_protocol_version'
SPC2_PROTOCOL_VERSION_FLAG = 'SPC2_Protocol_Version(SPC2)'
SCSI_3 = 'scsi_3'
SCSI_3_FLAG = 'SCSI_3(SC3)'
OPENVMS = 'openvms'
OPENVMS_FLAG = 'OpenVMS(OVMS)'
AVOID_RESET_BROADCAST = 'avoid_reset_broadcast'
AVOID_RESET_BROADCAST_FLAG = 'Avoid_Reset_Broadcast(ARB)'
VOLUME_SET_ADDRESSING = 'volume_set_addressing'
HOST_FLAGS = {
    'disable_q_reset_on_ua': {
        OVERRIDE: False, ENABLED: False},
    'environ_set': {
        OVERRIDE: False, ENABLED: False},
    VOLUME_SET_ADDRESSING: {
        OVERRIDE: False, ENABLED: False},
    'spc2_protocol_version': {
        OVERRIDE: False, ENABLED: False},
    'scsi_support1': {
        OVERRIDE: False, ENABLED: False},
    OPENVMS: {
        OVERRIDE: False, ENABLED: False},
    AVOID_RESET_BROADCAST: {
        OVERRIDE: False, ENABLED: False},
    SCSI_3: {
        OVERRIDE: TRUE, ENABLED: TRUE},
    CONSISTENT_LUN: False}

# Host Group constants
NUM_OF_HOSTS = 'num_of_hosts'
HOST_GROUP = 'host_group'
HOST_GROUP_ID = 'hostGroupId'

# SRP constants
SRP_CAPACITY = 'srp_capacity'
SRP_EFFICIENCY = 'srp_efficiency'
STORAGE_GROUP_DEMAND = 'storage_group_demand'
SRP_ID = 'srpId'
NUM_OF_DISK_GROUPS = 'num_of_disk_groups'
RESERVED_CAP_PERCENT = 'reserved_cap_percent'
TOTAL_SRDF_DSE_ALLOCATED_CAP_GB = 'total_srdf_dse_allocated_cap_gb'
RDFA_DSE = 'rdfa_dse'
DISK_GROUP_ID = 'diskGroupId'

# V3 SRP constants
SUBSCRIBED_ALLOCATED_TB = 'subscribed_allocated_tb'
SUBSCRIBED_TOTAL_TB = 'subscribed_total_tb'
SNAPSHOT_MODIFIED_TB = 'snapshot_modified_tb'
SNAPSHOT_TOTAL_TB = 'snapshot_total_tb'
USABLE_USED_TB = 'usable_used_tb'
USABLE_TOTAL_TB = 'usable_total_tb'
EFFECTIVE_USED_CAPACITY_PERCENT = 'effective_used_capacity_percent'

# V4 SRP constants
FBA_SRP_CAPACITY = 'fba_srp_capacity'
SERVICE_LEVELS = 'service_levels'
USED_TB = 'used_tb'
TOTAL_TB = 'total_tb'
FREE_TB = 'free_tb'
EFFECTIVE_CAPACITY_TB = 'effective_capacity_tb'
PROVISIONED_TB = 'provisioned_tb'
PROVISIONED_PERCENT = 'provisioned_percent'
EFFECTIVE_USED_PERCENT = 'effective_used_percent'
PHYSICAL_CAPACITY = 'physical_capacity'
EFFECTIVE_CAPACITY_RESOURCES = 'effective_capacity_resources'
EFFECTIVE_CAPACITY_USAGE = 'effective_capacity_usage'
PHYSICAL_USED_PERCENT = 'physical_used_percent'
REDUCING_DATA_PERCENT = 'reducing_data_percent'
SAVINGS_TB = 'savings_tb'
EFFECTIVE_USED = 'effective_used'
PHYSICAL_USED = 'physical_used'
SNAPSHOT_USED_TB = 'snapshot_used_tb'
USER_USED_TB = 'user_used_tb'
ENABLED_AND_REDUCING_TB = 'enabled_and_reducing_tb'
ENABLED_AND_UNREDUCIBLE_TB = 'enabled_and_unreducible_tb'
ENABLED_AND_UNEVALUATED_TB = 'enabled_and_unevaluated_tb'
DATA_REDUCTION_DISABLED_TB = 'data_reduction_disabled_tb'
DISABLED_AND_UNREDUCED_TB = 'disabled_and_unreduced_tb'

# Storage Group constants
STORAGE_GROUP_ID_CAMEL = 'storageGroupId'
STORAGE_GROUP_ID = 'storage_group_id'
NUM_OF_CHILD_SGS = 'num_of_child_sgs'
SERVICE_LEVEL = 'service_level'
BASE_SLO_NAME = 'base_slo_name'
SLO_COMPLIANCE = 'slo_compliance'
NUM_OF_VOLS = 'num_of_vols'
NUM_OF_PARENT_SGS = 'num_of_parent_sgs'
NUM_OF_MASKING_VIEWS = 'num_of_masking_views'
NUM_OF_SNAPSHOTS = 'num_of_snapshots'
DEVICE_EMULATION = 'device_emulation'
UNPROTECTED = 'unprotected'
COMPRESSION = 'compression'

# Port Group constants
PORT_GROUP = 'port_group'
PORT_GROUP_ID = 'portGroupId'

# Masking View constants
MASKING_VIEW_ID = 'maskingViewId'

# Volume constants
VOLUME_ID_CAMEL = 'volumeId'
VOLUME_ID = 'volume_id'
DEVICE_ID = 'device_id'
CAP_GB = 'cap_gb'
ALLOCATED_PERCENT = 'allocated_percent'
VOLUME_IDENTIFIER = 'volume_identifier'
VOLUME_NAME = 'volume_name'
WWN = 'wwn'
EFFECTIVE_WWN = 'effective_wwn'
HAS_EFFECTIVE_WWN = 'has_effective_wwn'
EMULATION = 'emulation'
TYPE = 'type'
SSID = 'ssid'
CAP_MB = 'cap_mb'
CAP_CYL = 'cap_cyl'
STATUS = 'status'
RESERVED = 'reserved'
PINNED = 'pinned'
ENCAPSULATED = 'encapsulated'
NUM_OF_FRONT_END_PATHS = 'num_of_front_end_paths'
SNAPVX_SOURCE = 'snapvx_source'
SNAPVX_TARGET = 'snapvx_target'
MOBILITY_ID_ENABLED = 'mobility_id_enabled'

# SLO constants
SLO_ID = 'sloId'
NUM_OF_STORAGE_GROUPS = 'num_of_storage_groups'

# Initiator constants
INITIATOR_ID = 'initiatorId'
LOGGED_IN = 'logged_in'
ALIAS = 'alias'
ON_FABRIC = 'on_fabric'
FCID = 'fcid'

# Regex search pattern constants
DIRECTOR_SEARCH_PATTERN = '\\w{2}-\\w{2}'
PORT_SEARCH_PATTERN = '\\d{1,3}'
WWN_SEARCH_PATTERN_16 = '[0-9a-fA-F]{16}'
WWN_SEARCH_PATTERN_32 = '[0-9a-fA-F]{32}'
ISCSI_IQN_SEARCH_PATTERN = (
    '^iqn.\\d{1,4}-\\d{2}.(?:com|org).\\w{1,}:(?:\\d{2}:)*'
    '[0-9a-fA-F]{1,32}$||.[0-9A-Fa-f]{16}')
non_iscsi_initiator_pattern = '{d}:{p}:{w}'.format(
    d=DIRECTOR_SEARCH_PATTERN, p=PORT_SEARCH_PATTERN,
    w=WWN_SEARCH_PATTERN_16)
iscsi_initiator_pattern = '{d}:{p}:{pa}'.format(
    d=DIRECTOR_SEARCH_PATTERN, p=PORT_SEARCH_PATTERN,
    pa=ISCSI_IQN_SEARCH_PATTERN)
INITIATOR_SEARCH_PATTERN = '{ni}|{i}'.format(
    ni=non_iscsi_initiator_pattern, i=iscsi_initiator_pattern)

# QOS constants
HOST_IO_LIMIT = 'hostIOLimit'
MAX_MBPS = 'maxMBPS'
DISTRIBUTION_TYPE = 'DistributionType'
HOST_IO_LIMIT_IO_SEC = 'host_io_limit_io_sec'
HOST_IO_LIMIT_MB_SEC = 'host_io_limit_mb_sec'
DYNAMIC_DISTRIBUTION = 'dynamicDistribution'

# System Health / Disk Checks
HEALTH = 'health'
HEALTH_CHECK = 'health_check'
FAILED = 'failed'
DISK = 'disk'
TAG = 'tag'
DESCRIPTION = 'description'
ARRAY_ID = 'array_id'
TAG_NAME = 'tag_name'
SG_ID = 'storage_group_id'
SG_NUM = 'num_of_storage_groups'
ARRAY_NUM = 'num_of_arrays'
HEALTH_SCORE = 'health_score_metric'
HEALTH_CHECK_ID = 'health_check_id'
TEST_RES = 'testResult'
JOB_ID = 'jobId'
RES_LINK = 'resourceLink'
NAME = 'name'
DISK_IDS = 'disk_ids'
SPINDLE_ID = 'spindle_id'
VENDOR = 'vendor'
CAPACITY = 'capacity'
ALERT_SUMMARY_KEYS = ['alert_count', 'all_unacknowledged_count',
                      'fatal_unacknowledged_count',
                      'critical_unacknowledged_count',
                      'warning_unacknowledged_count',
                      'info_unacknowledged_count',
                      'minor_unacknowledged_count',
                      'normal_unacknowledged_count',
                      'all_acknowledged_count', 'fatal_acknowledged_count',
                      'critical_acknowledged_count',
                      'warning_acknowledged_count',
                      'info_acknowledged_count', 'minor_acknowledged_count',
                      'normal_acknowledged_count']
SNAPSHOT_POLICY_INTERVALS = ['10 Minutes', '12 Minutes', '15 Minutes',
                             '20 Minutes', '30 Minutes', '1 Hour',
                             '2 Hours', '3 Hours', '4 Hours', '6 Hours',
                             '8 Hours', '12 Hours', '1 Day', '7 Days']
ASSOCIATE_TO_STORAGE_GROUPS = 'AssociateToStorageGroups'
DISASSOCIATE_FROM_STORAGE_GROUPS = 'DisassociateFromStorageGroups'
SNAPSHOT_POLICY = 'snapshot_policy'
SNAPSHOT_POLICY_NAME_FOR_TEST = 'DailyDefault'
MODIFY_POLICY = 'Modify'
SUSPEND_POLICY = 'Suspend'
RESUME_POLICY = 'Resume'
SNAPSHOT_POLICY_ACTIONS = [MODIFY_POLICY, SUSPEND_POLICY, RESUME_POLICY,
                           ASSOCIATE_TO_STORAGE_GROUPS,
                           DISASSOCIATE_FROM_STORAGE_GROUPS]

# Import/Export Settings
SETTINGS_FILENAME_TEMPLATE = 'PyU4V-SettingsExport'
SETTINGS = 'settings'
EXPORT_FILE = 'exportfile'
IMPORT_FILE = 'importfile'
SRC_ARRAY = 'source_array'
TGT_ARRAYS = 'target_arrays'
FILE_PASSWORD = 'file_password'
ZIP_FILE = 'zip_file'
ZIP_SUFFIX = '.zip'
PDF_SUFFIX = '.pdf'
FILE_READ_MODE = 'rb'
FILE_WRITE_MODE = 'wb'
ALL_SETTINGS = 'all'
EXCLUDE_UNI_SETTINGS = 'exclude_unisphere_setting_options'
EXCLUDE_SYS_SETTINGS = 'exclude_system_setting_options'
UNI_ALERT_SETTINGS = 'alert_notification_settings'
UNI_PERF_PREF_SETTINGS = 'performance_preference_settings'
UNI_PERF_USER_SETTINGS = 'performance_user_templates'
UNI_PERF_METRIC_SETTINGS = 'performance_metric_settings'
SYS_ALERT_SETTINGS = 'alert_policy_settings'
SYS_ALERT_NOTIFI_SETTINGS = 'alert_level_notification_settings'
SYS_THRESH_SETTINGS = 'system_threshold_settings'
SYS_PERF_THRESH_SETTINGS = 'performance_threshold_settings'

# Audit Log Constants
AUDIT_LOG_FILENAME_TEMPLATE = 'PyU4V-AuditLogRecord'
AUDIT_LOG_FILENAME = 'auditlogfilename'
AUDIT_RECORD_PATH = 'audit_record_path'
AUDIT_LOG_RECORD = 'audit_log_record'
AUDIT_RECORD_TIME = 'audit_record_time'
BINARY_DATA = 'binary_data'
RECORD_ID = 'record_id'
HOST_NAME = 'hostname'
CLIENT_HOST = 'client_host'
MESSAGE = 'message'
ACTIVITY_ID = 'activity_id'
APP_ID = 'application_id'
APP_VERSION = 'application_version'
TASK_ID = 'task_id'
PROCESS_ID = 'process_id'
VENDOR_ID = 'vendor_id'
OS_TYPE = 'os_type'
OS_REV = 'os_revision'
API_LIB = 'api_library'
API_VER = 'api_version'
AUDIT_CLASS = 'audit_class'
ACTION_CODE = 'action_code'
FUNC_CLASS = 'function_class'
SUCCESS = 'success'
COUNT = 'count'

# Date/Time
STR_TIME_FORMAT = '%Y%m%d%H%M%S'

# Port structure
PORT_STRUCTURE = [{
    'directorId': str,
    'portId': str}
]

# Serviceability Constants
SERVICEABILITY_LOG_FILENAME_TEMPLATE = 'PyU4V-ServiceabilityLogRecord'
SERVICEABILITY_LOG_FILENAME = 'serviceabilitylogfilename'
SERVICEABILITY_LOG_RECORD = 'serviceability_log_record'
SERVICEABILITY_RECORD_PATH = 'serviceability_record_path'
SERVICEABILITY_RECORD_TIME = 'serviceability_record_time'
SERVICEABILITY_EXPORT_FILE = 'export'
DEFAULT_NODE_NAME = 'Unisphere'
IP_CONFIGURATION = 'ip_configuration'
NATONE_IP_ADDRESS_IPV4 = 'natone_ip_address_ipv4'
NATONE_NETMASK_IPV4 = 'natone_netmask_ipv4'
NATONE_GATEWAY_IPV4 = 'natone_gateway_ipv4'
NATTWO_IP_ADDRESS_IPV4 = 'nattwo_ip_address_ipv4'
NATTWO_NETMASK_IPV4 = 'nattwo_netmask_ipv4'
NATTWO_GATEWAY_IPV4 = 'nattwo_gateway_ipv4'
NATONE_IP_ADDRESS_IPV6 = 'natone_ip_address_ipv6'
NATONE_PREFIX_IPV6 = 'natone_prefix_ipv6'
NATONE_GATEWAY_IPV6 = 'natone_gateway_ipv6'
NATTWO_IP_ADDRESS_IPV6 = 'nattwo_ip_address_ipv6'
NATTWO_PREFIX_IPV6 = 'nattwo_prefix_ipv6'
NATTWO_GATEWAY_IPV6 = 'natone_gateway_ipv6'
UPDATEIPV4 = 'UpdateIPV4'
UPDATEIPV6 = 'UpdateIPV6'
APPLICATION = 'application'
APPLICATIONS = 'applications'
UNISPHERE = 'unisphere'
CONFIGURATION = 'configuration'
VASA = 'vasa'
DEFAULT_VASA = 'VASA-0'
SOLUTIONS_ENABLER = 'solutions_enabler'
GUEST_NAME = 'guest_name'
NODE_NAME = 'node_name'
ACCESS_ID = 'access_id'
SERVER_ACCESS = 'server_access'
SE_BASE_CONFIGURATION = 'se_base_configuration'
SE_SERVICE_CONFIGURATION = 'se_service_configuration'
SYMM_LIST = 'symm_list'
SYMM_AVOID_LIST = 'symm_avoid_list'
VASA_APPLICATIONS = 'vasa_applications'
RUNNING_STATUS = 'running_status'
VP_LOG_FILE_SIZE_MB = 'vp_log_file_size_mb'
VP_LOG_LEVEL = 'vp_log_level'
VP_NUM_OF_FILES_TO_BE_RETAINED = 'vp_num_of_files_to_be_retained'
VP_MAX_CONNECTION_PER_SESSION = 'vp_max_connection_per_session'
RETAIN_VP_CERT = 'retain_vp_cert'
SYMAPI_DEBUG_LOG = 'symapi_debug_log'
SE_APPLICATIONS = 'se_applications'
SE_NETHOST = 'se_nethost'
ALLOW_SERVICE_ACCESS = 'AllowServerAccess'
CUSTOM_CERTIFICATE = 'custom_certificate'
IMPORT = 'import'
SELF_SIGNED_CERTIFICATE = 'self_signed_certificate'
NODE_DISPLAYNAME = 'node_displayname'
STORAGEGROUP_META_DATA = [
    {
        "name": "id",
        "type": "String",
        "required": True
    },
    {
        "name": "resource_type",
        "type": "String",
        "required": False
    },
    {
        "name": "type",
        "type": "String",
        "required": False
    },
    {
        "name": "uuid",
        "type": "String",
        "required": False
    },
    {
        "name": "system",
        "type": "StorageGroup_System",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            }
        ],
        "required": False
    },
    {
        "name": "volume_emulation",
        "type": "String",
        "required": False
    },
    {
        "name": "srp",
        "type": "StorageGroup_Srp",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            }
        ],
        "required": False
    },
    {
        "name": "num_of_volumes",
        "type": "Integer",
        "required": False
    },
    {
        "name": "volumes",
        "type": "List<StorageGroup_Volume>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "wwn",
                "type": "String",
                "required": False
            },
            {
                "name": "effective_wwn",
                "type": "String",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_non_gk_volumes",
        "type": "Integer",
        "required": False
    },
    {
        "name": "non_gk_volumes",
        "type": "List<StorageGroup_GateKeeperVolume>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "wwn",
                "type": "String",
                "required": False
            },
            {
                "name": "effective_wwn",
                "type": "String",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_child_storage_groups",
        "type": "Long",
        "required": False
    },
    {
        "name": "child_storage_groups",
        "type": "List<StorageGroup_ChildStorageGroup>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            }
        ],
        "required": False
    },
    {
        "name": "num_of_parent_storage_groups",
        "type": "Long",
        "required": False
    },
    {
        "name": "parent_storage_groups",
        "type": "List<StorageGroup_ParentStorageGroup>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            }
        ],
        "required": False
    },
    {
        "name": "num_of_masking_views",
        "type": "Long",
        "required": False
    },
    {
        "name": "masking_views",
        "type": "List<StorageGroup_MaskingView>",
        "attributes": [
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "host",
                "type": "StorageGroup_MaskingView_Host",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "port_group",
                "type": "StorageGroup_MaskingView_PortGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "storage_group",
                "type": "StorageGroup_MaskingView_StorageGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "uuid",
                "type": "String",
                "required": False
            },
            {
                "name": "last_update_time_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "masking_view_last_update_time_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "num_of_initiators",
                "type": "Long",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_snapshots",
        "type": "Long",
        "required": False
    },
    {
        "name": "snapshots",
        "type": "List<StorageGroup_Snapshot>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "name",
                "type": "String",
                "required": False
            },
            {
                "name": "timestamp_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "generation",
                "type": "Long",
                "required": False
            },
            {
                "name": "type",
                "type": "String",
                "required": False
            },
            {
                "name": "linked",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "restored",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "expired",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "secured",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "persistent",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "num_of_volumes",
                "type": "Long",
                "required": False
            },
            {
                "name": "volumes",
                "type": "List<StorageGroup_Snapshot_Volume>",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "cap_gb",
                "type": "Double",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_snapshot_policies",
        "type": "Long",
        "required": False
    },
    {
        "name": "snapshot_policies",
        "type": "List<StorageGroup_SnapshotPolicy>",
        "attributes": [
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "association_time_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "resumed",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "suspended",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "inherited",
                "type": "Boolean",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_clones",
        "type": "Long",
        "required": False
    },
    {
        "name": "clones",
        "type": "List<StorageGroup_Clone>",
        "attributes": [
            {
                "name": "target_storage_group",
                "type": "StorageGroup_Clone_StorageGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": True
            },
            {
                "name": "source_storage_group",
                "type": "StorageGroup_Clone_StorageGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": True
            },
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "states",
                "type": "List<String>",
                "required": False
            },
            {
                "name": "flags",
                "type": "List<String>",
                "required": False
            },
            {
                "name": "modified_tracks",
                "type": "Long",
                "required": False
            },
            {
                "name": "source_modified_tracks",
                "type": "Long",
                "required": False
            },
            {
                "name": "source_protected_tracks",
                "type": "Long",
                "required": False
            },
            {
                "name": "fully_cloned",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "last_action_timestamp_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "num_of_pairs",
                "type": "Long",
                "required": False
            },
            {
                "name": "pairs",
                "type": "List<StorageGroup_Clone_PairInfo>",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "source_volume",
                        "type": "StorageGroup_Clone_PairInfo_Volume",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": True
                            }
                        ],
                        "required": False
                    },
                    {
                        "name": "target_volume",
                        "type": "StorageGroup_Clone_PairInfo_Volume",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": True
                            }
                        ],
                        "required": False
                    },
                    {
                        "name": "state",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "flags",
                        "type": "List<String>",
                        "required": False
                    },
                    {
                        "name": "modified_tracks",
                        "type": "Long",
                        "required": False
                    },
                    {
                        "name": "source_modified_tracks",
                        "type": "Long",
                        "required": False
                    },
                    {
                        "name": "source_protected_tracks",
                        "type": "Long",
                        "required": False
                    },
                    {
                        "name": "last_action_timestamp_ms",
                        "type": "Long",
                        "required": False
                    },
                    {
                        "name": "percent_complete",
                        "type": "Long",
                        "required": False
                    },
                    {
                        "name": "system",
                        "type": "StorageGroup_Clone_PairInfo_System",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": True
                            }
                        ],
                        "required": False
                    }
                ],
                "required": False
            },
            {
                "name": "system",
                "type": "StorageGroup_Clone_System",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_rdf_infos",
        "type": "Long",
        "required": False
    },
    {
        "name": "rdf_infos",
        "type": "List<StorageGroup_RdfInfo>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "states",
                "type": "List<String>",
                "required": False
            },
            {
                "name": "types",
                "type": "List<String>",
                "required": False
            },
            {
                "name": "modes",
                "type": "List<String>",
                "required": False
            },
            {
                "name": "cap_gb",
                "type": "Double",
                "required": False
            },
            {
                "name": "cap_mb",
                "type": "Double",
                "required": False
            },
            {
                "name": "async",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "metro",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "num_of_pairs",
                "type": "Integer",
                "required": False
            },
            {
                "name": "pairs",
                "type": "List<StorageGroup_RdfPair>",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "local_volume",
                        "type": "StorageGroup_RdfPair_Volume",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": True
                            }
                        ],
                        "required": True
                    },
                    {
                        "name": "remote_volume",
                        "type": "StorageGroup_RdfPair_Volume",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": True
                            }
                        ],
                        "required": True
                    },
                    {
                        "name": "link_status",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "state",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "mode",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "adaptive_copy_state",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "consistency_state",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "suspend_state",
                        "type": "String",
                        "required": False
                    }
                ],
                "required": False
            },
            {
                "name": "local_rdf_group",
                "type": "StorageGroup_RdfGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    },
                    {
                        "name": "system",
                        "type": "StorageGroup_Rdf_Group_System",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": False
                            }
                        ],
                        "required": False
                    },
                    {
                        "name": "ucode",
                        "type": "String",
                        "required": False
                    }
                ],
                "required": False
            },
            {
                "name": "remote_rdf_group",
                "type": "StorageGroup_RdfGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    },
                    {
                        "name": "system",
                        "type": "StorageGroup_Rdf_Group_System",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": False
                            }
                        ],
                        "required": False
                    },
                    {
                        "name": "ucode",
                        "type": "String",
                        "required": False
                    }
                ],
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "host_io_limit_info",
        "type": "StorageGroup_HostIoInfo",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "host_io_limit_mb_sec",
                "type": "Long",
                "required": False
            },
            {
                "name": "host_io_limit_io_sec",
                "type": "Long",
                "required": False
            },
            {
                "name": "dynamic_distribution",
                "type": "String",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "service_level",
        "type": "StorageGroup_ServiceLevel",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "base_id",
                "type": "String",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "tags",
        "type": "List<StorageGroup_Tag>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "tagged_objects",
                "type": "List<StorageGroup_Tag_Tagged_Object>",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    },
                    {
                        "name": "type",
                        "type": "String",
                        "required": False
                    }
                ],
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_tags",
        "type": "Long",
        "required": False
    },
    {
        "name": "last_modified_time_ms",
        "type": "Long",
        "required": False
    },
    {
        "name": "group_last_modified_time_ms",
        "type": "Long",
        "required": False
    },
    {
        "name": "timestamp_ms",
        "type": "Long",
        "required": False
    },
    {
        "name": "effective_used_capacity_gb",
        "type": "Double",
        "required": False
    },
    {
        "name": "data_reduction_enabled",
        "type": "Boolean",
        "required": False
    },
    {
        "name": "data_reduction_ratio_to_one",
        "type": "Double",
        "required": False
    },
    {
        "name": "unreducible_data_gb",
        "type": "Double",
        "required": False
    },
    {
        "name": "cap_gb",
        "type": "Double",
        "required": False
    }
]
VOLUMES_METADATA = [
    {
        "name": "id",
        "type": "String",
        "required": True
    },
    {
        "name": "resource_type",
        "type": "String",
        "required": False
    },
    {
        "name": "type",
        "type": "String",
        "required": False
    },
    {
        "name": "system",
        "type": "Volume_System",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            }
        ],
        "required": False
    },
    {
        "name": "emulation",
        "type": "String",
        "required": False
    },
    {
        "name": "status",
        "type": "String",
        "required": False
    },
    {
        "name": "identifier",
        "type": "String",
        "required": False
    },
    {
        "name": "ssid",
        "type": "String",
        "required": False
    },
    {
        "name": "nguid",
        "type": "String",
        "required": False
    },
    {
        "name": "wwn",
        "type": "String",
        "required": False
    },
    {
        "name": "effective_wwn",
        "type": "String",
        "required": False
    },
    {
        "name": "has_effective_wwn",
        "type": "Boolean",
        "required": False
    },
    {
        "name": "mobility_id_enabled",
        "type": "Boolean",
        "required": False
    },
    {
        "name": "encapsulated",
        "type": "Boolean",
        "required": False
    },
    {
        "name": "snapvx_source",
        "type": "Boolean",
        "required": False
    },
    {
        "name": "snapvx_target",
        "type": "Boolean",
        "required": False
    },
    {
        "name": "num_of_storage_groups",
        "type": "Integer",
        "required": False
    },
    {
        "name": "storage_groups",
        "type": "List<Volume_StorageGroup>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            }
        ],
        "required": False
    },
    {
        "name": "num_of_masking_views",
        "type": "Long",
        "required": False
    },
    {
        "name": "masking_views",
        "type": "List<Volume_MaskingView>",
        "attributes": [
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "host",
                "type": "Volume_MaskingView_Host",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "port_group",
                "type": "Volume_MaskingView_PortGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "storage_group",
                "type": "Volume_MaskingView_StorageGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "uuid",
                "type": "String",
                "required": False
            },
            {
                "name": "last_update_time_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "masking_view_last_update_time_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "num_of_initiators",
                "type": "Long",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_snapshots",
        "type": "Long",
        "required": False
    },
    {
        "name": "snapshots",
        "type": "List<Volume_Snapshot>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            },
            {
                "name": "name",
                "type": "String",
                "required": False
            },
            {
                "name": "timestamp_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "generation",
                "type": "Long",
                "required": False
            },
            {
                "name": "type",
                "type": "String",
                "required": False
            },
            {
                "name": "linked",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "restored",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "expired",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "expiry_date",
                "type": "Long",
                "required": False
            },
            {
                "name": "secured",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "failed",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "persistent",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "cap_gb",
                "type": "Double",
                "required": False
            },
            {
                "name": "tracks",
                "type": "Long",
                "required": False
            },
            {
                "name": "track_size",
                "type": "Long",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_clones",
        "type": "Long",
        "required": False
    },
    {
        "name": "clones",
        "type": "List<Volume_Clone_PairInfo>",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "source_volume",
                "type": "Volume_Clone_PairInfo_Volume",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "target_volume",
                "type": "Volume_Clone_PairInfo_Volume",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            },
            {
                "name": "state",
                "type": "String",
                "required": False
            },
            {
                "name": "flags",
                "type": "List<String>",
                "required": False
            },
            {
                "name": "modified_tracks",
                "type": "Long",
                "required": False
            },
            {
                "name": "source_modified_tracks",
                "type": "Long",
                "required": False
            },
            {
                "name": "source_protected_tracks",
                "type": "Long",
                "required": False
            },
            {
                "name": "last_action_timestamp_ms",
                "type": "Long",
                "required": False
            },
            {
                "name": "percent_complete",
                "type": "Long",
                "required": False
            },
            {
                "name": "system",
                "type": "Volume_Clone_System",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "num_of_rdf_infos",
        "type": "Long",
        "required": False
    },
    {
        "name": "rdf_infos",
        "type": "List<Volume_RdfInfo>",
        "attributes": [
            {
                "name": "remote_volume",
                "type": "Volume_RdfInfo_Volume",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    }
                ],
                "required": True
            },
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "local_rdf_group",
                "type": "Volume_RdfGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    },
                    {
                        "name": "system",
                        "type": "Volume_Rdf_Group_System",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": True
                            }
                        ],
                        "required": False
                    },
                    {
                        "name": "ucode",
                        "type": "String",
                        "required": False
                    }
                ],
                "required": False
            },
            {
                "name": "remote_rdf_group",
                "type": "Volume_RdfGroup",
                "attributes": [
                    {
                        "name": "resource_type",
                        "type": "String",
                        "required": False
                    },
                    {
                        "name": "id",
                        "type": "String",
                        "required": True
                    },
                    {
                        "name": "system",
                        "type": "Volume_Rdf_Group_System",
                        "attributes": [
                            {
                                "name": "resource_type",
                                "type": "String",
                                "required": False
                            },
                            {
                                "name": "id",
                                "type": "String",
                                "required": True
                            }
                        ],
                        "required": False
                    },
                    {
                        "name": "ucode",
                        "type": "String",
                        "required": False
                    }
                ],
                "required": False
            },
            {
                "name": "state",
                "type": "String",
                "required": False
            },
            {
                "name": "type",
                "type": "String",
                "required": False
            },
            {
                "name": "mode",
                "type": "String",
                "required": False
            },
            {
                "name": "async",
                "type": "Boolean",
                "required": False
            },
            {
                "name": "metro",
                "type": "Boolean",
                "required": False
            }
        ],
        "required": False
    },
    {
        "name": "cap_tb",
        "type": "Double",
        "required": False
    },
    {
        "name": "cap_gb",
        "type": "Double",
        "required": False
    },
    {
        "name": "cap_mb",
        "type": "Double",
        "required": False
    },
    {
        "name": "cap_cyl",
        "type": "Double",
        "required": False
    },
    {
        "name": "unreducible_data_gb",
        "type": "Double",
        "required": False
    },
    {
        "name": "data_reduction_ratio_to_one",
        "type": "Double",
        "required": False
    },
    {
        "name": "data_reduction_enabled",
        "type": "Boolean",
        "required": False
    },
    {
        "name": "effective_used_capacity_gb",
        "type": "Double",
        "required": False
    },
    {
        "name": "srp",
        "type": "Volume_Srp",
        "attributes": [
            {
                "name": "resource_type",
                "type": "String",
                "required": False
            },
            {
                "name": "id",
                "type": "String",
                "required": True
            }
        ],
        "required": False
    }
]
