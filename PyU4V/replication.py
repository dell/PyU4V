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
"""replication.py."""
import logging

from PyU4V.utils import constants

LOG = logging.getLogger(__name__)

REPLICATION = constants.REPLICATION
ASYNC_UPDATE = constants.ASYNC_UPDATE


class ReplicationFunctions(object):
    """ReplicationFunctions."""

    def __init__(self, array_id, request, common, provisioning, u4v_version):
        """__init__."""
        self.array_id = array_id
        self.common = common
        self.request = request
        self.provisioning = provisioning
        self.U4V_VERSION = u4v_version
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource

    def get_replication_info(self):
        """Return replication information for an array.

        :return: dict
        """
        target_uri = "%s/replication/symmetrix/%s" % (
            self.U4V_VERSION, self.array_id)
        return self.common.get_request(target_uri, 'replication info')

    def get_array_replication_capabilities(self):
        """Check what replication facilities are available.

        :return: array_capabilities dict
        """
        array_capabilities = {}
        target_uri = "/%s/replication/capabilities/symmetrix" % (
            self.U4V_VERSION)
        capabilities = self.common.get_request(
            target_uri, 'replication capabilities')
        symm_list = capabilities.get(
            'symmetrixCapability', []) if capabilities else []
        for symm in symm_list:
            if symm['symmetrixId'] == self.array_id:
                array_capabilities = symm
                break
        return array_capabilities

    def is_snapvx_licensed(self):
        """Check if the snapVx feature is licensed and enabled.

        :returns: True if licensed and enabled; False otherwise.
        """
        snap_capability = False
        capabilities = self.get_array_replication_capabilities()
        if capabilities:
            snap_capability = capabilities['snapVxCapable']
        else:
            LOG.error("Cannot access replication capabilities "
                      "for array %(array)s", {'array': self.array_id})
        return snap_capability

    def get_storage_group_rep(self, storage_group_name):
        """Given a name, return storage group details wrt replication.

        :param storage_group_name: the name of the storage group
        :returns: storage group dict
        """
        return self.get_resource(
            self.array_id, REPLICATION, 'storagegroup',
            resource_name=storage_group_name)

    def get_storage_group_rep_list(self, has_snapshots=False, has_srdf=False):
        """Return list of storage groups with replication.

        :param has_snapshots: return only storagegroups with snapshots
        :param has_srdf: return only storagegroups with SRDF
        :returns: list of storage groups with associated replication
        """
        filters = {}
        if has_snapshots:
            filters.update({'hasSnapshots': 'true'})
        if has_srdf:
            filters.update({'hasSrdf': 'true'})
        response = self.get_resource(
            self.array_id, REPLICATION, 'storagegroup', params=filters)
        storage_group_list = response.get('name', []) if response else []
        return storage_group_list

    def get_storagegroup_snapshot_list(self, storagegroup_id):
        """Get a list of snapshots associated with a storagegroup.

        :param storagegroup_id: the storagegroup name
        :return: list of snapshot names
        """
        res_name = "storagegroup/%s/snapshot" % storagegroup_id
        response = self.get_resource(
            self.array_id, REPLICATION, res_name)
        snapshot_list = response.get('name', []) if response else []
        return snapshot_list

    def create_storagegroup_snap(
            self, sg_name, snap_name, ttl=None, hours=False):
        """Create a snapVx snapshot of a storage group.

        To establish a new generation of an existing SnapVX snapshot
        for a source SG, use the same name as the existing snapshot for
        the new snapshot.

        :param sg_name: the source group name
        :param snap_name: the name of the snapshot
        :param ttl: ttl in days, if any - int
        :param hours: Boolean, if set will specify TTL value is hours not days
        """
        payload = {"snapshotName": snap_name}
        if ttl:
            payload.update({"timeToLive": ttl})
            if hours:
                payload.update({"timeInHours": "True"})
        resource_type = "storagegroup/%(sg_name)s/snapshot" % (
            {'sg_name': sg_name})
        return self.create_resource(
            self.array_id, REPLICATION, resource_type, payload=payload)

    def get_storagegroup_snapshot_generation_list(
            self, storagegroup_id, snap_name):
        """Get a snapshot and its generation count information for an sg.

        The most recent snapshot will have a gen number of 0.
        The oldest snapshot will have a gen number = genCount - 1
        (i.e. if there are 4 generations of particular snapshot,
        the oldest will have a gen num of 3)

        :param storagegroup_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: list of generation numbers
        """
        gen_list = []
        res_name = "%s/snapshot/%s/generation" % (
            storagegroup_id, snap_name)
        response = self.get_resource(self.array_id, REPLICATION,
                                     'storagegroup', resource_name=res_name)
        if response and response.get('generations'):
            gen_list = response['generations']
        return gen_list

    def get_snapshot_generation_details(self, sg_id, snap_name, gen_num):
        """Get the details for a particular snapshot generation.

        :param sg_id: the storage group id
        :param snap_name: the snapshot name
        :param gen_num: Generation number
        :return: dict
        """
        resource_name = "%s/snapshot/%s/generation/%s" % (
            sg_id, snap_name, gen_num)
        return self.get_resource(
            self.array_id, REPLICATION, 'storagegroup',
            resource_name=resource_name)

    def find_expired_snapvx_snapshots(self):
        """Find all expired snapvx snapshots.

        Parses through all Snapshots for array and lists those that have
        snapshots where the expiration date has passed however snapshots
        have not been deleted as they have links. Example output:
        [{'storagegroup_name': 'my-storagegroup1',
        'snapshot_name': 'my-temporary-snap',
        'generation_number': '0',
        'expiration_time': '14:46:24 Wed, 24 Jan 2018',
        'linked_sg_name': 'my-linked-sg',
        'snap_creation_time': '14:46:24 Wed, 23 Jan 2018'}]

        :return: list of dicts with expired snap details,
        """
        expired_snap_list = []
        sglist = self.get_storage_group_rep_list(has_snapshots=True)
        for sg in sglist:
            snaplist = self.get_storage_group_rep(sg)
            for snapshot_name in snaplist["snapVXSnapshots"]:
                snapcount = self.get_storagegroup_snapshot_generation_list(
                    sg, snapshot_name)
                for x in range(0, len(snapcount)):
                    snapdetails = self.get_snapshot_generation_details(
                        sg, snapshot_name, x)
                    if snapdetails["isExpired"]:
                        snapcreation_time = snapdetails["timestamp"]
                        snapexpiration = snapdetails[
                            "timeToLiveExpiryDate"]
                        for linked_sg in snapdetails.get(
                                "linkedStorageGroup", []):
                            linked_sg_name = linked_sg["name"]
                            LOG.debug(
                                "Storage group %(sg)s has expired snapshot. "
                                "Snapshot name %(ss)s, Generation Number "
                                "%(gen_no)s, snapshot expired on %(snap_ex)s, "
                                "linked storage group name is %(sg_name)s",
                                {'sg': sg,
                                 'ss': snapshot_name,
                                 'gen_no': x,
                                 'snap_ex': snapexpiration,
                                 'sg_name': linked_sg_name})
                            expired_snap_details = {
                                'storagegroup_name': sg,
                                'snapshot_name': snapshot_name,
                                'generation_number': x,
                                'expiration_time': snapexpiration,
                                'linked_sg_name': linked_sg_name,
                                'snap_creation_time': snapcreation_time}
                            expired_snap_list.append(expired_snap_details)
        return expired_snap_list

    def modify_storagegroup_snap(
            self, source_sg_id, target_sg_id, snap_name, link=False,
            unlink=False, restore=False, new_name=None, gen_num=0,
            _async=False):
        """Modify a storage group snapshot.

        Please note that only one parameter can be modified at a time.
        Default action is not to create full copy

        :param source_sg_id: the source sg id
        :param target_sg_id: the target sg id (Can be None)
        :param snap_name: the snapshot name
        :param link: Flag to indicate action = Link
        :param unlink: Flag to indicate action = Unlink
        :param restore: Flag to indicate action = Restore
        :param new_name: the new name for the snapshot
        :param gen_num: the generation number
        :param _async: flag to indicate if call should be async
        """
        payload = {}
        if link:
            payload = {"link": {"linkStorageGroupName": target_sg_id,
                                "copy": False},
                       "action": "Link"}
        elif unlink:
            payload = {"unlink": {"unlinkStorageGroupName": target_sg_id},
                       "action": "Unlink"}

        elif restore:
            payload = {"action": "Restore"}

        elif new_name:
            payload = ({"rename": {"newSnapshotName": new_name},
                        "action": "Rename"})

        if _async:
            payload.update(ASYNC_UPDATE)

        resource_name = ("%s/snapshot/%s/generation/%s" % (
            source_sg_id, snap_name, gen_num))

        return self.modify_resource(
            self.array_id, REPLICATION, 'storagegroup', payload=payload,
            resource_name=resource_name)

    def restore_snapshot(self, sg_id, snap_name, gen_num=0):
        """Restore a storage group to its snapshot.

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot (int)
        :return: dict
        """
        return self.modify_storagegroup_snap(
            self.array_id, sg_id, None, snap_name,
            restore=True, gen_num=gen_num)

    def rename_snapshot(self, sg_id, snap_name, new_name, gen_num=0):
        """Rename an existing storage group snapshot.

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param new_name: the new name of the snapshot
        :param gen_num: generation number of a snapshot (int)
        :return: dict
        """
        return self.modify_storagegroup_snap(
            sg_id, None, snap_name,
            new_name=new_name, gen_num=gen_num)

    def link_gen_snapshot(self, sg_id, snap_name, link_sg_name,
                          _async=False, gen_num=0):
        """Link a snapshot to another storage group.

        Target storage group will be created if it does not exist.

        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param link_sg_name:  the target storage group name
        :param _async: flag to indicate if call is async
        :param gen_num: generation number of a snapshot (int)
        :return: dict
        """
        return self.modify_storagegroup_snap(
            sg_id, link_sg_name, snap_name,
            link=True, gen_num=gen_num, _async=_async)

    def unlink_gen_snapshot(self, sg_id, snap_name, unlink_sg_name,
                            _async=False, gen_num=0):
        """Unink a snapshot from another storage group.

        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param unlink_sg_name:  the target storage group name
        :param _async: flag to indicate if call is async
        :param gen_num: generation number of a snapshot (int)
        :return: dict
        """
        return self.modify_storagegroup_snap(
            sg_id, unlink_sg_name, snap_name,
            unlink=True, gen_num=gen_num, _async=_async)

    def delete_storagegroup_snapshot(self, storagegroup, snap_name, gen_num=0):
        """Delete the snapshot of a storagegroup.

        :param storagegroup: the storage group name
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number
        """
        resource_name = "storagegroup/%s/snapshot/%s/generation/%s" % (
            storagegroup, snap_name, gen_num)
        return self.delete_resource(
            self.array_id, REPLICATION, resource_name)

    def choose_snapshot_from_list_in_console(self, storagegroup_id):
        """Allow a user to select a snapshot from a list.

        :param storagegroup_id: the storagegoup id
        """
        snaplist = self.get_storagegroup_snapshot_list(storagegroup_id)
        print("Choose the snapshot you want from the below list: \n")
        for counter, value in enumerate(snaplist):
            print("%s: %s" % (counter, value))
        snapselection = input("Choice: ")
        snapshot_id = (snaplist[int(snapselection)])
        return snapshot_id

    def is_vol_in_rep_session(self, device_id):
        """Check if a volume is in a replication session.

        :param device_id: the device id
        :returns: snapvx_tgt -- bool, snapvx_src -- bool,
                 rdf_grp -- list or None
        """
        snapvx_src = False
        snapvx_tgt = False
        rdf_grp = None
        volume_details = self.provisioning.get_volume(device_id)
        if volume_details:
            LOG.debug("Vol details: %(vol)s", {'vol': volume_details})
            if volume_details.get('snapvx_target'):
                snapvx_tgt = volume_details['snapvx_target']
            if volume_details.get('snapvx_source'):
                snapvx_src = volume_details['snapvx_source']
            if volume_details.get('rdfGroupId'):
                rdf_grp = volume_details['rdfGroupId']
        return snapvx_tgt, snapvx_src, rdf_grp

    def get_rdf_group(self, rdf_number):
        """Get specific rdf group details.

        :param rdf_number: the rdf number
        """
        return self.get_resource(
            self.array_id, REPLICATION, 'rdf_group', resource_name=rdf_number)

    def get_rdf_group_list(self):
        """Get rdf group list from array.

        :returns: list of rdf group dicts with 'rdfgNumber' and 'label'
        """
        response = self.get_resource(self.array_id, REPLICATION, 'rdf_group')
        rdfg_dict_list = response.get('rdfGroupID', []) if response else []
        return rdfg_dict_list

    def get_rdf_group_volume(self, rdf_number, device_id):
        """Get specific volume details, from an RDF group.

        :param rdf_number: the rdf group number
        :param device_id: the device id
        """
        resource_name = "%(rdf)s/volume/%(dev)s" % (
            {'rdf': rdf_number, 'dev': device_id})
        return self.get_resource(
            self.array_id, REPLICATION, 'rdf_group',
            resource_name=resource_name)

    def get_rdf_group_volume_list(self, rdf_number):
        """Get specific volume details, from an RDF group.

        :param rdf_number: the rdf group number
        :returns: list of device ids
        """
        resource_name = "%s/volume" % rdf_number
        response = self.get_resource(
            self.array_id, REPLICATION, 'rdf_group',
            resource_name=resource_name)
        device_list = response.get('name', []) if response else []
        return device_list

    def are_vols_rdf_paired(self, remote_array, device_id,
                            target_device, rdf_group):
        """Check if a pair of volumes are RDF paired.

        :param remote_array: the remote array serial number
        :param device_id: the device id
        :param target_device: the target device id
        :param rdf_group: the rdf group
        :returns: paired -- bool, state -- string
        """
        paired, local_vol_state, rdf_pair_state = False, '', ''
        volume = self.get_rdf_group_volume(rdf_group, device_id)
        if volume:
            remote_volume = volume['remoteVolumeName']
            remote_symm = volume['remoteSymmetrixId']
            if (remote_volume == target_device and (
                    remote_array == remote_symm)):
                paired = True
                local_vol_state = volume['localVolumeState']
                rdf_pair_state = volume['rdfpairState']
        else:
            LOG.warning("Cannot find source RDF volume %(device_id)s.",
                        {'device_id': device_id})
        return paired, local_vol_state, rdf_pair_state

    def get_rdf_group_number(self, rdf_group_label):
        """Given an rdf_group_label, return the associated group number.

        :param rdf_group_label: the group label
        :returns: rdf_group_number
        """
        number = None
        rdf_list = self.get_rdf_group_list()
        if rdf_list:
            number = [rdf['rdfgNumber'] for rdf in rdf_list
                      if rdf['label'] == rdf_group_label][0]
        if number:
            rdf_group = self.get_rdf_group(number)
            if not rdf_group:
                number = None
        return number

    def get_storagegroup_srdfg_list(self, storagegroup_id):
        """Get the SRDF numbers for a storage group.

        :param storagegroup_id: Storage Group Name of replicated group
        :return: list of RDFG numbers
        """
        res_name = "%s/rdf_group" % storagegroup_id
        response = self.get_resource(
            self.array_id, REPLICATION, 'storagegroup', resource_name=res_name)
        rdfg_list = response.get('rdfgs', []) if response else []
        return rdfg_list

    def get_storagegroup_srdf_details(self, storagegroup_id, rdfg_num):
        """Get the SRDF details for an RDF group on a particular storagegroup.

        :param storagegroup_id: name of storage group
        :param rdfg_num: rdf number
        :return: dict
        """
        res_name = "%s/rdf_group/%s" % (storagegroup_id, rdfg_num)
        return self.get_resource(
            self.array_id, REPLICATION, 'storagegroup', resource_name=res_name)

    def create_storagegroup_srdf_pairings(
            self, storagegroup_id, remote_sid, srdfmode, establish=None,
            _async=False, rdfg_number=None, forceNewRdfGroup=False):
        """SRDF protect a storage group.

        :param storagegroup_id: Unique string up to 32 Characters
        :param remote_sid: Type Integer 12 digit VMAX ID e.g. 000197000008
        :param srdfmode: String, values can be Active, AdaptiveCopyDisk,
                         Synchronous, Asynchronous
        :param establish: default is none. Bool
        :param _async: Flag to indicate if call should be async
                      (NOT to be confused with the SRDF mode)
        :param rdfg_number: the required RDFG number (optional)
        :return: message and status Type JSON
        """
        res_type = "storagegroup/%s/rdf_group" % storagegroup_id
        establish_sg = "True" if establish else "False"
        rdf_payload = {"replicationMode": srdfmode,
                       "remoteSymmId": remote_sid,
                       "remoteStorageGroupName": storagegroup_id,
                       "establish": establish_sg}
        if rdfg_number is not None:
            rdf_payload['rdfgNumber'] = rdfg_number
        if forceNewRdfGroup:
            rdf_payload.update({'forceNewRdfGroup': True})
        if _async:
            rdf_payload.update(ASYNC_UPDATE)

        return self.create_resource(
            self.array_id, REPLICATION, res_type, payload=rdf_payload)

    def modify_storagegroup_srdf(
            self, storagegroup_id, action, rdfg, options=None, _async=False):
        """Modify the state of an srdf.

        This may be a long running task depending on the size of the SRDF
        group, can switch to async call if required.

        :param storagegroup_id: name of storage group
        :param action: the rdf action e.g. Suspend, Establish, SetMode etc
        :param rdfg: rdf number
        :param options: a dict of possible options - depends on action type,
        example options={setMode': {'mode': 'Asynchronous'}}
        :param _async: flag to indicate if call should be async
        """
        res_name = "%s/rdf_group/%s" % (storagegroup_id, rdfg)
        payload = {"action": action}
        if _async:
            payload.update(ASYNC_UPDATE)

        if options and action:
            payload.update(options)

        return self.modify_resource(
            self.array_id, REPLICATION, 'storagegroup',
            payload=payload, resource_name=res_name)

    def suspend_storagegroup_srdf(
            self, storagegroup_id, rdfg_no,
            suspend_options=None, _async=False):
        """Suspend io on the links for the given storagegroup.

        Optional parameters to set are "bypass", "metroBias", "star",
        "immediate", "hop2", "consExempt", "force", "symForce" - all
        true/false.

        :param storagegroup_id: the storagegroup id
        :param rdfg_no: the rdf group no
        :param suspend_options: Optional dict of suspend params
        :param _async: flag to indicate async call
        """
        return self.modify_storagegroup_srdf(
            storagegroup_id, 'suspend', rdfg_no,
            options=suspend_options, _async=_async)

    def establish_storagegroup_srdf(
            self, storagegroup_id, rdfg_no,
            establish_options=None, _async=False):
        """Establish io on the links for the given storagegroup.

        Optional parameters to set are "bypass", "metroBias", "star",
        "hop2", "force", "symForce", "full" - all true/false.

        :param storagegroup_id: the storagegroup id
        :param rdfg_no: the rdf group no
        :param establish_options: Optional dict of establish params
        :param _async: flag to indicate async call
        """
        return self.modify_storagegroup_srdf(
            storagegroup_id, 'establish', rdfg_no,
            options=establish_options, _async=_async)

    def failover_storagegroup_srdf(
            self, storagegroup_id, rdfg_no,
            failover_options=None, _async=False):
        """Failover a given storagegroup.

        Optional parameters to set are "bypass", "star", "restore",
        "immediate", "hop2", "force", "symForce", "remote", "establish" - all
        true/false.

        :param storagegroup_id: the storagegroup id
        :param rdfg_no: the rdf group no
        :param failover_options: Optional dict of failover params
        :param _async: flag to indicate async call
        """
        return self.modify_storagegroup_srdf(
            storagegroup_id, 'failover', rdfg_no,
            options=failover_options, _async=_async)

    def failback_storagegroup_srdf(
            self, storagegroup_id, rdfg_no, failback_options=None,
            _async=False):
        """Failback a given storagegroup.

        Optional parameters to set are "bypass", "recoverPoint", "star",
        "hop2", "force", "symForce", "remote" - all true/false.

        :param storagegroup_id: the storagegroup id
        :param rdfg_no: the rdf group no
        :param failback_options: Optional dict of failover params
        :param _async: flag to indicate async call
        """
        return self.modify_storagegroup_srdf(
            storagegroup_id, 'failback', rdfg_no,
            options=failback_options, _async=_async)

    def delete_storagegroup_srdf(
            self, storagegroup_id, rdfg_num=None):
        """Delete srdf pairings for a given storagegroup.

        :param storagegroup_id:
        :param rdfg_num: the rdfg number to remove pairings from - can be list
        """
        # Get a list of SRDF groups for storage group
        if not rdfg_num:
            rdfg_num = self.get_storagegroup_srdfg_list(storagegroup_id)
        if not isinstance(rdfg_num, list):
            rdfg_num = [rdfg_num]
        for rdfg in rdfg_num:
            res_name = "%s/rdf_group/%s" % (storagegroup_id, rdfg)
            self.delete_resource(
                self.array_id, REPLICATION,
                'storagegroup', resource_name=res_name)
