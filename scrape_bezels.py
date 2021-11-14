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


def init_local_dirs():
    if not os.path.isdir(BEZEL_ROOT_DIR):
        common_utils.make_dir(BEZEL_ROOT_DIR)
    for key in configs.PLATFORMS:
        subdir = os.path.join(BEZEL_ROOT_DIR, configs.PLATFORMS[key]['bezel_repo'])
        if not os.path.isdir(subdir):
            common_utils.make_dir(subdir)


def get_raw_url(repo, path):
    return 'https://raw.githubusercontent.com/thebezelproject/{0}/master/{1}'.format(repo, path).replace(' ', '%20')


def get_compare_name(name):
    return ' '.join(re.sub("[\(\[].*?[\)\]]", "", name).lower().split())


def get_basename_no_ext(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_bezel_data(repo, github_tree_item):
    path = github_tree_item['path']
    game_name = get_basename_no_ext(path)
    local_path = os.path.join(BEZEL_ROOT_DIR, repo, '{0}.png'.format(game_name))
    compare_name = get_compare_name(game_name)
    return compare_name, {
        'game_name': game_name,
        'url': get_raw_url(repo, path),
        'local_path': local_path
    }


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


def download_match(match_name, bezels):
    if not os.path.isfile(bezels[match_name]['local_path']):
        return download_file(bezels[match_name]['url'], bezels[match_name]['local_path'])
    logger.info('Bezel file for {0} already stored locally'.format(bezels[match_name]['game_name']))
    return True


def add_bezels_to_gamelist(input_path, bezels, platform_data, min_match_score=85):
    gamelist_tree = common_utils.read_gamelist_tree(input_path)
    bezel_compare_names = set(bezels.keys())
    matches = []
    default_local_path = os.path.join(BEZEL_ROOT_DIR, platform_data['bezel_repo'], os.path.basename(platform_data['default_bezel']))
    default_url = get_raw_url(platform_data['bezel_repo'], platform_data['default_bezel'])
    for game_entry in gamelist_tree.getroot():
        game_data = common_utils.parse_game_entry(game_entry)
        game_compare_name = get_basename_no_ext(game_data['rom_path']) if platform_data['bezel_repo'] == 'bezelproject-MAME' else get_compare_name(game_data['name'])
        best_match, score = process.extractOne(game_compare_name, bezel_compare_names)
        print(score, best_match)
        bezel_type_element = ET.SubElement(game_entry, 'bezel_type')
        bezel_path_element = ET.SubElement(game_entry, 'bezel_path')
        if score >= min_match_score:
            download_match(best_match, bezels)
            bezel_path_element.text = bezels[best_match]['local_path']
            bezel_type_element.text = 'matched'
        else:
            if not os.path.isfile(default_local_path):
                download_file(default_url, default_local_path)
            bezel_path_element.text = default_local_path
            bezel_type_element.text = 'default'
    gamelist_tree.write(input_path)
    common_utils.write_file('./matches', '\n'.join(matches), 'w')


logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(asctime)s : %(message)s", datefmt="%H:%M:%S")

SNES_GAMELIST = '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/SNES/gamelist/gamelist.xml'

MAME_GAMELIST = '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/MAME 078/gamelist/gamelist.xml'

init_local_dirs()
platform_data = configs.PLATFORMS['snes']
# repo = configs.PLATFORMS['mame-libretro']
bezels = get_available_bezels(platform_data['bezel_repo'])
add_bezels_to_gamelist(SNES_GAMELIST, bezels, platform_data)
# add_bezels_to_gamelist(MAME_GAMELIST, bezels, repo)

# download_bezel(bezel)


# '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/SNES/gamelist/gamelist.xml'

# No 'if name == __main__' as this can't be run as a distinct operation
