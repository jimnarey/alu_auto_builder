#!/usr/bin/env python3
import os
import re

import requests
# import pprint
from pathlib import Path
from xml.etree import ElementTree as ET
import logging

from fuzzywuzzy import process

from shared import configs, common_utils

logger = logging.getLogger(__name__)

BASE_TREE_URL = 'https://api.github.com/repos/thebezelproject/{0}/git/trees/master?recursive=1'

BEZEL_ROOT_DIR = os.path.join(str(Path.home()), '.bezels')

# BRACKET_REGEX = re.compile("[\(\[].*?[\)\]]")

# SHORT_REGION_STRINGS = (
#     '(J)',
#     '(U)',
#     '(E)',
#     '(JU)',
#     '(JE)',
#     '(UE)',
# )
#
# FULL_REGION_STRINGS = (
#     '(Japan)',
#     '(Europe)',
#     '(USA)',
#     '(World)'
#
#
# )

def init_local_dirs():
    if not os.path.isdir(BEZEL_ROOT_DIR):
        common_utils.make_dir(BEZEL_ROOT_DIR)
    for key in configs.PLATFORMS:
        subdir = os.path.join(BEZEL_ROOT_DIR, configs.PLATFORMS[key]['bezel_repo'])
        if not os.path.isdir(subdir):
            common_utils.make_dir(subdir)


def get_raw_url(repo, path):
    return 'https://raw.githubusercontent.com/thebezelproject/{0}/master/{1}'.format(repo, path).replace(' ', '%20')


def clean_compare_name(name):
    print(name)
    return ' '.join(re.sub("[\(\[].*?[\)\]]", "", name).lower().split())


def get_basename_no_ext(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_game_compare_name(game_data, platform_data, compare_filename):

    if compare_filename or platform_data['bezel_repo'] == 'bezelproject-MAME' or game_data['name'] is None:
        basename_no_ext = get_basename_no_ext(game_data['rom_path'])
        return clean_compare_name(basename_no_ext)
    return clean_compare_name(game_data['name'])


def get_bezel_data(repo, github_tree_item):
    path = github_tree_item['path']
    game_name = get_basename_no_ext(path)
    local_path = os.path.join(BEZEL_ROOT_DIR, repo, '{0}.png'.format(game_name))
    compare_name = clean_compare_name(game_name)
    return compare_name, {
        'game_name': game_name,
        'url': get_raw_url(repo, path),
        'local_path': local_path
    }


def get_default_data(platform_data):
    default_url = get_raw_url(platform_data['bezel_repo'], platform_data['default_bezel'])
    default_local_path = os.path.join(BEZEL_ROOT_DIR, platform_data['bezel_repo'], os.path.basename(platform_data['default_bezel']))
    return {'url': default_url, 'local_path': default_local_path}


def download_file(url, save_path):
    try:
        data = requests.get(url)
        if data.status_code != 200:
            logger.error('Server returned status code {0} for {1}'.format(url, data.status_code))
        common_utils.write_file(save_path, data.content, 'wb')
        logger.info('Downloaded remote file {0}'.format(url))
    except Exception as e:
        logger.error('Failed to download {0}: {1}'.format(url, e))
        return False
    return True


def get_available_bezels(repo):
    data = requests.get(BASE_TREE_URL.format(repo))
    tree = data.json()['tree']
    bezels = {}
    for item in tree:
        if item['type'] == 'blob':
            if os.path.splitext(item['path'])[-1] == '.png':
                key, value = get_bezel_data(repo, item)
                bezels[key] = value
    return bezels


def check_bezel_local_copy(match_name, bezels):
    if not os.path.isfile(bezels[match_name]['local_path']):
        return download_file(bezels[match_name]['url'], bezels[match_name]['local_path'])
    logger.info('Bezel file for {0} already stored locally'.format(bezels[match_name]['game_name']))
    return True


def apply_default_bezel_to_game_entry(bezel_match_element, bezel_path_element, default_bezel):
    if not os.path.isfile(default_bezel['local_path']):
        download_file(default_bezel['url'], default_bezel['local_path'])
    bezel_path_element.text = default_bezel['local_path']
    bezel_match_element.text = 'default'


def apply_matched_bezel_to_game_entry(bezel_match_element, bezel_path_element, score, best_match, bezels):
    check_bezel_local_copy(best_match, bezels)
    bezel_path_element.text = bezels[best_match]['local_path']
    bezel_match_element.text = str(score)


def is_japanese_game(game_data):
    for substring in ('(J)', 'Japan'):
        if substring in os.path.basename(game_data['rom_path']):
            return True
        if game_data['name'] is not None and substring in game_data['name']:
            return True
    return False


def add_bezel_to_game_entry(game_entry, bezel_compare_names, bezels, platform_data, min_match_score, default_bezel, compare_filename):
    bezel_match_element = ET.SubElement(game_entry, 'bezel_match')
    bezel_path_element = ET.SubElement(game_entry, 'bezel_path')
    game_data = common_utils.parse_game_entry(game_entry)
    game_compare_name = get_game_compare_name(game_data, platform_data, compare_filename)
    if is_japanese_game(game_data):
        apply_default_bezel_to_game_entry(bezel_match_element, bezel_path_element, default_bezel)
    else:
        best_match, score = process.extractOne(game_compare_name, bezel_compare_names)
        print(score, best_match)
        if score >= min_match_score:
            apply_matched_bezel_to_game_entry(bezel_match_element, bezel_path_element, score, best_match, bezels)
        else:
            apply_default_bezel_to_game_entry(bezel_match_element, bezel_path_element, default_bezel)


def add_bezels_to_gamelist(input_path, bezels, platform_data, min_match_score=85, compare_filename=False):
    gamelist_tree = common_utils.read_gamelist_tree(input_path)
    bezel_compare_names = set(bezels.keys())
    default_bezel = get_default_data(platform_data)
    for game_entry in gamelist_tree.getroot():
        add_bezel_to_game_entry(game_entry, bezel_compare_names, bezels, platform_data, min_match_score, default_bezel, compare_filename)
    gamelist_tree.write(input_path)


logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(asctime)s : %(message)s", datefmt="%H:%M:%S")

SNES_GAMELIST = '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/SNES_NO_INTRO/gamelist/gamelist.xml'

MAME_GAMELIST = '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/MAME 078/gamelist/gamelist.xml'

# add_bezels_to_gamelist(MAME_GAMELIST, bezels, repo)
# repo = configs.PLATFORMS['mame-libretro']


init_local_dirs()
platform_data = configs.PLATFORMS['snes']

bezels = get_available_bezels(platform_data['bezel_repo'])
add_bezels_to_gamelist(SNES_GAMELIST, bezels, platform_data)


# download_bezel(bezel)


# '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/SNES/gamelist/gamelist.xml'

# No 'if name == __main__' as this can't be run as a distinct operation
