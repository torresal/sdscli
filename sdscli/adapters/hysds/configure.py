"""
Configuration for HySDS cluster.
"""
from __future__ import absolute_import
from __future__ import print_function

import os, yaml, logging, traceback

from sdscli.conf_utils import SettingsConf


log_format = "[%(asctime)s: %(levelname)s/%(name)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)


def configure():
    """Configure SDS config file for HySDS."""

    logging.info("Got here for HySDS")
    conf = SettingsConf()
    logging.info(conf)
