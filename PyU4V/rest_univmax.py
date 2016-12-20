try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config
import logging.config
from rest_requests import Restful

# register configuration file
LOG = logging.getLogger('PyU4V')
CONF_FILE = 'PyU4V.conf'
logging.config.fileConfig(CONF_FILE)
CFG = Config.ConfigParser()
CFG.read(CONF_FILE)

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


class rest_functions:
    def __init__(self):
        """ constructor"""
        self.array_id = CFG.get('setup', 'array')
        self.rest_client = Restful()

    ###############################
    # system functions
    ###############################

    def set_array(self, array):
        """Change to a different array.

        :param array: The VMAX serial number
        """
        self.array_id = array

    def get_jobList(self, jobID=None, name=None, status=None):
        """
        call queries for a list of Job ids for the specified symmetrix.
        :param jobID: specific ID of the job (optional)
        :param name: specific name of the job (optional)
        :param status: filter by status (optional).
                       Options are: CREATED, SCHEDULED, RETRIEVING_PICTURE, RUNNING,
                       SUCCEEDED, FAILED, ABORTED, UNKNOWN, VALIDATING, VALIDATED,
                       VALIDATE_FAILED, INVALID
        :return: server response (dict)
        """
        if jobID:
            url_add = "/" + jobID
        else:
            url_add = ""
        if name:
            url_add += "/?name=" + name
        if status:
            url_add += "/?status=" + status
        target_uri = "/system/symmetrix/%s/job%s" % (self.array_id, url_add)
        return self.rest_client.rest_request(target_uri, GET)

    def get_uni_version(self):
        target_uri = "/system/version"
        return self.rest_client.rest_request(target_uri, GET)

    def get_system_info(self):
        target_uri = "/system/symmetrix/%s" % self.array_id
        return self.rest_client.rest_request(target_uri, GET)

    #############################
    ### SRP & SLO functions
    #############################

    def get_SRP(self, SRP=None):
        """Gets a list of available SRP's on a given array, or returns
        details on a specific SRP if one is passed in in the parameters.

        :param SRP: the storage resource pool, optional
        :return: SRP details
        """
        if SRP:
            url_add = "/" + SRP
        else:
            url_add = ""
        target_uri = ("/sloprovisioning/symmetrix/%s/srp%s"
                      % (self.array_id, url_add))
        return self.rest_client.rest_request(target_uri, GET)

    def get_SLO(self, SLO_Id=None):
        """Gets a list of available SLO's on a given array, or returns
        details on a specific SLO if one is passed in in the parameters.

        :param SLO_Id: the service level agreement, optional
        :return: SLO details
        """
        if SLO_Id:
            url_add = "/" + SLO_Id
        else:
            url_add = ""
        target_uri = ("/sloprovisioning/symmetrix/%s/slo%s"
                      % (self.array_id, url_add))
        return self.rest_client.rest_request(target_uri, GET)

    def get_workload(self):
        """Gets details of all available workload types.

        :return: workload details
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/workloadtype"
                      % self.array_id)
        return self.rest_client.rest_request(target_uri, GET)

    ###########################
    ### storage group functions.
    #  Note: Can only create a volume in relation to a sg
    ###########################

    def get_sg(self, sg_id=None):
        """Gets details of all storage groups on a given array, or returns
        details on a specific sg if one is passed in in the parameters.

        :param sg_id: the storage group name, optional
        :return: sg details
        """
        if sg_id:
            url_add = "/" + sg_id
        else:
            url_add = ""
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup%s"
                      % (self.array_id, url_add))
        return self.rest_client.rest_request(target_uri, GET)

    def create_sg(self, new_sg_data):
        """Creates a new storage group with supplied specifications,
        given in dictionary form for json formatting

        :param new_sg_data: the payload of the request
        :return: response - dict
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup"
                      % (self.array_id))
        return self.rest_client.rest_request(
            target_uri, POST, request_object=new_sg_data)

    def get_mv_from_sg(self, storageGroup):
        """Get the associated masking view(s) from a given storage group

        :param storageGroup: the name of the storage group
        :return: Masking view list, or None
        """
        response = self.get_sg(storageGroup)
        mvlist = response["storageGroup"][0]["maskingview"]
        if len(mvlist) > 1:
            return mvlist
        else:
            return None

    # create volumes in new storage group

    def create_vols_in_new_SG(self, srpID, sg_id, slo, workload, num_vols, vol_size, capUnit):
        """Generates a dictionary for json formatting and calls the create_sg function
        to create a new storage group with the specified volumes

        :param srpID: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param num_vols: the amount of volumes to be created
        :param vol_size: the size of each volume
        :param capUnit: the capacity unit (MB, GB)
        :return: message
        """
        new_sg_data = ({"srpId": srpID, "storageGroupId": sg_id,
                        "sloBasedStorageGroupParam": [{"sloId": slo,
                                                       "workloadSelection": workload,
                                                       "num_of_vols": num_vols,
                                                       "volumeAttribute": {
                                                            "volume_size": vol_size,
                                                            "capacityUnit": capUnit}}]})
        return self.create_sg(new_sg_data)

    # create an empty storage group
    def create_empty_sg(self, srpID, sg_id, slo, workload):
        """Generates a dictionary for json formatting and calls the create_sg function
        to create an empty storage group

        :param srpID: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :return: message
        """
        new_sg_data = ({"srpId": srpID, "storageGroupId": sg_id,
                        "sloBasedStorageGroupParam": [{
                                            "num_of_vols": 1,
                                            "sloId": slo,
                                            "workloadSelection": workload,
                                            "volumeAttribute": {
                                                "volume_size": "0",
                                                "capacityUnit": "GB"}}],
                        "create_empty_storage_group": "true"})
        return self.create_sg(new_sg_data)

    def edit_sg(self, sg_id, edit_sg_data):
        """Edits an existing storage group

        :param sg_id: the name of the storage group
        :param edit_sg_data: the payload of the request
        :return: message
        """
        target_uri = ("/83/sloprovisioning/symmetrix/%s/storagegroup/%s"
                      % (self.array_id, sg_id))
        return self.rest_client.rest_request(
            target_uri, PUT, request_object=edit_sg_data)

    def add_existing_vol_to_sg(self, sg_id, vol_id):
        """Edit an existing storage group to add an existing volume to it

        :param sg_id: the name of the storage group
        :param vol_id: the device id of the volume
        :return: message
        """
        addVolData = {"editStorageGroupActionParam": {
                                    "addVolumeParam": {
                                            "volumeId": [vol_id]}}}
        return self.edit_sg(sg_id, addVolData)

    # create volume in an existing storage group
    def add_new_vol_to_sg(self, sg_id, num_vols, vol_size, capUnit):
        """Edit an existing storage group to create new volumes in it

        :param sg_id: the name of the storage group
        :param num_vols: the number of volumes
        :param vol_size: the size of the volumes
        :param capUnit: the capacity unit
        :return: message
        """
        expand_sg_data = ({"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "num_of_vols": num_vols,
                "emulation": "FBA",
                "volumeAttribute": {
                    "volume_size": vol_size,
                    "capacityUnit": capUnit
                },
                "create_new_volumes": "true"},}})
        return self.edit_sg(sg_id, expand_sg_data)

    # remove volume from SG
    def remove_vol_from_SG(self, sg_id, volID):
        """Remove a volume from a given storage group

        :param sg_id: the name of the storage group
        :param volID: the device id of the volume
        :return: message
        """
        del_vol_data = ({"editStorageGroupActionParam": {
            "removeVolumeParam": {
                "volumeId": [volID]}}})
        return self.edit_sg(sg_id, del_vol_data)

    def delete_sg(self, sg_id):
        """Delete a given storage group.

        A storage group cannot be deleted if it
        is associated with a masking view
        :param sg_id: the name of the storage group
        :return: status code
        """
        target_uri = "/83/sloprovisioning/symmetrix/%s/storagegroup/%s" \
                     % (self.array_id, sg_id)
        return self.rest_client.rest_request(target_uri, DELETE)

    #####################
    ### volume functions (except create)
    #####################

    def get_volume_by_id(self, volID):
        """Get a volume details by searching by device id.

        :param volID: the device ID of the volume
        :return: volume details
        """
        target_uri = "/sloprovisioning/symmetrix/%s/volume/%s" % (self.array_id, volID)
        return self.rest_client.rest_request(target_uri, GET)

    def get_vols_from_array(self, filters=None):
        """Gets details of volumes from array

        :param filters: can be eg storage group, vol ID etc. Optional.
        :return: volume details
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/volume"
                      % self.array_id)
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def get_deviceId_from_volume(self, vol_identifier):
        """Given the volume identifier (name), return the device ID

        :param vol_identifier: the identifier of the volume
        :return: the device ID of the volume
        """
        response = self.get_vols_from_array({'volume_identifier': vol_identifier})
        result = response['resultList']['result'][0]
        return result['volumeId']

    def get_vols_from_SG(self, sgID):
        """Retrieve volume information associated with a particular sg

        :param sgID: the name of the storage group
        :return: list of device IDs of associated volumes
        """
        vols = []
        response = self.get_vols_from_array({'storageGroupId': sgID})
        vol_list = response['resultList']['result']
        for vol in vol_list:
            vol_id = vol['volumeId']
            vols.append(vol_id)
        return vols

    def get_SG_from_vols(self, vol_id):
        """Retrieves sg information for a specified volume.
        Note that a FAST managed volume cannot be a
        member of more than one storage group.

        :param vol_id: the device ID of the volume
        :return: list of storage groups, or None
        """
        response = self.get_volume_by_id(vol_id)
        try:
            sglist = response["volume"][0]["storageGroupId"]
            return sglist
        except KeyError:
            return None

    def delete_volume(self, vol_id):
        """Delete a specified volume off the array.
        Note that you cannot delete volumes with any associations/ allocations

        :param vol_id: the device ID of the volume
        :return: status code (204 means the request has been successful
                              and that there is no additional content
                              to send in the response payload body.)
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/volume/%s"
                      % (self.array_id, vol_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    ###########################
    #   snapshot functions
    ###########################

    def check_snap_capabilities(self):
        """Check what replication facilities are available

        :return: Replication information
        """
        target_uri = "/replication/capabilities/symmetrix"
        return self.rest_client.rest_request(target_uri, GET)

    def get_snap_sg(self, sg_id):
        """get snapshot information on a particular sg

        :param sg_id: the name of the storage group
        :return: snapshot information
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot"
                      % (self.array_id, sg_id))
        return self.rest_client.rest_request(target_uri, GET)

    def get_snap_sg_generation(self, sg_id, snap_name):
        """Gets a snapshot and its generation count information for a Storage Group.
        The most recent snapshot will have a gen number of 0.
        The oldest snapshot will have a gen number = genCount - 1
        (i.e. if there are 4 generations of particular snapshot,
        the oldest will have a gen num of 3)

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: snapshot information
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot/%s"
                      % (self.array_id, sg_id, snap_name))
        return self.rest_client.rest_request(target_uri, GET)

    def create_sg_snapshot(self, sg_id, snap_name):
        """Creates a new snapshot of a specified sg

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot"
                      % (self.array_id, sg_id))
        snap_data = ({"snapshotName": snap_name})
        return self.rest_client.rest_request(
            target_uri, POST, request_object=snap_data)

    def create_new_gen_snap(self, sg_id, snap_name):
        """Establish a new generation of a SnapVX snapshot for a source SG

        :param sg_id: the name of the storage group
        :param snap_name: the name of the existing snapshot
        :return: message
        """
        target_uri = (
            "/replication/symmetrix/%s/storagegroup/%s/snapshot/%s/generation"
            % (self.array_id, sg_id, snap_name))
        data = ({})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=data)

    def restore_snapshot(self, sg_id, snap_name, gen_num):
        """Restore a storage group to its snapshot

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/"
                      "%s/snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({"action": "Restore"})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def rename_gen_snapshot(self, sg_id, snap_name, gen_num, new_name):
        """Rename an existing storage group snapshot

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot
        :param new_name: the new name of the snapshot
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/"
                      "snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({"rename": {"newSnapshotName": new_name},
                      "action": "Rename"})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def link_gen_snapshot(self, sg_id, snap_name, gen_num, link_sg_name):
        """Link a snapshot to another storage group

        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param gen_num: generation number of a snapshot
        :param link_sg_name:  the target storage group name
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/"
                      "snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({{"action": "Link",
                       "link": {"linkStorageGroupName": link_sg_name},
                       }})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def delete_sg_snapshot(self, sg_id, snap_name, gen_num):
        """Deletes a specified snapshot.
        Can only delete snap if generation number is known

        :param sg_id: name of the storage group
        :param snap_name: name of the snapshot
        :param gen_num: the generation number of the snapshot
        :return: status code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/"
                      "%s/snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        return self.rest_client.rest_request(target_uri, DELETE)

    def is_clone_licensed(self, array):
        """Check if the snapVx feature is licensed and enabled.

        :param session: the current rest session object
        :param array: the Symm array serial number
        :return: True if licensed and enabled; False otherwise
        """
        snapCapability = False
        target_uri = "/replication/capabilities/symmetrix"
        response = self.rest_client.rest_request(target_uri, GET)
        try:
            symmList = response['symmetrixCapability']
            for symm in symmList:
                if symm['symmetrixId'] == array:
                    snapCapability = symm['snapVxCapable']
                    break
        except KeyError:
            LOG.error("Cannot access replication capabilities")
        return snapCapability

    ######################################
    # ports/ hosts/ initiator groups functions
    ######################################

    def get_pg(self, portgroup):
        """Get details of a given portgroup

        :param portgroup: the name of the portgroup
        :return: portgroup details
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup/%s"
                      % (self.array_id, portgroup))
        return self.rest_client.rest_request(target_uri, GET)

    def extract_directorId_pg(self, portgroup):
        """Get the symm director information from the port group

        :param portgroup: the name of the portgroup
        :return: the director information
        """
        info = self.get_pg(portgroup)
        try:
            portKey = info["portGroup"][0]["symmetrixPortKey"]
            return portKey
        except KeyError:
            LOG.error("Cannot find port key information from given portgroup")

    def get_port_info(self, director, portNo):
        """Get details of the symmetrix port

        :param director: the director ID e.g. FA-1D
        :param portNo: the port number e.g. 1
        :return: the port information
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/director/%s/port/%s"
                      % (self.array_id, director, portNo))
        return self.rest_client.rest_request(target_uri, GET)

    def get_port_identifier(self, director, portNo):
        """Get the identifier (if FC - wwn; if iscsi - iqn) of the physical port

        :param director: the ID of the director
        :param portNo: the number of the port
        :return: wwn (FC) or iqn (iscsi), or None
        """
        info = self.get_port_info(director, portNo)
        try:
            identifier = info["symmetrixPort"][0]["identifier"]
            return identifier
        except KeyError:
            LOG.error("Cannot retrieve port information")
            return None

    def get_ig_list(self, host_id=None):
        """Get a list of all hosts/ initiator groups,
        or details on a particular host if provided

        :param host_id: the name of the host, optional
        :return: host details
        """
        if host_id:
            url_add = "/" + host_id
        else:
            url_add = ""
        target_uri = ("/sloprovisioning/symmetrix/%s/host%s"
                      % (self.array_id, url_add))
        return self.rest_client.rest_request(target_uri, GET)

    def get_mvs_from_ig(self, host_id):
        """Retrieve masking view information for a specified host.

        :param host_id: the name of the host
        :return: list of masking views or None
        """
        response = self.get_ig_list(host_id)
        try:
            mv_list = response["host"][0]["maskingview"]
            return mv_list
        except KeyError:
            LOG.debug("No masking views found for host %s." % host_id)
            return None

    def get_hwIDs_from_ig(self, host_id):
        """Get initiator details from a host.

        :param host_id: the name of the host
        :return: list of initiator IDs, or None
        """
        response = self.get_ig_list(host_id)
        try:
            initiator_list = response["host"][0]["initiator"]
            return initiator_list
        except KeyError:
            return None

    def create_ig(self, hostName, initiator_list):
        """Create a host with the given initiators.

        The initiators must not be associated with another host.
        :param hostName: the name of the new host
        :param initiator_list: list of initiators
        :return: message
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/host"
                      % self.array_id)
        new_ig_data = ({"hostId": hostName, "initiatorId": initiator_list})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=new_ig_data)

    def modify_ig(self, ig_id, ig_data):
        """Edit an existing host

        :param ig_id: the name of the host
        :param ig_data: the json payload
        :return: message
        """
        target_uri = "/sloprovisioning/symmetrix/%s/host/%s" \
                     % (self.array_id, ig_id)
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=ig_data)

    def delete_ig(self, ig_id):
        """Delete a given host.
        Cannot delete if associated with a masking view

        :param ig_id: name of the host
        :return: status code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/host/%s"
                      % (self.array_id, ig_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    # add initiator to existing ig
    def add_initiator_to_ig(self, hostId, initiatorId_list):
        """Add a list of initiators to an existing host.
        Initiators must not be associated with another host

        :param hostId: the name of the host
        :param initiatorId_list: the list of initiators
        :return: message
        """
        edit_ig_data = ({"editHostActionParam":
                            {"addInitiatorParam":
                                {"initiator": initiatorId_list}}})
        return self.modify_ig(hostId, edit_ig_data)

    def remove_initiators_from_ig(self, hostId, initiator_list):
        """Remove a list of initiators from an existing host.

        :param hostId: the name of the host
        :param initiatorId_list: the list of initiators
        :return: message
        """
        edit_ig_data = ({"editHostActionParam":
                             {"removeInitiatorParam":
                                  {"initiator": initiator_list}}})
        return self.modify_ig(hostId, edit_ig_data)

    def get_mv_connections(self, mv_name):
        """Get all connection information for a given masking view

        :param mv_name: the name of the masking view
        :return: connection information
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s/connections"
                      % (self.array_id, mv_name))
        return self.rest_client.rest_request(target_uri, GET)

    def list_initiators(self, filters=None):
        """Lists initiators on a given array

        :param filters: Optional filters e.g. {'in_a_host': 'true'}
        :return: initiator list
        """
        target_uri = "/sloprovisioning/symmetrix/%s/initiator" % self.array_id
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def is_initiator_in_host(self, initiator):
        """Check to see if a given initiator is already assigned to a host

        :param initiator: the initiator ID
        :return: bool
        """
        param = {'in_a_host': 'true', 'initiator_hba': initiator}
        response = self.list_initiators(param)
        try:
            if response['message'] == 'No Initiators Found':
                return False
        except KeyError:
            return True

    ###########################################
    ## masking views
    ###########################################

    def get_ig_from_mv(self, masking_view_id):
        """Given a masking view, get the associated host

        :param masking_view_id: the name of the masking view
        :return:
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s"
                      % (self.array_id, masking_view_id))
        response = self.rest_client.rest_request(target_uri, GET)
        try:
            hostId = response['maskingView'][0]['hostId']
            return hostId
        except KeyError:
            LOG.error("Error retrieving host ID from masking view")

    def delete_masking_view(self, masking_view_id):
        """Delete a given masking view.

        :param masking_view_id: the name of the masking view
        :return: status code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s"
                      % (self.array_id, masking_view_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_sg_from_mv(self, masking_view_id):
        """Given a masking view, get the associated storage group

        :param masking_view_id:
        :return: the name of the storage group, or None
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s"
                      % (self.array_id, masking_view_id))
        response = self.rest_client.rest_request(target_uri, GET)
        try:
            for r in response["maskingView"]:
                return r["storageGroupId"]
        except KeyError:
            return None

    def create_masking_view(self, port_group_name, masking_view_name,
                            host_name, storage_group_name):
        """Create a new masking view using existing/
        pre-created portgroup, host, and storage group

        :param port_group_name: name of the port group
        :param masking_view_name: name of the new masking view
        :param host_name: name of the host (initiator group)
        :param storage_group_name: name of the storage group
        :return: response - dict
        """
        info = ""
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview"
                      % self.array_id)

        mv_payload = {"portGroupSelection": {
            "useExistingPortGroupParam": {
                "portGroupId": port_group_name}},
            "maskingViewId": masking_view_name,
            "hostOrHostGroupSelection": {
                "useExistingHostParam": {
                    "hostId": host_name}},
            "storageGroupSelection": {
                "useExistingStorageGroupParam": {
                    "storageGroupId": storage_group_name}}
        }

        response = self.rest_client.rest_request(target_uri, POST,
                                                 request_object=mv_payload)
        if 'success' in response:
            LOG.info("Masking View Created Successfully. "
                     "Masking View ID: %s" % masking_view_name)
        elif 'message' in response:
            LOG.info("There was an error creating the Masking View."
                     "The message is: %s") % response['message']
        return response

    def close_session(self):
        """Close the current rest session
        """
        response = self.rest_client.close_session()
        return response
