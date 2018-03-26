from __future__ import absolute_import
from __future__ import print_function

import os, re, json, boto3, hashlib
from pprint import pformat
from collections import OrderedDict
from operator import itemgetter
from fabric.api import execute

from prompt_toolkit.shortcuts import prompt, print_tokens
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from pygments.token import Token

from sdscli.log_utils import logger
from sdscli.conf_utils import get_user_config_path, get_user_files_path, SettingsConf
from sdscli.os_utils import validate_dir
from sdscli.func_utils import get_func
from sdscli.prompt_utils import (YesNoValidator, SelectionValidator,
MultipleSelectionValidator, Ec2InstanceTypeValidator, PriceValidator, highlight,
print_component_header)
from .utils import *


prompt_style = style_from_dict({
    Token.Alert: 'bg:#D8060C',
    Token.Username: '#D8060C',
    Token.Param: '#3CFF33',
})


@cloud_config_check
def ls(args, conf):
    """List all buckets."""

    for bucket in get_buckets(): print(bucket['Name'])


@cloud_config_check
def ship_style(args, conf):
    """Ship style to bucket."""

    # get bucket name
    bucket_name = conf.get('DATASET_BUCKET') if args.bucket is None else args.bucket

    # get fab function
    func = get_func('sdscli.adapters.{}.fabfile'.format(args.type), args.subparser2)

    # execute
    execute(func, bucket_name, args.encrypt, roles=['mozart']) 

    # turn on website hosting and set index and error docs
    bw_args = {
        'WebsiteConfiguration': {
            'ErrorDocument': {
                'Key': 'index.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        }
    }
    configure_bucket_website(bucket_name, **bw_args)


@cloud_config_check
def create_staging_area(args, conf):
    """Provision staging area in bucket."""

    # create boto3 clients
    s3_res = boto3.resource('s3')
    sns_client = boto3.client('sns')

    # get bucket name
    bucket_name = conf.get('DATASET_BUCKET') if args.bucket is None else args.bucket
    bucket = get_bucket(bucket_name, c=s3_res)
    logger.debug("bucket: {}".format(bucket))

    # create SNS topic
    logger.debug("prefix: {}".format(args.prefix))
    logger.debug("suffix: {}".format(args.suffix))
    shasum = hashlib.sha224("{}-{}".format(args.prefix, args.suffix)).hexdigest()
    topic_name = "{}-{}-{}".format(conf.get('VENUE'), bucket_name, shasum[:4])
    logger.debug("topic_name: {}".format(topic_name))
    topic_arn = create_topic(Name=topic_name, c=sns_client)['TopicArn']
    logger.debug("topic_arn: {}".format(topic_arn))

    # add policy to allow S3 to publish to topic
    pol = {
        "Version": "2008-10-17",
        "Id": "__default_policy_ID",
        "Statement": [
            {
                "Sid": "__default_statement_ID",
                "Effect": "Allow",
                "Principal": { "AWS": "*" },
                "Action": [
                    "SNS:GetTopicAttributes",
                    "SNS:SetTopicAttributes",
                    "SNS:AddPermission",
                    "SNS:RemovePermission",
                    "SNS:DeleteTopic",
                    "SNS:Subscribe",
                    "SNS:ListSubscriptionsByTopic",
                    "SNS:Publish",
                    "SNS:Receive"
                ],
                "Resource": topic_arn,
                "Condition": {
                    "StringEquals": {
                        "aws:SourceArn": "arn:aws:s3:::{}".format(bucket_name)
                    }
                }
            }
        ]
    }
    sns_client.set_topic_attributes(TopicArn=topic_arn, AttributeName="Policy",
                                    AttributeValue=json.dumps(pol))
    sns_client.set_topic_attributes(TopicArn=topic_arn, AttributeName="DisplayName",
                                    AttributeValue=topic_name)
    

    # create notification event on bucket staging area
    notification_name = "data-staged-{}".format(topic_name)
    logger.debug("notification_name: {}".format(notification_name))
    bn_args = {
        'NotificationConfiguration': {
            'TopicConfigurations': [
                {
                    'Id': notification_name,
                    'TopicArn': topic_arn,
                    'Events': [
                        's3:ObjectCreated:*',
                    ],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'prefix',
                                    'Value': args.prefix,
                                },
                                {
                                    'Name': 'suffix',
                                    'Value': args.suffix,
                                },
                            ]
                        }
                    }
                }
            ] 
        }
    }
    configure_bucket_notification(bucket_name, c=s3_res, **bn_args)
