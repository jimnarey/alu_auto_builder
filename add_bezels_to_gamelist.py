#!/usr/bin/env python3

import os
import re
from xml.dom import minidom
from xml.etree import ElementTree as ET
import logging

from fuzzywuzzy import process

from shared import configs, common_utils, info_messages, error_messages

logger = logging.getLogger(__name__)


def validate_args(input_path, platform, min_match_score):
    logger.info('Validating arguments for create_gamelist')
    valid = True
    if not platform or platform not in configs.PLATFORMS.keys():
        logger.error(error_messages.SCRAPE_INVALID_PLATFORM)
        valid = False
    if not common_utils.validate_required_path(input_path, 'Specified gamelist'):
        valid = False
    if min_match_score:
        min_match_score = common_utils.score_to_int(min_match_score)
        if not min_match_score:
            valid = False
    return valid


def init_local_dirs():
    if not os.path.isdir(configs.BEZEL_ROOT_DIR):
        common_utils.make_dir(configs.BEZEL_ROOT_DIR)
    for key in configs.PLATFORMS:
        subdir = os.path.join(configs.BEZEL_ROOT_DIR, configs.PLATFORMS[key]['bezel_repo'])
        if not os.path.isdir(subdir):
            common_utils.make_dir(subdir)


def get_raw_url(repo, path):
    return configs.BASE_BEZEL_RAW_URL.format(repo, path).replace(' ', '%20')


# TODO - Consider option to retain (and add) no-intro region codes, using
def clean_compare_name(name):
    return ' '.join(re.sub("[\(\[].*?[\)\]]", "", name).lower().split())


# def get_basename_no_ext(path):
#     return os.path.splitext(os.path.basename(path))[0]


def get_game_compare_name(game_data, compare_filename):
    if compare_filename:
        compare_name = clean_compare_name(game_data['basename_no_ext'])
    elif not game_data['name']:
        logger.info(info_messages.reverting_to_filename_compare(game_data['basename_no_ext']))
        compare_name = clean_compare_name(game_data['basename_no_ext'])
    else:
        compare_name = clean_compare_name(game_data['name'])
    return compare_name


def get_bezel_data(repo, github_tree_item):
    path = github_tree_item['path']
    game_name = common_utils.get_basename_no_ext(path)
    local_path = os.path.join(configs.BEZEL_ROOT_DIR, repo, '{0}.png'.format(game_name))
    compare_name = clean_compare_name(game_name)
    return compare_name, {
        'game_name': game_name,
        'url': get_raw_url(repo, path),
        'local_path': local_path
    }


def get_default_data(platform_data):
    default_url = get_raw_url(platform_data['bezel_repo'], platform_data['default_bezel'])
    default_local_path = os.path.join(configs.BEZEL_ROOT_DIR, platform_data['bezel_repo'], os.path.basename(platform_data['default_bezel']))
    return {'url': default_url, 'local_path': default_local_path}


def get_available_bezels(repo):
    data = common_utils.download_data(configs.BASE_BEZEL_TREE_URL.format(repo))
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
        return common_utils.download_file(bezels[match_name]['url'], bezels[match_name]['local_path'])
    logger.info(info_messages.bezel_local_copy_found(bezels[match_name]['game_name']))
    return True


def apply_default_bezel_to_game_entry(bezel_match_element, bezel_path_element, default_bezel):
    if not os.path.isfile(default_bezel['local_path']):
        common_utils.download_file(default_bezel['url'], default_bezel['local_path'])
    bezel_path_element.text = default_bezel['local_path']
    bezel_match_element.text = 'default'


def apply_matched_bezel_to_game_entry(bezel_match_element, bezel_path_element, score, best_match, bezels):
    check_bezel_local_copy(best_match, bezels)
    bezel_path_element.text = bezels[best_match]['local_path']
    bezel_match_element.text = str(score)


def is_unsupported_region(game_data):
    for substring in configs.BEZEL_SCRAPE_UNSUPPORTED_REGIONS:
        if substring in os.path.basename(game_data['rom_path']):
            return True
        if substring in game_data['name']:
            return True
    return False


def get_game_data(game_entry, compare_filename):
    game_data = common_utils.parse_game_entry(game_entry)
    game_data['basename_no_ext'] = common_utils.get_basename_no_ext(game_data['rom_path'])
    game_data['compare_name'] = get_game_compare_name(game_data, compare_filename)
    game_data['is_unsupported_region'] = is_unsupported_region(game_data)
    return game_data


def add_bezel_to_game_entry(game_entry, bezel_compare_names, bezels, default_bezel, min_match_score, compare_filename, filter_unsupported_regions):
    bezel_match_element = ET.SubElement(game_entry, 'bezel_match')
    bezel_path_element = ET.SubElement(game_entry, 'bezel_path')
    game_data = get_game_data(game_entry, compare_filename)
    if filter_unsupported_regions and game_data['is_unsupported_region']:
        apply_default_bezel_to_game_entry(bezel_match_element, bezel_path_element, default_bezel)
    else:
        best_match, score = process.extractOne(game_data['compare_name'], bezel_compare_names)
        if score >= min_match_score:
            apply_matched_bezel_to_game_entry(bezel_match_element, bezel_path_element, score, best_match, bezels)
        else:
            apply_default_bezel_to_game_entry(bezel_match_element, bezel_path_element, default_bezel)


def format_gamelist(gamelist_tree):
    lines = minidom.parseString(ET.tostring(gamelist_tree.getroot())).toprettyxml(indent=' ').split('\n')
    return '\n'.join([line for line in lines if line.strip()])


def main(input_path, platform, min_match_score=None, compare_filename=False, filter_unsupported_regions=True):
    platform_data = configs.PLATFORMS.get(platform, False)
    if not platform_data or not validate_args(input_path, platform, min_match_score):
        return False
    # TODO - Avoid converting to int here and in validate_args
    min_match_score = int(min_match_score) if min_match_score else 85
    init_local_dirs()
    bezels = get_available_bezels(platform_data['bezel_repo'])
    gamelist_tree = common_utils.read_gamelist_tree(input_path)
    bezel_compare_names = set(bezels.keys())
    default_bezel = get_default_data(platform_data)
    if not compare_filename and platform_data.get('use_filename', False):
        logger.warning(info_messages.FORCE_COMPARE_FILENAME)
        compare_filename = True
    for game_entry in gamelist_tree.getroot():
        add_bezel_to_game_entry(game_entry, bezel_compare_names, bezels, default_bezel, min_match_score, compare_filename, filter_unsupported_regions)
    common_utils.write_file(os.path.join(input_path), format_gamelist(gamelist_tree), 'w')


# No 'if name == __main__' as this can't be run as a distinct operation
