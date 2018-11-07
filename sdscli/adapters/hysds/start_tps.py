"""
Start TPS components for HySDS.
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


def start_mozart(conf, comp='mozart'):
    """"Start TPS on mozart component."""

    # progress bar
    with tqdm(total=3) as bar:

        # start rabbitmq
        set_bar_desc(bar, 'Starting rabbitmq-server')
        execute(fab.systemctl, 'start', 'rabbitmq-server', roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Started rabbitmq-server')

        # start redis
        set_bar_desc(bar, 'Starting redis')
        execute(fab.systemctl, 'start', 'redis', roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Started redis')

        # start elasticsearch
        set_bar_desc(bar, 'Starting elasticsearch')
        execute(fab.systemctl, 'start', 'elasticsearch', roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Started elasticsearch')


def start_metrics(conf, comp='metrics'):
    """"Start TPS on metrics component."""

    # progress bar
    with tqdm(total=2) as bar:

        # start redis
        set_bar_desc(bar, 'Starting redis')
        execute(fab.systemctl, 'start', 'redis', roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Started redis')

        # start elasticsearch
        set_bar_desc(bar, 'Starting elasticsearch')
        execute(fab.systemctl, 'start', 'elasticsearch', roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Started elasticsearch')


def start_grq(conf, comp='grq'):
    """"Start TPS on grq component."""

    # progress bar
    with tqdm(total=1) as bar:

        # start elasticsearch
        set_bar_desc(bar, 'Starting elasticsearch')
        execute(fab.systemctl, 'start', 'elasticsearch', roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Started elasticsearch')


def start_ci(conf, comp='ci'):
    """"Start TPS on CI component."""

    # progress bar
    with tqdm(total=1) as bar:

        # start jenkins
        set_bar_desc(bar, 'Starting jenkins')
        execute(fab.systemctl, 'start', 'jenkins', roles=[comp])
        bar.update()
        set_bar_desc(bar, 'Started jenkins')


def start_comp(comp, conf):
    """Start component."""

    # if all, create progress bar
    if comp == 'all':
    
        # progress bar
        with tqdm(total=4) as bar:
            set_bar_desc(bar, "Starting TPS on grq")
            start_grq(conf)
            bar.update()
            set_bar_desc(bar, "Starting TPS on mozart")
            start_mozart(conf)
            bar.update()
            set_bar_desc(bar, "Starting TPS on metrics")
            start_metrics(conf)
            bar.update()
            set_bar_desc(bar, "Starting TPS on ci")
            start_ci(conf)
            bar.update()
            set_bar_desc(bar, "Started TPS on all")
            print("")
    else:
        if comp == 'grq': start_grq(conf)
        if comp == 'mozart': start_mozart(conf)
        if comp == 'metrics': start_metrics(conf)
        if comp == 'ci': start_ci(conf)


def start(comp, debug=False, force=False):
    """Start TPS components."""

    # prompt user
    if not force:
        cont = prompt(get_prompt_tokens=lambda x: [(Token.Alert, 
                      "Starting TPS on component[s]: {}. Continue [y/n]: ".format(comp)), (Token, " ")],
                      validator=YesNoValidator(), style=prompt_style) == 'y'
        if not cont: return 0

    # get user's SDS conf settings
    conf = SettingsConf()

    logger.debug("Starting %s" % comp)

    if debug: start_comp(comp, conf)
    else:
        with hide('everything'):
            start_comp(comp, conf)
