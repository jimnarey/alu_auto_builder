#!/usr/bin/env python3

import os
import time
import logging

from shared import common_utils, info_messages

logger = logging.getLogger(__name__)


def split_uce(input_path):
    logger.info(info_messages.split_uce(input_path))
    data = common_utils.get_file_content(input_path, 'rb')
    squashfs_etc_data = data[:-4194304]
    save_data = data[-4194304:]
    return squashfs_etc_data, save_data


def rebuild_uce(input_path, squashfs_etc_data, img_path):
    logger.info(info_messages.rebuild_uce(input_path))
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


def make_save_part_from_dir(temp_dir, root_dir_path, img_path):
    # debugfs_temp_dir = os.path.join(temp_dir, 'debugfs_temp')
    # common_utils.make_dir(debugfs_temp_dir)
    create_blank_file(img_path)
    # common_utils.recursive_chmod_rw(root_dir_path)
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
    # modify_inodes(debugfs_temp_dir, img_path)


def ls_img_dir(debugfs_temp_dir, img_path, img_dir):
    output_path = os.path.join(debugfs_temp_dir, 'debug_ls_out-{0}'.format(time.time_ns()))
    bin_ = common_utils.get_platform_bin('debugfs.exe', 'debugfs')
    cmd = "{0} -R 'ls -p {1}' {2} > {3}".format(bin_, img_dir, img_path, output_path)
    proc = os.popen(cmd)
    out = proc.read()
    print(out)
    return [line for line in common_utils.get_file_content(output_path, 'r').split('\n') if line]


def ls_recursive(debugfs_temp_dir, img_path, img_dir):
    dirs = []
    files = []
    for item in ls_img_dir(debugfs_temp_dir, img_path, img_dir):
        item_name = item.split('/')[5]
        if item[-2:] == '//':
            if item_name not in ('.', '..'):
                dirs.append('{0}{1}/'.format(img_dir, item_name))
        else:
            if item_name:
                files.append('{0}{1}'.format(img_dir, item_name))
    for dir_ in dirs:
        dirs_, files_ = ls_recursive(debugfs_temp_dir, img_path, dir_)
        dirs += dirs_
        files += files_
    return dirs, files


def modify_inode(item, img_path, perm_octal):
    bin_ = common_utils.get_platform_bin('debugfs.exe', 'debugfs')
    cmds = [
        "{0} -R 'sif {1} mode {2}' -w {3}".format(bin_, item, perm_octal, img_path),
        "{0} -R 'sif {1} gid 12' -w {2}".format(bin_, item, img_path),
        "{0} -R 'sif {1} uid 12' -w {2}".format(bin_, item, img_path),
        ]
    for cmd in cmds:
        proc = os.popen(cmd)
        out = proc.read()
        print(out)


def modify_inodes(debugfs_temp_dir, img_path):
    print('Modifying permissions for: ', img_path)
    logger.info(info_messages.modifying_save_part_perms(img_path))
    dirs, files = ls_recursive(debugfs_temp_dir, img_path, '/')
    print(dirs, files)
    for item in files:
        modify_inode(item, img_path, '0100777')
    for item in dirs:
        modify_inode(item[:-1], img_path, '040777')
