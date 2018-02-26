"""
Update components for HySDS.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import os, yaml, pwd, hashlib, traceback
from fabric.api import execute

from prompt_toolkit.shortcuts import prompt, print_tokens
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from pygments.token import Token

from sdscli.log_utils import logger
from sdscli.conf_utils import get_user_config_path, SettingsConf
from sdscli.os_utils import validate_dir
from sdscli.prompt_utils import YesNoValidator

from . import fabfile as fab


prompt_style = style_from_dict({
    Token.Alert: 'bg:#D8060C',
    Token.Username: '#D8060C',
    Token.Param: '#3CFF33',
})


def update(comp):
    """Update components."""

    logger.debug("Updating %s" % comp)

    if comp in ['mozart', 'all']:
        execute(fab.mozartd_stop, roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/osaka', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/prov_es', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds_commons', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds/third_party/celery-v3.1.25.pqueue', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/sciflo', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/mozart', roles=[comp])
        execute(fab.rm_rf, '~/mozart/ops/hysds/celeryconfig.py', roles=[comp])
        execute(fab.rm_rf, '~/mozart/ops/hysds/celeryconfig.pyc', roles=[comp])
        execute(fab.send_celeryconf, 'mozart', roles=[comp])
