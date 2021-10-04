#!/usr/bin/env python3

import os

import build_from_recipes
import build_uce_tool
import create_gamelist
import build_recipes
import edit_uce
import extract_save_part
import replace_save_part
from shared import common_utils


def scrape_and_build_uces(args):
    temp_dir = common_utils.create_temp_dir(__name__)
    recipes_temp_dir = os.path.join(temp_dir, 'recipes')
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=temp_dir)
    build_recipes.main(os.path.join(temp_dir, 'gamelist.xml'), args['core_path'], bios_dir=args['bios_dir'],
                       output_dir=recipes_temp_dir)
    build_from_recipes.main(recipes_temp_dir, output_dir=args['output_dir'])
    common_utils.cleanup_temp_dir(__name__)


def scrape_and_make_recipes(args):
    temp_dir = common_utils.create_temp_dir(__name__)
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=temp_dir)
    build_recipes.main(os.path.join(temp_dir, 'gamelist.xml'), args['core_path'], bios_dir=args['bios_dir'],
                       output_dir=args['output_dir'])
    common_utils.cleanup_temp_dir(__name__)


def scrape_and_make_gamelist(args):
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=args['output_dir'])


def build_uces_from_gamelist(args):
    temp_dir = common_utils.create_temp_dir(__name__)
    build_recipes.main(args['input_path'], args['core_path'], bios_dir=args['bios_dir'], output_dir=temp_dir)
    build_from_recipes.main(temp_dir, output_dir=args['output_dir'])
    common_utils.cleanup_temp_dir(__name__)


def build_recipes_from_gamelist(args):
    build_recipes.main(args['input_path'], args['core_path'], bios_dir=args['bios_dir'], output_dir=args['output_dir'])


def build_uces_from_recipes(args):
    build_from_recipes.main(args['input_dir'], output_dir=args['output_dir'])


def build_single_uce_from_recipe(args):
    build_uce_tool.main(args['input_dir'], output_path=args['output_path'])


def edit_uce_save_partition(args):
    edit_uce.main(args['input_path'], backup_uce=args['backup_uce'], mount_method=args['mount_method'],
                  file_manager=args['file_manager'])


def extract_uce_save_partition(args):
    extract_save_part.main(args['input_path'], output_path=args['output_path'])


def replace_uce_save_partition(args):
    replace_save_part.main(args['input_path'], args['part_path'], backup_uce=args['backup_uce'])
