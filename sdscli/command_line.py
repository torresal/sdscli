#!/usr/bin/env python
"""
SDSKit command line interface.
"""

import os, json, yaml, logging, traceback, argparse

import sdscli


log_format = "[%(asctime)s: %(levelname)s/%(name)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


def configure(args):
    """Configure HySDS config file."""

    print("got to configure(): %s" % args)


def job_list(args):
    """Configure HySDS config file."""

    print("got to job_list(): %s" % args)


def main():
    """Process command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(help='Functions')

    # parser for configure
    parser_configure = subparsers.add_parser('configure', help="configure HySDS config file")
    parser_configure.set_defaults(func=configure)


    # parser for jobs
    parser_job = subparsers.add_parser('job', help="HySDS job subcommand")
    job_subparsers = parser_job.add_subparsers(help="Job functions.")

    # parser for jobs listing
    parser_job_list = job_subparsers.add_parser('list', help="List HySDS job counts")
    parser_job_list.add_argument("status", help="Job status to list counts for")
    parser_job_list.set_defaults(func=job_list)

    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        print("No func specified for args %s" % args)


if __name__ == "__main__":
    main()
