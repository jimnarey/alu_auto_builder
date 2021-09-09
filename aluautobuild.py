#!/usr/bin/env python3

import os
import errno
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pprint import pprint
from optparse import OptionParser

import cmd_help
import configs
import build_uce_tool


# TODO - ESSENTIAL
# TODO - Ensure gamelist is created for games with no data
# TODO - Ensure something is done for games with no metadata/image
# TODO - Print some output
# TODO - Cleanup
# TODO - Something if user-provided gamelist points nowhere

# TODO - FEATURE
# TODO - Add marquees
# TODO - Add something to ignore existing Skyscraper config
# TODO - Allow creation of gamelist without scraping (not very useful, implement without Skyscraper)
# TODO - Add option to discontinue based on scrape results
# TODO - Add option to allow user to specify default png
# TODO - Handle (MAME) roms which need individual config file/metadata subfolder
# TODO - Check images are png (check whether this is a requirement first)
# TODO - Incorporate defaults into optparse call
# TODO - Look in input dir for core
# TODO - Error handling:
# - Skyscraper fail
# - Can't create dirs/write files
# - Can't read gamelist.xml


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
    cmd_out = os.popen(cmd).read()
    print(cmd_out)


def set_paths(input_dir, output_dir, core_path, other_dir):
    temp_dir = tempfile.TemporaryDirectory().name
    return {
        'input_dir': input_dir,
        'core_path': core_path,
        'other_dir': other_dir,
        'output_dir': output_dir if output_dir else os.path.join(input_dir, 'output'),
        'temp_dir': temp_dir,
        'app_root_dir': os.path.split(os.path.realpath(__file__))[0],
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


def write_cart_xml(game_dir, game_title, game_desc):
    cart_xml = ''.join(configs.CARTRIDGE_XML) \
        .replace('GAME_TITLE', game_title) \
        .replace('GAME_DESCRIPTION', game_desc)
    write_file(os.path.join(game_dir, 'cartridge.xml'), cart_xml)


def write_exec_sh(game_dir, core_file_name, game_file_name):
    exec_sh = ''.join(configs.EXEC_SH) \
        .replace('CORE_FILE_NAME', core_file_name) \
        .replace('GAME_FILE_NAME', game_file_name)
    write_file(os.path.join(game_dir, 'exec.sh'), exec_sh)


def copy_dir_contents(source_dir, dest_dir):
    for file_name in os.listdir(source_dir):
        source_file_path = os.path.join(source_dir, file_name)
        if os.path.isfile(source_file_path):
            shutil.copy(source_file_path, os.path.join(dest_dir, file_name))


def copy_source_files(data_paths, game_data, game_dir):
    box_art_target_path = os.path.join(game_dir, 'boxart', 'boxart.png')
    shutil.copyfile(data_paths['core_path'], os.path.join(game_dir, 'emu', os.path.basename(data_paths['core_path'])))
    shutil.copyfile(game_data['rom_path'], os.path.join(game_dir, 'roms', os.path.basename(game_data['rom_path'])))
    try:
        shutil.copyfile(game_data['boxart_path'], box_art_target_path)
    except (TypeError, FileNotFoundError):
        shutil.copyfile(os.path.join(data_paths['app_root_dir'], 'common', 'title.png'), box_art_target_path)
    if data_paths['other_dir']:
        copy_dir_contents(data_paths['other_dir'], os.path.join(game_dir, 'roms'))
    os.symlink(box_art_target_path, os.path.join(game_dir, 'title.png'))


def setup_uce_source(data_paths, game_data, game_dir):
    safe_make_dir(game_dir)
    make_uce_sub_dirs(game_dir)
    write_cart_xml(game_dir, game_data['name'], game_data['description'])
    write_exec_sh(game_dir, os.path.basename(data_paths['core_path']), os.path.basename(game_data['rom_path']))
    copy_source_files(data_paths, game_data, game_dir)


def build_uce(data_paths, game_dir):
    target_path = os.path.join(data_paths['output_dir'], '{0}{1}'.format(os.path.basename(game_dir), '.UCE'))
    build_uce_tool.run(game_dir, target_path)


def build_uces(data_paths):
    game_list = read_gamelist(os.path.join(data_paths['temp_dir'], 'gamelist.xml'))
    for game_entry in game_list:
        game_data = parse_game_entry(game_entry)
        game_dir = os.path.join(data_paths['temp_dir'], os.path.splitext(os.path.basename(game_data['rom_path']))[0])
        setup_uce_source(data_paths, game_data, game_dir)
        build_uce(data_paths, game_dir)


def run(platform, input_dir, flags, scrape_source, user_creds, output_dir, core_path, other_dir, game_list):
    data_paths = set_paths(input_dir, output_dir, core_path, other_dir)
    setup(data_paths)
    if game_list:
        shutil.copy(game_list, os.path.join(data_paths['temp_dir'], 'gamelist.xml'))
    else:
        scrape(platform, flags, data_paths, scrape_source, user_creds)
        create_gamelist(platform, flags, data_paths)
    build_uces(data_paths)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help=cmd_help.PLATFORM)
    parser.add_option('-s', '--scraper', dest='scraper', help=cmd_help.SCRAPE_MODULE)
    parser.add_option('-u', '--usercreds', dest='user_creds', help=cmd_help.USER_CREDS)
    parser.add_option('-k', '--keepbrackets', dest='keep_brackets', help=cmd_help.KEEP_BRACKETS)
    parser.add_option('-a', '--allroms', dest='all_roms', help=cmd_help.ALL_ROMS)
    parser.add_option('-i', '--inputdir', dest='input_dir', help=cmd_help.INPUT_DIR)
    parser.add_option('-o', '--output', dest='output_dir', help=cmd_help.OUTPUT_DIR)
    parser.add_option('-c', '--core', dest='core', help=cmd_help.CORE)
    parser.add_option('-b', '--other', dest='other_dir', help=cmd_help.OTHER_DIR)
    parser.add_option('-g', '--gamelist', dest='game_list', help=cmd_help.GAME_LIST)
    return parser


def validate_opts(parser):
    (options, args) = parser.parse_args()
    valid = True
    if options.core is None:
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

    flags = configs.FLAGS
    input_dir = options.input_dir if options.input_dir else os.getcwd()
    scrape_source = options.scraper if options.scraper else 'screenscraper'
    user_creds = options.user_creds if options.user_creds else None
    output_dir = options.output_dir if options.output_dir else None
    other_dir = options.other_dir if options.other_dir else None
    game_list = options.game_list if options.game_list else None
    run(options.platform, input_dir, flags, scrape_source, user_creds, output_dir, options.core, other_dir, game_list)
