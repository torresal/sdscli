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
from sdscli.os_utils import validate_dir, normpath

from osaka.main import get


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


def export(args):
    """Export HySDS package."""

    # get user's SDS conf settings
    conf = SettingsConf()

    # container id
    cont_id = args.id

    # query for container
    es_url = "http://{}:9200".format(conf.get('MOZART_ES_PVT_IP'))
    hits = run_query(es_url, "containers", {
        "query": {
            "term": { "_id": cont_id }
        }
    })
    if len(hits) == 0:
        logger.error("SDS package id {} not found.".format(cont_id))
        return 1
    cont_info = hits[0]
    logger.debug("cont_info: {}".format(json.dumps(cont_info, indent=2)))

    # set export directory
    export_name = "{}.sdspkg".format(cont_id)
    export_dir = normpath(os.path.join(args.outdir, export_name))
    logger.debug("export_dir: {}".format(export_dir))

    # if directory exists, stop
    if os.path.exists(export_dir):
        logger.error("SDS package export directory {} exists. Not continuing.".format(export_dir))
        return 1

    # create export directory
    validate_dir(export_dir)

    # download container
    get(cont_info['_source']['url'], export_dir)

    # query job specs
    hits = run_query(es_url, "job_specs", {
        "query": {
            "term": { "container": cont_id }
        }
    })
    logger.debug("job_specs: {}".format(json.dumps(hits, indent=2)))
