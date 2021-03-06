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
from cloudify_awssdk.common.tests.test_base import TestBase, mock_decorator
from cloudify_awssdk.s3.resources.tagging import (
    S3BucketTagging, BUCKET, TAGSET)
from mock import patch, MagicMock
from cloudify_awssdk.common.constants import EXTERNAL_RESOURCE_ID
from cloudify_awssdk.s3.resources import tagging

PATCH_PREFIX = 'cloudify_awssdk.s3.resources.tagging.'


class TestS3BucketTagging(TestBase):

    def setUp(self):
        super(TestS3BucketTagging, self).setUp()
        self.tagging = S3BucketTagging("ctx_node",
                                       resource_id=True,
                                       client=True, logger=None)
        mock1 = patch('cloudify_awssdk.common.decorators.aws_resource',
                      mock_decorator)
        mock1.start()
        reload(tagging)

    def test_class_properties(self):
        effect = self.get_client_error_exception(name='S3 Bucket')
        self.tagging.client = self.make_client_function(
            'get_bucket_tagging',
            side_effect=effect)
        res = self.tagging.properties
        self.assertIsNone(res)

        self.tagging.client = self.make_client_function(
            'get_bucket_tagging',
            return_value={})
        res = self.tagging.properties
        self.assertEqual(res, [])

        value = {TAGSET: ['tag']}
        self.tagging.client = self.make_client_function(
            'get_bucket_tagging',
            return_value=value)
        res = self.tagging.properties
        self.assertEqual(res, ['tag'])

    def test_class_status(self):
        res = self.tagging.status
        self.assertIsNone(res)

    def test_class_create(self):
        value = 'test'
        self.tagging.client = self.make_client_function('put_bucket_tagging',
                                                        return_value=value)
        res = self.tagging.create({})
        self.assertEqual(res, 'test')

    def test_class_delete(self):
        params = {}
        self.tagging.client = self.make_client_function(
            'delete_bucket_tagging')
        self.tagging.delete(params)
        self.assertTrue(self.tagging.client.delete_bucket_tagging.called)

        params = {BUCKET: 'bucket'}
        self.tagging.delete(params)
        self.assertEqual(params[BUCKET], 'bucket')

    def test_prepare(self):
        ctx = self.get_mock_ctx("Bucket")
        tagging.prepare(ctx, 'config')
        self.assertEqual(ctx.instance.runtime_properties['resource_config'],
                         'config')

    def test_create(self):
        ctx = self.get_mock_ctx("Bucket")
        config = {BUCKET: 'bucket'}
        iface = MagicMock()
        tagging.create(ctx, iface, config)
        self.assertEqual(ctx.instance.runtime_properties[BUCKET],
                         'bucket')

        config = {}
        ctx_target = self.get_mock_relationship_ctx(
            "bucket",
            test_target=self.get_mock_ctx("Bucket", {},
                                          {EXTERNAL_RESOURCE_ID: 'ext_id'}))
        iface = MagicMock()
        iface.create = self.mock_return('location')
        with patch(PATCH_PREFIX + 'utils') as utils:
            utils.find_rel_by_node_type = self.mock_return(ctx_target)
            tagging.create(ctx, iface, config)
            self.assertEqual(ctx.instance.runtime_properties[BUCKET],
                             'ext_id')

    def test_delete(self):
        iface = MagicMock()
        tagging.delete(iface, {})
        self.assertTrue(iface.delete.called)


if __name__ == '__main__':
    unittest.main()
