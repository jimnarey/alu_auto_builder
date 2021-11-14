#!/usr/bin/env python3
import os
import re

import requests
import pprint
from pathlib import Path

from fuzzywuzzy import process

from shared import configs, common_utils

BASE_TREE_URL = 'https://api.github.com/repos/thebezelproject/{0}/git/trees/master?recursive=1'

BEZEL_ROOT_DIR = os.path.join(str(Path.home()), '.bezels')


def init_local_dirs():
    if not os.path.isdir(BEZEL_ROOT_DIR):
        common_utils.make_dir(BEZEL_ROOT_DIR)
    for key in configs.PLATFORMS:
        subdir = os.path.join(BEZEL_ROOT_DIR, configs.PLATFORMS[key])
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
    local_path = os.path.join(BEZEL_ROOT_DIR, repo, game_name)
    compare_name = get_compare_name(game_name)
    return compare_name, {
        'game_name': game_name,
        'url': get_raw_url(repo, path),
        'local_path': local_path if os.path.isfile(local_path) else None
    }


def download_bezel(url):
    data = requests.get(url)
    common_utils.write_file('test.png', data.content, 'wb')


def get_available_bezels(repo):
    data = requests.get(BASE_TREE_URL.format(repo))
    tree = data.json()['tree']
    bezels = {}
    for item in tree:
        if item['type'] == 'blob':
            if os.path.splitext(item['path'])[-1] == '.png':
                key, value = get_bezel_data(repo, item)
                bezels[key] = value
                # bezels.append(get_bezel_data(repo, item))
    # pprint.pprint(bezels)
    return bezels


def add_bezels_to_gamelist(input_path, bezels, repo):
    gamelist_tree = common_utils.read_gamelist_tree(input_path)
    bezel_compare_names = set(bezels.keys())
    matches = []
    for game_entry in gamelist_tree.getroot():
        game_data = common_utils.parse_game_entry(game_entry)
        game_compare_name = get_basename_no_ext(game_data['rom_path']) if repo == 'bezelproject-MAME' else get_compare_name(game_data['name'])
        best_match, score = process.extractOne(game_compare_name, bezel_compare_names)
        print(best_match, score)
        matches.append(' : '.join([str(score), best_match, game_data['name'], bezels[best_match]['game_name'], game_compare_name]))
    common_utils.write_file('./matches', '\n'.join(matches), 'w')


SNES_GAMELIST = '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/SNES/gamelist/gamelist.xml'

init_local_dirs()
repo = configs.PLATFORMS['snes']
bezels = get_available_bezels(repo)
add_bezels_to_gamelist(SNES_GAMELIST, bezels, repo)
# download_bezel(bezel)


# '/media/jimnarey/HDD_Data_B/Retro/AtGames ALU/match_testing/SNES/gamelist/gamelist.xml'

# No 'if name == __main__' as this can't be run as a distinct operation
