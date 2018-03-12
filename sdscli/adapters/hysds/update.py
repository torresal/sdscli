"""
Update components for HySDS.
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
from sdscli.prompt_utils import YesNoValidator, set_bar_desc

from . import fabfile as fab


prompt_style = style_from_dict({
    Token.Alert: 'bg:#D8060C',
    Token.Username: '#D8060C',
    Token.Param: '#3CFF33',
})


def update_mozart(conf, comp='mozart'):
    """"Update mozart component."""

    # progress bar
    with tqdm(total=24) as bar:

        # ensure venv
        set_bar_desc(bar, 'Ensuring HySDS venv')
        execute(fab.ensure_venv, comp, roles=[comp])
        bar.update()

        # stop services
        set_bar_desc(bar, 'Stopping mozartd')
        execute(fab.mozartd_stop, roles=[comp])
        bar.update()

        # update reqs
        set_bar_desc(bar, 'Updating HySDS core')
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/osaka', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/prov_es', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds_commons', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds/third_party/celery-v3.1.25.pqueue', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/hysds', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/sciflo', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'mozart', '~/mozart/ops/mozart', roles=[comp])
        bar.update()

        # update celery config
        set_bar_desc(bar, 'Updating celery config')
        execute(fab.rm_rf, '~/mozart/ops/hysds/celeryconfig.py', roles=[comp])
        execute(fab.rm_rf, '~/mozart/ops/hysds/celeryconfig.pyc', roles=[comp])
        execute(fab.send_celeryconf, 'mozart', roles=[comp])
        bar.update()

        # update supervisor config
        set_bar_desc(bar, 'Updating supervisor config')
        execute(fab.rm_rf, '~/mozart/etc/supervisord.conf', roles=[comp])
        execute(fab.send_template_user_override, 'supervisord.conf.mozart', 
                '~/mozart/etc/supervisord.conf', '~/mozart/ops/hysds/configs/supervisor',
                roles=[comp])
        bar.update()

        # update orchestrator config
        set_bar_desc(bar, 'Updating orchestrator config')
        execute(fab.rm_rf, '~/mozart/etc/orchestrator_*.json', roles=[comp])
        execute(fab.copy, '~/mozart/ops/hysds/configs/orchestrator/orchestrator_jobs.json',
                '~/mozart/etc/orchestrator_jobs.json', roles=[comp])
        execute(fab.copy, '~/mozart/ops/hysds/configs/orchestrator/orchestrator_datasets.json',
                '~/mozart/etc/orchestrator_datasets.json', roles=[comp])
        bar.update()

        # update job_creators
        set_bar_desc(bar, 'Updating job_creators')
        execute(fab.rm_rf, '~/mozart/etc/job_creators', roles=[comp])
        execute(fab.cp_rp, '~/mozart/ops/hysds/scripts/job_creators', '~/mozart/etc/', roles=[comp])
        bar.update()

        #update datasets config; overwrite datasets config with domain-specific config
        set_bar_desc(bar, 'Updating datasets config')
        execute(fab.rm_rf, '~/mozart/etc/datasets.json', roles=[comp])
        execute(fab.send_template, 'datasets.json', '~/mozart/etc/datasets.json', roles=[comp])
        bar.update()

        # ship logstash shipper configs
        set_bar_desc(bar, 'Updating logstash shipper config')
        execute(fab.send_shipper_conf, 'mozart', '/home/hysdsops/mozart/log', conf.get('MOZART_ES_CLUSTER'),
                '127.0.0.1', conf.get('METRICS_ES_CLUSTER'), conf.get('METRICS_PVT_IP'), roles=[comp])
        bar.update()

        # update mozart config
        set_bar_desc(bar, 'Updating mozart config')
        execute(fab.rm_rf, '~/mozart/ops/mozart/settings.cfg', roles=[comp])
        execute(fab.send_mozartconf, roles=[comp])
        execute(fab.rm_rf, '~/mozart/ops/mozart/actions_config.json', roles=[comp])
        execute(fab.copy, '~/mozart/ops/mozart/configs/actions_config.json.example', 
                '~/mozart/ops/mozart/actions_config.json', roles=[comp])
        bar.update()

        # update figaro config
        set_bar_desc(bar, 'Updating figaro config')
        execute(fab.rm_rf, '~/mozart/ops/figaro/settings.cfg', roles=[comp])
        execute(fab.send_figaroconf, roles=[comp])
        bar.update()

        # create user_rules index
        set_bar_desc(bar, 'Creating user_rules index')
        execute(fab.create_user_rules_index, roles=[comp])
        bar.update()

        # ensure self-signed SSL certs exist
        set_bar_desc(bar, 'Configuring SSL')
        execute(fab.ensure_ssl, 'mozart', roles=[comp])
        bar.update()

        # link ssl certs to apps
        execute(fab.ln_sf, '~/ssl/server.key', '~/mozart/ops/mozart/server.key', roles=[comp])
        execute(fab.ln_sf, '~/ssl/server.pem', '~/mozart/ops/mozart/server.pem', roles=[comp])
        bar.update()

        # expose hysds log dir via webdav
        set_bar_desc(bar, 'Expose logs')
        execute(fab.mkdir, '/data/work', None, None, roles=[comp])
        execute(fab.ln_sf, '~/mozart/log', '/data/work/log', roles=[comp])
        bar.update()

        # ship netrc
        set_bar_desc(bar, 'Configuring netrc')
        execute(fab.send_template, 'netrc.mozart', '.netrc', roles=[comp])
        execute(fab.chmod, 600, '.netrc', roles=[comp])
        bar.update()

        # update ES template
        set_bar_desc(bar, 'Update ES template')
        execute(fab.install_pkg_es_templates, roles=[comp])
        bar.update()
        
        # ship AWS creds
        set_bar_desc(bar, 'Configuring AWS creds')
        execute(fab.send_awscreds, roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Updated mozart')


def update_metrics(conf, comp='metrics'):
    """"Update metrics component."""

    # progress bar
    with tqdm(total=20) as bar:

        # ensure venv
        set_bar_desc(bar, 'Ensuring HySDS venv')
        execute(fab.ensure_venv, comp, roles=[comp])
        bar.update()

        # stop services
        set_bar_desc(bar, 'Stopping metricsd')
        execute(fab.metricsd_stop, roles=[comp])
        bar.update()

        # update
        set_bar_desc(bar, 'Syncing packages')
        execute(fab.rm_rf, '~/metrics/ops/*', roles=[comp])
        execute(fab.rsync_code, 'metrics', roles=[comp])
        bar.update()

        # update reqs
        set_bar_desc(bar, 'Updating HySDS core')
        execute(fab.pip_install_with_req, 'metrics', '~/metrics/ops/osaka', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'metrics', '~/metrics/ops/prov_es', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'metrics', '~/metrics/ops/hysds_commons', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'metrics', '~/metrics/ops/hysds/third_party/celery-v3.1.25.pqueue', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'metrics', '~/metrics/ops/hysds', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'metrics', '~/metrics/ops/sciflo', roles=[comp])
        bar.update()

        # update celery config
        set_bar_desc(bar, 'Updating celery config')
        execute(fab.rm_rf, '~/metrics/ops/hysds/celeryconfig.py', roles=[comp])
        bar.update()
        execute(fab.rm_rf, '~/metrics/ops/hysds/celeryconfig.pyc', roles=[comp])
        bar.update()
        execute(fab.send_celeryconf, 'metrics', roles=[comp])
        bar.update()

        # update supervisor config
        set_bar_desc(bar, 'Updating supervisor config')
        execute(fab.rm_rf, '~/metrics/etc/supervisord.conf', roles=[comp])
        bar.update()
        execute(fab.send_template_user_override, 'supervisord.conf.metrics',
                '~/metrics/etc/supervisord.conf', '~/mozart/ops/hysds/configs/supervisor',
                roles=[comp])
        bar.update()

        #update datasets config; overwrite datasets config with domain-specific config
        set_bar_desc(bar, 'Updating datasets config')
        execute(fab.rm_rf, '~/metrics/etc/datasets.json', roles=[comp])
        bar.update()
        execute(fab.send_template, 'datasets.json', '~/metrics/etc/datasets.json', roles=[comp])
        bar.update()

        # ship logstash shipper configs
        set_bar_desc(bar, 'Updating logstash shipper config')
        execute(fab.send_shipper_conf, 'metrics', '/home/hysdsops/metrics/log', conf.get('MOZART_ES_CLUSTER'),
                conf.get('MOZART_PVT_IP'), conf.get('METRICS_ES_CLUSTER'), '127.0.0.1', roles=[comp])
        bar.update()

        # ship kibana config
        set_bar_desc(bar, 'Updating kibana config')
        execute(fab.send_template, 'kibana.yml', '~/kibana/config/kibana.yml', roles=[comp])
        bar.update()

        # expose hysds log dir via webdav
        set_bar_desc(bar, 'Expose logs')
        execute(fab.mkdir, '/data/work', None, None, roles=[comp])
        execute(fab.ln_sf, '~/metrics/log', '/data/work/log', roles=[comp])
        bar.update()

        # ship AWS creds
        set_bar_desc(bar, 'Configuring AWS creds')
        execute(fab.send_awscreds, roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Updated metrics')


def update_grq(conf, comp='grq'):
    """"Update grq component."""

    # progress bar
    with tqdm(total=21) as bar:

        # ensure venv
        set_bar_desc(bar, 'Ensuring HySDS venv')
        execute(fab.ensure_venv, 'sciflo', roles=[comp])
        bar.update()

        # stop services
        set_bar_desc(bar, 'Stopping grqd')
        execute(fab.grqd_stop, roles=[comp])
        bar.update()

        # update
        set_bar_desc(bar, 'Syncing packages')
        execute(fab.rm_rf, '~/sciflo/ops/*', roles=[comp])
        execute(fab.rsync_code, 'grq', 'sciflo', roles=[comp])
        execute(fab.pip_upgrade, 'gunicorn', 'sciflo', roles=[comp]) # ensure latest gunicorn
        bar.update()

        # update reqs
        set_bar_desc(bar, 'Updating HySDS core')
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/osaka', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/prov_es', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/hysds_commons', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/hysds/third_party/celery-v3.1.25.pqueue', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/hysds', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/sciflo', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/grq2', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'sciflo', '~/sciflo/ops/tosca', roles=[comp])
        bar.update()

        # update celery config
        set_bar_desc(bar, 'Updating celery config')
        execute(fab.rm_rf, '~/sciflo/ops/hysds/celeryconfig.py', roles=[comp])
        execute(fab.rm_rf, '~/sciflo/ops/hysds/celeryconfig.pyc', roles=[comp])
        execute(fab.send_celeryconf, 'grq', roles=[comp])
        bar.update()

        # update grq2 config
        set_bar_desc(bar, 'Updating grq2 config')
        execute(fab.rm_rf, '~/sciflo/ops/grq2/settings.cfg', roles=[comp])
        execute(fab.send_grq2conf, roles=[comp])
        bar.update()

        # update tosca config
        set_bar_desc(bar, 'Updating tosca config')
        execute(fab.rm_rf, '~/sciflo/ops/tosca/settings.cfg', roles=[comp])
        execute(fab.send_toscaconf, 'tosca_settings.cfg.tmpl', roles=[comp])
        execute(fab.ln_sf, '~/sciflo/ops/tosca/configs/actions_config.json.example', 
                '~/sciflo/ops/tosca/actions_config.json', roles=[comp])
        bar.update()

        # update supervisor config
        set_bar_desc(bar, 'Updating supervisor config')
        execute(fab.rm_rf, '~/sciflo/etc/supervisord.conf', roles=[comp])
        execute(fab.send_template_user_override, 'supervisord.conf.grq',
                '~/sciflo/etc/supervisord.conf', '~/mozart/ops/hysds/configs/supervisor',
                roles=[comp])
        bar.update()

        #update datasets config; overwrite datasets config with domain-specific config
        set_bar_desc(bar, 'Updating datasets config')
        execute(fab.rm_rf, '~/sciflo/etc/datasets.json', roles=[comp])
        execute(fab.send_template, 'datasets.json', '~/sciflo/etc/datasets.json', roles=[comp])
        bar.update()

        # ensure self-signed SSL certs exist
        set_bar_desc(bar, 'Configuring SSL')
        execute(fab.ensure_ssl, 'grq', roles=[comp])
        bar.update()

        # link ssl certs to apps
        execute(fab.ln_sf, '~/ssl/server.key', '~/sciflo/ops/grq2/server.key', roles=[comp])
        execute(fab.ln_sf, '~/ssl/server.pem', '~/sciflo/ops/grq2/server.pem', roles=[comp])
        execute(fab.ln_sf, '~/ssl/server.key', '~/sciflo/ops/tosca/server.key', roles=[comp])
        execute(fab.ln_sf, '~/ssl/server.pem', '~/sciflo/ops/tosca/server.pem', roles=[comp])
        bar.update()

        # expose hysds log dir via webdav
        set_bar_desc(bar, 'Expose logs')
        execute(fab.mkdir, '/data/work', None, None, roles=[comp])
        execute(fab.ln_sf, '~/sciflo/log', '/data/work/log', roles=[comp])
        bar.update()

        # update ES template
        set_bar_desc(bar, 'Update ES template')
        execute(fab.install_es_template, roles=[comp])
        execute(fab.install_pkg_es_templates, roles=[comp])
        bar.update()
        
        # ship AWS creds
        set_bar_desc(bar, 'Configuring AWS creds')
        execute(fab.send_awscreds, roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Updated grq')


def update_factotum(conf, comp='factotum'):
    """"Update factotum component."""

    # progress bar
    with tqdm(total=14) as bar:

        # ensure venv
        set_bar_desc(bar, 'Ensuring HySDS venv')
        execute(fab.ensure_venv, 'verdi', roles=[comp])
        bar.update()

        # stop services
        set_bar_desc(bar, 'Stopping verdid')
        execute(fab.verdid_stop, roles=[comp])
        execute(fab.kill_hung, roles=[comp])
        bar.update()

        # update
        set_bar_desc(bar, 'Syncing packages')
        execute(fab.rm_rf, '~/verdi/ops/*', roles=[comp])
        execute(fab.rsync_code, 'factotum', 'verdi', roles=[comp])
        execute(fab.set_spyddder_settings, roles=[comp])
        bar.update()

        # update reqs
        set_bar_desc(bar, 'Updating HySDS core')
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/osaka', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/prov_es', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/hysds_commons', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/hysds/third_party/celery-v3.1.25.pqueue', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/hysds', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/sciflo', roles=[comp])
        bar.update()

        # update celery config
        set_bar_desc(bar, 'Updating celery config')
        execute(fab.rm_rf, '~/verdi/ops/hysds/celeryconfig.py', roles=[comp])
        execute(fab.rm_rf, '~/verdi/ops/hysds/celeryconfig.pyc', roles=[comp])
        execute(fab.send_celeryconf, 'verdi', roles=[comp])
        bar.update()

        # update supervisor config
        set_bar_desc(bar, 'Updating supervisor config')
        execute(fab.rm_rf, '~/verdi/etc/supervisord.conf', roles=[comp])
        execute(fab.send_template_user_override, 'supervisord.conf.factotum', 
                '~/verdi/etc/supervisord.conf', '~/mozart/ops/hysds/configs/supervisor',
                roles=[comp])
        bar.update()

        #update datasets config; overwrite datasets config with domain-specific config
        set_bar_desc(bar, 'Updating datasets config')
        execute(fab.rm_rf, '~/verdi/etc/datasets.json', roles=[comp])
        execute(fab.send_template, 'datasets.json', '~/verdi/etc/datasets.json', roles=[comp])
        bar.update()

        # expose hysds log dir via webdav
        set_bar_desc(bar, 'Expose logs')
        execute(fab.mkdir, '/data/work', None, None, roles=[comp])
        execute(fab.ln_sf, '~/verdi/log', '/data/work/log', roles=[comp])
        bar.update()

        # ship netrc
        netrc = os.path.join(get_user_files_path(), 'netrc')
        if os.path.exists(netrc):
            set_bar_desc(bar, 'Configuring netrc')
            execute(fab.copy, netrc, '.netrc', roles=[comp])
            execute(fab.chmod, 600, '.netrc', roles=[comp])

        # ship AWS creds
        set_bar_desc(bar, 'Configuring AWS creds')
        execute(fab.send_awscreds, roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Updated factotum')


def update_verdi(conf, comp='verdi'):
    """"Update verdi component."""

    # progress bar
    with tqdm(total=15) as bar:

        # ensure venv
        set_bar_desc(bar, 'Ensuring HySDS venv')
        execute(fab.ensure_venv, comp, roles=[comp])
        bar.update()

        # stop services
        set_bar_desc(bar, 'Stopping verdid')
        execute(fab.verdid_stop, roles=[comp])
        execute(fab.kill_hung, roles=[comp])
        bar.update()

        # remove code bundle stuff
        set_bar_desc(bar, 'Remove code bundle')
        execute(fab.rm_rf, '~/verdi/ops/etc', roles=[comp])
        execute(fab.rm_rf, '~/verdi/ops/install.sh', roles=[comp])
        bar.update()

        # update
        set_bar_desc(bar, 'Syncing packages')
        execute(fab.rm_rf, '~/verdi/ops/*', roles=[comp])
        execute(fab.rsync_code, 'verdi', roles=[comp])
        bar.update()

        # update reqs
        set_bar_desc(bar, 'Updating HySDS core')
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/osaka', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/prov_es', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/hysds_commons', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/hysds/third_party/celery-v3.1.25.pqueue', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/hysds', roles=[comp])
        bar.update()
        execute(fab.pip_install_with_req, 'verdi', '~/verdi/ops/sciflo', roles=[comp])
        bar.update()

        # update celery config
        set_bar_desc(bar, 'Updating celery config')
        execute(fab.rm_rf, '~/verdi/ops/hysds/celeryconfig.py', roles=[comp])
        execute(fab.rm_rf, '~/verdi/ops/hysds/celeryconfig.pyc', roles=[comp])
        execute(fab.send_celeryconf, 'verdi', roles=[comp])
        bar.update()

        # update supervisor config
        set_bar_desc(bar, 'Updating supervisor config')
        execute(fab.rm_rf, '~/verdi/etc/supervisord.conf', roles=[comp])
        execute(fab.send_template_user_override, 'supervisord.conf.verdi', 
                '~/verdi/etc/supervisord.conf', '~/mozart/ops/hysds/configs/supervisor',
                roles=[comp])
        bar.update()

        #update datasets config; overwrite datasets config with domain-specific config
        set_bar_desc(bar, 'Updating datasets config')
        execute(fab.rm_rf, '~/verdi/etc/datasets.json', roles=[comp])
        execute(fab.send_template, 'datasets.json', '~/verdi/etc/datasets.json', roles=[comp])
        bar.update()

        # expose hysds log dir via webdav
        set_bar_desc(bar, 'Expose logs')
        execute(fab.mkdir, '/data/work', None, None, roles=[comp])
        execute(fab.ln_sf, '~/verdi/log', '/data/work/log', roles=[comp])
        bar.update()

        # ship netrc
        netrc = os.path.join(get_user_files_path(), 'netrc')
        if os.path.exists(netrc):
            set_bar_desc(bar, 'Configuring netrc')
            execute(fab.copy, netrc, '.netrc', roles=[comp])
            execute(fab.chmod, 600, '.netrc', roles=[comp])

        # ship AWS creds
        set_bar_desc(bar, 'Configuring AWS creds')
        execute(fab.send_awscreds, roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Updated verdi')


def update_comp(comp, conf):
    """Update component."""

    # if all, create progress bar
    if comp == 'all':
    
        # progress bar
        with tqdm(total=5) as bar:
            set_bar_desc(bar, "Updating grq")
            update_grq(conf)
            bar.update()
            set_bar_desc(bar, "Updating mozart")
            update_mozart(conf)
            bar.update()
            set_bar_desc(bar, "Updating metrics")
            update_metrics(conf)
            bar.update()
            set_bar_desc(bar, "Updating factotum")
            update_factotum(conf)
            bar.update()
            set_bar_desc(bar, "Updating verdi")
            update_verdi(conf)
            bar.update()
            set_bar_desc(bar, "Updated all")
            print("")
    else:
        if comp == 'grq': update_grq(conf)
        if comp == 'mozart': update_mozart(conf)
        if comp == 'metrics': update_metrics(conf)
        if comp == 'factotum': update_factotum(conf)
        if comp == 'verdi': update_verdi(conf)


def update(comp, debug=False, force=False):
    """Update components."""

    # prompt user
    if not force:
        cont = prompt(get_prompt_tokens=lambda x: [(Token.Alert, 
                      "Updating component[s]: {}. Continue [y/n]: ".format(comp)), (Token, " ")],
                      validator=YesNoValidator(), style=prompt_style) == 'y'
        if not cont: return 0

    # get user's SDS conf settings
    conf = SettingsConf()

    logger.debug("Updating %s" % comp)

    if debug: update_comp(comp, conf)
    else:
        with hide('everything'):
            update_comp(comp, conf)


def ship_verdi(conf, encrypt=False):
    """"Ship verdi code/config bundle."""

    comp = 'verdi'
    venue = conf.get('VENUE', 'ops')
    projects = [i.strip() for i in conf.get('PROJECTS').split()]

    # progress bar
    with tqdm(total=len(projects)+2) as bar:

        # ensure venv
        set_bar_desc(bar, 'Ensuring HySDS venv')
        execute(fab.ensure_venv, comp, roles=[comp])
        bar.update()

        # stop services
        set_bar_desc(bar, 'Stopping verdid')
        execute(fab.verdid_stop, roles=[comp])
        execute(fab.kill_hung, roles=[comp])
        bar.update()

        # iterate over projects
        for project in projects:

            set_bar_desc(bar, 'Shipping {} project'.format(project))

            # progress bar
            with tqdm(total=5) as proj_bar:

                # send project-specific install.sh script and configs
                set_bar_desc(proj_bar, 'Sending project-specific config')
                execute(fab.rm_rf, '~/verdi/ops/install.sh', roles=[comp])
                execute(fab.rm_rf, '~/verdi/etc/datasets.json', roles=[comp])
                execute(fab.rm_rf, '~/verdi/etc/supervisord.conf', roles=[comp])
                execute(fab.rm_rf, '~/verdi/etc/supervisord.conf.tmpl', roles=[comp])
                execute(fab.send_project_config, project, roles=[comp])
                execute(fab.chmod, '755', '~/verdi/ops/install.sh', roles=[comp])
                execute(fab.chmod, '644', '~/verdi/etc/datasets.json', roles=[comp])
                proj_bar.update()

                # copy config
                set_bar_desc(proj_bar, 'Copying config')
                execute(fab.rm_rf, '~/verdi/ops/etc', roles=[comp])
                execute(fab.cp_rp, '~/verdi/etc', '~/verdi/ops/', roles=[comp])
                proj_bar.update()

                # copy creds
                set_bar_desc(proj_bar, 'Copying creds')
                execute(fab.rm_rf, '~/verdi/ops/creds', roles=[comp])
                execute(fab.mkdir, '~/verdi/ops/creds', 'ops', 'ops', roles=[comp])
                execute(fab.cp_rp_exists, '~/.netrc', '~/verdi/ops/creds/', roles=[comp])
                execute(fab.cp_rp_exists, '~/.boto', '~/verdi/ops/creds/', roles=[comp])
                execute(fab.cp_rp_exists, '~/.s3cfg', '~/verdi/ops/creds/', roles=[comp])
                execute(fab.cp_rp_exists, '~/.aws', '~/verdi/ops/creds/', roles=[comp])
                proj_bar.update()

                # send work directory stylesheets
                style_tar = os.path.join(get_user_files_path(), 'beefed-autoindex-open_in_new_win.tbz2')
                set_bar_desc(proj_bar, 'Sending work dir stylesheets')
                execute(fab.rm_rf, '~/verdi/ops/beefed-autoindex-open_in_new_win.tbz2', roles=[comp])
                execute(fab.copy, style_tar, '~/verdi/ops/beefed-autoindex-open_in_new_win.tbz2', roles=[comp])
                proj_bar.update()

                # create venue bundle
                set_bar_desc(proj_bar, 'Creating/shipping bundle')
                execute(fab.rm_rf, '~/{}-{}.tbz2'.format(project, venue), roles=[comp])
                execute(fab.ship_code, '~/verdi/ops', '~/{}-{}.tbz2'.format(project, venue), encrypt, roles=[comp])
                proj_bar.update()
            bar.update()
        set_bar_desc(bar, 'Finished shipping')
        print("")


def ship(encrypt, debug=False):
    """Update components."""

    # get user's SDS conf settings
    conf = SettingsConf()

    if debug: ship_verdi(conf, encrypt)
    else:
        with hide('everything'):
            ship_verdi(conf, encrypt)
