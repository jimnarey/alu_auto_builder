#!/usr/bin/env python3

import logging

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


def create_blank_file(file_path, size=4194304):
    bin_ = common_utils.get_platform_bin('truncate.exe', 'truncate')
    cmd = [
        bin_,
        '-s',
        str(size),
        file_path
    ]
    common_utils.execute_with_output(cmd)


def make_save_part_from_dir(root_dir_path, img_path):
    create_blank_file(img_path)
    common_utils.recursive_chmod_rw(root_dir_path)
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
