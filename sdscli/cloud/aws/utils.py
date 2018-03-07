from __future__ import absolute_import
from __future__ import print_function

import os, boto3
from botocore.exceptions import NoCredentialsError

from sdscli.log_utils import logger


def is_configured():
    """Return if AWS account is configured."""

    try: boto3.client('s3').list_buckets()
    except NoCredentialsError:
        return False
    return True
