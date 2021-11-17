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
import export_gamelist_assets
import summarise_gamelist
import add_bezels_to_gamelist
from shared import common_utils, info_messages

logger = logging.getLogger(__name__)


def scrape_and_build_uces(args):
    logger.info(info_messages.start_operation("'scrape to uces'"))
    temp_dir = common_utils.create_temp_dir(__name__)
    recipes_temp_dir = os.path.join(temp_dir, 'recipes')
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=temp_dir,
                         refresh_rom_data=args['refresh_rom_data'], scrape_videos=args['scrape_videos'])
    gamelist_path = os.path.join(temp_dir, 'gamelist.xml')
    print('Hello 1')
    add_bezels_to_gamelist.main(gamelist_path, args['platform'], min_match_score=args['min_match_score'], compare_filename=args['compare_filename'], filter_unsupported_regions=args['filter_unsupported_regions'])


    build_recipes.main(gamelist_path, args['core_path'], bios_dir=args['bios_dir'],
                       output_dir=recipes_temp_dir)
    output_dir = args['output_dir'] if args['output_dir'] else os.path.join(args['input_dir'], 'UCE')
    build_from_recipes.main(recipes_temp_dir, output_dir=output_dir)
    export_gamelist_assets.main(gamelist_path, output_dir, export_cox_assets=args['export_cox_assets'], export_bitpixel_marquees=args['export_bitpixel_marquees'])

    if args['do_summarise_gamelist']:
        summarise_gamelist.main(gamelist_path, output_dir=output_dir)
    common_utils.cleanup_temp_dir(__name__)
    logger.info(info_messages.end_operation("'scrape to uces'"))


def scrape_and_make_recipes(args):
    logger.info(info_messages.start_operation("'scrape to recipes'"))
    temp_dir = common_utils.create_temp_dir(__name__)
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=temp_dir,
                         refresh_rom_data=args['refresh_rom_data'], scrape_videos=args['scrape_videos'])
    output_dir = args['output_dir'] if args['output_dir'] else os.path.join(args['input_dir'], 'recipes')
    gamelist_path = os.path.join(temp_dir, 'gamelist.xml')

    add_bezels_to_gamelist.main(gamelist_path, args['platform'], min_match_score=args['min_match_score'], compare_filename=args['compare_filename'], filter_unsupported_regions=args['filter_unsupported_regions'])

    build_recipes.main(gamelist_path, args['core_path'], bios_dir=args['bios_dir'],
                       output_dir=output_dir)
    export_gamelist_assets.main(gamelist_path, output_dir, export_cox_assets=args['export_cox_assets'], export_bitpixel_marquees=args['export_bitpixel_marquees'])
    if args['do_summarise_gamelist']:
        summarise_gamelist.main(gamelist_path, output_dir=output_dir)
    common_utils.cleanup_temp_dir(__name__)
    logger.info(info_messages.end_operation("'scrape to recipes'"))


def scrape_and_make_gamelist(args):
    logger.info(info_messages.start_operation("'scrape to gamelist'"))
    create_gamelist.main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'],
                         user_name=args['user_name'], password=args['password'], output_dir=args['output_dir'],
                         refresh_rom_data=args['refresh_rom_data'], scrape_videos=args['scrape_videos'])
    # TODO - what if no output_dir provided?
    gamelist_path = os.path.join(args['output_dir'], 'gamelist.xml')
    add_bezels_to_gamelist.main(gamelist_path, args['platform'], min_match_score=args['min_match_score'], compare_filename=args['compare_filename'], filter_unsupported_regions=args['filter_unsupported_regions'])
    if args['do_summarise_gamelist']:
        summarise_gamelist.main(gamelist_path, output_dir=args['output_dir'])

    logger.info(info_messages.end_operation("'scrape to gamelist'"))


def build_uces_from_gamelist(args):
    logger.info(info_messages.start_operation("'gamelist to uces'"))
    temp_dir = common_utils.create_temp_dir(__name__)
    build_recipes.main(args['input_path'], args['core_path'], bios_dir=args['bios_dir'], output_dir=temp_dir)
    output_dir = args['output_dir'] if args['output_dir'] else os.path.join(os.path.dirname(args['input_path']), 'UCE')
    build_from_recipes.main(temp_dir, output_dir=output_dir)
    export_gamelist_assets.main(args['input_path'], output_dir, export_cox_assets=args['export_cox_assets'], export_bitpixel_marquees=args['export_bitpixel_marquees'])
    if args['do_summarise_gamelist']:
        summarise_gamelist.main(args['input_path'], output_dir=args['output_dir'])
    common_utils.cleanup_temp_dir(__name__)
    logger.info(info_messages.end_operation("'gamelist to uces'"))


def build_recipes_from_gamelist(args):
    logger.info(info_messages.start_operation("'gamelist to recipes'"))
    build_recipes.main(args['input_path'], args['core_path'], bios_dir=args['bios_dir'], output_dir=args['output_dir'])
    export_gamelist_assets.main(args['input_path'], output_dir=args['output_dir'], export_cox_assets=args['export_cox_assets'], export_bitpixel_marquees=args['export_bitpixel_marquees'])
    if args['do_summarise_gamelist']:
        summarise_gamelist.main(args['input_path'], output_dir=args['output_dir'])
    logger.info(info_messages.end_operation("'gamelist to recipes'"))


def export_assets_from_gamelist(args):
    export_gamelist_assets.main(args['input_path'], output_dir=args['output_dir'], export_cox_assets=args['export_cox_assets'], export_bitpixel_marquees=args['export_bitpixel_marquees'])
    if args['do_summarise_gamelist']:
        summarise_gamelist.main(args['input_path'], output_dir=args['output_dir'])
    logger.info(info_messages.end_operation("'export gamelist assets'"))


def add_bezels_to_existing_gamelist(args):
    add_bezels_to_gamelist.main(args['input_path'], args['platform'], min_match_score=args['min_match_score'], compare_filename=args['compare_filename'], filter_unsupported_regions=args['filter_unsupported_regions'])
    if args['do_summarise_gamelist']:
        summarise_gamelist.main(args['input_path'], output_dir=None)
    logger.info(info_messages.end_operation("'add bezels to gamelist'"))


def create_summary_of_gamelist(args):
    summarise_gamelist.main(args['input_path'], output_dir=args['output_dir'])
    logger.info(info_messages.end_operation("'summarise gamelist'"))


def build_uces_from_recipes(args):
    logger.info(info_messages.start_operation("'recipes to uces'"))
    build_from_recipes.main(args['input_dir'], output_dir=args['output_dir'])
    logger.info(info_messages.end_operation("'recipes to uces'"))


def build_single_uce_from_recipe(args):
    logger.info(info_messages.start_operation("'recipe to uce'"))
    build_uce_tool.main(args['input_dir'], output_path=args['output_path'])
    logger.info(info_messages.end_operation("'recipe to uce'"))


def edit_uce_save_partition(args):
    logger.info(info_messages.start_operation("'edit save partition'"))
    edit_uce.main(args['input_path'], backup_uce=args['backup_uce'], mount_method=args['mount_method'],
                  file_manager=args['file_manager'], continue_check=args['continue_check'])
    logger.info(info_messages.end_operation("'edit save partition'"))


def extract_uce_save_partition(args):
    logger.info(info_messages.start_operation("'extract save partition'"))
    extract_save_part.main(args['input_path'], output_path=args['output_path'])
    logger.info(info_messages.end_operation("'extract save partition'"))


def replace_uce_save_partition(args):
    logger.info(info_messages.start_operation("'replace save partition'"))
    replace_save_part.main(args['input_path'], args['part_path'], backup_uce=args['backup_uce'])
    logger.info(info_messages.end_operation("'replace save partition'"))
