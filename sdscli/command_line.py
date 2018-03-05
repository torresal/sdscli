"""
SDSKit command line interface.
"""
from __future__ import absolute_import
from __future__ import print_function

import os, sys, importlib, json, yaml, traceback, argparse, logging
from importlib import import_module

import sdscli
from sdscli.log_utils import logger


def get_adapter_module(sds_type, mod_name):
    """Import adapter module."""

    try:
        return import_module('sdscli.adapters.%s.%s' % (sds_type, mod_name))
    except ImportError:
        logger.error('Failed to import adapter module "%s" for SDS type "%s".' % (mod_name, sds_type))
        logger.error('Not implemented yet. Mahalo for trying. ;)')
        sys.exit(1)


def get_adapter_func(sds_type, mod_name, func_name):
    """Import adapter function."""

    adapter_mod = get_adapter_module(sds_type, mod_name)
    logger.debug("adapter_mod: %s" % adapter_mod)
    try:
        return getattr(adapter_mod, func_name)
    except AttributeError:
        logger.error('Failed to get function "%s" from adapter module "%s".' % (func_name, adapter_mod))
        logger.error('Not implemented yet. Mahalo for trying. ;)')
        sys.exit(1)


def configure(args):
    """Configure SDS config file."""

    logger.debug("got to configure(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'configure', 'configure') 
    logger.debug("func: %s" % func)
    func()


def update(args):
    """Update SDS components."""

    logger.debug("got to update(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'update', 'update') 
    logger.debug("func: %s" % func)
    func(args.component, args.debug)


def start(args):
    """Start SDS components."""

    logger.debug("got to start(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'start', 'start') 
    logger.debug("func: %s" % func)
    func(args.component, args.debug)


def stop(args):
    """Stop SDS components."""

    logger.debug("got to stop(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'stop', 'stop') 
    logger.debug("func: %s" % func)
    func(args.component, args.debug)


def reset(args):
    """Reset SDS components."""

    logger.debug("got to reset(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'reset', 'reset') 
    logger.debug("func: %s" % func)
    func(args.component, args.debug)


def status(args):
    """SDS component status."""

    logger.debug("got to status(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'status', 'status') 
    logger.debug("func: %s" % func)
    func(args.component, args.debug)


def ci(args):
    """Continuous integration functions."""

    logger.debug("got to ci(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'ci', args.subparser)
    logger.debug("func: %s" % func)
    func(args)


def pkg(args):
    """SDS package managment functions."""

    logger.debug("got to pkg(): %s" % args)
    sds_type = args.type
    logger.debug("sds_type: %s" % sds_type)
    func = get_adapter_func(sds_type, 'pkg', 'import_pkg' if args.subparser == 'import' else args.subparser)
    logger.debug("func: %s" % func)
    func(args)


def job_list(args):
    """Configure SDS config file."""

    logger.debug("got to job_list(): %s" % args)


def dispatch(args):
    """Dispatch to appropriate function."""

    # turn on debugging
    if args.debug: logger.setLevel(logging.DEBUG)

    logger.debug("args: %s" % args)

    if args.func:
        return args.func(args)
    else:
        logger.error("No func specified for args %s" % args)
        return 1


def main():
    """Process command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', '-d', action='store_true', help="turn on debugging")
    subparsers = parser.add_subparsers(help='Functions')

    # parser for configure
    parser_configure = subparsers.add_parser('configure', help="configure SDS config file")
    parser_configure.add_argument('type', default='hysds', const='hysds', nargs='?',
                                  choices=['hysds', 'sdskit'])
    parser_configure.set_defaults(func=configure)

    # parser for update
    parser_update = subparsers.add_parser('update', help="update SDS components")
    parser_update.add_argument('--type', '-t', default='hysds', const='hysds', nargs='?',
                                  choices=['hysds', 'sdskit'])
    parser_update.add_argument('component', choices=['mozart', 'grq', 'metrics', 
                               'factotum', 'ci', 'verdi', 'all'])
    parser_update.set_defaults(func=update)

    # parser for start
    parser_start = subparsers.add_parser('start', help="start SDS components")
    parser_start.add_argument('--type', '-t', default='hysds', const='hysds', nargs='?',
                              choices=['hysds', 'sdskit'])
    parser_start.add_argument('component', choices=['mozart', 'grq', 'metrics', 
                              'factotum', 'all'])
    parser_start.set_defaults(func=start)

    # parser for stop
    parser_stop = subparsers.add_parser('stop', help="stop SDS components")
    parser_stop.add_argument('--type', '-t', default='hysds', const='hysds', nargs='?',
                             choices=['hysds', 'sdskit'])
    parser_stop.add_argument('component', choices=['mozart', 'grq', 'metrics', 
                             'factotum', 'all'])
    parser_stop.set_defaults(func=stop)

    # parser for reset
    parser_reset = subparsers.add_parser('reset', help="reset SDS components")
    parser_reset.add_argument('--type', '-t', default='hysds', const='hysds', nargs='?',
                              choices=['hysds', 'sdskit'])
    parser_reset.add_argument('component', choices=['mozart', 'grq', 'metrics', 
                              'factotum', 'all'])
    parser_reset.set_defaults(func=reset)

    # parser for status
    parser_status = subparsers.add_parser('status', help="status of SDS components")
    parser_status.add_argument('--type', '-t', default='hysds', const='hysds', nargs='?',
                               choices=['hysds', 'sdskit'])
    parser_status.add_argument('component', choices=['mozart', 'grq', 'metrics', 
                               'factotum', 'ci', 'verdi', 'all'])
    parser_status.set_defaults(func=status)

    # parser for ci
    parser_ci = subparsers.add_parser('ci', help="configure continuous integration for SDS cluster")
    parser_ci.add_argument('--type', '-t', default='hysds', const='hysds', nargs='?',
                               choices=['hysds', 'sdskit'])
    parser_ci_subparsers = parser_ci.add_subparsers(dest='subparser', help='Continuous integration functions')
    parser_ci_add_job = parser_ci_subparsers.add_parser('add_job', help="add Jenkins job")
    parser_ci_add_job.add_argument('repo', help='git repository url')
    parser_ci_add_job.add_argument('storage', choices=['s3', 's3s', 'gs', 'dav', 'davs'],
                                   help='image storage type')
    parser_ci_add_job.add_argument('uid', help="image's ops UID")
    parser_ci_add_job.add_argument('gid', help="image's ops GID")
    parser_ci_add_job.add_argument('--branch', '-b', default=None,
                                   help="register git branch instead of release")
    parser_ci_add_job.add_argument('--token', '-k', action='store_true', help="use configured OAuth token")
    #parser_ci_rm_job = parser_ci_subparsers.add_parser('remove_job', help="remove Jenkins job")
    #parser_ci_rm_job.add_argument('name', help='jenkins job name')
    parser_ci.set_defaults(func=ci)

    # parser for pkg
    parser_pkg = subparsers.add_parser('pkg', help="SDS package management")
    parser_pkg.add_argument('--type', '-t', default='hysds', const='hysds', nargs='?',
                               choices=['hysds', 'sdskit'])
    parser_pkg_subparsers = parser_pkg.add_subparsers(dest='subparser', help='SDS package management functions')
    parser_pkg_ls = parser_pkg_subparsers.add_parser('ls', help="list SDS package ids")
    parser_pkg_export = parser_pkg_subparsers.add_parser('export', help="export SDS package")
    parser_pkg_export.add_argument('id', help='SDS package id to export')
    parser_pkg_export.add_argument('--outdir', '-o', default=".",
                                   help="root output directory of SDS package")
    parser_pkg_import = parser_pkg_subparsers.add_parser('import', help="import SDS package")
    parser_pkg_import.add_argument('file', help='SDS package to import')
    parser_pkg.set_defaults(func=pkg)

    # parser for jobs
    parser_job = subparsers.add_parser('job', help="SDS job subcommand")
    job_subparsers = parser_job.add_subparsers(help="Job functions.")

    # parser for jobs listing
    parser_job_list = job_subparsers.add_parser('list', help="list SDS job counts")
    parser_job_list.add_argument("status", help="job status to list counts for")
    parser_job_list.set_defaults(func=job_list)

    # dispatch
    args = parser.parse_args()
    return dispatch(args)


if __name__ == "__main__":
    sys.exit(main())
