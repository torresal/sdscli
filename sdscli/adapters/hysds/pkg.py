"""
SDS package management functions.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import os, json, yaml, requests, traceback
from fabric.api import execute, hide

from prompt_toolkit.shortcuts import prompt, print_tokens
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from pygments.token import Token

from sdscli.log_utils import logger
from sdscli.conf_utils import get_user_files_path, SettingsConf
from sdscli.query_utils import run_query


def ls(args):
    """List HySDS packages."""

    # get user's SDS conf settings
    conf = SettingsConf()

    # query for containers
    es_url = "http://{}:9200".format(conf.get('MOZART_ES_PVT_IP'))
    hits = run_query(es_url, "containers", {
        "query": {
            "match_all": {}
        }
    })

    # list
    for hit in hits:
        logger.debug(json.dumps(hit, indent=2))
        print(hit['_id'])
    return
