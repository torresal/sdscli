from __future__ import absolute_import
from __future__ import print_function

import os, json, boto3
from pprint import pformat

from sdscli.log_utils import logger
from .utils import cloud_config_check


@cloud_config_check
def ls(args, conf):
    """List all Autoscaling groups."""

    # get client
    c = boto3.client('autoscaling')

    # print autoscaling groups
    for asg in c.describe_auto_scaling_groups().get('AutoScalingGroups', []):
        logger.debug(pformat(asg, indent=2))
        print(asg['AutoScalingGroupName'])
