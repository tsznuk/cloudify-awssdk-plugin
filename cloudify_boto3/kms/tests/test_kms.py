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

import unittest
from mock import MagicMock

from cloudify.state import current_ctx

from cloudify_boto3.common.tests.test_base import TestServiceBase
from cloudify_boto3.common.tests.test_base import TestBase, CLIENT_CONFIG
from cloudify_boto3.kms import KMSBase

NODE_PROPERTIES = {
    'use_external_resource': False,
    'resource_config': {},
    'client_config': CLIENT_CONFIG
}

RUNTIME_PROPERTIES = {
    'aws_resource_id': 'aws_resource',
    'resource_config': {}
}


class TestKMSBase(TestServiceBase):

    def setUp(self):
        self.base = KMSBase("ctx_node", resource_id=True,
                            client=True, logger=None)


class TestKMS(TestBase):

    def _prepare_context(self, type_hierarchy, node_prop=None,
                         runtime_prop=None):

        mock_child = MagicMock()
        mock_child.type_hierarchy = 'cloudify.relationships.contained_in'
        mock_child.target.instance.runtime_properties = {
            'aws_resource_id': 'a'
        }
        mock_child.target.node.type_hierarchy = [
            'cloudify.nodes.Root',
            'cloudify.nodes.aws.kms.CustomerMasterKey'
        ]

        mock_child.target.node.id = 'aws-sample-node'
        mock_child.target.instance.relationships = []

        _ctx = self.get_mock_ctx(
            'test_create',
            test_properties=(
                node_prop if node_prop else NODE_PROPERTIES
            ),
            test_runtime_properties=(
                runtime_prop if runtime_prop else RUNTIME_PROPERTIES
            ),
            type_hierarchy=type_hierarchy,
            test_relationships=[mock_child]
        )

        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('kms')
        return _ctx, fake_boto, fake_client


if __name__ == '__main__':
    unittest.main()