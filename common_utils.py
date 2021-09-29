#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import tempfile
import stat
import time
from subprocess import Popen, PIPE

# TODO - what can go wrong/should catch with os.getcwd() ?

active_temp_dirs = {}


# TODO - Issue a critical if this doesn't happen
def create_temp_dir(calling_module):
    try:
        temp_dir = tempfile.mkdtemp()
    except OSError as e:
        logging.error('Failed to create temp dir: '.format(e))
        return False
    logging.info('Created temp dir for module {0}'.format(calling_module))
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
            logging.error('Last command exited with error code {0}: {1}'.format(return_code, ' '.join(cmd)))
            return False
    except OSError as e:
        logging.error('Command failed to run: {0}'.format(' '.join(cmd)))
        return False
    logging.info('Successfully ran command: {0}'.format(' '.join(cmd)))
    return True


def simple_execute(cmd):
    try:
        cmd_out = os.popen(' '.join(cmd)).read()
    except OSError as e:
        logging.error('Last command does not appear to have completed successfully: {0}'.format(e))
        return False
    logging.info('Successfully ran command: {0}'.format(' '.join(cmd)))
    return True


def write_file(file_path, file_content, write_type):
    try:
        with open(file_path, write_type) as target_file:
            target_file.write(file_content)
    except OSError as e:
        logging.error('Failed to write data to {0}: {1}'.format(file_path, e))
        return False
    logging.info('Successfully wrote data to {0}'.format(file_path))
    return True


def get_file_content(file_path, read_type):
    try:
        with open(file_path, read_type) as read_file:
            content = read_file.read()
    except OSError as e:
        logging.error('Failed to read from file {0}: {1}'.format(file_path, e))
        return False
    logging.info('Successfully read data from {0}'.format(file_path))
    return content


def make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        logging.info('Directory {0} already exists'.format(path))
    except OSError as e:
        logging.error('Failed to create directory {0}: {1}'.format(path, e))
        return False
    logging.info('Successfully made new dir {0}'.format(path))
    return True


def remove_dir(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        logging.error('Failed to remove directory {0}: {1}'.format(dir_path, e))
        return False
    logging.info('Successfully removed directory {0}'.format(dir_path))
    return True


def copyfile(source, dest):
    try:
        shutil.copy(source, dest)
    except OSError as e:
        logging.error('Error copying {0} to {1}: {2}'.format(source, dest, e))
        return False
    logging.info('Successfully copied file {0} to {1}'.format(source, dest))
    return True


def copytree(source, dest, symlinks=False):
    try:
        shutil.copytree(source, dest, symlinks=symlinks)
    except OSError as e:
        logging.error('Error copying whole directory {0} to {1}: {2}'.format(source, dest, e))
        return False
    logging.info('Successfully copied whole directory {0} to {1}'.format(source, dest))
    return True


def create_symlink(target, symlink):
    try:
        os.symlink(target, symlink)
    except OSError as e:
        logging.error('Failed to create symlink {0} to target {1}: {2}'.format(symlink, target, e))
        return False
    logging.info('Successfully created symlink {0} to target {1}'.format(symlink, target))
    return True


def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        logging.error('Failed to delete file {0}: {1}'.format(file_path, e))
        return False
    logging.info('Successfully deleted file {0}'.format(file_path))
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
    return os.path.split(os.path.realpath(__file__))[0]


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
        logging.error('You must specify a valid path for {0}'.format(option_name))
        return False
    return True


def validate_optional_dir(dir_path, option_name=''):
    if dir_path and not os.path.isfile(dir_path):
        logging.error('You must specify a valid path for {0}'.format(option_name))
        return False
    return True


def validate_required_dir(dir_path, option_name=''):
    if not dir_path or not os.path.isdir(dir_path):
        logging.error('You must specify a valid path for {0}'.format(option_name))
        return False
    return True



# Deprecated

# def create_debugfs_write_cmd_file(temp_dir, items, source_path=None):
#     cmd_file_contents = []
#     for item in items:
#         target = item.replace('{0}/'.format(source_path), '') if source_path else item
#         cmd_file_contents.append('{0} "{1}" "/{2}"'.format('write', item, target))
#     return write_cmd_file(temp_dir, cmd_file_contents)

# def make_ext4_part(cart_save_file):
#     bin_ = get_platform_bin('make_ext4_part.bat', 'make_ext4_part.sh', linux_script=True)
#     cmd = [bin_, cart_save_file]
#     execute_with_output(cmd)
