# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
"""snapshot.py."""

import logging
from typing import Any

from PyU4V.common import CommonFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.utils import constants
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

ASYNC_UPDATE = constants.ASYNC_UPDATE
REPLICATION = constants.REPLICATION
SYMMETRIX = constants.SYMMETRIX
STORAGEGROUP = constants.STORAGEGROUP
SNAPSHOT = constants.SNAPSHOT
GENERATION = constants.GENERATION
SNAP_ID = constants.SNAP_ID


class SnapshotFunctions(object):
    """SnapshotFunctions."""

    def __init__(self, array_id: str, rest_client: Any) -> None:
        """__init__."""
        self.provisioning = ProvisioningFunctions(array_id, rest_client)
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id

    def is_snapvx_licensed(self) -> bool:
        """Check if the snapVx feature is licensed and enabled.

        :returns: bool
        """
        snap_capability = False
        capabilities = self._get_array_replication_capabilities()
        if capabilities:
            snap_capability = capabilities.get('snapVxCapable', False)
        else:
            LOG.error('Cannot access replication capabilities '
                      'for array {arr}'.format(arr=self.array_id))
        return snap_capability

    def get_storage_group_snapshot_list(self, storage_group_id: str) -> list[str]:
        """Get a list of snapshots associated with a storage group.

        :param storage_group_id: storage group id -- str
        :returns: snapshot ids -- list
        """
        try:
            response = self.common.get_request(
                target_uri=f"/{self.common.UNI_VERSION}/replication"
                f"/symmetrix/{self.array_id}/storagegroup"
                f"/{storage_group_id}/snapshot",
                resource_type=None)
        except exception.ResourceNotFoundException:
            return list()
        return response.get('name', list()) if response else list()

    def create_storage_group_snapshot(
            self, storage_group_id: str, snap_name: str, ttl: int | None = None, hours: bool = False,
            secure: bool = False, bothsides: bool = False) -> dict[str, Any]:
        """Create a snapVx snapshot of a storage group.

        To establish a new generation of an existing SnapVX snapshot for a
        source SG, use the same name as the existing snapshot for the new
        snapshot.

        :param storage_group_id: source storage group id -- str
        :param snap_name: snapshot name -- str
        :param ttl: Time To Live -- str
        :param hours: if TTL is in hours instead of days -- bool
        :param secure: sets secure snapshot, snapshot created with secure
               option can not be deleted before ttl expires -- bool
        :param bothsides: if both sides should be snapshotted -- bool
        :returns: snapshot details -- dict
        """
        payload = {'snapshotName': snap_name}
        if ttl:
            if secure:
                payload.update({'secure': ttl})
            else:
                payload.update({'timeToLive': ttl})
            if hours:
                payload.update({'timeInHours': 'True'})
        if bothsides:
            payload.update({'bothSides': 'True'})
        return self.common.create_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}/snapshot",
            payload=payload)

    def get_storage_group_snapshot_generation_list(
            self, storage_group_id: str, snap_name: str) -> dict[str, Any]:
        """Get a snapshot and its generation count information for an sg.

        This is for arrays with microcode less than 5978.669.669.
        Please use get_storage_group_snapshot_snap_id_list for microcode
        greater than 5978.669.669.

        The most recent snapshot will have a gen number of 0. The oldest
        snapshot will have a gen number = genCount - 1 (i.e. if there are 4
        generations of particular snapshot, the oldest will have a gen num
        of 3).

        :param storage_group_id: name of the storage group -- str
        :param snap_name: the name of the snapshot -- str
        :returns: generation numbers -- list
        """
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}/snapshot/{snap_name}"
            f"/generation",
            resource_type=None)
        return response.get('generations', list()) if response else list()

    def get_storage_group_snapshot_snap_id_list(
            self, storage_group_id: str, snap_name: str) -> dict[str, Any]:
        """Get a snapshot and its snap id information for an sg.

        Each snapid is unique.  These have replaced generations starting
        at U4P9.2. Snap ids are only available on microcode 5978.669.669
        and greater.

        :param storage_group_id: name of the storage group -- str
        :param snap_name: the name of the snapshot -- str
        :returns: snapids -- list
        """
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}/snapshot/{snap_name}"
            f"/snapid",
            resource_type=None)
        return response.get('snapids', list()) if response else list()

    def get_snapshot_generation_details(self, sg_id: str, snap_name: str, gen_num: int) -> dict[str, Any]:
        """Get the details for a particular snapshot generation.

        This is for arrays with microcode less than 5978.669.669.
        Please use get_snapshot_snap_id_details for microcode greater than
        5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param gen_num: generation number -- int
        :returns: snapshot generation details -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{sg_id}/snapshot/{snap_name}"
            f"/generation/{gen_num}",
            resource_type=None)

    def get_snapshot_snap_id_details(self, sg_id: str, snap_name: str, snap_id: int) -> dict[str, Any]:
        """Get the details for a particular snapshot snap_id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param snap_id: unique snap id -- int
        :returns: snapshot snap id details -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{sg_id}/snapshot/{snap_name}"
            f"/snapid/{snap_id}",
            resource_type=None)

    def find_expired_snapvx_snapshots(self) -> list[dict[str, Any]]:
        """Find all expired snapvx snapshots.

        This is for arrays with microcode less than 5978.669.669.
        Please use find_expired_snapvx_snapshots_by_snap_ids for microcode
        greater than 5978.669.669.

        Parses through all Snapshots for array and lists those that have
        snapshots where the expiration date has passed however snapshots
        have not been deleted as they have links.

        :returns: expired snapshot details -- list
        """
        expired_snap_list = list()
        sg_list = self._get_replication_enabled_storage_groups(
            has_snapshots=True)
        for sg in sg_list:
            snap_list = self._get_storage_group_replication_details(sg)
            for snapshot_name in snap_list['snapVXSnapshots']:
                snap_gen_list = (
                    self.get_storage_group_snapshot_generation_list(
                        sg, snapshot_name))
                for x in snap_gen_list:
                    snap_details = self.get_snapshot_generation_details(
                        sg, snapshot_name, x)
                    expired = snap_details.get(
                        'isExpired') if snap_details.get(
                        'isExpired') else snap_details.get('expired')
                    if expired:
                        snap_creation_time = snap_details.get('timestamp')
                        for linked_sg in snap_details.get(
                                'linkedStorageGroup', list()):
                            linked_sg_name = linked_sg['name']
                            LOG.debug(
                                'Storage group {sg} has expired snapshot. '
                                'Snapshot name {ss}, Generation Number {gen}, '
                                'linked storage group name is {sg_l}'.format(
                                    sg=sg, ss=snapshot_name, gen=x,
                                    sg_l=linked_sg_name))
                            expired_snap_details = ({
                                'storagegroup_name': sg,
                                'snapshot_name': snapshot_name,
                                'generation_number': x,
                                'linked_sg_name': linked_sg_name,
                                'snap_creation_time': snap_creation_time})
                            expired_snap_list.append(expired_snap_details)
        return expired_snap_list

    def find_expired_snapvx_snapshots_by_snap_ids(self) -> list[dict[str, Any]]:
        """Find all expired snapvx snapshots using snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        Parses through all Snapshots for array and lists those that have
        snapshots where the expiration date has passed however snapshots
        have not been deleted as they have links.

        :returns: expired snapshot details -- list
        """
        expired_snap_list = list()
        sg_list = self._get_replication_enabled_storage_groups(
            has_snapshots=True)
        for sg in sg_list:
            sg_snap_info = self._get_storage_group_replication_details(sg)
            if not sg_snap_info.get('snapVXSnapshots'):
                continue
            for snapshot_name in sg_snap_info.get('snapVXSnapshots'):
                snap_id_list = (
                    self.get_storage_group_snapshot_snap_id_list(
                        sg, snapshot_name))
                for x in snap_id_list:
                    snap_details = self.get_snapshot_snap_id_details(
                        sg, snapshot_name, x)
                    expired = snap_details.get(
                        'isExpired') if snap_details.get(
                        'isExpired') else snap_details.get('expired')
                    if expired:
                        snap_creation_time = snap_details.get('timestamp')
                        for linked_sg in snap_details.get(
                                'linked_storage_group', list()):
                            linked_sg_name = linked_sg['name']
                            LOG.debug(
                                'Storage group {sg} has expired snapshot. '
                                'Snapshot name {ss}, Snap Id {snap_id}, '
                                'linked storage group name is {sg_l}'.format(
                                    sg=sg, ss=snapshot_name, snap_id=x,
                                    sg_l=linked_sg_name))
                            expired_snap_details = ({
                                'storagegroup_name': sg,
                                'snapshot_name': snapshot_name,
                                'snap_id': x,
                                'linked_sg_name': linked_sg_name,
                                'snap_creation_time': snap_creation_time})
                            expired_snap_list.append(expired_snap_details)
        return expired_snap_list

    def modify_storage_group_snapshot(
            self, src_storage_grp_id: str, tgt_storage_grp_id: str | None, snap_name: str,
            link: bool = False, unlink: bool = False, restore: bool = False, new_name: str | None = None,
            gen_num: int = 0, _async: bool = False, relink: bool = False) -> dict[str, Any]:
        """Modify a storage group snapshot.

        This is for arrays with microcode less than 5978.669.669.
        Please use modify_storage_group_snapshot_by_snap_id for microcode
        greater than 5978.669.669.

        Please note that only one parameter can be modified at a time.
        Default action is not to create full copy.

        :param src_storage_grp_id: name of the storage group -- str
        :param tgt_storage_grp_id: target sg id (Can be None) -- str
        :param snap_name: snapshot name -- str
        :param link: link action required -- bool
        :param unlink: unlink action required -- bool
        :param restore: restore action required -- bool
        :param new_name: new name for the snapshot -- str
        :param gen_num: generation number -- int
        :param _async: if call should be async -- bool
        :param relink: relink action required -- bool
        :returns: modified storage group snapshot details -- dict
        """
        payload = dict()
        if link:
            payload = ({'action': 'Link', 'link': {
                'linkStorageGroupName': tgt_storage_grp_id,
                'copy': False}})
        elif unlink:
            payload = ({'action': 'Unlink', 'unlink': {
                'unlinkStorageGroupName': tgt_storage_grp_id}})
        elif restore:
            payload = {'action': 'Restore'}
        elif new_name:
            payload = ({'rename': {'newSnapshotName': new_name},
                        'action': 'Rename'})
        elif relink:
            payload = ({'action': 'Relink', 'relink': {
                'relinkStorageGroupName': tgt_storage_grp_id}})
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.common.modify_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{src_storage_grp_id}/snapshot/{snap_name}"
            f"/generation/{gen_num}",
            resource_type=None, payload=payload)

    def modify_storage_group_snapshot_by_snap_id(
            self, src_storage_grp_id: str, tgt_storage_grp_id: str | None, snap_name: str,
            snap_id: int, link: bool = False, unlink: bool = False, restore: bool = False, new_name: str | None = None,
            _async: bool = False, relink: bool = False, remote: bool = False, force: bool = False) -> dict[str, Any]:
        """Modify a storage group snapshot using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        Please note that only one parameter can be modified at a time.
        Default action is not to create full copy

        :param src_storage_grp_id: name of the storage group -- str
        :param tgt_storage_grp_id: target sg id (Can be None) -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snap id -- int
        :param link: link action required -- bool
        :param unlink: unlink action required -- bool
        :param restore: restore action required -- bool
        :param new_name: new name for the snapshot -- str
        :param _async: if call should be async -- bool
        :param relink: relink action required -- bool
        :param remote: used when linking/relinking to established R1 Storage
                       group,using this feature acknowledges that the data
                       from snapshot will be transmitted to R2 site,removes
                       the need to suspend/establish SRDF as part of link
                       operation.Caution should be applied -- bool
        :param force: forces operation to succeed that would normally
                      fail.Example terminate snapshots in SG where devices
                      have been added,using symforce will bypass the device
                      count check.Should be used with caution. -- bool
        :returns: modified storage group snapshot details -- dict
        """
        payload = dict()
        if link:
            payload = ({'action': 'Link', 'link': {
                'storage_group_name': tgt_storage_grp_id,
                'remote': remote,
                'force': force,
                'copy': False}})
        elif unlink:
            payload = ({'action': 'Unlink', 'unlink': {
                'storage_group_name': tgt_storage_grp_id,
                'force': force}})
        elif restore:
            payload = {'action': 'Restore'}
        elif new_name:
            payload = ({'rename': {'new_snapshot_name': new_name},
                        'action': 'Rename'})
        elif relink:
            payload = ({'action': 'Relink', 'relink': {
                'storage_group_name': tgt_storage_grp_id,
                'remote': remote,
                'force': force}})
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.common.modify_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{src_storage_grp_id}/snapshot/{snap_name}"
            f"/snapid/{snap_id}",
            resource_type=None, payload=payload)

    def restore_snapshot(self, sg_id: str, snap_name: str, gen_num: int = 0) -> dict[str, Any]:
        """Restore a storage group to its snapshot.

        This is for arrays with microcode less than 5978.669.669.
        Please use restore_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            sg_id, None, snap_name, restore=True, gen_num=gen_num)

    def restore_snapshot_by_snap_id(self, sg_id: str, snap_name: str, snap_id: int) -> dict[str, Any]:
        """Restore a storage group to its snapshot using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, None, snap_name, snap_id, restore=True)

    def rename_snapshot(self, sg_id: str, snap_name: str, new_name: str, gen_num: int = 0) -> dict[str, Any]:
        """Rename an existing storage group snapshot.

        This is for arrays with microcode less than 5978.669.669.
        Please use rename_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param new_name: new snapshot name -- str
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            sg_id, None, snap_name,
            new_name=new_name, gen_num=gen_num)

    def rename_snapshot_by_snap_id(self, sg_id: str, snap_name: str, new_name: str, snap_id: int) -> dict[str, Any]:
        """Rename an existing storage group snapshot using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param new_name: new snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, None, snap_name, snap_id, new_name=new_name)

    def link_gen_snapshot(self, sg_id: str, snap_name: str, link_sg_name: str,
                          _async: bool = False, gen_num: int = 0) -> dict[str, Any]:
        """Link a snapshot to another storage group.

        This is for arrays with microcode less than 5978.669.669.
        Please use link_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        Target storage group will be created if it does not exist.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param link_sg_name: target storage group name -- str
        :param _async: if call should be async -- bool
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            sg_id, link_sg_name, snap_name,
            link=True, gen_num=gen_num, _async=_async)

    def link_snapshot_by_snap_id(
            self, sg_id: str, link_sg_name: str, snap_name: str, snap_id: int, _async: bool = False) -> dict[str, Any]:
        """Link a snapshot to another storage group using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        Target storage group will be created if it does not exist.

        :param sg_id: storage group id -- str
        :param link_sg_name: target storage group name -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :param _async: if call should be async -- bool
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, link_sg_name, snap_name, snap_id, link=True, _async=_async)

    def unlink_gen_snapshot(self, sg_id: str, snap_name: str, unlink_sg_name: str,
                            _async: bool = False, gen_num: int = 0) -> dict[str, Any]:
        """Unlink a snapshot from another storage group.

        This is for arrays with microcode less than 5978.669.669.
        Please use unlink_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param unlink_sg_name: target storage group name -- str
        :param _async: if call should be async -- bool
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            sg_id, unlink_sg_name, snap_name,
            unlink=True, gen_num=gen_num, _async=_async)

    def unlink_snapshot_by_snap_id(
            self, sg_id: str, unlink_sg_name: str, snap_name: str, snap_id: int, _async: bool = False) -> dict[str, Any]:
        """Unlink a snapshot from another storage group using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param unlink_sg_name: target storage group name -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :param _async: if call should be async -- bool
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, unlink_sg_name, snap_name, snap_id,
            unlink=True, _async=_async)

    def delete_storage_group_snapshot(self, storage_group_id: str, snap_name: str,
                                      gen: int = 0) -> None:
        """Delete the snapshot of a storage group.

        This is for arrays with microcode less than 5978.669.669.
        Please use delete_storage_group_snapshot_by_snap_id for microcode
        greater than 5978.669.669.

        :param storage_group_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param gen: snapshot generation number -- int
        """
        self.common.delete_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}/snapshot/{snap_name}"
            f"/generation/{gen}")

    def delete_storage_group_snapshot_by_snap_id(
            self, storage_group_id: str, snap_name: str, snap_id: int, force: bool = False,
            array_id: str | None = None, symforce: bool = False) -> None:
        """Delete the snapshot of a storage group using the snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param storage_group_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :param force: sets force flag -- bool
        :param array_id: 12 digit array id -- int
        :param symforce: sets symforce flag -- bool
        :returns: dict
        """
        params = {}
        if force:
            params.update({'force': force})
        if force:
            params.update({'symforce': symforce})
        array_id = self.array_id if not array_id else array_id
        self.common.delete_resource(
            target_uri=f'/{self.common.UNI_VERSION}/replication/symmetrix'
            f'/{array_id}/storagegroup/'
            f'{storage_group_id}/snapshot/{snap_name}/'
            f'snapid/{snap_id}',
            params=params)

    def bulk_terminate_snapshots(
            self, storage_group_id: str, snap_name: str,
            keep_count: int | None = None, terminate_all_snapshots: bool = False,
            snapset_id_and_older: str | None = None, force: bool = False, array_id: str | None = None) -> None:
        """Terminate Multiple snapshots in a bulk operation.

        :param storage_group_id: Name of the storage group with snapshots --str
        :param snap_name: optional name of snapshot to be terminated -- str
        :param terminate_all_snapshots: Value that terminates all snapshots
                                        -- bool
        :param keep_count: Value that terminates a number of snapshots so
                           that there is only the specified number of most
                           recent snapshots retained -- int
        :param snapset_id_and_older: Value that terminates all snapshots with
                                     the snapset id or older --str
        :param force: Value that sets the force flag -- bool
        :param array_id: 12 digit array id -- int
        """
        params = {
            'terminate_all_snapshots': terminate_all_snapshots,
            'snapshot_name': snap_name
        }
        if force:
            params.update({'force': force})

        if keep_count:
            params.update({'keep_count': keep_count})

        if snapset_id_and_older:
            params.update({'snapset_id_and_older': snapset_id_and_older})

        array_id = array_id if array_id else self.array_id
        self.common.delete_resource(
            target_uri=f'/{self.common.UNI_VERSION}/replication/symmetrix/'
            f'{array_id}/storagegroup/{storage_group_id}/snapshot',
            params=params)

    def _get_array_replication_capabilities(self, array_id=None):
        """Get replication capabilities for array (internal helper).

        :param array_id: array serial number -- str
        :returns: replication capability details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication/capabilities"
            f"/symmetrix",
            resource_type=None)
        array_capabilities = dict()
        if response and response.get('symmetrixCapability'):
            for capabilities in response['symmetrixCapability']:
                if capabilities['symmetrixId'] == array_id:
                    array_capabilities = capabilities
                    break
        return array_capabilities

    def _get_replication_enabled_storage_groups(
            self, has_snapshots=None):
        """Get storage groups with replication enabled (internal helper).

        :param has_snapshots: filter by snapshot presence -- bool
        :returns: list of storage groups -- list
        """
        query_params = {'hasSnapshots': has_snapshots}
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication/symmetrix/"
            f"{self.array_id}/storagegroup",
            resource_type=None, params=query_params)
        return response.get('name', list()) if response else list()

    def _get_storage_group_replication_details(self, storage_group_id):
        """Get storage group replication details (internal helper).

        :param storage_group_id: storage group id -- str
        :returns: storage group replication details -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}",
            resource_type=None)
