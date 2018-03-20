from __future__ import absolute_import
from __future__ import print_function

import os, sys, boto3
from botocore.exceptions import NoCredentialsError

from sdscli.log_utils import logger


def is_configured():
    """Return if AWS account is configured."""

    try: boto3.client('s3').list_buckets()
    except NoCredentialsError:
        return False
    return True


def cloud_config_check(func):
    """Wrapper function to perform cloud config check."""

    def wrapper(*args, **kwargs):
        if is_configured():
            return func(*args, **kwargs)
        else:
            logger.error("Not configured for AWS.")
            sys.exit(1)
    return wrapper


@cloud_config_check
def get_asgs(c=None):
    """List all Autoscaling groups."""

    if c is None: c = boto3.client('autoscaling')
    return c.describe_auto_scaling_groups().get('AutoScalingGroups', [])


@cloud_config_check
def get_lcs(c=None):
    """List all launch configurations."""

    if c is None: c = boto3.client('autoscaling')
    return c.describe_launch_configurations().get('LaunchConfigurations', [])


@cloud_config_check
def get_keypairs(c=None):
    """List all key pairs."""

    if c is None: c = boto3.client('ec2')
    return c.describe_key_pairs().get('KeyPairs', [])


@cloud_config_check
def get_images(c=None, **kargs):
    """List all AMIs."""

    if c is None: c = boto3.client('ec2')
    return c.describe_images(**kargs).get('Images', [])


@cloud_config_check
def get_sgs(c=None):
    """List all security groups."""

    if c is None: c = boto3.client('ec2')
    return c.describe_security_groups().get('SecurityGroups', [])


@cloud_config_check
def get_azs(c=None):
    """List all availability zones."""

    if c is None: c = boto3.client('ec2')
    return c.describe_availability_zones().get('AvailabilityZones', [])


@cloud_config_check
def get_subnets_by_vpc(vpc_id, c=None):
    """List all subnets for a VPC."""

    if c is None: c = boto3.resource('ec2')
    return list(c.subnets.filter(Filters=[{'Name': 'vpc-id',
                                           'Values': [ vpc_id ] }]))


@cloud_config_check
def create_lc(c=None, **kargs):
    """Create launch configuration."""

    if c is None: c = boto3.client('autoscaling')
    return c.create_launch_configuration(**kargs)


@cloud_config_check
def create_asg(c=None, **kargs):
    """Create Autoscaling group."""

    if c is None: c = boto3.client('autoscaling')
    return c.create_auto_scaling_group(**kargs)


@cloud_config_check
def get_buckets(c=None, **kargs):
    """List all buckets."""

    if c is None: c = boto3.client('s3')
    return c.list_buckets(**kargs).get('Buckets', [])
