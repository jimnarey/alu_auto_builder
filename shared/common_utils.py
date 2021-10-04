#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import tempfile
import stat
import argparse
from subprocess import Popen, PIPE

from shared import error_messages, info_messages

# TODO - what can go wrong/should catch with os.getcwd() ?

active_temp_dirs = {}


# TODO - Issue a critical if this doesn't happen
def create_temp_dir(calling_module):
    try:
        temp_dir = tempfile.mkdtemp()
    except OSError as e:
        logging.error(error_messages.failed_to_create_temp_dir(e))
        return False
    logging.info(info_messages.created_temp_dir(calling_module))
    active_temp_dirs[calling_module] = temp_dir
    return temp_dir


# TODO - Issue a warning if this doesn't happen
def cleanup_temp_dir(calling_module):
    if calling_module in active_temp_dirs:
        remove_dir(active_temp_dirs[calling_module])


def execute_with_output(cmd, shell=False):
    try:
        with Popen(cmd, stdout=PIPE, bufsize=1,
                   universal_newlines=True, shell=shell) as p:
            for line in p.stdout:
                print(line, end='')
            return_code = p.wait()
        if return_code:
            logging.error(error_messages.command_exited_non_zero(return_code, cmd))
            return False
    except OSError as e:
        logging.error(error_messages.command_failed_with_exception(cmd, e))
        return False
    logging.info(info_messages.ran_command(cmd))
    return True


def write_file(file_path, file_content, write_type):
    try:
        with open(file_path, write_type) as target_file:
            target_file.write(file_content)
    except OSError as e:
        logging.error(error_messages.access_failure('write', file_path, e))
        return False
    logging.info(info_messages.access_success('wrote', file_path))
    return True


def get_file_content(file_path, read_type):
    try:
        with open(file_path, read_type) as read_file:
            content = read_file.read()
    except OSError as e:
        logging.error(error_messages.access_failure('read', file_path, e))
        return False
    logging.info(info_messages.access_success('read', file_path))
    return content


def make_dir(dir_path):
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        logging.info(info_messages.dir_already_exists(dir_path))
    except OSError as e:
        logging.error(error_messages.make_dir_failure(dir_path, e))
        return False
    logging.info(info_messages.make_dir_success(dir_path))
    return True


def remove_dir(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        logging.error(error_messages.delete_failure('directory', dir_path, e))
        return False
    logging.info(info_messages.remove_success('directory', dir_path))
    return True


def copyfile(source, dest):
    try:
        shutil.copy(source, dest)
    except OSError as e:
        logging.error(error_messages.copy_failure('file', source, dest, e))
        return False
    logging.info(info_messages.copy_success('file', source, dest))
    return True


def copytree(source, dest, symlinks=False):
    try:
        shutil.copytree(source, dest, symlinks=symlinks)
    except OSError as e:
        logging.error(error_messages.copy_failure('directory', source, dest, e))
        return False
    logging.info(info_messages.copy_success('directory', source, dest))
    return True


def create_symlink(target, symlink):
    try:
        os.symlink(target, symlink)
    except OSError as e:
        logging.error(error_messages.symlink_failure(symlink, target, e))
        return False
    logging.info(info_messages.symlink_success(symlink, target))
    return True


def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        logging.error(error_messages.delete_failure('file', file_path, e))
        return False
    logging.info(info_messages.remove_success('file', file_path))
    return True


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


def set_755(file_path):
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def validate_required_path(file_path, option_name=''):
    if not file_path or not os.path.isfile(file_path):
        logging.error(error_messages.invalid_path(option_name, file_path, 'file path'))
        return False
    return True


def validate_optional_dir(dir_path, option_name=''):
    if dir_path and not os.path.isfile(dir_path):
        logging.error(error_messages.invalid_path(option_name, dir_path, 'directory'))
        return False
    return True


def validate_existing_dir(dir_path, option_name=''):
    if not dir_path or not os.path.isdir(dir_path):
        logging.error(error_messages.invalid_path(option_name, dir_path, 'directory'))
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
        short_opt = '-{0}'.format(opt['short'])
        action, default = get_arg_params(opt['short'])
        parser.add_argument(long_opt, short_opt, dest=opt['name'], default=default, action=action)


# TODO Remove the 'optional arguments' message from --help
def get_cmd_line_args(opt_set):
    parser = argparse.ArgumentParser(prog='')
    add_arguments_to_parser(parser, opt_set)
    return parser

