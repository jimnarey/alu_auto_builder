#!/usr/bin/env python3

import os
import logging

import build_from_recipes
import build_uce_tool
import create_gamelist
import build_recipes
import edit_uce
import extract_save_part
import replace_save_part
from shared import common_utils, info_messages


def scrape_and_build_uces(args):
    logging.info(info_messages.start_operation("'scrape to uces'"))
    temp_dir = common_utils.create_temp_dir(__name__)
    recipes_temp_dir = os.path.join(temp_dir, 'recipes')
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=temp_dir)
    build_recipes.main(os.path.join(temp_dir, 'gamelist.xml'), args['core_path'], bios_dir=args['bios_dir'],
                       output_dir=recipes_temp_dir)
    output_dir = args['output_dir'] if args['output_dir'] else os.path.join(args['input_dir'], 'UCE')
    build_from_recipes.main(recipes_temp_dir, output_dir=output_dir)
    common_utils.cleanup_temp_dir(__name__)
    logging.info(info_messages.end_operation("'scrape to uces'"))


def scrape_and_make_recipes(args):
    logging.info(info_messages.start_operation("'scrape to recipes'"))
    temp_dir = common_utils.create_temp_dir(__name__)
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=temp_dir)
    output_dir = args['output_dir'] if args['output_dir'] else os.path.join(args['input_dir'], 'recipes')
    build_recipes.main(os.path.join(temp_dir, 'gamelist.xml'), args['core_path'], bios_dir=args['bios_dir'],
                       output_dir=output_dir)
    common_utils.cleanup_temp_dir(__name__)
    logging.info(info_messages.end_operation("'scrape to recipes'"))


def scrape_and_make_gamelist(args):
    logging.info(info_messages.start_operation("'scrape to gamelist'"))
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=args['output_dir'])
    logging.info(info_messages.end_operation("'scrape to gamelist'"))


def build_uces_from_gamelist(args):
    logging.info(info_messages.start_operation("'gamelist to uces'"))
    temp_dir = common_utils.create_temp_dir(__name__)
    build_recipes.main(args['input_path'], args['core_path'], bios_dir=args['bios_dir'], output_dir=temp_dir)
    output_dir = args['output_dir'] if args['output_dir'] else os.path.join(os.path.dirname(args['input_path']), 'UCE')
    build_from_recipes.main(temp_dir, output_dir=output_dir)
    common_utils.cleanup_temp_dir(__name__)
    logging.info(info_messages.end_operation("'gamelist to uces'"))


def build_recipes_from_gamelist(args):
    logging.info(info_messages.start_operation("'gamelist to recipes'"))
    build_recipes.main(args['input_path'], args['core_path'], bios_dir=args['bios_dir'], output_dir=args['output_dir'])
    logging.info(info_messages.end_operation("'gamelist to recipes'"))


def build_uces_from_recipes(args):
    logging.info(info_messages.start_operation("'recipes to uces'"))
    build_from_recipes.main(args['input_dir'], output_dir=args['output_dir'])
    logging.info(info_messages.end_operation("'recipes to uces'"))


def build_single_uce_from_recipe(args):
    logging.info(info_messages.start_operation("'recipe to uce'"))
    build_uce_tool.main(args['input_dir'], output_path=args['output_path'])
    logging.info(info_messages.end_operation("'recipe to uce'"))


def edit_uce_save_partition(args):
    logging.info(info_messages.start_operation("'edit save partition'"))
    edit_uce.main(args['input_path'], backup_uce=args['backup_uce'], mount_method=args['mount_method'],
                  file_manager=args['file_manager'])
    logging.info(info_messages.end_operation("'edit save partition'"))


def extract_uce_save_partition(args):
    logging.info(info_messages.start_operation("'extract save partition'"))
    extract_save_part.main(args['input_path'], output_path=args['output_path'])
    logging.info(info_messages.end_operation("'extract save partition'"))


def replace_uce_save_partition(args):
    logging.info(info_messages.start_operation("'replace save partition'"))
    replace_save_part.main(args['input_path'], args['part_path'], backup_uce=args['backup_uce'])
    logging.info(info_messages.end_operation("'replace save partition'"))
