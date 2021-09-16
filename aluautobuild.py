#!/usr/bin/env python3

import os
import tempfile
from optparse import OptionParser
import logging

import cmd_help
import create_gamelist
import build_uces
import common_utils
import errors


# TODO - ESSENTIAL
# TODO - Print some output
# TODO - Something if user-provided gamelist points nowhere

# TODO - FEATURE
# TODO - Allow creation of gamelist without scraping (not very useful, implement without Skyscraper)
# TODO - Add option to discontinue based on scrape results
# TODO - Add option to allow user to specify default png
# TODO - Handle (MAME) roms which need individual config file/metadata subfolder
# TODO - Check images are png (check whether this is a requirement first)
# TODO - Look in input dir for core
# TODO - Error handling:
# - Skyscraper fail
# - Can't create dirs/write files
# - Can't read gamelist.xml
# TODO - Custom save concept:
# User points to an overall 'save' dir
# Contains custom saves with same names as games
# Failing that uses a generic, custom save.zip


def main(opts):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    temp_dir_obj = tempfile.TemporaryDirectory()
    temp_dir = temp_dir_obj.name
    if opts.gamelist_path:
        common_utils.copyfile(opts.gamelist_path, os.path.join(temp_dir, 'gamelist.xml'))
    else:
        create_gamelist.main(opts.platform, opts.input_dir, scrape_module=opts.scrape_module,
                             user_creds=opts.user_creds, temp_dir=temp_dir)
    build_uces.main(opts.output_dir, opts.core_path, opts.bios_dir, temp_dir)


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

# parser.add_option('-k', '--keepbrackets', dest='keep_brackets', help=cmd_help.KEEP_BRACKETS)
# parser.add_option('-a', '--allroms', dest='all_roms', help=cmd_help.ALL_ROMS)
