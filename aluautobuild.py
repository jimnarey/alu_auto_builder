#!/usr/bin/env python3

import os
import shutil
import tempfile
from optparse import OptionParser

import cmd_help
import create_gamelist
import build_uces


# TODO - ESSENTIAL
# TODO - Print some output
# TODO - Something if user-provided gamelist points nowhere

# TODO - FEATURE
# TODO - Command line interface for build_uces
# TODO - Add marquees
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


def run(opts):
    temp_dir_obj = tempfile.TemporaryDirectory()
    temp_dir = temp_dir_obj.name
    if opts.game_list:
        shutil.copy(opts.game_list, os.path.join(temp_dir, 'gamelist.xml'))
    else:
        create_gamelist.run(opts.platform, opts.input_dir, scrape_source=opts.scrape_source,
                            user_creds=opts.user_creds, temp_dir=temp_dir)
    build_uces.build_uces(opts.output_dir, opts.core_path, opts.other_dir, temp_dir=temp_dir)


# TODO - Allow keeping of rom attributes, region, rom-code, none, etc
def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help=cmd_help.PLATFORM, default=None)
    parser.add_option('-s', '--scraper', dest='scrape_source', help=cmd_help.SCRAPE_MODULE, default=None)
    parser.add_option('-u', '--usercreds', dest='user_creds', help=cmd_help.USER_CREDS, default=None)
    parser.add_option('-i', '--inputdir', dest='input_dir', help=cmd_help.INPUT_DIR, default=os.getcwd())
    parser.add_option('-o', '--output', dest='output_dir', help=cmd_help.OUTPUT_DIR,
                      default=os.path.join(os.getcwd(), 'output'))
    parser.add_option('-c', '--core', dest='core_path', help=cmd_help.CORE, default=None)
    parser.add_option('-b', '--other', dest='other_dir', help=cmd_help.OTHER_DIR, default=None)
    parser.add_option('-g', '--gamelist', dest='game_list', help=cmd_help.GAME_LIST, default=None)
    return parser


def validate_opts(parser):
    (options, args) = parser.parse_args()
    valid = True
    if options.core_path is None:
        valid = False
    if options.platform is None and options.game_list is None:
        valid = False
    if valid is False:
        parser.print_help()
        exit(0)
    return options, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (options, args) = validate_opts(parser)
    run(options)

# parser.add_option('-k', '--keepbrackets', dest='keep_brackets', help=cmd_help.KEEP_BRACKETS)
# parser.add_option('-a', '--allroms', dest='all_roms', help=cmd_help.ALL_ROMS)
