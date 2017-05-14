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

from mock import patch, MagicMock
import unittest

from cloudify.state import current_ctx

from botocore.exceptions import UnknownServiceError

from cloudify_boto3.common.tests.test_base import CLIENT_CONFIG
from cloudify_boto3.kms.tests.test_kms import TestKMS

from cloudify_boto3.kms.resources import alias


# Constants
ALIAS_TH = ['cloudify.nodes.Root',
            'cloudify.nodes.aws.kms.Alias']

NODE_PROPERTIES = {
    'use_external_resource': False,
    'resource_config': {
        "kwargs": {
            "AliasName": "alias/test_key"
        }
    },
    'client_config': CLIENT_CONFIG
}

RUNTIME_PROPERTIES = {
    'aws_resource_id': 'aws_resource',
    'resource_config': {}
}


class TestKMSAlias(TestKMS):

    def test_prepare(self):
        _ctx = self.get_mock_ctx(
            'test_prepare',
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES,
            type_hierarchy=ALIAS_TH
        )

        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('kms')

        with patch('boto3.client', fake_boto):
            alias.prepare(ctx=_ctx, resource_config=None, iface=None)
            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'aws_resource_id': 'aws_resource',
                    'resource_config': {
                        "AliasName": "alias/test_key"
                    }
                }
            )

    def test_create_raises_UnknownServiceError(self):
        _ctx, fake_boto, fake_client = self._prepare_context(ALIAS_TH,
                                                             NODE_PROPERTIES)

        with patch('boto3.client', fake_boto):
            with self.assertRaises(UnknownServiceError) as error:
                alias.create(ctx=_ctx, resource_config=None, iface=None)

            self.assertEqual(
                str(error.exception),
                "Unknown service: 'kms'. Valid service names are: ['rds']"
            )

            fake_boto.assert_called_with('kms', **CLIENT_CONFIG)

    def test_create(self):
        _ctx, fake_boto, fake_client = self._prepare_context(ALIAS_TH,
                                                             NODE_PROPERTIES)

        with patch('boto3.client', fake_boto):
            fake_client.create_alias = MagicMock(return_value={})

            alias.create(ctx=_ctx, resource_config=None, iface=None)

            fake_boto.assert_called_with('kms', **CLIENT_CONFIG)

            fake_client.create_alias.assert_called_with(
                AliasName='alias/test_key', TargetKeyId='a'
            )

            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'aws_resource_id': 'aws_resource', 'resource_config': {}
                }
            )

    def test_delete(self):
        _ctx, fake_boto, fake_client = self._prepare_context(ALIAS_TH,
                                                             NODE_PROPERTIES)

        with patch('boto3.client', fake_boto):
            fake_client.delete_alias = MagicMock(return_value={})

            alias.delete(ctx=_ctx, resource_config=None, iface=None)

            fake_boto.assert_called_with('kms', **CLIENT_CONFIG)

            fake_client.delete_alias.assert_called_with(
                AliasName='alias/test_key'
            )

            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'aws_resource_id': 'aws_resource', 'resource_config': {}
                }
            )

    def test_delete_without_alias(self):
        _ctx, fake_boto, fake_client = self._prepare_context(ALIAS_TH, {
            'use_external_resource': False,
            'resource_config': {},
            'client_config': CLIENT_CONFIG
        })

        with patch('boto3.client', fake_boto):
            fake_client.delete_alias = MagicMock(return_value={})

            alias.delete(ctx=_ctx, resource_config=None, iface=None)

            fake_boto.assert_called_with('kms', **CLIENT_CONFIG)

            fake_client.delete_alias.assert_called_with(
                AliasName='aws_resource'
            )

            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'aws_resource_id': 'aws_resource', 'resource_config': {}
                }
            )

    def test_KMSKeyAlias_status(self):
        fake_boto, fake_client = self.fake_boto_client('sqs')

        test_instance = alias.KMSKeyAlias("ctx_node", resource_id='queue_id',
                                          client=fake_client, logger=None)

        self.assertEqual(test_instance.status, None)

    def test_KMSKeyAlias_properties(self):
        fake_boto, fake_client = self.fake_boto_client('sqs')

        test_instance = alias.KMSKeyAlias("ctx_node", resource_id='queue_id',
                                          client=fake_client, logger=None)

        self.assertEqual(test_instance.properties, None)

    def test_KMSKeyAlias_enable(self):
        fake_boto, fake_client = self.fake_boto_client('sqs')

        test_instance = alias.KMSKeyAlias("ctx_node", resource_id='queue_id',
                                          client=fake_client, logger=None)

        self.assertEqual(test_instance.enable(None), None)

    def test_KMSKeyAlias_disable(self):
        fake_boto, fake_client = self.fake_boto_client('sqs')

        test_instance = alias.KMSKeyAlias("ctx_node", resource_id='queue_id',
                                          client=fake_client, logger=None)

        self.assertEqual(test_instance.disable(None), None)


if __name__ == '__main__':
    unittest.main()
