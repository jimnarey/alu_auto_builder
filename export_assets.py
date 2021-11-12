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
    if marquee_path:
        img = Image.open(marquee_path)
        img = img.resize((128, 32))
        save_path = os.path.join(asset_paths['bitpixel'], os.path.basename(marquee_path))
        img.save(save_path)


def add_to_playlists(game_data, playlists):
    genres = [genre.strip() for genre in game_data['genre'].split(',')]
    for genre in genres:
        if genre:
            if genre not in playlists['genres']:
                playlists['genres'][genre] = []
            playlists['genres'][genre].append(game_data['name'])
    publisher = game_data['publisher']
    if publisher:
        if publisher not in playlists['publishers']:
            playlists['publishers'][publisher] = []
        playlists['publishers'][publisher].append(game_data['name'])
    num_players = game_data['players']
    if num_players:
        players_key = '{0} Player'.format(num_players)
        if players_key not in playlists['players']:
            playlists['players'][players_key] = []
        playlists['players'][players_key].append(game_data['name'])
    playlists['all'].append(game_data['name'])


def exp_cox_assets(game_data, asset_paths):
    if game_data['boxart_path']:
        common_utils.copyfile(game_data['boxart_path'], asset_paths['covers'])
    if game_data['marquee_path']:
        common_utils.copyfile(game_data['marquee_path'], asset_paths['marquees'])
    if game_data['logo_path']:
        common_utils.copyfile(game_data['logo_path'], asset_paths['logos'])
    if game_data['video_path']:
        common_utils.copyfile(game_data['video_path'], asset_paths['videos'])


def export(gamelist, asset_paths, export_cox_assets, export_bitpixel_marquees):
    playlists = {'genres': {}, 'publishers': {}, 'players': {}, 'all': []}
    for game_entry in gamelist:
        print(game_entry)
        game_data = common_utils.parse_game_entry(game_entry)
        print(game_data)
        if export_bitpixel_marquees:
            exp_bitpixel_marquee(game_data, asset_paths)
        if export_cox_assets:
            exp_cox_assets(game_data, asset_paths)
            add_to_playlists(game_data, playlists)
    print(playlists)


def main(input_path, output_dir, export_cox_assets=False, export_bitpixel_marquees=False):
    if not check_export_required(export_cox_assets, export_bitpixel_marquees):
        return False
    if not validate_args(input_path, output_dir):
        return False
    gamelist = common_utils.read_gamelist(input_path)
    asset_paths = get_asset_paths(output_dir)
    make_asset_dirs(asset_paths, export_cox_assets, export_bitpixel_marquees)
    export(gamelist, asset_paths, export_cox_assets, export_bitpixel_marquees)

# No 'if name == __main__' as this can't be run as a distinct operation