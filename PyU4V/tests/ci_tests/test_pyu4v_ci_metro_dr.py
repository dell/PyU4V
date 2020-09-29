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
"""test_pyu4v_ci_metro_dr.py.py."""
import testtools
import time

from PyU4V.tests.ci_tests import base
from PyU4V.utils.exception import VolumeBackendAPIException


class CITestMetroDR(base.TestBaseTestCase, testtools.TestCase):
    """Test Replication Functions."""

    def setUp(self):
        """SetUp."""
        super(CITestMetroDR, self).setUp()
        self.replication = self.conn.replication
        self.provisioning = self.conn.provisioning
        self.metro_dr = self.conn.metro_dr

        if not self.conn.remote_array or not self.conn.remote_array_2:
            self.skipTest('There is not the required two remote arrays '
                          'configured in PyU4V.conf to run Metro DR CI tests.')
        try:
            self.conn.common.get_array(self.conn.remote_array)
            self.conn.common.get_array(self.conn.remote_array_2)
        except VolumeBackendAPIException as e:
            self.skipTest('There is an issue with the Metro DR environment '
                          'configuration: {msg}'.format(msg=e))

    def test_get_metrodr_environment_list(self):
        """Test get_metrodr_environment_list."""
        environment_list = self.metro_dr.get_metrodr_environment_list()
        self.assertIsInstance(environment_list, list)

    def test_create_metrodr_environment(self):
        """Test create_metrodr_environment.

        This test also covers all aspects of Metro DR lifecycle including
        modify, convert and delete functions. Because this is a long
        running test may take 15 minutes or more.
        """
        sg_name, environment_name = self.setup_metro_dr()
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertEqual(environment_name, metro_dr_env_details['name'])
        environment_list = self.metro_dr.get_metrodr_environment_list()
        self.assertIn(environment_name, environment_list)

    def test_delete_and_convert_metro_dr_env(self):
        """Test delete_metrodr_environment and convert_metro_dr_env.

        This test also covers all aspects of Metro DR lifecycle including
        modify, convert and delete functions. Because this is a long
        running test may take 15 minutes or more.
        """
        sg_name, environment_name = self.setup_metro_dr()
        self.metro_dr.delete_metrodr_environment(
            environment_name=environment_name)
        environment_list = self.metro_dr.get_metrodr_environment_list()
        self.assertNotIn(environment_name, environment_list)
        time.sleep(120)  # Allowing time to sync.
        job = self.metro_dr.convert_to_metrodr_environment(
            storage_group_name=sg_name, environment_name=environment_name)
        self.common.wait_for_job_complete(job=job)
        metro_dr_list = self.metro_dr.get_metrodr_environment_list()
        self.assertIn(environment_name, metro_dr_list)

    def test_suspend_establish_metro_dr(self):
        """Test suspend_metro_dr_env and establish_metro_dr.

        This test also covers all aspects of Metro DR lifecycle including
        modify, convert and delete functions. Because this is a long
        running test may take 15 minutes or more.
        """
        sg_name, environment_name = self.setup_metro_dr()
        self.metro_dr.modify_metrodr_environment(
            environment_name=environment_name, action='suspend', metro=True)
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertEqual('Suspended', metro_dr_env_details['metro_state'])
        self.metro_dr.modify_metrodr_environment(
            environment_name=environment_name, action='establish', metro=True)
        time.sleep(180)
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertIn('Active', metro_dr_env_details['metro_state'])

    def test_set_metro_dr_mode(self):
        """Test modify_metro_dr_env changing mode of DR leg.

        This test also covers all aspects of Metro DR lifecycle including
        modify, convert and delete functions. Because this is a long
        running test may take 15 minutes or more.
        """
        sg_name, environment_name = self.setup_metro_dr()
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertEqual('Adaptive Copy', metro_dr_env_details['dr_rdf_mode'])
        self.metro_dr.modify_metrodr_environment(
            environment_name=environment_name, action='setmode',
            dr_replication_mode='Asynchronous')
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertEqual('Asynchronous', metro_dr_env_details['dr_rdf_mode'])
        self.metro_dr.modify_metrodr_environment(
            environment_name=environment_name, action='setmode',
            dr_replication_mode='AdaptiveCopyDisk')
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertEqual('Adaptive Copy', metro_dr_env_details['dr_rdf_mode'])

    def test_restore_metro_dr(self):
        """Test modify_metro_dr_env for a restore operation.

        This test also covers all aspects of Metro DR lifecycle including
        modify, convert and delete functions. Because this is a long
        running test may take 15 minutes or more.
        """
        sg_name, environment_name = self.setup_metro_dr()
        self.metro_dr.modify_metrodr_environment(
            environment_name=environment_name, action='suspend', metro=True,
            dr=True)
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertEqual('Suspended', metro_dr_env_details['metro_state'])
        self.assertEqual('Suspended', metro_dr_env_details['dr_state'])
        self.metro_dr.modify_metrodr_environment(
            environment_name=environment_name, action='restore', metro=True,
            force=True)
        time.sleep(120)
        metro_dr_env_details = (
            self.metro_dr.get_metrodr_environment_details(
                environment_name=environment_name))
        self.assertEqual('ActiveActive', metro_dr_env_details['metro_state'])
        self.metro_dr.modify_metrodr_environment(
            environment_name=environment_name, action='establish',
            dr=True)
