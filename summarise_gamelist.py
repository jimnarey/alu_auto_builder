#!/usr/bin/env python3

import os
import logging
from shared import common_utils
from shared import error_messages

logger = logging.getLogger(__name__)


def validate_args(input_path, output_dir):
    logger.info('Validating arguments for summarise_gamelist')
    valid = True
    if not common_utils.validate_required_path(input_path, 'Specified gamelist'):
        valid = False
    if not common_utils.validate_existing_dir(output_dir, 'Output dir'):
        valid = False
    return valid


# def score_to_int(value):
#     try:
#         return int(value.strip())
#     except ValueError as e:
#         logger.error(error_messages.score_not_number(value, e))
#     return 0


def append_to_summary_table(summary_table, game_data, rom_basename, bezel_basename):
    summary_table.append(
        [
            rom_basename,
            game_data.get('name', None),
            bezel_basename,
            game_data.get('bezel_match', None),
            True if game_data.get('boxart_path', False) else False,
            True if game_data.get('marquee_path', False) else False,
            True if game_data.get('logo_path', False) else False,
            True if game_data.get('video_path', False) else False,
        ]
    )


def append_to_summary_lists(summary_lists, game_data, rom_basename, bezel_basename):
    bezel_match = game_data.get('bezel_match', '')
    if not game_data.get('name', None):
        summary_lists['no_scraped_title'].append(rom_basename)
    if not game_data.get('boxart_path', False):
        summary_lists['no_cover'].append(rom_basename)
    if not game_data.get('logo_path', False):
        summary_lists['no_logo'].append(rom_basename)
    if not game_data.get('video_path', False):
        summary_lists['no_video'].append(rom_basename)
    if not game_data.get('marquee_path', False):
        summary_lists['no_marquee'].append(rom_basename)
    if bezel_match == 'default':
        summary_lists['default_bezel'].append(rom_basename),
    elif bezel_match != '100':
        summary_lists['non_100_bezel_match'].append([common_utils.score_to_int(bezel_match), rom_basename, bezel_basename])


def get_sublist_header(summary_lists, key):
    num_items = len(summary_lists[key])
    list_title = 'Has {0}'.format(key.replace('_', ' ').title())
    return '----------------------------\n{0} ({1})\n----------------------------\n'.format(list_title, num_items)


def format_bezel_not_100_list(summary_lists):
    return '\n'.join(['{0} -- {1} \t\t\t--\t\t\t {2}'.format(row[0], row[1], row[2])
                      for row in summary_lists['non_100_bezel_match']])


def format_summary_lists(summary_lists):
    summary_text = ''
    for key in ('no_scraped_title', 'no_cover', 'no_logo', 'no_marquee', 'no_video', 'default_bezel'):
        summary_text = '{0}{1}\n{2}\n\n'.format(summary_text,
                                                get_sublist_header(summary_lists, key),
                                                '\n'.join(summary_lists[key]))
    summary_lists['non_100_bezel_match'].sort(key=lambda x: x[0], reverse=True)
    summary_text = '{0}\n{1}\n{2}'.format(summary_text,
                                          get_sublist_header(summary_lists, 'non_100_bezel_match'),
                                          format_bezel_not_100_list(summary_lists))
    return summary_text


def main(input_path, output_dir=None):
    output_dir = output_dir if output_dir else os.path.abspath(os.path.dirname(input_path))
    if not validate_args(input_path, output_dir):
        return False
    gamelist = common_utils.read_gamelist_tree(input_path).getroot()
    summary_table = [['Filename', 'Gamelist name', 'Bezel name', 'Bezel match', 'Has cover', 'Has marquee', 'Has logo',
                      'Has video', ], ]
    summary_lists = {
        'no_scraped_title': [],
        'no_cover': [],
        'no_logo': [],
        'no_marquee': [],
        'no_video': [],
        'default_bezel': [],
        'non_100_bezel_match': []
    }
    for game_entry in gamelist:
        game_data = common_utils.parse_game_entry(game_entry)
        rom_basename = os.path.basename(game_data.get('rom_path', ''))
        bezel_basename = os.path.basename(game_data.get('bezel_path', ''))
        append_to_summary_table(summary_table, game_data, rom_basename, bezel_basename)
        append_to_summary_lists(summary_lists, game_data, rom_basename, bezel_basename)
    common_utils.write_file(os.path.join(output_dir, 'summary_lists.txt'), format_summary_lists(summary_lists), 'w')
    common_utils.write_csv(os.path.join(output_dir, 'summary_table.csv'), summary_table)
