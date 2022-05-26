#!/usr/bin/env python3

import os
import logging

from shared import common_utils, configs, info_messages
import operations

logger = logging.getLogger(__name__)

MAX_FILE_NAME_LENGTH = 62


def validate_args(input_path, core_path, bios_dir, output_dir):
    logger.info('Validating arguments for build_recipes')
    valid = True
    if not common_utils.validate_required_path(input_path, 'Specified gamelist'):
        valid = False
    if not common_utils.validate_required_path(core_path, 'Specified core'):
        valid = False
    if not common_utils.validate_parent_dir(output_dir, 'Output dir'):
        valid = False
    if not common_utils.validate_optional_dir(bios_dir, 'Bios dir'):
        valid = False
    return valid


def get_target_filename(filename):
    filename = common_utils.remove_special_chars(filename)
    if len(filename) > MAX_FILE_NAME_LENGTH:
        name, ext = os.path.splitext(filename)
        name_max_length = MAX_FILE_NAME_LENGTH - len(ext)
        while len(name) > name_max_length:
            name = common_utils.remove_bracketed_text(name)
            name = name[:name_max_length]
        filename = '{0}{1}'.format(name, ext)
    return filename


def make_uce_sub_dirs(game_dir):
    for sub_dir in ('emu', 'roms', 'boxart', 'save'):
        common_utils.make_dir(os.path.join(game_dir, sub_dir))


def write_cart_xml(game_dir, game_name, game_desc):
    cart_xml = ''.join(configs.CARTRIDGE_XML)\
        .replace('GAME_TITLE', game_name)\
        .replace('GAME_DESCRIPTION', game_desc if game_desc else '')
    common_utils.write_file(os.path.join(game_dir, 'cartridge.xml'), cart_xml, 'w')


def write_exec_sh(game_dir, core_file_name, game_file_name):
    exec_sh = ''.join(configs.EXEC_SH) \
        .replace('CORE_FILE_NAME', core_file_name) \
        .replace('GAME_FILE_NAME', game_file_name)
    common_utils.write_file(os.path.join(game_dir, 'exec.sh'), exec_sh, 'w')


def copy_dir_contents(source_dir, dest_dir):
    for file_name in os.listdir(source_dir):
        source_file_path = os.path.join(source_dir, file_name)
        if os.path.isfile(source_file_path):
            common_utils.copyfile(source_file_path, os.path.join(dest_dir, file_name))


def copy_and_resize_bezel(game_data, game_dir):
    bezel_path = game_data['bezel_path']
    if bezel_path:
        common_utils.resize_and_save_image(bezel_path, os.path.join(game_dir, 'boxart', 'addon.z.png'), 1280, 720)


def copy_boxart(game_data, game_dir):
    boxart_source_path = game_data['boxart_path']
    box_art_target_path = os.path.join(game_dir, 'boxart', 'boxart.png')
    if boxart_source_path:
        common_utils.copyfile(boxart_source_path, box_art_target_path)
    else:
        logger.info(info_messages.NO_BOXART_FOUND)
        common_utils.copyfile(os.path.join(common_utils.get_app_root(), 'data', 'title.png'), box_art_target_path)
    if not common_utils.create_symlink(box_art_target_path, os.path.join(game_dir, 'title.png')):
        logger.info(info_messages.COPY_SYMLINK_FAILED)
        common_utils.copyfile(game_data['boxart_path'], os.path.join(game_dir, 'title.png'))


def copy_source_files(core_path, bios_dir, game_data, game_dir, target_rom_filename):
    common_utils.copyfile(core_path, os.path.join(game_dir, 'emu', os.path.basename(core_path)))
    common_utils.copyfile(game_data['rom_path'], os.path.join(game_dir, 'roms', target_rom_filename))
    copy_boxart(game_data, game_dir)
    copy_and_resize_bezel(game_data, game_dir)
    if bios_dir:
        copy_dir_contents(bios_dir, os.path.join(game_dir, 'roms'))


def setup_uce_source(core_path, bios_dir, game_data, output_dir):
    # Modify the target_rom_filename to deal with limitations on exec.sh rom name length, special chars
    # target_rom_filename = common_utils.remove_special_chars(os.path.basename(game_data['rom_path']))
    target_rom_filename = get_target_filename(os.path.basename(game_data['rom_path']))
    game_dir = os.path.join(output_dir, os.path.splitext(target_rom_filename)[0])
    common_utils.make_dir(game_dir)
    make_uce_sub_dirs(game_dir)
    cart_xml_game_name = game_data['name'] if game_data['name'] else os.path.splitext(target_rom_filename)[0]
    write_cart_xml(game_dir, cart_xml_game_name, game_data['description'])
    write_exec_sh(game_dir, os.path.basename(core_path), target_rom_filename)
    copy_source_files(core_path, bios_dir, game_data, game_dir, target_rom_filename)


def main(input_path, core_path, bios_dir=None, output_dir=None):
    if not validate_args(input_path, core_path, bios_dir, output_dir):
        return
    output_dir = os.path.abspath(output_dir) if output_dir else os.path.join(os.path.split(os.path.abspath(input_path))[0], 'recipes')
    common_utils.make_dir(output_dir)
    gamelist = common_utils.read_gamelist_tree(input_path).getroot()
    if gamelist:
        for game_entry in gamelist:
            game_data = common_utils.parse_game_entry(game_entry)
            setup_uce_source(core_path, bios_dir, game_data, output_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(asctime)s : %(message)s", datefmt="%H:%M:%S")
    parser = common_utils.get_cmd_line_args(operations.operations['gamelist_to_recipes']['options'])
    args = vars(parser.parse_args())
    main(args['input_path'], args['core_path'], bios_dir=args['bios_dir'], output_dir=args['output_dir'])



