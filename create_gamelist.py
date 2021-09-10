#!/usr/bin/env python3

import os
import configs
import tempfile
from optparse import OptionParser

import cmd_help


def write_file(file_path, file_content):
    with open(file_path, 'w') as target_file:
        target_file.write(file_content)


def scrape(platform, input_dir, scrape_flags, config_path, scrape_source=None, user_creds=None):
    opts = '-s {0}'.format(scrape_source if scrape_source else 'screenscraper')
    opts = opts + ' -u {0}'.format(user_creds) if user_creds else opts
    run_skyscraper(platform, input_dir, scrape_flags, config_path, opts)


def create_gamelist(platform, input_dir, game_list_flags, config_path, art_xml_path, game_list_target_dir):
    opts = '-a "{0}" -g "{1}"'.format(art_xml_path, game_list_target_dir)
    run_skyscraper(platform, input_dir, game_list_flags, config_path, opts)


def run_skyscraper(platform, input_dir, flags, config_path, opts):
    cmd = 'Skyscraper -p {0} -i "{1}" -c "{2}" {3}'.format(platform, input_dir, config_path, opts)
    cmd = cmd + ' --flags {0}'.format(','.join(flags)) if flags else cmd
    print(cmd)
    cmd_out = os.popen(cmd).read()
    print(cmd_out)


def run(platform, input_dir, scrape_source=None, user_creds=None, scrape_flags=None, game_list_flags=None,
        temp_dir=None, game_list_target_dir=None):
    if not temp_dir:
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_obj.name
    game_list_target_dir = game_list_target_dir if game_list_target_dir else temp_dir
    config_path = os.path.join(temp_dir, 'config.ini')
    art_xml_path = os.path.join(temp_dir, 'artwork.xml')
    scrape_flags = scrape_flags if scrape_flags else configs.SCRAPE_FLAGS
    game_list_flags = game_list_flags if game_list_flags else configs.GAME_LIST_FLAGS
    write_file(config_path, ''.join(configs.CONFIG))
    write_file(art_xml_path, ''.join(configs.ARTWORK))
    scrape(platform, input_dir, scrape_flags, config_path, scrape_source, user_creds)
    create_gamelist(platform, input_dir, game_list_flags, config_path, art_xml_path, game_list_target_dir)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help=cmd_help.PLATFORM)
    parser.add_option('-s', '--scraper', dest='scraper', help=cmd_help.SCRAPE_MODULE)
    parser.add_option('-u', '--usercreds', dest='user_creds', help=cmd_help.USER_CREDS)
    parser.add_option('-i', '--inputdir', dest='input_dir', help=cmd_help.INPUT_DIR)
    return parser


def validate_opts(parser):
    (options, args) = parser.parse_args()
    if options.platform is None:
        parser.print_help()
        exit(0)
    return options, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (options, args) = validate_opts(parser)


    input_dir = options.input_dir if options.input_dir else os.getcwd()
    scrape_source = options.scraper if options.scraper else None
    user_creds = options.user_creds if options.user_creds else None

    run(options.platform, input_dir, scrape_source, user_creds)
