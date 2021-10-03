#!/usr/bin/env python3

import os
import argparse
import logging

import common_utils
import operations
import build_from_recipes
import build_uce_tool
import create_gamelist
import build_recipes
import edit_uce
import extract_save_part
import replace_save_part


def scrape_and_build_uces(args):
    pass


def scrape_and_make_recipes(args):
    pass


def scrape_and_make_gamelist(args):
    create_gamelist.run_with_args(args)


def build_uces_from_gamelist(args):
    pass


def build_recipes_from_gamelist(args):
    build_recipes.run_with_args(args)


def build_uces_from_recipes(args):
    build_from_recipes.run_with_args(args)


def build_single_uce_from_recipe(args):
    build_uce_tool.run_with_args(args)


def edit_uce_save_partition(args):
    edit_uce.run_with_args(args)


def extract_uce_save_partition(args):
    extract_save_part.run_with_args(args)


def replace_uce_save_partition(args):
    replace_save_part.run_with_args(args)


subcommands = {
    'scrape_and_build_uces': scrape_and_build_uces,
    'scrape_and_make_recipes': scrape_and_make_recipes,
    'scrape_and_make_gamelist': scrape_and_make_gamelist,
    'build_uces_from_gamelist': build_uces_from_gamelist,
    'build_recipes_from_gamelist': build_recipes_from_gamelist,
    'build_uces_from_recipes': build_uces_from_recipes,
    'build_single_uce_from_recipe': build_single_uce_from_recipe,
    'edit_uce_save_partition': edit_uce_save_partition,
    'extract_uce_save_partition': extract_uce_save_partition,
    'replace_uce_save_partition': replace_uce_save_partition
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    parser = argparse.ArgumentParser(prog='ALU UCE Auto Builder')
    sub_parsers = parser.add_subparsers(help='sub-command help', dest='subcommand')
    for operation in operations.operations:
        subcommand_parser = sub_parsers.add_parser(operation.replace('_', '-'))
        common_utils.add_arguments_to_parser(subcommand_parser, operations.operations[operation])
    args = vars(parser.parse_args())
    if args['subcommand']:
        subcommand = args['subcommand'].replace('-', '_')
        subcommands[args['subcommand'].replace('-', '_')](args)


