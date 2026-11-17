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
"""replication.py.

This module provides backward-compatible access to all replication
functions.  Snapshot and SRDF functions have been moved to dedicated
modules (``PyU4V.snapshot`` and ``PyU4V.srdf``).  Calls through this
module still work but emit a deprecation warning directing users to the
new location.
"""

import logging
from typing import Any

from PyU4V.common import CommonFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.snapshot import SnapshotFunctions
from PyU4V.srdf import SRDFFunctions
from PyU4V.utils import constants
from PyU4V.utils import exception
from PyU4V.utils.decorators import refactoring_notice

LOG = logging.getLogger(__name__)

# Replication constants — kept for backward compatibility
ESTABLISH = constants.ESTABLISH
FAILBACK = constants.FAILBACK
FAILOVER = constants.FAILOVER
RESTORE = constants.RESTORE
RESUME = constants.RESUME
SETBIAS = constants.SETBIAS
SETMODE = constants.SETMODE
ENABLECONSISTENCY = constants.ENABLECONSISTENCY
DISABLECONSISTENCY = constants.DISABLECONSISTENCY
SPLIT = constants.SPLIT
SUSPEND = constants.SUSPEND
SWAP = constants.SWAP
SNAP_ID = constants.SNAP_ID

# Resource constants — kept for backward compatibility
ASYNC_UPDATE = constants.ASYNC_UPDATE
REPLICATION = constants.REPLICATION
SYMMETRIX = constants.SYMMETRIX
CAPABILITIES = constants.CAPABILITIES
STORAGEGROUP = constants.STORAGEGROUP
SNAPSHOT = constants.SNAPSHOT
GENERATION = constants.GENERATION
RDFG = constants.RDFG
VOLUME = constants.VOLUME
RDF_DIRECTOR = constants.RDF_DIRECTOR
PORT = constants.PORT
REMOTE_PORT = constants.REMOTE_PORT
RDF_GROUP = constants.RDF_GROUP

# Decorator shorthand
_snap_notice = refactoring_notice(
    'ReplicationFunctions', 'conn.snapshot.{func}',
    '10.5', 'a future version')
_srdf_notice = refactoring_notice(
    'ReplicationFunctions', 'conn.srdf.{func}',
    '10.5', 'a future version')


class ReplicationFunctions(object):
    """ReplicationFunctions."""

    def __init__(self, array_id: str, rest_client: Any) -> None:
        """__init__."""
        self.provisioning = ProvisioningFunctions(array_id, rest_client)
        self.common = CommonFunctions(rest_client)
        self._snapshot = SnapshotFunctions(array_id, rest_client)
        self._srdf = SRDFFunctions(array_id, rest_client)
        # Share the common instance so class-level mocks in tests propagate
        self._snapshot.common = self.common
        self._srdf.common = self.common
        self.array_id = array_id

    @property
    def version(self) -> str:
        """Unisphere version used for requests (single source of truth).

        Reflects the live ``common.UNI_VERSION`` rather than a value cached
        at construction time, so it stays correct after the connection
        negotiates or overrides the API version.

        :returns: Unisphere REST API version -- str
        """
        return getattr(
            self.common, 'UNI_VERSION', constants.UNISPHERE_VERSION)

    def get_replication_info(self) -> dict[str, Any]:
        """Return replication information for an array.

        :returns: replication details -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}",
            resource_type=None)

    def get_array_replication_capabilities(self, array_id: str | None = None) -> dict[str, Any]:
        """Check what replication facilities are available.

        :returns: replication capability details -- dict
        """
        array_id = array_id if array_id else self.array_id
        capabilities = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/capabilities/symmetrix",
            resource_type=None)
        symm_list = capabilities.get(
            'symmetrixCapability', list()) if capabilities else list()
        array_capabilities = dict()
        for symm in symm_list:
            if symm['symmetrixId'] == array_id:
                array_capabilities = symm
                break
        return array_capabilities

    @_snap_notice
    def is_snapvx_licensed(self) -> bool:
        """Check if the snapVx feature is licensed and enabled.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.is_snapvx_licensed`

        :returns: bool
        """
        return self._snapshot.is_snapvx_licensed()

    def get_storage_group_replication_details(
            self, storage_group_id: str, return_remote_sg_info: bool = False,
            exclude_sl_snaps: bool = False, exclude_manual_snaps: bool = False) -> dict[str, Any]:
        """Given a storage group id, return storage group srdf info and
        snapshot information.

        :param storage_group_id: storage group id -- str
        :param return_remote_sg_info: returns additional information for keys
               remote_storage_groups -- bool
        :param exclude_sl_snaps: excludes details of any service level snaps
               from the return -- bool
        :param exclude_manual_snaps: excludes details of any manual snaps from
               the return -- bool
        :returns: storage group replication details -- dict
        """
        filters = {
            'include_remote_sgs': return_remote_sg_info,
            'exclude_sl_snaps': exclude_sl_snaps,
            'exclude_manual_snaps': exclude_manual_snaps
        }

        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}",
            resource_type=None, params=filters)

    def get_replication_enabled_storage_groups(
            self, array_id: str | None = None, has_srdf: bool | None = None, has_snapshots: bool | None = None,
            has_cloud_snapshots: bool | None = None, is_link_target: bool | None = None,
            has_snap_policies: bool | None = None, has_clones: bool | None = None) -> list[str]:
        """Return list of storage groups with replication.

        :param has_snapshots: return only storage groups with snapshots
        :param has_srdf: return only storage groups with SRDF
        :param has_cloud_snapshots: Value that filters returned list to display
                                  Storage Groups that have Cloud Snapshots
                                  -- bool
        :param is_link_target: Value that filters returned list to display
                               Storage Groups that are Link Targets -- bool
        :param has_snap_policies: Value that filters returned list to display
                                  Storage Groups that have Snapshot Policies
                                  -- bool
        :param has_clones: Value that filters returned list to display Storage
                           Groups that have Clones -- bool
        :returns: list of storage groups with associated replication
        """
        array_id = array_id if array_id else self.array_id
        query_params = {'hasSrdf': has_srdf, 'hasSnapshots': has_snapshots,
                        'hasCloudSnapshots': has_cloud_snapshots,
                        'is_link_target': is_link_target,
                        'has_snap_policies': has_snap_policies,
                        'has_clones': has_clones}
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication/symmetrix/"
            f"{array_id}/storagegroup",
            resource_type=None, params=query_params)
        storage_group_list = (
            response.get('name', list()) if response else list())
        return storage_group_list

    @_snap_notice
    def get_storage_group_snapshot_list(self, storage_group_id: str) -> list[str]:
        """Get a list of snapshots associated with a storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.get_storage_group_snapshot_list`
        """
        return self._snapshot.get_storage_group_snapshot_list(
            storage_group_id)

    @_snap_notice
    def create_storage_group_snapshot(
            self, storage_group_id: str, snap_name: str, ttl: int | None = None, hours: bool = False,
            secure: bool = False, bothsides: bool = False) -> dict[str, Any]:
        """Create a snapVx snapshot of a storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.create_storage_group_snapshot`
        """
        return self._snapshot.create_storage_group_snapshot(
            storage_group_id, snap_name, ttl=ttl, hours=hours,
            secure=secure, bothsides=bothsides)

    @_snap_notice
    def get_storage_group_snapshot_generation_list(
            self, storage_group_id: str, snap_name: str) -> dict[str, Any]:
        """Get a snapshot and its generation count information for an sg.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.get_storage_group_snapshot_generation_list`
        """
        return self._snapshot.get_storage_group_snapshot_generation_list(
            storage_group_id, snap_name)

    @_snap_notice
    def get_storage_group_snapshot_snap_id_list(
            self, storage_group_id: str, snap_name: str) -> dict[str, Any]:
        """Get a snapshot and its snap id information for an sg.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.get_storage_group_snapshot_snap_id_list`
        """
        return self._snapshot.get_storage_group_snapshot_snap_id_list(
            storage_group_id, snap_name)

    @_snap_notice
    def get_snapshot_generation_details(self, sg_id: str, snap_name: str, gen_num: int) -> dict[str, Any]:
        """Get the details for a particular snapshot generation.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.get_snapshot_generation_details`
        """
        return self._snapshot.get_snapshot_generation_details(
            sg_id, snap_name, gen_num)

    @_snap_notice
    def get_snapshot_snap_id_details(self, sg_id: str, snap_name: str, snap_id: int) -> dict[str, Any]:
        """Get the details for a particular snapshot snap_id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.get_snapshot_snap_id_details`
        """
        return self._snapshot.get_snapshot_snap_id_details(
            sg_id, snap_name, snap_id)

    @_snap_notice
    def find_expired_snapvx_snapshots(self) -> list[dict[str, Any]]:
        """Find all expired snapvx snapshots.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.find_expired_snapvx_snapshots`
        """
        return self._snapshot.find_expired_snapvx_snapshots()

    @_snap_notice
    def find_expired_snapvx_snapshots_by_snap_ids(self) -> list[dict[str, Any]]:
        """Find all expired snapvx snapshots using snap id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.find_expired_snapvx_snapshots_by_snap_ids`
        """
        return self._snapshot.find_expired_snapvx_snapshots_by_snap_ids()

    @_snap_notice
    def modify_storage_group_snapshot(
            self, src_storage_grp_id: str, tgt_storage_grp_id: str, snap_name: str,
            link: bool = False, unlink: bool = False, restore: bool = False, new_name: str | None = None,
            gen_num: int = 0, _async: bool = False, relink: bool = False) -> dict[str, Any]:
        """Modify a storage group snapshot.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.modify_storage_group_snapshot`
        """
        return self._snapshot.modify_storage_group_snapshot(
            src_storage_grp_id, tgt_storage_grp_id, snap_name,
            link=link, unlink=unlink, restore=restore, new_name=new_name,
            gen_num=gen_num, _async=_async, relink=relink)

    @_snap_notice
    def modify_storage_group_snapshot_by_snap_id(
            self, src_storage_grp_id: str, tgt_storage_grp_id: str, snap_name: str,
            snap_id: int, link: bool = False, unlink: bool = False, restore: bool = False, new_name: str | None = None,
            _async: bool = False, relink: bool = False, remote: bool = False, force: bool = False) -> dict[str, Any]:
        """Modify a storage group snapshot using it's snap id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.modify_storage_group_snapshot_by_snap_id`
        """
        return self._snapshot.modify_storage_group_snapshot_by_snap_id(
            src_storage_grp_id, tgt_storage_grp_id, snap_name, snap_id,
            link=link, unlink=unlink, restore=restore, new_name=new_name,
            _async=_async, relink=relink, remote=remote, force=force)

    @_snap_notice
    def restore_snapshot(self, sg_id: str, snap_name: str, gen_num: int = 0) -> dict[str, Any]:
        """Restore a storage group to its snapshot.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.restore_snapshot`
        """
        return self._snapshot.restore_snapshot(sg_id, snap_name, gen_num)

    @_snap_notice
    def restore_snapshot_by_snap_id(self, sg_id: str, snap_name: str, snap_id: int) -> dict[str, Any]:
        """Restore a storage group to its snapshot using it's snap id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.restore_snapshot_by_snap_id`
        """
        return self._snapshot.restore_snapshot_by_snap_id(
            sg_id, snap_name, snap_id)

    @_snap_notice
    def rename_snapshot(self, sg_id: str, snap_name: str, new_name: str, gen_num: int = 0) -> dict[str, Any]:
        """Rename an existing storage group snapshot.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.rename_snapshot`
        """
        return self._snapshot.rename_snapshot(
            sg_id, snap_name, new_name, gen_num)

    @_snap_notice
    def rename_snapshot_by_snap_id(self, sg_id: str, snap_name: str, new_name: str, snap_id: int) -> dict[str, Any]:
        """Rename an existing storage group snapshot using it's snap id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.rename_snapshot_by_snap_id`
        """
        return self._snapshot.rename_snapshot_by_snap_id(
            sg_id, snap_name, new_name, snap_id)

    @_snap_notice
    def link_gen_snapshot(self, sg_id: str, snap_name: str, link_sg_name: str,
                          _async: bool = False, gen_num: int = 0) -> dict[str, Any]:
        """Link a snapshot to another storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.link_gen_snapshot`
        """
        return self._snapshot.link_gen_snapshot(
            sg_id, snap_name, link_sg_name, _async=_async, gen_num=gen_num)

    @_snap_notice
    def link_snapshot_by_snap_id(
            self, sg_id: str, link_sg_name: str, snap_name: str, snap_id: int, _async: bool = False) -> dict[str, Any]:
        """Link a snapshot to another storage group using it's snap id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.link_snapshot_by_snap_id`
        """
        return self._snapshot.link_snapshot_by_snap_id(
            sg_id, link_sg_name, snap_name, snap_id, _async=_async)

    @_snap_notice
    def unlink_gen_snapshot(self, sg_id: str, snap_name: str, unlink_sg_name: str,
                            _async: bool = False, gen_num: int = 0) -> dict[str, Any]:
        """Unlink a snapshot from another storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.unlink_gen_snapshot`
        """
        return self._snapshot.unlink_gen_snapshot(
            sg_id, snap_name, unlink_sg_name, _async=_async, gen_num=gen_num)

    @_snap_notice
    def unlink_snapshot_by_snap_id(
            self, sg_id: str, unlink_sg_name: str, snap_name: str, snap_id: int, _async: bool = False) -> dict[str, Any]:
        """Unlink a snapshot from another storage group using it's snap id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.unlink_snapshot_by_snap_id`
        """
        return self._snapshot.unlink_snapshot_by_snap_id(
            sg_id, unlink_sg_name, snap_name, snap_id, _async=_async)

    @_snap_notice
    def delete_storage_group_snapshot(self, storage_group_id: str, snap_name: str,
                                      gen: int = 0) -> dict[str, Any]:
        """Delete the snapshot of a storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.delete_storage_group_snapshot`
        """
        return self._snapshot.delete_storage_group_snapshot(
            storage_group_id, snap_name, gen)

    @_snap_notice
    def delete_storage_group_snapshot_by_snap_id(
            self, storage_group_id: str, snap_name: str, snap_id: int, force: bool = False,
            array_id: str | None = None, symforce: bool = False) -> dict[str, Any]:
        """Delete the snapshot of a storage group using the snap id.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.delete_storage_group_snapshot_by_snap_id`
        """
        return self._snapshot.delete_storage_group_snapshot_by_snap_id(
            storage_group_id, snap_name, snap_id, force=force,
            array_id=array_id, symforce=symforce)

    @_snap_notice
    def bulk_terminate_snapshots(
            self, storage_group_id: str, snap_name: str,
            keep_count: int | None = None, terminate_all_snapshots: bool = False,
            snapset_id_and_older: int | None = None, force: bool = False, array_id: str | None = None) -> dict[str, Any]:
        """Terminate Multiple snapshots in a bulk operation.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.snapshot.SnapshotFunctions.bulk_terminate_snapshots`
        """
        return self._snapshot.bulk_terminate_snapshots(
            storage_group_id, snap_name, keep_count=keep_count,
            terminate_all_snapshots=terminate_all_snapshots,
            snapset_id_and_older=snapset_id_and_older,
            force=force, array_id=array_id)

    def is_volume_in_replication_session(self, device_id: str) -> tuple[bool, bool, int | None]:
        """Check if a volume is in a replication session.

        NOTE: There may be a time delay between the snapshot creation
        and the object model update.  See the following test for usage:
        tests.ci_tests.test_pyu4v_ci_replication.CITestReplication.
        test_is_volume_in_replication_session

        :param device_id: device id -- str
        :returns: snap vx target, snap vx source, rdf group -- bool, bool, list
        """
        snapvx_src, snapvx_tgt, rdf_grp = False, False, None
        volume_details = self.provisioning.get_volume(device_id)
        if volume_details:
            LOG.debug('Vol details: {vol}'.format(vol=volume_details))
            if volume_details.get('snapvx_target'):
                snapvx_tgt = volume_details['snapvx_target']
            if volume_details.get('snapvx_source'):
                snapvx_src = volume_details['snapvx_source']
            if volume_details.get('rdfGroupId'):
                rdf_grp = volume_details['rdfGroupId']
        return snapvx_tgt, snapvx_src, rdf_grp

    @_srdf_notice
    def get_rdf_group(self, rdf_number: int, array_id: str | None = None) -> dict[str, Any]:
        """Get specific rdf group details.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_group`
        """
        return self._srdf.get_rdf_group(rdf_number, array_id=array_id)

    @_srdf_notice
    def get_rdf_group_list(self, array_id: str | None = None, remote_symmetrix_id: str | None = None,
                           rdf_mode: str | None = None, volume_count: int | None = None, group_type: str | None = None) -> list[dict[str, Any]]:
        """Get rdf group list from array.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_group_list`
        """
        return self._srdf.get_rdf_group_list(
            array_id=array_id, remote_symmetrix_id=remote_symmetrix_id,
            rdf_mode=rdf_mode, volume_count=volume_count,
            group_type=group_type)

    @_srdf_notice
    def get_rdf_group_volume(self, rdf_number: int, device_id: str) -> dict[str, Any]:
        """Get specific volume details, from an RDF group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_group_volume`
        """
        return self._srdf.get_rdf_group_volume(rdf_number, device_id)

    @_srdf_notice
    def get_rdf_group_volume_list(self, rdf_number: int) -> list[str]:
        """Get specific volume details, from an RDF group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_group_volume_list`
        """
        return self._srdf.get_rdf_group_volume_list(rdf_number)

    @_srdf_notice
    def are_volumes_rdf_paired(self, remote_array: str, device_id: str,
                               target_device: str, rdf_group: int) -> bool:
        """Check if a pair of volumes are RDF paired.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.are_volumes_rdf_paired`
        """
        return self._srdf.are_volumes_rdf_paired(
            remote_array, device_id, target_device, rdf_group)

    @_srdf_notice
    def get_rdf_group_number(self, rdf_group_label: str) -> int:
        """Given a group label, return the associated group number.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_group_number`
        """
        return self._srdf.get_rdf_group_number(rdf_group_label)

    @_srdf_notice
    def get_storage_group_srdf_group_list(self, storage_group_id: str,
                                          array_id: str | None = None) -> list[int]:
        """Get the rdf group numbers for a storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_storage_group_srdf_group_list`
        """
        return self._srdf.get_storage_group_srdf_group_list(
            storage_group_id, array_id=array_id)

    @_srdf_notice
    def get_storage_group_srdf_details(self, storage_group_id: str, rdfg_num: int) -> dict[str, Any]:
        """Get the details for an rdf group on a particular storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_storage_group_srdf_details`
        """
        return self._srdf.get_storage_group_srdf_details(
            storage_group_id, rdfg_num)

    @_srdf_notice
    def create_storage_group_srdf_pairings(
            self, storage_group_id: str, remote_sid: str, srdf_mode: str, establish: bool | None = None,
            _async: bool = False, rdfg_number: int | None = None, force_new_rdf_group: bool = False,
            remote_storage_group_id: str | None = None) -> dict[str, Any]:
        """SRDF protect a storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.create_storage_group_srdf_pairings`
        """
        return self._srdf.create_storage_group_srdf_pairings(
            storage_group_id, remote_sid, srdf_mode, establish=establish,
            _async=_async, rdfg_number=rdfg_number,
            force_new_rdf_group=force_new_rdf_group,
            remote_storage_group_id=remote_storage_group_id)

    @_srdf_notice
    def modify_storage_group_srdf(
            self, storage_group_id: str, action: str, srdf_group_number: int, options: dict[str, Any] | None = None,
            _async: bool = False) -> dict[str, Any]:
        """Modify the state of a rdf group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.modify_storage_group_srdf`
        """
        return self._srdf.modify_storage_group_srdf(
            storage_group_id, action, srdf_group_number,
            options=options, _async=_async)

    @_srdf_notice
    def suspend_storage_group_srdf(self, storage_group_id: str, srdf_group_number: int,
                                   suspend_options: dict[str, Any] | None = None, _async: bool = False) -> dict[str, Any]:
        """Suspend IO on the links for the given storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.suspend_storage_group_srdf`
        """
        return self._srdf.suspend_storage_group_srdf(
            storage_group_id, srdf_group_number,
            suspend_options=suspend_options, _async=_async)

    @_srdf_notice
    def establish_storage_group_srdf(
            self, storage_group_id: str, srdf_group_number: int,
            establish_options: dict[str, Any] | None = None, _async: bool = False) -> dict[str, Any]:
        """Establish io on the links for the given storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.establish_storage_group_srdf`
        """
        return self._srdf.establish_storage_group_srdf(
            storage_group_id, srdf_group_number,
            establish_options=establish_options, _async=_async)

    @_srdf_notice
    def failover_storage_group_srdf(
            self, storage_group_id: str, srdf_group_number: int,
            failover_options: dict[str, Any] | None = None, _async: bool = False) -> dict[str, Any]:
        """Failover a given storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.failover_storage_group_srdf`
        """
        return self._srdf.failover_storage_group_srdf(
            storage_group_id, srdf_group_number,
            failover_options=failover_options, _async=_async)

    @_srdf_notice
    def failback_storage_group_srdf(
            self, storage_group_id: str, srdf_group_number: int, failback_options: dict[str, Any] | None = None,
            _async: bool = False) -> dict[str, Any]:
        """Failback a given storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.failback_storage_group_srdf`
        """
        return self._srdf.failback_storage_group_srdf(
            storage_group_id, srdf_group_number,
            failback_options=failback_options, _async=_async)

    @_srdf_notice
    def delete_storage_group_srdf(
            self, storage_group_id: str, srdf_group_number: int, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Delete srdf pairings for a given storage group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.delete_storage_group_srdf`
        """
        return self._srdf.delete_storage_group_srdf(
            storage_group_id, srdf_group_number, filters=filters)

    @_srdf_notice
    def get_rdf_director_list(self, array_id: str | None = None, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Finds out directors configured for SRDF on the specified array.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_director_list`
        """
        return self._srdf.get_rdf_director_list(
            array_id=array_id, filters=filters)

    @_srdf_notice
    def get_rdf_director_detail(self, director_id: str, array_id: str | None = None) -> dict[str, Any]:
        """Retrieves details for specified RDF_director.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_director_detail`
        """
        return self._srdf.get_rdf_director_detail(
            director_id, array_id=array_id)

    @_srdf_notice
    def get_rdf_director_port_list(self, director_id: str, array_id: str | None = None,
                                   filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Retrieves list of ports available on RDF_director.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_director_port_list`
        """
        return self._srdf.get_rdf_director_port_list(
            director_id, array_id=array_id, filters=filters)

    @_srdf_notice
    def get_rdf_director_port_details(self, director_id: str, port_id: str,
                                      array_id: str | None = None) -> dict[str, Any]:
        """Retrieves details of specified RDF ports.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_director_port_details`
        """
        return self._srdf.get_rdf_director_port_details(
            director_id, port_id, array_id=array_id)

    @_srdf_notice
    def get_rdf_port_remote_connections(self, director_id: str, port_id: str,
                                        array_id: str | None = None) -> dict[str, Any]:
        """Performs a scan of the RDF environment via specified port.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.get_rdf_port_remote_connections`
        """
        return self._srdf.get_rdf_port_remote_connections(
            director_id, port_id, array_id=array_id)

    @_srdf_notice
    def create_rdf_group(self, local_director_port_list: list[dict[str, Any]], remote_array_id: str,
                         label: str, local_rdfg_number: int, remote_rdfg_number: int,
                         remote_director_port_list: list[dict[str, Any]], array_id: str | None = None) -> dict[str, Any]:
        """Create a new RDF group between directors and ports on two PowerMax.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.create_rdf_group`
        """
        return self._srdf.create_rdf_group(
            local_director_port_list, remote_array_id, label,
            local_rdfg_number, remote_rdfg_number,
            remote_director_port_list, array_id=array_id)

    @_srdf_notice
    def modify_rdf_group(self, action: str, srdf_group_number: int, array_id: str | None = None,
                         port_list: list[dict[str, Any]] | None = None, label: str | None = None, dev_list: list[str] | None = None,
                         target_rdf_group: int | None = None, consistency_exempt: bool | None = None,
                         keepR1: bool | None = None, keepR2: bool | None = None) -> dict[str, Any]:
        """Function to Modify Ports, devices or change label of RDF group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.modify_rdf_group`
        """
        return self._srdf.modify_rdf_group(
            action, srdf_group_number, array_id=array_id,
            port_list=port_list, label=label, dev_list=dev_list,
            target_rdf_group=target_rdf_group,
            consistency_exempt=consistency_exempt,
            keepR1=keepR1, keepR2=keepR2)

    @_srdf_notice
    def delete_rdf_group(self, srdf_group_number: int, array_id: str | None = None) -> dict[str, Any]:
        """Function to Delete SRDF groups between VMAX or PowerMax arrays.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.delete_rdf_group`
        """
        return self._srdf.delete_rdf_group(
            srdf_group_number, array_id=array_id)

    @_srdf_notice
    def create_storage_group_from_rdfg(
            self, storage_group_name: str, srdf_group_number: int, array_id: str | None = None,
            rdf_type: str | None = None, remote_storage_group_name: str | None = None) -> dict[str, Any]:
        """Creates management storage group from all devices in SRDF group.

        .. deprecated:: 10.5
            Use :py:meth:`~PyU4V.srdf.SRDFFunctions.create_storage_group_from_rdfg`
        """
        return self._srdf.create_storage_group_from_rdfg(
            storage_group_name, srdf_group_number, array_id=array_id,
            rdf_type=rdf_type,
            remote_storage_group_name=remote_storage_group_name)
