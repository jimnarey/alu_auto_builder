#!/usr/bin/env python3

import os
import logging
import time

from shared import common_utils

logger = logging.getLogger(__name__)


def split_uce(input_path):
    logger.info('Splitting UCE file {0} into main section and save partition'.format(input_path))
    data = common_utils.get_file_content(input_path, 'rb')
    squashfs_etc_data = data[:-4194304]
    save_data = data[-4194304:]
    return squashfs_etc_data, save_data


def rebuild_uce(input_path, squashfs_etc_data, img_path):
    save_data = common_utils.get_file_content(img_path, 'rb')
    common_utils.write_file(input_path, squashfs_etc_data + save_data, 'wb')


# def write_cmd_file(temp_dir, contents):
#     cmd_file_path = os.path.join(temp_dir, 'debug_fs_cmd.txt-{0}'.format(time.time_ns()))
#     common_utils.write_file(cmd_file_path, '\n'.join(contents) + '\n', 'w')
#     return cmd_file_path


# def create_debugfs_mkdir_cmd_file(temp_dir, items, source_path=None):
#     cmd_file_contents = []
#     for item in items:
#         target = item.replace('{0}/'.format(source_path), '') if source_path else item
#         cmd_file_contents.append('{0} "/{1}"'.format('mkdir', target))
#     return write_cmd_file(temp_dir, cmd_file_contents)
#
#
# def run_debugfs_cmd_file(cmd_file, img_path, return_dir=os.getcwd()):
#     bin_ = common_utils.get_platform_bin('debugfs.exe', 'debugfs')
#     cmd = [
#         bin_,
#         '-w',
#         '-f',
#         cmd_file,
#         img_path
#     ]
#     common_utils.execute_with_output(cmd)
#
#
# def create_save_part_base_dirs(temp_dir, img_path):
#     cmd_file = create_debugfs_mkdir_cmd_file(temp_dir, ['work', 'upper'])
#     run_debugfs_cmd_file(cmd_file, img_path)


def create_blank_file(file_path, size=4194304):
    bin_ = common_utils.get_platform_bin('truncate.exe', 'truncate')
    cmd = [
        bin_,
        '-s',
        str(size),
        file_path
    ]
    common_utils.execute_with_output(cmd)


# def make_ext4_part(cart_save_file):
#     create_blank_file(cart_save_file)
#     bin_ = common_utils.get_platform_bin('mke2fs.exe', 'mke2fs')
#     cmd = [
#         bin_,
#         '-t',
#         'ext4',
#         cart_save_file
#     ]
#     common_utils.execute_with_output(cmd)


def make_save_part_from_dir(root_dir_path, img_path):
    create_blank_file(img_path)
    bin_ = common_utils.get_platform_bin('mke2fs.exe', 'mke2fs')
    cmd = [
        bin_,
        '-d',
        root_dir_path,
        '-t',
        'ext4',
        img_path
    ]
    common_utils.execute_with_output(cmd)
