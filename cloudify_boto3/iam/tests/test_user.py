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
from cloudify_boto3.common.tests.test_base import TestBase, CLIENT_CONFIG
from cloudify_boto3.common.tests.test_base import DELETE_RESPONSE
from cloudify_boto3.iam.resources import user


# Constants
USER_TH = ['cloudify.nodes.Root',
           'cloudify.nodes.aws.iam.User']

NODE_PROPERTIES = {
    'resource_id': 'CloudifyUser',
    'use_external_resource': False,
    'resource_config': {
        'kwargs': {
            "Path": "user_path"
        }
    },
    'client_config': CLIENT_CONFIG
}

RUNTIME_PROPERTIES = {
    'aws_resource_id': 'aws_resource',
    'resource_config': {}
}

RUNTIME_PROPERTIES_AFTER_CREATE = {
    'aws_resource_arn': 'arn_id',
    'aws_resource_id': 'user_name_id',
    'resource_config': {}
}


class TestIAMUser(TestBase):

    def test_create_raises_UnknownServiceError(self):
        self._prepare_create_raises_UnknownServiceError(
            type_hierarchy=USER_TH,
            type_name='iam',
            type_class=user
        )

    def test_create(self):
        _ctx = self.get_mock_ctx(
            'test_create',
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES,
            type_hierarchy=USER_TH
        )

        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.create_user = MagicMock(return_value={
                'User': {
                    'UserName': 'user_name_id',
                    'Arn': 'arn_id'
                }
            })

            user.create(ctx=_ctx, resource_config=None, iface=None)

            fake_boto.assert_called_with('iam', **CLIENT_CONFIG)

            fake_client.create_user.assert_called_with(Path='user_path',
                                                       UserName='aws_resource')

            self.assertEqual(
                _ctx.instance.runtime_properties,
                RUNTIME_PROPERTIES_AFTER_CREATE
            )

    def test_delete(self):
        _ctx = self.get_mock_ctx(
            'test_delete',
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES_AFTER_CREATE,
            type_hierarchy=USER_TH
        )

        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.delete_user = MagicMock(
                return_value=DELETE_RESPONSE
            )

            user.delete(ctx=_ctx, resource_config=None, iface=None)

            fake_boto.assert_called_with('iam', **CLIENT_CONFIG)

            fake_client.delete_user.assert_called_with(UserName='user_name_id')

            self.assertEqual(
                _ctx.instance.runtime_properties,
                {
                    'aws_resource_id': 'user_name_id',
                    '__deleted': True,
                    'resource_config': {},
                    'aws_resource_arn': 'arn_id'
                }
            )

    def test_attach_to_Group(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_attach_to',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.Group']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.add_user_to_group = MagicMock(return_value={})

            user.attach_to(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.add_user_to_group.assert_called_with(
                GroupName='aws_target_mock_id',
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_attach_to_AccessKey(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_attach_to',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.AccessKey']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.create_access_key = MagicMock(return_value={
                'AccessKey': {
                    'AccessKeyId': 'aws_access_key_id',
                    'SecretAccessKey': 'aws_secret_access_key'
                }
            })

            user.attach_to(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.create_access_key.assert_called_with(
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

            self.assertEqual(
                _target_ctx.instance.runtime_properties, {
                    'SecretAccessKey': 'aws_secret_access_key',
                    'aws_resource_arn': 'aws_resource_mock_arn',
                    'aws_resource_id': 'aws_access_key_id',
                    'resource_id': 'prepare_attach_target'
                }
            )

    def test_attach_to_Policy(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_attach_to',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.Policy']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.attach_user_policy = MagicMock(return_value={})

            user.attach_to(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.attach_user_policy.assert_called_with(
                PolicyArn='aws_resource_mock_arn',
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_attach_to_LoginProfile_Create(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_attach_to',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.LoginProfile']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.create_login_profile = MagicMock(return_value={})

            user.attach_to(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.create_login_profile.assert_called_with(
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_attach_to_LoginProfile_Update(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_attach_to',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.LoginProfile']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.get_login_profile = MagicMock(return_value={})
            fake_client.update_login_profile = MagicMock(return_value={})

            user.attach_to(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.get_login_profile.assert_called_with(
                UserName='aws_resource_mock_id'
            )
            fake_client.update_login_profile.assert_called_with(
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_detach_from_Group(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_detach_from',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.Group']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.remove_user_from_group = MagicMock(return_value={})

            user.detach_from(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.remove_user_from_group.assert_called_with(
                GroupName='aws_target_mock_id',
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_detach_from_AccessKey(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_detach_from',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.AccessKey']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.delete_access_key = MagicMock(return_value={})

            user.detach_from(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.delete_access_key.assert_called_with(
                AccessKeyId='aws_target_mock_id',
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_detach_from_Policy(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_detach_from',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.Policy']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.detach_user_policy = MagicMock(return_value={})

            user.detach_from(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.detach_user_policy.assert_called_with(
                PolicyArn='aws_resource_mock_arn',
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_detach_from_LoginProfile(self):
        _source_ctx, _target_ctx, _ctx = self._create_common_relationships(
            'test_detach_from',
            USER_TH,
            ['cloudify.nodes.Root', 'cloudify.nodes.aws.iam.LoginProfile']
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('iam')

        with patch('boto3.client', fake_boto):
            fake_client.delete_login_profile = MagicMock(return_value={})

            user.detach_from(
                ctx=_ctx, resource_config=None, iface=None
            )

            fake_client.delete_login_profile.assert_called_with(
                UserName='aws_resource_mock_id'
            )

            self.assertEqual(
                _source_ctx.instance.runtime_properties, {
                    '_set_changed': True,
                    'aws_resource_id': 'aws_resource_mock_id',
                    'resource_config': {},
                    'resource_id': 'prepare_attach_source'
                }
            )

    def test_IAMUserClass_properties(self):
        fake_boto, fake_client = self.fake_boto_client('iam')
        with patch('boto3.client', fake_boto):
            fake_client.get_user = MagicMock(return_value={
                'User': {
                    'UserName': 'user_name_id',
                    'Arn': 'arn_id'
                }
            })

            test_instance = user.IAMUser("ctx_node", resource_id='user_id',
                                         client=fake_client, logger=None)

            self.assertEqual(test_instance.properties, {
                'UserName': 'user_name_id',
                'Arn': 'arn_id'
            })

            fake_client.get_user.assert_called_with(
                UserName='user_id'
            )

    def test_IAMUserClass_status(self):
        fake_boto, fake_client = self.fake_boto_client('iam')
        with patch('boto3.client', fake_boto):
            fake_client.get_user = MagicMock(return_value={
                'User': {
                    'UserName': 'user_name_id',
                    'Arn': 'arn_id'
                }
            })

            test_instance = user.IAMUser("ctx_node", resource_id='user_id',
                                         client=fake_client, logger=None)

            self.assertEqual(test_instance.status, 'available')

            fake_client.get_user.assert_called_with(
                UserName='user_id'
            )


if __name__ == '__main__':
    unittest.main()