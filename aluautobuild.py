#!/usr/bin/env python3

import os
import tempfile
from optparse import OptionParser
import logging

import cmd_help
import create_gamelist
import build_recipes
import common_utils
import errors


def main(opts):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    temp_dir = common_utils.create_temp_dir(__name__)
    temp_gamelist_path = os.path.join(temp_dir, 'gamelist.xml')
    if opts.gamelist_path:
        common_utils.copyfile(opts.gamelist_path, temp_gamelist_path)
    else:
        create_gamelist.main(opts.platform, opts.input_dir, scrape_module=opts.scrape_module,
                             user_creds=opts.user_creds, temp_dir=temp_dir)
    build_recipes.main(temp_gamelist_path, opts.core_path, bios_dir=opts.bios_dir, output_dir=temp_dir)
    common_utils.cleanup_temp_dir(__name__)

# (gamelist_path, core_path, bios_dir=None, output_dir=None)

# TODO - Allow keeping of rom attributes, region, rom-code, none, etc
def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help=cmd_help.PLATFORM, default=None)
    parser.add_option('-s', '--scraper', dest='scrape_module', help=cmd_help.SCRAPE_MODULE, default=None)
    parser.add_option('-u', '--usercreds', dest='user_creds', help=cmd_help.USER_CREDS, default=None)
    parser.add_option('-i', '--inputdir', dest='input_dir', help=cmd_help.INPUT_DIR, default=os.getcwd())
    parser.add_option('-o', '--output', dest='output_dir', help=cmd_help.OUTPUT_DIR,
                      default=os.path.join(os.getcwd(), 'output'))
    parser.add_option('-c', '--core', dest='core_path', help=cmd_help.CORE, default=None)
    parser.add_option('-b', '--bios', dest='bios_dir', help=cmd_help.BIOS_DIR, default=None)
    parser.add_option('-g', '--gamelist', dest='gamelist_path', help=cmd_help.GAME_LIST, default=None)
    return parser


def validate_opts(parser):
    (opts, args) = parser.parse_args()
    valid = True
    if opts.core_path is None:
        print(errors.NO_CORE_FILE)
        valid = False
    if opts.platform is None and opts.gamelist_path is None:
        print(errors.NO_GAMELIST_OR_PLATFORM)
        valid = False
    if valid is False:
        parser.print_help()
        exit(0)
    return opts, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = validate_opts(parser)
    main(opts)

