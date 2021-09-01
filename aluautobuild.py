#!/usr/bin/env python3

import errno
from genericpath import isfile
import os
# import sys
from pprint import pp, pprint
from optparse import OptionParser
from configs import CONFIG, ARTWORK, FLAGS

# TODO - Add something to ignore existing Skyscraper config
# TODO - Ensure temp files are created in input dir, not in whatever dir the script is run in

def write_file(file_path, lines):
    with open(file_path, 'w') as target_file:
        target_file.writelines(lines)

def safe_make_dir(path):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    pass

def scrape(platform, flags, paths, scrape_source, user_creds=None):
    opts = '-s {0}'.format(scrape_source)
    opts = opts + ' -u {0}'.format(user_creds) if user_creds else opts
    run_skyscraper(platform, flags, paths, opts)

def create_gamelist(platform, flags, paths):
    opts = '-a "{0}"'.format(paths['art_xml_path'])
    run_skyscraper(platform, flags, paths, opts)

def run_skyscraper(platform, flags, paths, opts):
    cmd = 'Skyscraper -p {0} -i "{1}" --flags {2} -c "{3}" {4}'.format(platform, input_dir, flags, paths['config_file'], opts)
    print(cmd)
    os.system(cmd)

def get_app_paths():
    this_dir = os.path.split(os.path.realpath(__file__))[0]
    return { 'root': this_dir, 'common_files': os.path.join(this_dir, 'common'), 'vendor_scripts': os.path.join(this_dir, 'vendor')}

def set_paths(input_dir, output_dir):
    temp_dir = os.path.join(input_dir, 'temp')
    return {
        'input_dir': input_dir,
        'output_dir': output_dir if output_dir else os.path.join(input_dir, 'output'),
        'temp_dir': temp_dir,
        'config_file': os.path.join(temp_dir, 'config.ini'),
        'art_xml_path': os.path.join(temp_dir, 'artwork.xml')
    }

def setup(paths):
    safe_make_dir(paths['temp_dir'])
    safe_make_dir(paths['output_dir'])
    write_file(paths['config_file'], CONFIG)
    write_file(paths['art_xml_path'], ARTWORK)

def get_rom_paths(paths):
    rom_paths = [rom_path for rom_path in os.listdir(paths['input_dir']) if os.path.isfile(rom_path)]
    return rom_paths

def make_source_dirs(paths, rom_paths):
    for rom_path in rom_paths:
        pass

def run(platform, input_dir, flags, scrape_source, user_creds, output_dir):
    paths = set_paths(input_dir, output_dir)
    app_paths = get_app_paths()
    pprint(paths)
    pprint(app_paths)
    setup(paths)
    pprint(get_rom_paths(paths))
    scrape(platform, flags, paths, scrape_source, user_creds)
    create_gamelist(platform, flags, paths)

def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help="Emulated platform. Run 'Skyscraper --help' to see available platforms.")
    parser.add_option('-i', '--inputdir', dest='input_dir', help="Location of input roms.")
    parser.add_option('-s', '--scraper', dest='scraper', help="Scraping source. Run 'Skyscraper --help' to see available scraping modules.")
    parser.add_option('-o', '--output', dest='output_dir', help="Output directory.")
    parser.add_option('-u', '--usercreds', dest='user_creds', help="User credentials for scraping module.")
    return parser

def validate_opts(parser):
    (options, args) = parser.parse_args()
    if options.platform is None:
        print(parser.usage)
        exit(0)
    return options, args

if __name__ == "__main__":
    
    parser = get_opts_parser()
    (options, args) = validate_opts(parser)
    
    
    flags=FLAGS
    input_dir = options.input_dir if options.input_dir else os.getcwd()
    scrape_source = options.scraper if options.scraper else 'screenscraper'
    user_creds = options.user_creds if options.user_creds else None
    output_dir = options.output_dir if options.output_dir else None
    run(options.platform, input_dir, flags, scrape_source, user_creds, output_dir)
