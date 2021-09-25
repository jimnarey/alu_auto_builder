#!/usr/bin/env python3

import os
import tempfile
from optparse import OptionParser
from pathlib import Path
import logging

import configs
import common_utils
import cmd_help
import errors

PLATFORM = common_utils.get_platform()

APP_ROOT = common_utils.get_app_root()


def setup_windows_skyscraper(local_skyscraper_dir):
    home_dir = str(Path.home())
    skyscraper_target = os.path.join(home_dir, '.skyscraper')
    retro_pie_target = os.path.join(home_dir, 'RetroPie')
    for dir_ in (skyscraper_target, retro_pie_target):
        if not os.path.isdir(dir_):
            logging.info('Attempting to copy required .skyscraper and RetroPie dirs to user home dir')
            common_utils.copytree(os.path.join(local_skyscraper_dir, 'deploy', '.skyscraper'), skyscraper_target)
            common_utils.copytree(os.path.join(local_skyscraper_dir, 'deploy', 'RetroPie'), retro_pie_target)


def get_skyscraper_bin():
    if PLATFORM == 'win32':
        local_skyscraper_dir = os.path.join(APP_ROOT, 'windows', 'skyscraper')
        if os.path.isdir(local_skyscraper_dir):
            logging.info('Using packaged copy of Skyscraper for Windows')
            setup_windows_skyscraper(local_skyscraper_dir)
            return os.path.join(local_skyscraper_dir, 'Skyscraper.exe')
    logging.info('Attempting to use external copy of Skyscraper')
    return 'Skyscraper'


def validate_args(platform, input_dir, scrape_module):
    if platform not in configs.PLATFORMS:
        logging.error(errors.SCRAPE_INVALID_PLATFORM)
        return False
    if not os.path.isdir(input_dir):
        logging.error(errors.invalid_path(input_dir, 'directory'))
        return False
    if scrape_module not in configs.SCRAPING_MODULES:
        logging.error(errors.SCRAPE_INVALID_MODULE)
        return False
    return True


def run_skyscraper(platform, input_dir, flags, config_path, sky_args, skyscraper_bin):
    cmd = [skyscraper_bin,
           '-p', platform,
           '-i', '{0}'.format(input_dir),
           '-c', '{0}'.format(config_path)] + sky_args
    cmd += ['--flags', ','.join(flags)] if flags else cmd
    common_utils.execute_with_output(cmd)


def scrape(platform, input_dir, scrape_flags, config_path, scrape_module, user_creds, skyscraper_bin):
    sky_args = ['-s', scrape_module]
    sky_args += ['-u', user_creds] if user_creds else sky_args
    run_skyscraper(platform, input_dir, scrape_flags, config_path, sky_args, skyscraper_bin)


def create_gamelist(platform, input_dir, game_list_flags, config_path, art_xml_path, temp_dir, output_dir, skyscraper_bin):
    output_dir = os.path.abspath(output_dir) if output_dir else temp_dir
    sky_args = ['-a', '{0}'.format(art_xml_path),
                '-g', '{0}'.format(output_dir),
                '-o', '{0}'.format(os.path.join(output_dir, 'media'))]
    run_skyscraper(platform, input_dir, game_list_flags, config_path, sky_args, skyscraper_bin)


def main(platform, input_dir, scrape_module=None, user_creds=None, scrape_flags=None, game_list_flags=None,
         temp_dir=None, output_dir=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    logging.info('Starting gamelist builder\n\n\n')
    skyscraper_bin = get_skyscraper_bin()
    scrape_module = scrape_module if scrape_module else 'screenscraper'
    if not validate_args(platform, input_dir, scrape_module):
        return
    if not temp_dir:
        temp_dir = common_utils.create_temp_dir(__name__)
        # temp_dir_obj = tempfile.TemporaryDirectory()
        # temp_dir = temp_dir_obj.name
    config_path = os.path.join(temp_dir, 'config.ini')
    art_xml_path = os.path.join(temp_dir, 'artwork.xml')
    scrape_flags = scrape_flags if scrape_flags else configs.SCRAPE_FLAGS
    game_list_flags = game_list_flags if game_list_flags else configs.GAME_LIST_FLAGS
    common_utils.write_file(config_path, ''.join(configs.CONFIG), 'w')
    common_utils.write_file(art_xml_path, ''.join(configs.ARTWORK), 'w')
    scrape(platform, input_dir, scrape_flags, config_path, scrape_module, user_creds, skyscraper_bin)
    create_gamelist(platform, input_dir, game_list_flags, config_path, art_xml_path, temp_dir, output_dir, skyscraper_bin)
    common_utils.cleanup_temp_dir(__name__)


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
        print(errors.SCRAPE_NO_PLATFORM)
        parser.print_help()
        exit(0)
    return opts, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = validate_opts(parser)
    main(opts.platform, opts.input_dir, opts.scrape_module, opts.user_creds,
         output_dir=opts.output_dir)

# TODO - Allow user manipulation of scraping/gamelist flags
