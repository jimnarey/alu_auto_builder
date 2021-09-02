#!/usr/bin/env python3


import os
# import sys
import errno
import xml.etree.ElementTree as ET
from genericpath import isfile
from pprint import pp, pprint
from optparse import OptionParser
import configs

# TODO - Add marquees
# TODO - Add something to ignore existing Skyscraper config
# TODO - Ensure temp files are created in input dir, not in whatever dir the script is run in
# TODO - Allow user to specify gamelist.xml
# TODO - Allow creation of gamelist without scraping (not very useful)
# TODO - Error handling:
# - Skyscraper fail
# - Can't create dirs
# - Can't read xml

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
    opts = '-a "{0}" -g "{1}"'.format(paths['art_xml_path'], paths['temp_dir'])
    run_skyscraper(platform, flags, paths, opts)

def run_skyscraper(platform, flags, paths, opts):
    cmd = 'Skyscraper -p {0} -i "{1}" --flags {2} -c "{3}" {4}'.format(platform, input_dir, flags, paths['config_file'], opts)
    # print(cmd)
    x = os.popen(cmd).read()

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
    write_file(paths['config_file'], configs.CONFIG)
    write_file(paths['art_xml_path'], configs.ARTWORK)

def read_gamelist(gamelist_path):
    tree = ET.parse(gamelist_path)
    return tree.getroot()

def parse_game_entry(game_entry):
    return {
        'name': game_entry.find('name').text,
        'path': game_entry.find('path').text,
        'boxart': game_entry.find('thumbnail').text,
        'marquee': game_entry.find('marquee').text,
        'description': game_entry.find('desc').text
    }

def make_uce_sub_dirs(game_dir):
    for dir in ('emu', 'roms', 'boxart', 'save'):
        safe_make_dir(os.path.join(game_dir, dir))

def write_cart_xml(game_dir, game_title, game_desc):
    # cart_xml = ''.join(configs.CARTRIDGE_XML).replace()
    pass


def setup_uce_sources(paths):
    game_list = read_gamelist(os.path.join(paths['temp_dir'], 'gamelist.xml'))
    for game_entry in game_list:
        game_data = parse_game_entry(game_entry)
        game_dir = os.path.join(paths['temp_dir'], os.path.splitext( os.path.basename(game_data['path']) )[0])
        safe_make_dir(game_dir)
        make_uce_sub_dirs(game_dir)
        

def run(platform, input_dir, flags, scrape_source, user_creds, output_dir):
    paths = set_paths(input_dir, output_dir)
    app_paths = get_app_paths()
    
    setup(paths)
    scrape(platform, flags, paths, scrape_source, user_creds)
    create_gamelist(platform, flags, paths)
    setup_uce_sources(paths)
    

def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help="Emulated platform. Run 'Skyscraper --help' to see available platforms.")
    parser.add_option('-i', '--inputdir', dest='input_dir', help="Location of input roms.")
    parser.add_option('-s', '--scraper', dest='scraper', help="Scraping source. Run 'Skyscraper --help' to see available scraping modules.")
    parser.add_option('-o', '--output', dest='output_dir', help="Output directory.")
    parser.add_option('-u', '--usercreds', dest='user_creds', help="User credentials for scraping module.")
    parser.add_option('-c', '--core', dest='core', help="Libretro core compatible with input roms")
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
    
    
    flags=configs.FLAGS
    input_dir = options.input_dir if options.input_dir else os.getcwd()
    scrape_source = options.scraper if options.scraper else 'screenscraper'
    user_creds = options.user_creds if options.user_creds else None
    output_dir = options.output_dir if options.output_dir else None
    run(options.platform, input_dir, flags, scrape_source, user_creds, output_dir)

