"""
Continuous integration functions.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import os, yaml, pwd, hashlib, traceback
from fabric.api import execute, hide
from tqdm import tqdm

from prompt_toolkit.shortcuts import prompt, print_tokens
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from pygments.token import Token

from sdscli.log_utils import logger
from sdscli.conf_utils import get_user_files_path, SettingsConf
from sdscli.os_utils import validate_dir
from sdscli.prompt_utils import print_component_header

from . import fabfile as fab


#def remove_job(args):
#    """Component status."""
#
#    # get user's SDS conf settings
#    conf = SettingsConf()
#
#    raise RuntimeError("Unimplemented.")


def add_job(args):
    """Component status."""

    # get user's SDS conf settings
    conf = SettingsConf()

    # add jenkins job for branch or release
    if args.branch is None:
        execute(fab.add_ci_job_release, args.repo, args.storage, args.uid, 
                args.gid, roles=['ci'])
    else:
        execute(fab.add_ci_job, args.repo, args.storage, args.uid, 
                args.gid, args.branch, roles=['ci'])

    # reload
    execute(fab.reload_configuration, roles=['ci'])
