"""
SDS cloud management functions.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import os, json, pkgutil, traceback
from importlib import import_module
from fabric.api import execute, hide

from prompt_toolkit.shortcuts import prompt, print_tokens
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from pygments.token import Token

from sdscli.log_utils import logger
from sdscli.conf_utils import get_user_files_path, SettingsConf
from sdscli.prompt_utils import highlight
import sdscli.cloud


def ls(args):
    """List HySDS packages."""

    # get user's SDS conf settings
    conf = SettingsConf()

    # check which cloud platforms configured
    for importer, mod_name, ispkg in pkgutil.iter_modules(sdscli.cloud.__path__):
        mod = import_module('sdscli.cloud.{}.utils'.format(mod_name))
        print("{}: {}".format(mod_name, highlight("configured", 'green') if 
              mod.is_configured() else highlight("unimplemented or not configured", 'red')))
