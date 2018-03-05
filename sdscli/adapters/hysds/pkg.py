"""
SDS package management functions.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import os, json, yaml, requests, tarfile, shutil, traceback
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
    mozart_es_url = "http://{}:9200".format(conf.get('MOZART_ES_PVT_IP'))
    grq_es_url = "http://{}:9200".format(conf.get('GRQ_ES_PVT_IP'))
    hits = run_query(mozart_es_url, "containers", {
        "query": {
            "term": { "_id": cont_id }
        }
    })
    if len(hits) == 0:
        logger.error("SDS package id {} not found.".format(cont_id))
        return 1
    cont_info = hits[0]['_source']
    logger.debug("cont_info: {}".format(json.dumps(cont_info, indent=2)))

    # set export directory
    outdir = normpath(args.outdir)
    export_name = "{}.sdspkg".format(cont_id)
    export_dir = os.path.join(outdir, export_name)
    logger.debug("export_dir: {}".format(export_dir))

    # if directory exists, stop
    if os.path.exists(export_dir):
        logger.error("SDS package export directory {} exists. Not continuing.".format(export_dir))
        return 1

    # create export directory
    validate_dir(export_dir)

    # download container
    get(cont_info['url'], export_dir)
    cont_info['url'] = os.path.basename(cont_info['url'])

    # query job specs
    job_specs = [i['_source'] for i in run_query(mozart_es_url, "job_specs", {
        "query": {
            "term": { "container.raw": cont_id }
        }
    })]
    logger.debug("job_specs: {}".format(json.dumps(job_specs, indent=2)))

    # pull hysds_ios for each job_spec and download any dependency images
    hysds_ios = []
    dep_images = {}
    for job_spec in job_specs:
        # download dependency images
        for d in job_spec.get('dependency_images', []):
            if d['container_image_name'] in dep_images:
                d['container_image_url'] = dep_images[d['container_image_name']]
            else:
                # download container
                get(d['container_image_url'], export_dir)
                d['container_image_url'] = os.path.basename(d['container_image_url'])
                dep_images[d['container_image_name']] = d['container_image_url']


        # collect hysds_ios from mozart
        mozart_hysds_ios = [i['_source'] for i in run_query(mozart_es_url, "hysds_ios", {
            "query": {
                "term": { "job-specification.raw": job_spec['id'] }
            }
        })]
        logger.debug("Found {} hysds_ios on mozart for {}.".format(len(mozart_hysds_ios), job_spec['id']))
        hysds_ios.extend(mozart_hysds_ios)
        
        # collect hysds_ios from mozart
        grq_hysds_ios = [i['_source'] for i in run_query(grq_es_url, "hysds_ios", {
            "query": {
                "term": { "job-specification.raw": job_spec['id'] }
            }
        })]
        logger.debug("Found {} hysds_ios on grq for {}.".format(len(grq_hysds_ios), job_spec['id']))
        hysds_ios.extend(grq_hysds_ios)
    logger.debug("Found {} hysds_ios total.".format(len(hysds_ios)))

    # clean out allowed accounts
    for hysds_io in hysds_ios:
        if 'allowed_accounts' in hysds_io:
            del hysds_io['allowed_accounts']

    # dump manifest JSON
    manifest = {
        "containers" : cont_info,
        "job_specs": job_specs,
        "hysds_ios": hysds_ios,
    }
    manifest_file = os.path.join(export_dir, 'manifest.json')
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    # tar up hysds package
    tar_file = os.path.join(outdir, "{}.tar".format(export_name))
    with tarfile.open(tar_file, "w") as tar:
        tar.add(export_dir, arcname=os.path.relpath(export_dir, outdir))

    # remove package dir
    shutil.rmtree(export_dir)
