#!/usr/bin/env python3

import argparse
import logging

from shared import common_utils
from operations import operations

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(name)s : %(levelname)s : %(message)s", datefmt="%H:%M:%S")
    parser = argparse.ArgumentParser(prog='ALU UCE Auto Builder')
    sub_parsers = parser.add_subparsers(dest='subcommand', title='Subcommands')
    sub_parsers.metavar = 'subcommand-name'
    for operation, spec in operations.items():
        subcommand_parser = sub_parsers.add_parser(operation.replace('_', '-'), help=spec['help'])
        common_utils.add_arguments_to_parser(subcommand_parser, operations[operation]['options'])
    args = vars(parser.parse_args())
    if args['subcommand']:
        subcommand = args['subcommand'].replace('-', '_')
        operations[args['subcommand'].replace('-', '_')]['runner'](args)
