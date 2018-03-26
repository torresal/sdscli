from __future__ import absolute_import
from __future__ import print_function

import os, re, json, boto3
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
    #execute(func, bucket_name, args.encrypt, roles=['mozart']) 

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
