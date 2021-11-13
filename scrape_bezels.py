#!/usr/bin/env python3
import os
import re

import requests
import pprint
from pathlib import Path

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


def get_bezel_data(repo, github_tree_item):
    path = github_tree_item['path']
    basename = os.path.splitext(os.path.basename(path))[0]
    local_path = os.path.join(BEZEL_ROOT_DIR, repo, basename)
    return {
        'game_name': basename,
        'compare_name': ' '.join(re.sub("[\(\[].*?[\)\]]", "", basename).lower().split()),
        'url': get_raw_url(repo, path),
        'local_path': local_path if os.path.isfile(local_path) else None
    }


def download_bezel(url):
    data = requests.get(url)
    common_utils.write_file('test.png', data.content, 'wb')


def get_available_bezels(repo):
    data = requests.get(BASE_TREE_URL.format(repo))
    tree = data.json()['tree']
    # bezels = {}
    bezels = []
    for item in tree:
        if item['type'] == 'blob':
            if os.path.splitext(item['path'])[-1] == '.png':
                # bezels[os.path.basename(item['path'])] = get_raw_url(repo, item['path'])
                bezels.append(get_bezel_data(repo, item))
    pprint.pprint(bezels)
    return bezels


init_local_dirs()
repo = configs.PLATFORMS['gamegear']
bezels = get_available_bezels(repo)
# download_bezel(bezel)


# No 'if name == __main__' as this can't be run as a distinct operation
