#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import tempfile
import stat
import argparse
import re
import csv
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ParseError
from subprocess import Popen, PIPE

from PIL import Image, UnidentifiedImageError
import requests

from shared import error_messages, info_messages

# TODO - what can go wrong/should catch with os.getcwd() ?

logger = logging.getLogger(__name__)

ANSI_ESCAPE = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

SPECIAL_CHARS = '\'"<>:/\|?*'

active_temp_dirs = {}


# TODO - Issue a critical if this doesn't happen
def create_temp_dir(calling_module):
    try:
        temp_dir = tempfile.mkdtemp()
    except OSError as e:
        logger.error(error_messages.failed_to_create_temp_dir(e))
        return False
    logger.info(info_messages.created_temp_dir(calling_module))
    active_temp_dirs[calling_module] = temp_dir
    return temp_dir


# TODO - Issue a warning if this doesn't happen
def cleanup_temp_dir(calling_module):
    if calling_module in active_temp_dirs:
        remove_dir(active_temp_dirs[calling_module])


def escape_ansi(line):
    return ANSI_ESCAPE.sub('', line)


def remove_special_chars(text, replace_val=''):
    for char in SPECIAL_CHARS:
        text = text.replace(char, replace_val)
    return text


def execute_with_output(cmd, shell=False):
    try:
        with Popen(cmd, stdout=PIPE, bufsize=1,
                   universal_newlines=True, shell=shell) as p:
            for line in p.stdout:
                log_text = escape_ansi(line.strip())
                if log_text:
                    logger.info(log_text)
            return_code = p.wait()
        if return_code:
            logger.error(error_messages.command_exited_non_zero(return_code, cmd))
            return False
    except OSError as e:
        logger.error(error_messages.command_failed_with_exception(cmd, e))
        return False
    logger.info(info_messages.ran_command(cmd))
    return True


def write_file(file_path, file_content, write_type):
    try:
        with open(file_path, write_type) as target_file:
            target_file.write(file_content)
    except OSError as e:
        logger.error(error_messages.access_failure('write', file_path, e))
        return False
    logger.info(info_messages.access_success('wrote', file_path))
    return True


def write_csv(file_path, rows):
    try:
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)
    except OSError as e:
        logger.error(error_messages.access_failure('write', file_path, e))
        return False
    logger.info(info_messages.access_success('wrote', file_path))
    return True


def get_file_content(file_path, read_type):
    try:
        with open(file_path, read_type) as read_file:
            content = read_file.read()
    except OSError as e:
        logger.error(error_messages.access_failure('read', file_path, e))
        return False
    logger.info(info_messages.access_success('read', file_path))
    return content


def make_dir(dir_path):
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        logger.info(info_messages.dir_already_exists(dir_path))
    except OSError as e:
        logger.error(error_messages.make_dir_failure(dir_path, e))
        return False
    logger.info(info_messages.make_dir_success(dir_path))
    return True


def remove_dir(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        logger.error(error_messages.delete_failure('directory', dir_path, e))
        return False
    logger.info(info_messages.remove_success('directory', dir_path))
    return True


def copyfile(source, dest):
    try:
        shutil.copy(source, dest)
    except OSError as e:
        logger.error(error_messages.copy_failure('file', source, dest, e))
        return False
    logger.info(info_messages.copy_success('file', source, dest))
    return True


def copytree(source, dest, symlinks=False):
    try:
        shutil.copytree(source, dest, symlinks=symlinks)
    except OSError as e:
        logger.error(error_messages.copy_failure('directory', source, dest, e))
        return False
    logger.info(info_messages.copy_success('directory', source, dest))
    return True


def create_symlink(target, symlink):
    try:
        os.symlink(target, symlink)
    except PermissionError:
        logger.warning(error_messages.symlink_failure_permissions(symlink, target))
        return False
    except OSError as e:
        logger.error(error_messages.symlink_failure_other(symlink, target, e))
        return False
    logger.info(info_messages.symlink_success(symlink, target))
    return True


def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        logger.error(error_messages.delete_failure('file', file_path, e))
        return False
    logger.info(info_messages.remove_success('file', file_path))
    return True


def download_data(url):
    try:
        data = requests.get(url)
        if 400 <= data.status_code < 600:
            logger.error('Server returned status code {0} for {1}'.format(url, data.status_code))
            data = None
        logger.info('Downloaded remote file {0}'.format(url))
    except Exception as e:
        logger.error('Failed to fetch {0}: {1}'.format(url, e))
        data = None
    return data


def download_file(url, save_path, write_type='wb'):
    data = download_data(url)
    write_file(save_path, data.content, write_type)


def get_platform():
    if sys.platform.startswith('linux'):
        return 'linux'
    if sys.platform in ('win32'):
        return sys.platform
    return False


def get_app_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.realpath(os.path.split(os.path.dirname(__file__))[0])


def get_platform_bin(windows_bin, linux_bin, linux_script=False):
    if get_platform() == 'win32':
        bin_ = os.path.join(get_app_root(), 'windows', windows_bin)
    else:
        bin_ = os.path.join(get_app_root(), 'bash_scripts', linux_bin) if linux_script else linux_bin
    return bin_


def set_755(path):
    os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def set_666(path):
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)


def set_766(path):
    os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)


def recursive_chmod_rw(root_path):
    set_766(root_path)
    for root, dirs, files in os.walk(root_path):
        for dir in dirs:
            set_766(os.path.join(root, dir))
        for file in files:
            set_666(os.path.join(root, file))


def validate_required_path(file_path, option_name=''):
    if not file_path or not os.path.isfile(file_path):
        logger.error(error_messages.invalid_path(option_name, file_path, 'file path'))
        return False
    return True


def validate_optional_dir(dir_path, option_name=''):
    if dir_path and not os.path.isdir(dir_path):
        logger.error(error_messages.invalid_path(option_name, dir_path, 'directory'))
        return False
    return True


def validate_existing_dir(dir_path, option_name=''):
    if not dir_path or not os.path.isdir(dir_path):
        logger.error(error_messages.invalid_path(option_name, dir_path, 'directory'))
        return False
    return True


def validate_parent_dir(dir_path, option_name=''):
    if dir_path and not validate_existing_dir(os.path.split(dir_path)[0], option_name=option_name):
        return False
    return True


def get_arg_params(opt_short_name):
    if opt_short_name.islower():
        action = 'store'
        default = None
    else:
        action = 'store_true'
        default = False
    return action, default


def add_arguments_to_parser(parser, opt_set):
    for opt in opt_set:
        long_opt = '--{0}'.format(opt['name']).replace('_', '')
        short_opt = '-{0}'.format(opt['cli_short'])
        action, default = get_arg_params(opt['cli_short'])
        parser.add_argument(long_opt, short_opt, dest=opt['name'], default=default, action=action, help=opt['help'])


# TODO Remove the 'optional arguments' message from --help
def get_cmd_line_args(opt_set):
    parser = argparse.ArgumentParser(prog='')
    add_arguments_to_parser(parser, opt_set)
    return parser


def read_gamelist_tree(input_path):
    try:
        tree = ET.parse(input_path)
    except ParseError:
        logger.error(error_messages.invalid_path('Specified gamelist', input_path, 'XML file'))
        return False
    return tree


def get_game_entry_val(game_entry, tag_name):
    tag = game_entry.find(tag_name)
    if tag is not None and tag.text is not None:
        return tag.text
    return ''


def parse_game_entry(game_entry):
    return {
        'name': get_game_entry_val(game_entry, 'name'),
        'rom_path': get_game_entry_val(game_entry, 'path'),
        'boxart_path': get_game_entry_val(game_entry, 'thumbnail'),
        'marquee_path': get_game_entry_val(game_entry, 'marquee'),
        'logo_path': get_game_entry_val(game_entry, 'image'),
        'video_path': get_game_entry_val(game_entry, 'video'),
        'description': get_game_entry_val(game_entry, 'desc'),
        'genre': get_game_entry_val(game_entry, 'genre'),
        'publisher': get_game_entry_val(game_entry, 'publisher'),
        'players': get_game_entry_val(game_entry, 'players'),
        'bezel_match': get_game_entry_val(game_entry, 'bezel_match'),
        'bezel_path': get_game_entry_val(game_entry, 'bezel_path')
    }


def score_to_int(value):
    try:
        return int(value.strip())
    except ValueError as e:
        logger.error(error_messages.score_not_number(value, e))
    return 0


def resize_and_save_image(source_path, dest_path, x, y, image_format='PNG'):
    try:
        img = Image.open(source_path)
        img = img.resize((x, y))
        img.save(dest_path, image_format)
        logger.info(info_messages.image_resize_success(source_path, dest_path))
        return True
    except (OSError, FileNotFoundError, UnidentifiedImageError, ValueError) as e:
        logger.error(error_messages.image_resize_failure(source_path, dest_path, x, y, e))


def get_basename_no_ext(path):
    return os.path.splitext(os.path.basename(path))[0]
