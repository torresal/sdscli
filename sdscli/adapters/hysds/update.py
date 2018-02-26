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
from sdscli.conf_utils import SettingsConf
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

    # get user's SDS conf settings
    conf = SettingsConf()

    logger.debug("Updating %s" % comp)

    if comp in ['mozart', 'all']:

        # stop services on mozart
        execute(fab.mozartd_stop, roles=[comp])

        # update reqs
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/osaka', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/prov_es', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds_commons', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds/third_party/celery-v3.1.25.pqueue', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/sciflo', roles=[comp])
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/mozart', roles=[comp])

        # update celery config
        execute(fab.rm_rf, '~/mozart/ops/hysds/celeryconfig.py', roles=[comp])
        execute(fab.rm_rf, '~/mozart/ops/hysds/celeryconfig.pyc', roles=[comp])
        execute(fab.send_celeryconf, 'mozart', roles=[comp])

        # update supervisor config
        execute(fab.rm_rf, '~/mozart/etc/supervisord.conf', roles=[comp])
        execute(fab.send_template, 'supervisord.conf.mozart', '~/mozart/etc/supervisord.conf', 
                '~/mozart/ops/hysds/configs/supervisor', roles=[comp])

        # update orchestrator config
        execute(fab.rm_rf, '~/mozart/etc/orchestrator_*.json', roles=[comp])
        execute(fab.copy, '~/mozart/ops/hysds/configs/orchestrator/orchestrator_jobs.json',
                '~/mozart/etc/orchestrator_jobs.json', roles=[comp])
        execute(fab.copy, '~/mozart/ops/hysds/configs/orchestrator/orchestrator_datasets.json',
                '~/mozart/etc/orchestrator_datasets.json', roles=[comp])

        #update datasets config; overwrite datasets config with domain-specific config
        execute(fab.rm_rf, '~/mozart/etc/datasets.json', roles=[comp])
        execute(fab.send_template, 'datasets.json', '~/mozart/etc/datasets.json', roles=[comp])

        # ship logstash shipper configs
        execute(fab.send_shipper_conf, 'mozart', '/home/hysdsops/mozart/log', conf.get('MOZART_ES_CLUSTER'),
                '127.0.0.1', conf.get('METRICS_ES_CLUSTER'), conf.get('METRICS_PVT_IP'), roles=[comp])

        # update mozart config
        execute(fab.rm_rf, '~/mozart/ops/mozart/settings.cfg', roles=[comp])
        execute(fab.send_mozartconf, roles=[comp])
        execute(fab.rm_rf, '~/mozart/ops/mozart/actions_config.json', roles=[comp])
        execute(fab.copy, '~/mozart/ops/mozart/configs/actions_config.json.example', 
                '~/mozart/ops/mozart/actions_config.json', roles=[comp])

        # update figaro config
        execute(fab.rm_rf, '~/mozart/ops/figaro/settings.cfg', roles=[comp])
        execute(fab.send_figaroconf, roles=[comp])

        # create user_rules index
        execute(fab.create_user_rules_index, roles=[comp])

        # ensure self-signed SSL certs exist
        execute(fab.ensure_ssl, 'mozart', roles=[comp])

        # link ssl certs to apps
        execute(fab.ln_sf, '~/ssl/server.key', '~/mozart/ops/mozart/server.key', roles=[comp])
        execute(fab.ln_sf, '~/ssl/server.pem', '~/mozart/ops/mozart/server.pem', roles=[comp])

        # expose hysds log dir via webdav
        #execute(fab.ln_sf, '~/mozart/log', '/data/work/log', roles=[comp])

        # ship netrc
        execute(fab.send_template, 'netrc.mozart', '.netrc', roles=[comp])
        execute(fab.chmod, 600, '.netrc', roles=[comp])

        # ship AWS creds
        execute(fab.send_awscreds, roles=[comp])
