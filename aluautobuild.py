#!/usr/bin/env python3

import os
import argparse
import logging

import common_utils
from operations import operations


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    parser = argparse.ArgumentParser(prog='ALU UCE Auto Builder')
    sub_parsers = parser.add_subparsers(help='sub-command help', dest='subcommand')
    for operation in operations:
        subcommand_parser = sub_parsers.add_parser(operation.replace('_', '-'))
        common_utils.add_arguments_to_parser(subcommand_parser, operations[operation]['options'])
    args = vars(parser.parse_args())
    if args['subcommand']:
        subcommand = args['subcommand'].replace('-', '_')
        operations[args['subcommand'].replace('-', '_')]['runner'](args)


