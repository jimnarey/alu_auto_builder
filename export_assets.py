#!/usr/bin env python3

import os
import logging

from PIL import Image

from shared import common_utils

logger = logging.getLogger(__name__)


def get_asset_paths(output_dir):
    asset_dir = os.path.join(output_dir, 'assets')
    cox_dir = os.path.join(asset_dir, 'cox')
    return {
        'assets': asset_dir,
        'bitpixel': os.path.join(asset_dir, 'bitpixel'),
        'cox': cox_dir,
        'covers': os.path.join(cox_dir, 'covers'),
        'marquees': os.path.join(cox_dir, 'marquees'),
        'logos': os.path.join(cox_dir, 'logos'),
        'videos': os.path.join(cox_dir, 'videos')

    }


def validate_args(input_path, output_dir):
    logger.info('Validating arguments for export_assets')
    valid = True
    if not common_utils.validate_required_path(input_path, 'Specified gamelist'):
        valid = False
    if not common_utils.validate_existing_dir(output_dir, 'Output dir'):
        valid = False
    return valid


def check_export_required(*args):
    for job in args:
        if job:
            return True
    return False


def make_asset_dirs(asset_paths, export_cox_assets, export_bitpixel_marquees):
    common_utils.make_dir(asset_paths['assets'])
    if export_cox_assets:
        common_utils.make_dir(asset_paths['cox'])
        for subdir in ('covers', 'logos', 'marquees', 'videos'):
            common_utils.make_dir(asset_paths[subdir])
    if export_bitpixel_marquees:
        common_utils.make_dir(asset_paths['bitpixel'])


def exp_bitpixel_marquee(game_data, asset_paths):
    marquee_path = game_data['marquee_path']
    img = Image.open(marquee_path)
    img = img.resize((128, 32))
    save_path = os.path.join(asset_paths['bitpixel'], os.path.basename(marquee_path))
    img.save(save_path)


def exp_cox_assets(game_data, asset_paths):
    common_utils.copyfile(game_data['boxart_path'], asset_paths['covers'])
    common_utils.copyfile(game_data['marquee_path'], asset_paths['marquees'])
    common_utils.copyfile(game_data['logo_path'], asset_paths['logos'])
    common_utils.copyfile(game_data['video_path'], asset_paths['videos'])


def main(input_path, output_dir, export_cox_assets=False, export_bitpixel_marquees=False):
    if not check_export_required(export_cox_assets, export_bitpixel_marquees):
        return False
    if not validate_args(input_path, output_dir):
        return False
    gamelist = common_utils.read_gamelist(input_path)
    asset_paths = get_asset_paths(output_dir)
    make_asset_dirs(asset_paths, export_cox_assets, export_bitpixel_marquees)
    for game_entry in gamelist:
        game_data = common_utils.parse_game_entry(game_entry)
        if export_bitpixel_marquees:
            exp_bitpixel_marquee(game_data, asset_paths)
        if export_cox_assets:
            exp_cox_assets(game_data, asset_paths)


# No 'if name == __main__' as this can't be run as a distinct operation
