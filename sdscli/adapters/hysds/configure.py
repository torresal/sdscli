"""
Configuration for HySDS cluster.
"""
from __future__ import absolute_import
from __future__ import print_function

import os, yaml, traceback

from sdscli.log_utils import logger
from sdscli.conf_utils import SettingsConf


def configure():
    """Configure SDS config file for HySDS."""

    logger.debug("Got here for HySDS")
    conf = SettingsConf()
    logger.debug(conf)
