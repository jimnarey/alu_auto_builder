#!/usr/bin/env python3

import os
import shutil
import errno
import xml.etree.ElementTree as ET

import configs
import build_uce_tool


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


def write_cart_xml(game_dir, game_name, game_desc):
    cart_xml = ''.join(configs.CARTRIDGE_XML)\
        .replace('GAME_TITLE', game_name)\
        .replace('GAME_DESCRIPTION', game_desc if game_desc else '')
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
