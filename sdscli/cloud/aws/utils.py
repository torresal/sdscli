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
