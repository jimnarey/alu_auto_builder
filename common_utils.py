#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import tempfile
import stat
import time
import errno
import pprint
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
    # logging.info('Running command: {0}'.format(' '.join(cmd)))
    with Popen(cmd, stdout=PIPE, bufsize=1,
               universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')
        return_code = p.wait()
    logging.info('Successfully ran command: {0}'.format(' '.join(cmd)))
    if return_code:
        logging.error('Last command does not appear to have completed successfully')
    return return_code


def simple_execute(cmd):
    try:
        cmd_out = os.popen(' '.join(cmd)).read()
        # logging.info('Waiting....')
        # time.sleep(3)
        print(cmd_out)
        logging.info('Successfully ran command: {0}'.format(' '.join(cmd)))
    except OSError as e:
        logging.error('Last command does not appear to have completed successfully: {0}'.format(e))


def write_file(file_path, file_content, write_type):
    logging.info('Writing data to {0}'.format(file_path))
    try:
        with open(file_path, write_type) as target_file:
            target_file.write(file_content)
    except OSError as e:
        logging.error('Unable to write to {0}: {1}'.format(file_path, e))


# TODO - Fix ref before assignment
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


# def remove_run_dir_prefixes(items, run_dir):
#     return [item.replace('{0}/'.format(run_dir), '') for item in items]

# def remove_source_path(item, source_path):
#     return item.replace('{0}/'.format(source_path), '')


def write_cmd_file(temp_dir, contents):
    cmd_file_path = os.path.join(temp_dir, 'debug_fs_cmd.txt')
    write_file(cmd_file_path, '\n'.join(contents), 'w')
    print(get_file_content(cmd_file_path, 'r'))
    return cmd_file_path

#
# def split_dirs_debugfs(dirs):


def create_debugfs_mkdir_cmd_file(temp_dir, items, source_path=None):
    cmd_file_contents = []
    for item in items:
        target = item.replace('{0}/'.format(source_path), '') if source_path else item
        cmd_file_contents.append('{0} "/{1}"'.format('mkdir', target))
    return write_cmd_file(temp_dir, cmd_file_contents)


def create_debugfs_write_cmd_file(temp_dir, items, source_path=None):
    cmd_file_contents = []
    for item in items:
        target = item.replace('{0}/'.format(source_path), '') if source_path else item
        cmd_file_contents.append('{0} "{1}" "/{2}"'.format('write', item, target))
    return write_cmd_file(temp_dir, cmd_file_contents)


def run_debugfs_cmd_file(cmd_file, img_path, return_dir=os.getcwd()):
    bin_ = get_platform_bin('debugfs.exe', 'debugfs')
    # os.chdir(run_dir)
    cmd = [
        bin_,
        '-w',
        '-f',
        cmd_file,
        img_path
    ]
    # execute_with_output(cmd)
    simple_execute(cmd)
    # os.chdir(return_dir)


# def create_debugfs_cmd_file(temp_dir, save_part_contents_path, items, cmd):
#     cmd_file_contents = []
#     for item in items:
#         item = item.replace(save_part_contents_path, '')
#         if cmd == 'mkdir':
#             # TODO - Add " to dirname and test
#             cmd_file_contents.append('{0} {1}'.format(cmd, item))
#         elif cmd == 'write':
#             cmd_file_contents.append('{0} "{1}" "{2}"'.format(cmd, item[1:], item))
#     cmd_file_path = os.path.join(temp_dir, '{0}_cmd.txt'.format(cmd))
#     common_utils.write_file(cmd_file_path, '\n'.join(cmd_file_contents), 'w')
#     return cmd_file_path


def create_blank_file(file_path, size=4194304):
    bin_ = get_platform_bin('truncate.exe', 'truncate')
    cmd = [
        bin_,
        '-s',
        str(size),
        file_path
    ]
    execute_with_output(cmd)


def make_ext4_part_2(cart_save_file):
    create_blank_file(cart_save_file)
    bin_ = get_platform_bin('mke2fs.exe', 'mke2fs')
    cmd = [
        bin_,
        '-t',
        'ext4',
        cart_save_file
    ]
    execute_with_output(cmd)


def create_save_part_base_dirs(temp_dir, img_path):
    cmd_file = create_debugfs_mkdir_cmd_file(temp_dir, ['work', 'upper'])
    run_debugfs_cmd_file(cmd_file, img_path)


def set_755(file_path):
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

