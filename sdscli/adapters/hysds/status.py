"""
Status of HySDS components.
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


prompt_style = style_from_dict({
    Token.Alert: 'bg:#D8060C',
    Token.Username: '#D8060C',
    Token.Param: '#3CFF33',
})


def print_status(conf, comp):
    """"Status of component."""

    print_component_header(comp)
    execute(fab.status, roles=[comp])


def status_comp(comp, conf):
    """Update component."""

    if comp in ('all', 'grq'): print_status(conf, 'grq')
    if comp in ('all', 'mozart'): print_status(conf, 'mozart')
    if comp in ('all', 'metrics'): print_status(conf, 'metrics')
    if comp in ('all', 'factotum'): print_status(conf, 'factotum')
    if comp in ('all', 'ci'): print_status(conf, 'ci')
    if comp in ('all', 'verdi'): print_status(conf, 'verdi')


def status(comp, debug=False):
    """Component status."""

    # get user's SDS conf settings
    conf = SettingsConf()

    logger.debug("Status for %s component(s)" % comp)

    status_comp(comp, conf)
