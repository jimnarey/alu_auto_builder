#!/usr/bin/env python3


import os
# import sys
import errno
import shutil
import xml.etree.ElementTree as ET
from genericpath import isfile
from pprint import pp, pprint
from optparse import OptionParser
import configs


# TODO - ESSENTIAL
# TODO - Ensure gamelist is created for games with no data
# TODO - Ensure something is done for games with no metadata/image
# TODO - Print some output
# TODO - Cleanup

# TODO - FEATURE
# TODO - Add marquees
# TODO - Add something to ignore existing Skyscraper config
# TODO - Allow user to specify gamelist.xml
# TODO - Allow creation of gamelist without scraping (not very useful)
# TODO - Add option to discontinue based on scrape results
# TODO - Add option to allow user to specify default png
# TODO - Handle (MAME) roms which need individual config file/metadata subfolder
# TODO - Error handling:
# - Skyscraper fail
# - Can't create dirs/write files
# - Can't read gamelist.xml

# TODO - CHECK MET
# TODO - Ensure temp files are created in input dir, not in whatever dir the script is run in

def write_file(file_path, file_content):
    with open(file_path, 'w') as target_file:
        target_file.write(file_content)


def safe_make_dir(path):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    pass


def scrape(platform, flags, data_paths, scrape_source, user_creds=None):
    opts = '-s {0}'.format(scrape_source)
    opts = opts + ' -u {0}'.format(user_creds) if user_creds else opts
    run_skyscraper(platform, flags, data_paths, opts)


def create_gamelist(platform, flags, data_paths):
    opts = '-a "{0}" -g "{1}"'.format(data_paths['art_xml_path'], data_paths['temp_dir'])
    run_skyscraper(platform, flags, data_paths, opts)


def run_skyscraper(platform, flags, data_paths, opts):
    cmd = 'Skyscraper -p {0} -i "{1}" --flags {2} -c "{3}" {4}'.format(platform, input_dir, flags,
                                                                       data_paths['config_file'], opts)
    # print(cmd)
    x = os.popen(cmd).read()
    print(x)


def get_app_paths():
    this_dir = os.path.split(os.path.realpath(__file__))[0]
    return {'root': this_dir, 'common_files': os.path.join(this_dir, 'common'),
            'vendor_scripts': os.path.join(this_dir, 'vendor')}


def set_paths(input_dir, output_dir, core_path):
    temp_dir = os.path.join(input_dir, 'temp')
    return {
        'input_dir': input_dir,
        'core_path': core_path,
        'output_dir': output_dir if output_dir else os.path.join(input_dir, 'output'),
        'temp_dir': temp_dir,
        'config_file': os.path.join(temp_dir, 'config.ini'),
        'art_xml_path': os.path.join(temp_dir, 'artwork.xml')
    }


def setup(data_paths):
    safe_make_dir(data_paths['temp_dir'])
    safe_make_dir(data_paths['output_dir'])
    write_file(data_paths['config_file'], ''.join(configs.CONFIG))
    write_file(data_paths['art_xml_path'], ''.join(configs.ARTWORK))


def read_gamelist(gamelist_path):
    tree = ET.parse(gamelist_path)
    return tree.getroot()


def parse_game_entry(game_entry):
    return {
        'name': game_entry.find('name').text,
        'rom_path': game_entry.find('path').text,
        'boxart_path': game_entry.find('thumbnail').text,
        'marquee': game_entry.find('marquee').text,
        'description': game_entry.find('desc').text
    }


def make_uce_sub_dirs(game_dir):
    for sub_dir in ('emu', 'roms', 'boxart', 'save'):
        safe_make_dir(os.path.join(game_dir, sub_dir))


def write_cart_xml(game_dir, game_title, game_desc, boxart_file_name):
    cart_xml = ''.join(configs.CARTRIDGE_XML)\
        .replace('GAME_TITLE', game_title)\
        .replace('GAME_DESCRIPTION', game_desc)\
        .replace('BOXART_FILE_NAME', boxart_file_name)
    write_file(os.path.join(game_dir, 'cartridge.xml'), cart_xml)


def write_exec_sh(game_dir, core_file_name, game_file_name):
    exec_sh = ''.join(configs.EXEC_SH)\
        .replace('CORE_FILE_NAME', core_file_name)\
        .replace('GAME_FILE_NAME', game_file_name)
    write_file(os.path.join(game_dir, 'exec.sh'), exec_sh)


def copy_source_files(data_paths, game_data, game_dir):
    box_art_target_path = os.path.join(game_dir, 'boxart', os.path.basename(game_data['boxart_path']))
    shutil.copyfile(data_paths['core_path'], os.path.join(game_dir, 'emu', os.path.basename(data_paths['core_path'])))
    shutil.copyfile(game_data['rom_path'], os.path.join(game_dir, 'roms', os.path.basename(game_data['rom_path'])))
    shutil.copyfile(game_data['boxart_path'], box_art_target_path)
    os.symlink(box_art_target_path, os.path.join(game_dir, 'title.png'))


def setup_uce_source(data_paths, game_data, game_dir):
    safe_make_dir(game_dir)
    make_uce_sub_dirs(game_dir)
    write_cart_xml(game_dir, game_data['name'], game_data['description'], os.path.basename(game_data['boxart_path']))
    write_exec_sh(game_dir, os.path.basename(data_paths['core_path']), os.path.basename(game_data['rom_path']))
    copy_source_files(data_paths, game_data, game_dir)


def build_uce(app_paths, data_paths, game_dir):
    target_path = os.path.join(data_paths['output_dir'], '{0}{1}'.format(os.path.basename(game_dir), '.UCE'))
    build_exec = os.path.join(app_paths['vendor_scripts'], 'build_uce.sh')
    cmd = '{0} "{1}" "{2}"'.format(build_exec, game_dir, target_path)
    x = os.popen(cmd).read()
    print(x)


def build_uces(app_paths, data_paths):
    game_list = read_gamelist(os.path.join(data_paths['temp_dir'], 'gamelist.xml'))
    for game_entry in game_list:
        game_data = parse_game_entry(game_entry)
        game_dir = os.path.join(data_paths['temp_dir'], os.path.splitext(os.path.basename(game_data['rom_path']))[0])
        setup_uce_source(data_paths, game_data, game_dir)
        build_uce(app_paths, data_paths, game_dir)


def run(platform, input_dir, flags, scrape_source, user_creds, output_dir, core_path):
    data_paths = set_paths(input_dir, output_dir, core_path)
    app_paths = get_app_paths()

    setup(data_paths)
    scrape(platform, flags, data_paths, scrape_source, user_creds)
    create_gamelist(platform, flags, data_paths)
    build_uces(app_paths, data_paths)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform',
                      help="Emulated platform. Run 'Skyscraper --help' to see available platforms.")
    parser.add_option('-i', '--inputdir', dest='input_dir', help="Location of input roms.")
    parser.add_option('-s', '--scraper', dest='scraper',
                      help="Scraping source. Run 'Skyscraper --help' to see available scraping modules.")
    parser.add_option('-o', '--output', dest='output_dir', help="Output directory.")
    parser.add_option('-u', '--usercreds', dest='user_creds', help="User credentials for scraping module.")
    parser.add_option('-c', '--core', dest='core', help="Libretro core compatible with input roms")
    return parser


def validate_opts(parser):
    (options, args) = parser.parse_args()
    if None in (options.platform, options.core):
        parser.print_help()
        exit(0)
    return options, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (options, args) = validate_opts(parser)

    flags = configs.FLAGS
    input_dir = options.input_dir if options.input_dir else os.getcwd()
    scrape_source = options.scraper if options.scraper else 'screenscraper'
    user_creds = options.user_creds if options.user_creds else None
    output_dir = options.output_dir if options.output_dir else None
    run(options.platform, input_dir, flags, scrape_source, user_creds, output_dir, options.core)
