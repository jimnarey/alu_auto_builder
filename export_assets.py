#!/usr/bin env python3

import os
import logging

from PIL import Image, ImageDraw, ImageFont

from shared import common_utils

logger = logging.getLogger(__name__)


def get_playlist_art_spec():
    return {
        'font': os.path.join(common_utils.get_app_root(), 'data', 'RobotoMono-Bold.ttf'),
        'text_color': '#FFFFFF',
        'margin': 10
    }


def get_asset_paths(output_dir):
    asset_dir = os.path.join(output_dir, 'assets')
    cox_dir = os.path.join(asset_dir, 'cox')
    return {
        'assets': asset_dir,
        'bitpixel': os.path.join(asset_dir, 'bitpixel'),
        'cox': cox_dir,
        'covers': os.path.join(cox_dir, 'cover'),
        'marquees': os.path.join(cox_dir, 'marquee'),
        'logos': os.path.join(cox_dir, 'logo'),
        'videos': os.path.join(cox_dir, 'video'),
        'playlists': os.path.join(cox_dir, 'playlists'),
        'playlist_art': os.path.join(cox_dir, 'playlist_art')

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
    uce_basename = os.path.basename(game_data['rom_path'])
    for genre in genres:
        if genre:
            if genre not in playlists['genres']:
                playlists['genres'][genre] = []
            playlists['genres'][genre].append(uce_basename)
    publisher = game_data['publisher']
    if publisher:
        if publisher not in playlists['publishers']:
            playlists['publishers'][publisher] = []
        playlists['publishers'][publisher].append(uce_basename)
    num_players = game_data['players']
    if num_players:
        players_key = '{0} Player'.format(num_players)
        if players_key not in playlists['players']:
            playlists['players'][players_key] = []
        playlists['players'][players_key].append(uce_basename)
    playlists['all']['All'].append(uce_basename)


def exp_cox_assets(game_data, asset_paths):
    if game_data['boxart_path']:
        common_utils.copyfile(game_data['boxart_path'], asset_paths['covers'])
    if game_data['marquee_path']:
        common_utils.copyfile(game_data['marquee_path'], asset_paths['marquees'])
    if game_data['logo_path']:
        common_utils.copyfile(game_data['logo_path'], asset_paths['logos'])
    if game_data['video_path']:
        common_utils.copyfile(game_data['video_path'], asset_paths['videos'])


def save_playlist_art(playlist_name, playlist_file_name, playlist_art_spec, asset_paths):
    font = ImageFont.truetype(playlist_art_spec['font'], size=36)
    text_width, text_height = font.getsize(playlist_name)
    img = Image.new('RGBA',
                    (text_width + (2 * playlist_art_spec['margin']), text_height + (2 * playlist_art_spec['margin'])),
                    (0, 0, 0, 0))
    canvas = ImageDraw.Draw(img)
    canvas.text((playlist_art_spec['margin'], playlist_art_spec['margin']), playlist_name, font=font, fill='#FFFFFF')
    img.save(os.path.join(asset_paths['playlist_art'], playlist_file_name), 'PNG')


def save_playlists(playlists, asset_paths):
    common_utils.make_dir(asset_paths['playlists'])
    common_utils.make_dir(asset_paths['playlist_art'])
    playist_art_spec = get_playlist_art_spec()
    for index, playlist_cat in enumerate(playlists):
        for playlist in playlists[playlist_cat]:
            playlist_file_name = common_utils.clean_file_name(playlist)
            common_utils.write_file(os.path.join(asset_paths['playlists'], '{0} {1}'.format(index, playlist_file_name)),
                                    '\n'.join(playlists[playlist_cat][playlist]), 'w')
            save_playlist_art(playlist, playlist_file_name, playist_art_spec, asset_paths)


def export(gamelist, asset_paths, export_cox_assets, export_bitpixel_marquees):
    playlists = {'genres': {}, 'publishers': {}, 'players': {}, 'all': {'All': []}}
    for game_entry in gamelist:
        # print(game_entry)
        game_data = common_utils.parse_game_entry(game_entry)
        # print(game_data)
        if export_bitpixel_marquees:
            exp_bitpixel_marquee(game_data, asset_paths)
        if export_cox_assets:
            exp_cox_assets(game_data, asset_paths)
            add_to_playlists(game_data, playlists)
    save_playlists(playlists, asset_paths)
    # breakpoint()


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
