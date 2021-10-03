#!/usr/bin/env python3

import os
from pathlib import Path
import logging

import configs
import common_utils
import errors
import operations


PLATFORM = common_utils.get_platform()

APP_ROOT = common_utils.get_app_root()


def validate_args(platform, scrape_module, input_dir, output_dir):
    valid = True
    if not platform or platform not in configs.PLATFORMS:
        logging.error('You must provide a valid platform')
        valid = False
    if scrape_module not in configs.SCRAPING_MODULES:
        logging.error(errors.SCRAPE_INVALID_MODULE)
        valid = False
    if not common_utils.validate_existing_dir(input_dir):
        valid = False
    if not common_utils.validate_parent_dir(output_dir):
        valid = False
    return valid


def setup_windows_skyscraper(local_skyscraper_dir):
    home_dir = str(Path.home())
    skyscraper_target = os.path.join(home_dir, '.skyscraper')
    retro_pie_target = os.path.join(home_dir, 'RetroPie')
    for dir_ in (skyscraper_target, retro_pie_target):
        if not os.path.isdir(dir_):
            logging.info('Attempting to copy required .skyscraper and RetroPie dirs to user home dir')
            common_utils.copytree(os.path.join(local_skyscraper_dir, 'deploy', '.skyscraper'), skyscraper_target)
            common_utils.copytree(os.path.join(local_skyscraper_dir, 'deploy', 'RetroPie'), retro_pie_target)


def get_user_creds_arg(user_name, password):
    if user_name and password:
        return '{0}:{1}'.format(user_name, password)
    return None


def get_skyscraper_bin():
    if PLATFORM == 'win32':
        local_skyscraper_dir = os.path.join(APP_ROOT, 'windows', 'skyscraper')
        if os.path.isdir(local_skyscraper_dir):
            logging.info('Using packaged copy of Skyscraper for Windows')
            setup_windows_skyscraper(local_skyscraper_dir)
            return os.path.join(local_skyscraper_dir, 'Skyscraper.exe')
    logging.info('Attempting to use external copy of Skyscraper')
    return 'Skyscraper'


def run_skyscraper(platform, input_dir, flags, config_path, sky_args):
    bin_ = get_skyscraper_bin()
    cmd = [bin_,
           '-p', platform,
           '-i', '{0}'.format(input_dir),
           '-c', '{0}'.format(config_path)] + sky_args
    cmd += ['--flags', ','.join(flags)] if flags else cmd
    common_utils.execute_with_output(cmd)


def scrape(platform, input_dir, scrape_flags, config_path, scrape_module, user_creds):
    sky_args = ['-s', scrape_module]
    sky_args += ['-u', user_creds] if user_creds else sky_args
    run_skyscraper(platform, input_dir, scrape_flags, config_path, sky_args)


def create_gamelist(platform, input_dir, game_list_flags, config_path, art_xml_path, output_dir):
    sky_args = ['-a', '{0}'.format(art_xml_path),
                '-g', '{0}'.format(output_dir),
                '-o', '{0}'.format(os.path.join(output_dir, 'media'))]
    run_skyscraper(platform, input_dir, game_list_flags, config_path, sky_args)


def main(platform, input_dir, scrape_module=None, user_name=None, password=None, output_dir=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    logging.info('Starting gamelist builder\n\n\n')
    scrape_module = scrape_module if scrape_module else 'screenscraper'
    input_dir = os.path.abspath(input_dir) if input_dir else os.getcwd()
    if not validate_args(platform, scrape_module, input_dir, output_dir):
        return
    output_dir = os.path.abspath(output_dir) if output_dir else os.path.join(input_dir, 'gamelist')
    temp_dir = common_utils.create_temp_dir(__name__)
    config_path = os.path.join(temp_dir, 'config.ini')
    art_xml_path = os.path.join(temp_dir, 'artwork.xml')
    common_utils.write_file(config_path, ''.join(configs.CONFIG), 'w')
    common_utils.write_file(art_xml_path, ''.join(configs.ARTWORK), 'w')
    user_creds = get_user_creds_arg(user_name, password)
    scrape(platform, input_dir, configs.SCRAPE_FLAGS, config_path, scrape_module, user_creds)
    create_gamelist(platform, input_dir, configs.GAME_LIST_FLAGS, config_path, art_xml_path, output_dir)
    common_utils.cleanup_temp_dir(__name__)


def run_with_args(args):
    main(args['platform'], args['input_dir'], scrape_module=args['scrape_module'], user_name=['user_name'],
         password=args['password'], output_dir=args['output_dir'])


if __name__ == "__main__":
    parser = common_utils.get_cmd_line_args(operations.operations['scrape_and_make_gamelist'])
    args = vars(parser.parse_args())
    run_with_args(args)

# TODO - Allow user manipulation of scraping/gamelist flags
