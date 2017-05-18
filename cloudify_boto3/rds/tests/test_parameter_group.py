# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from cloudify_boto3.rds.resources import parameter_group
from cloudify.exceptions import OperationRetry
from botocore.exceptions import UnknownServiceError

from mock import patch, MagicMock
import unittest

from cloudify.state import current_ctx

from cloudify_boto3.common.tests.test_base import TestBase

# Constants
PARAMETER_GROUP_TH = ['cloudify.nodes.Root',
                      'cloudify.nodes.aws.rds.ParameterGroup']

NODE_PROPERTIES = {
    'resource_id': 'dev-db-param-group',
    'use_external_resource': False,
    'resource_config': {
        'kwargs': {
            'DBParameterGroupFamily': 'mysql5.7',
            'Description': 'MySQL5.7 Parameter Group for Dev'
        }
    }
}

RUNTIME_PROPERTIES_AFTER_CREATE = {
    'aws_resource_arn': 'DBParameterGroupArn',
    'aws_resource_id': 'dev-db-param-group',
    'resource_config': {}
}


class TestRDSParameterGroup(TestBase):

    def test_create_raises_UnknownServiceError(self):
        _test_name = 'test_create_UnknownServiceError'
        _test_node_properties = {
            'use_external_resource': False
        }
        _test_runtime_properties = {
            'resource_config': {}
        }
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=_test_node_properties,
            test_runtime_properties=_test_runtime_properties,
            type_hierarchy=PARAMETER_GROUP_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            with self.assertRaises(UnknownServiceError) as error:
                parameter_group.create(
                    ctx=_ctx, resource_config=None, iface=None
                )

            self.assertEqual(
                str(error.exception),
                "Unknown service: 'rds'. Valid service names are: ['rds']"
            )

            fake_boto.assert_called_with('rds', region_name=None)

    def test_configure_empty(self):
        _test_name = 'test_configure'
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES_AFTER_CREATE,
            type_hierarchy=PARAMETER_GROUP_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            parameter_group.configure(
                ctx=_ctx, resource_config=None, iface=None
            )

            self.assertEqual(
                _ctx.instance.runtime_properties,
                RUNTIME_PROPERTIES_AFTER_CREATE
            )

    def test_configure(self):
        _test_name = 'test_configure'
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES_AFTER_CREATE,
            type_hierarchy=PARAMETER_GROUP_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            fake_client.modify_db_parameter_group = MagicMock(
                return_value={'DBParameterGroupName': 'abc'}
            )
            parameter_group.configure(
                ctx=_ctx, resource_config={
                    "Parameters": [
                        {
                            "ParameterName": "time_zone",
                            "ParameterValue": "US/Eastern",
                            "ApplyMethod": "immediate"
                        }, {
                            "ParameterName": "lc_time_names",
                            "ParameterValue": "en_US",
                            "ApplyMethod": "immediate"
                        }
                    ]
                }, iface=None
            )

            fake_client.modify_db_parameter_group.assert_called_with(
                DBParameterGroupName='dev-db-param-group',
                Parameters=[{
                    'ParameterName': 'time_zone',
                    'ParameterValue': 'US/Eastern',
                    'ApplyMethod': 'immediate'
                }, {
                    'ParameterName': 'lc_time_names',
                    'ParameterValue': 'en_US',
                    'ApplyMethod': 'immediate'
                }]
            )

            self.assertEqual(
                _ctx.instance.runtime_properties,
                RUNTIME_PROPERTIES_AFTER_CREATE
            )

    def test_create(self):
        _test_name = 'test_create_UnknownServiceError'
        _test_runtime_properties = {
            'resource_config': {}
        }
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=_test_runtime_properties,
            type_hierarchy=PARAMETER_GROUP_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            fake_client.create_db_parameter_group = MagicMock(
                return_value={
                    'DBParameterGroup': {
                        'DBParameterGroupName': 'dev-db-param-group',
                        'DBParameterGroupArn': 'DBParameterGroupArn'
                    }
                }
            )
            parameter_group.create(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.create_db_parameter_group.assert_called_with(
                DBParameterGroupFamily='mysql5.7',
                DBParameterGroupName='dev-db-param-group',
                Description='MySQL5.7 Parameter Group for Dev'
            )

            self.assertEqual(
                _ctx.instance.runtime_properties,
                RUNTIME_PROPERTIES_AFTER_CREATE
            )

    def test_delete(self):
        _test_name = 'test_delete'
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES_AFTER_CREATE,
            type_hierarchy=PARAMETER_GROUP_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            fake_client.delete_db_parameter_group = MagicMock(
                return_value={}
            )
            parameter_group.delete(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.delete_db_parameter_group.assert_called_with(
                DBParameterGroupName='dev-db-param-group'
            )

            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'aws_resource_arn': 'DBParameterGroupArn',
                    '__deleted': True,
                    'aws_resource_id': 'dev-db-param-group',
                    'resource_config': {}
                }
            )

    def test_immortal_delete(self):
        _test_name = 'test_immortal_delete'
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES_AFTER_CREATE,
            type_hierarchy=PARAMETER_GROUP_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            fake_client.delete_db_parameter_group = MagicMock(
                return_value={}
            )
            fake_client.describe_db_parameter_groups = MagicMock(
                return_value={
                    'DBParameterGroups': [{
                        'DBParameterGroupName': 'dev-db-param-group',
                        'DBParameterGroupArn': 'DBParameterGroupArn'
                    }]
                }
            )
            with self.assertRaises(OperationRetry) as error:
                parameter_group.delete(
                    ctx=_ctx, resource_config=None, iface=None
                )

            self.assertEqual(
                str(error.exception),
                (
                    'RDS Parameter Group ID# "dev-db-param-group"' +
                    ' is still in a pending state.'
                )
            )

    def _create_parameter_relationships(self, node_id):
        _source_ctx = self.get_mock_ctx(
            'test_attach_source',
            test_properties={},
            test_runtime_properties={
                'resource_id': 'prepare_attach_source',
                'aws_resource_id': 'aws_resource_mock_id',
                '_set_changed': True
            },
            type_hierarchy=PARAMETER_GROUP_TH
        )

        _target_ctx = self.get_mock_ctx(
            'test_attach_target',
            test_properties={},
            test_runtime_properties={
                'resource_id': 'prepare_attach_target',
                'aws_resource_id': 'aws_target_mock_id',
            },
            type_hierarchy=['cloudify.nodes.Root',
                            'cloudify.nodes.aws.rds.Parameter']
        )

        _ctx = self.get_mock_relationship_ctx(
            node_id,
            test_properties={},
            test_runtime_properties={},
            test_source=_source_ctx,
            test_target=_target_ctx,
            type_hierarchy=['cloudify.nodes.Root']
        )

        return _source_ctx, _target_ctx, _ctx

    def test_attach_to(self):
        _source_ctx, _target_ctx, _ctx = self._create_parameter_relationships(
            'test_attach_to'
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')

        with patch('boto3.client', fake_boto):
            fake_client.modify_db_parameter_group = MagicMock(
                return_value={
                    'DBParameterGroupName': 'abc'
                }
            )
            parameter_group.attach_to(
                ctx=_ctx, resource_config=None, iface=None
            )
            self.assertEqual(_target_ctx.instance.runtime_properties, {
                'aws_resource_id': 'aws_target_mock_id',
                'resource_id': 'prepare_attach_target'
            })
            fake_client.modify_db_parameter_group.assert_called_with(
                DBParameterGroupName='aws_resource_mock_id',
                Parameters=[{'ParameterName': 'aws_target_mock_id'}]
            )

    def test_detach_from(self):
        _source_ctx, _target_ctx, _ctx = self._create_parameter_relationships(
            'test_detach_from'
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')

        with patch('boto3.client', fake_boto):
            parameter_group.detach_from(
                ctx=_ctx, resource_config=None, iface=None
            )
            self.assertEqual(_target_ctx.instance.runtime_properties, {
                'aws_resource_id': 'aws_target_mock_id',
                'resource_id': 'prepare_attach_target'
            })


if __name__ == '__main__':
    unittest.main()