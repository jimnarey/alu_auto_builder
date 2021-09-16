#!/usr/bin/env python3

import os
import tempfile
from optparse import OptionParser
import logging

import configs
import common_utils
import cmd_help


def validate_args(platform, input_dir, scrape_module):
    if platform not in configs.PLATFORMS:
        logging.error('You must specify a valid platform when scraping')
        return False
    if not os.path.isdir(input_dir):
        logging.error('{0} is not a valid directory'.format(input_dir))
        return False
    if scrape_module not in configs.SCRAPING_MODULES:
        logging.error('{0} is not a valid scraping module - run "Skyscraper --help"'.format(scrape_module))
        return False
    return True


def scrape(platform, input_dir, scrape_flags, config_path, scrape_module, user_creds):
    opts = '-s {0}'.format(scrape_module)
    opts = opts + ' -u {0}'.format(user_creds) if user_creds else opts
    run_skyscraper(platform, input_dir, scrape_flags, config_path, opts)


def create_gamelist(platform, input_dir, game_list_flags, config_path, art_xml_path, temp_dir, output_dir):
    output_dir = os.path.abspath(output_dir) if output_dir else temp_dir
    opts = '-a "{0}" -g "{1}" -o "{2}"'.format(art_xml_path, output_dir, os.path.join(output_dir, 'media'))
    run_skyscraper(platform, input_dir, game_list_flags, config_path, opts)


def run_skyscraper(platform, input_dir, flags, config_path, opts):
    cmd = 'Skyscraper -p {0} -i "{1}" -c "{2}" {3}'.format(platform, input_dir, config_path, opts)
    cmd = cmd + ' --flags {0}'.format(','.join(flags)) if flags else cmd
    logging.info('Running command: {0}'.format(cmd))
    cmd_out = os.popen(cmd).read()


def main(platform, input_dir, scrape_module=None, user_creds=None, scrape_flags=None, game_list_flags=None,
         temp_dir=None, output_dir=None):
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting gamelist builder\n\n\n')
    scrape_module = scrape_module if scrape_module else 'screenscraper'
    if not validate_args(platform, input_dir, scrape_module):
        return
    if not temp_dir:
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_obj.name
    config_path = os.path.join(temp_dir, 'config.ini')
    art_xml_path = os.path.join(temp_dir, 'artwork.xml')
    scrape_flags = scrape_flags if scrape_flags else configs.SCRAPE_FLAGS
    game_list_flags = game_list_flags if game_list_flags else configs.GAME_LIST_FLAGS
    common_utils.write_file(config_path, ''.join(configs.CONFIG), 'w')
    common_utils.write_file(art_xml_path, ''.join(configs.ARTWORK), 'w')
    scrape(platform, input_dir, scrape_flags, config_path, scrape_module, user_creds)
    create_gamelist(platform, input_dir, game_list_flags, config_path, art_xml_path, temp_dir, output_dir)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help=cmd_help.PLATFORM, default=None)
    parser.add_option('-s', '--scraper', dest='scrape_module', help=cmd_help.SCRAPE_MODULE, default=None)
    parser.add_option('-u', '--usercreds', dest='user_creds', help=cmd_help.USER_CREDS, default=None)
    parser.add_option('-i', '--inputdir', dest='input_dir', help=cmd_help.INPUT_DIR, default=os.getcwd())
    parser.add_option('-o', '--output', dest='output_dir', help=cmd_help.GAME_LIST_TARGET_DIR, default=os.getcwd())
    return parser


def validate_opts(parser):
    (opts, args) = parser.parse_args()
    if opts.platform is None:
        parser.print_help()
        exit(0)
    return opts, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = validate_opts(parser)
    main(opts.platform, opts.input_dir, opts.scrape_module, opts.user_creds,
         output_dir=opts.output_dir)

# TODO - Allow user manipulation of scraping/gamelist flags
