# #######
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
"""Cloudify plugin package config"""

from setuptools import setup


setup(
    name='cloudify-boto3-plugin',
    version='1.0.0',
    license='LICENSE',
    packages=[
        'cloudify_boto3',
        'cloudify_boto3.common',
        'cloudify_boto3.autoscaling',
        'cloudify_boto3.autoscaling.resources',
        'cloudify_boto3.cloudwatch',
        'cloudify_boto3.cloudwatch.resources',
        'cloudify_boto3.cloudformation',
        'cloudify_boto3.cloudformation.resources',
        'cloudify_boto3.dynamodb',
        'cloudify_boto3.dynamodb.resources',
        'cloudify_boto3.ec2',
        'cloudify_boto3.ec2.resources',
        'cloudify_boto3.efs',
        'cloudify_boto3.efs.resources',
        'cloudify_boto3.elb',
        'cloudify_boto3.elb.resources',
        'cloudify_boto3.elb.resources.classic',
        'cloudify_boto3.iam',
        'cloudify_boto3.iam.resources',
        'cloudify_boto3.kms',
        'cloudify_boto3.kms.resources',
        'cloudify_boto3.lambda_serverless',
        'cloudify_boto3.lambda_serverless.resources',
        'cloudify_boto3.rds',
        'cloudify_boto3.rds.resources',
        'cloudify_boto3.route53',
        'cloudify_boto3.route53.resources',
        'cloudify_boto3.s3',
        'cloudify_boto3.s3.resources',
        'cloudify_boto3.sns',
        'cloudify_boto3.sns.resources',
        'cloudify_boto3.sqs',
        'cloudify_boto3.sqs.resources'
    ],
    description='A Cloudify plugin for AWS',
    install_requires=[
        'cloudify-plugins-common>=3.4',
        'boto3==1.4.4',
        'botocore==1.5.44'
    ]
)
