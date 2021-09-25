#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import tempfile
import stat
import errno
from subprocess import Popen, PIPE

active_temp_dirs = {}


# TODO - Issue a critical if this doesn't happen
def create_temp_dir(calling_module):
    logging.info('Attempting to create temp dir')
    try:
        temp_dir = tempfile.mkdtemp()
    except OSError as e:
        logging.error('Failed to create temp dir: '.format(e))
        return False
    active_temp_dirs[calling_module] = temp_dir
    return temp_dir


# TODO - Issue a warning if this doesn't happen
def cleanup_temp_dir(calling_module):
    if calling_module in active_temp_dirs:
        logging.info('Attempting to remove temp dir')
        remove_dir(active_temp_dirs[calling_module])


def execute_with_output(cmd):
    logging.info('Running command: {0}'.format(' '.join(cmd)))
    with Popen(cmd, stdout=PIPE, bufsize=1,
               universal_newlines=True) as p:
        print('PID ', p.pid)
        for line in p.stdout:
            print(line, end='')
        return_code = p.wait()
    if return_code:
        logging.error('Last command does not appear to have completed successfully')
    return return_code


def write_file(file_path, file_content, write_type):
    logging.info('Writing data to {0}'.format(file_path))
    try:
        with open(file_path, write_type) as target_file:
            target_file.write(file_content)
    except OSError as e:
        logging.error('Unable to write to {0}: {1}'.format(file_path, e))


def get_file_content(file_path, read_type):
    logging.info('Reading data from {0}'.format(file_path))
    try:
        with open(file_path, read_type) as read_file:
            content = read_file.read()
    except OSError as e:
        logging.error('Unable to read from file {0}: {1}'.format(file_path, e))
    return content


def make_dir(path):
    logging.info('Attempting to make new dir {0}'.format(path))
    try:
        os.mkdir(path)
    except FileExistsError:
        logging.info('Directory {0} already exists'.format(path))
    except OSError as e:
        logging.error('Failed to create directory {0}: {1}'.format(path, e))


def remove_dir(dir_path):
    logging.info('Attempting to remove directory {0}'.format(dir_path))
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        logging.error('Failed to remove directory {0}: {1}'.format(dir_path, e))
        return False
    return True


def copyfile(source, dest):
    logging.info('Copying file {0} to {1}'.format(source, dest))
    try:
        shutil.copy(source, dest)
    except OSError as e:
        logging.error('Error copying {0} to {1}: {2}'.format(source, dest, e))


def copytree(source, dest, symlinks=False):
    logging.info('Copying whole directory {0} to {1}'.format(source, dest))
    try:
        shutil.copytree(source, dest, symlinks=symlinks)
    except OSError as e:
        logging.error('Error copying whole directory {0} to {1}: {2}'.format(source, dest, e))


def create_symlink(target, symlink):
    logging.info('Attempting to create symlink {0} to target {1}'.format(symlink, target))
    try:
        os.symlink(target, symlink)
    except OSError as e:
        logging.error('Failed to create symlink {0} to target {1}: {2}'.format(symlink, target, e))


def delete_file(file_path):
    logging.info('Attempting to delete file {0}'.format(file_path))
    try:
        os.remove(file_path)
    except OSError as e:
        logging.error('Failed to delete file {0}: {1}'.format(file_path, e))


def get_platform():
    if sys.platform.startswith('linux'):
        return 'linux'
    # if sys.platform in ('darwin', 'win32'):    
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


def make_ext4_part(cart_save_file):
    bin_ = get_platform_bin('make_ext4_part.bat', 'make_ext4_part.sh', linux_script=True)
    cmd = [bin_, cart_save_file]
    execute_with_output(cmd)


def set_755(file_path):
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

