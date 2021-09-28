#!/usr/bin/env python3
import pprint
import sys
import os
import logging
from optparse import OptionParser

import common_utils


def pre_flight(uce_path, replace_path, file_manager):
    valid = True
    if not uce_path or not os.path.isfile(uce_path):
        logging.error('You must provide a path to a UCE file to edit')
        valid = False
    if replace_path and not os.path.isfile(replace_path):
        logging.error('The provided path to a replacement save image is not valid')
        valid = False
    # if common_utils.get_platform() == 'linux' and os.getuid() != 0:
    #     logging.error('This tool must be run as root under Linux')
    #     valid = False
    return valid
    # TODO Check file_manager is a valid executable or select from those available


def split_uce(uce_path):
    logging.info('Splitting UCE file {0} into main section and save partition'.format(uce_path))
    data = common_utils.get_file_content(uce_path, 'rb')
    squashfs_etc = data[:-4194304]
    save_data = data[-4194304:]
    return squashfs_etc, save_data


def rebuild_uce(uce_path, squashfs_etc, img_path):
    save_data = common_utils.get_file_content(img_path, 'rb')
    common_utils.write_file(uce_path, squashfs_etc + save_data, 'wb')


def open_file_manager(path, file_manager):
    if common_utils.get_platform() == 'win32':
        bin_ = 'explorer.exe'
    else:
        bin_ = file_manager
    common_utils.execute_with_output([bin_, path])


def edit_contents(save_part_contents_path, retro_ini_path, file_manager):
    if retro_ini_path:
        common_utils.copyfile(retro_ini_path, os.path.join(save_part_contents_path, 'upper', 'retroplayer.ini'))
    else:
        open_file_manager(save_part_contents_path, file_manager)

# Mount-based edit functions


def mount_image(img_path, save_part_contents_path):
    cmd = [
        'mount',
        '-o',
        'loop',
        img_path,
        save_part_contents_path
    ]
    common_utils.execute_with_output(cmd)


def unmount_image(save_part_contents_path):
    cmd = [
        'umount',
        save_part_contents_path
    ]
    common_utils.execute_with_output(cmd)

# Cmd-based edit functions


def extract_img_contents(temp_dir, return_dir=os.getcwd()):
    bin_ = common_utils.get_platform_bin('debugfs.exe', 'debugfs')
    cmd_file_path = os.path.join(temp_dir, 'extract_cmd.txt')
    common_utils.write_file(cmd_file_path, 'rdump / save_part_contents', 'w')
    os.chdir(temp_dir)
    cmd = [
        bin_,
        '-f',
        cmd_file_path,
        'save.img'
    ]
    common_utils.execute_with_output(cmd)
    os.chdir(return_dir)


def get_save_contents(save_part_contents_path):
    save_dirs = []
    save_files = []
    for root, dirs, files in os.walk(save_part_contents_path):
        for dir_ in dirs:
            save_dirs.append(os.path.join(root, dir_))
        for file in files:
            save_files.append(os.path.join(root, file))
    return save_dirs, save_files


def set_all_755(save_part_contents_path):
    dirs, files = get_save_contents(save_part_contents_path)
    for file in files:
        common_utils.set_755(file)
    for dir_ in dirs:
        common_utils.set_755(dir_)


def edit_save_part_with_mount(img_path, save_part_contents_path, retro_ini_path, file_manager):
    if common_utils.get_platform() == 'linux' and os.getuid() == 0:
        mount_image(img_path, save_part_contents_path)
        edit_contents(save_part_contents_path, retro_ini_path, file_manager)
        unmount_image(save_part_contents_path)
        common_utils.remove_dir(save_part_contents_path)
        return True
    else:
        logging.error('Mount option is only available under Linux and when running as root')
        return False


def edit_save_part_with_cmds(temp_dir, img_path, save_part_contents_path, retro_ini_path, file_manager):
    extract_img_contents(temp_dir)
    set_all_755(save_part_contents_path)
    edit_contents(save_part_contents_path, retro_ini_path, file_manager)
    input('Press enter when ready')
    common_utils.delete_file(img_path)
    common_utils.create_blank_file(img_path)
    common_utils.make_save_part_from_dir(save_part_contents_path, img_path)
    return True


def edit_save_part(temp_dir, img_path, save_part_contents_path, retro_ini_path, file_manager, mount_method):
    if mount_method:
        return edit_save_part_with_mount(img_path, save_part_contents_path, retro_ini_path, file_manager)
    else:
        return edit_save_part_with_cmds(temp_dir, img_path, save_part_contents_path, retro_ini_path, file_manager)


def main(uce_path, extract_path=None, replace_path=None, backup_uce=False, mount_method=False, retro_ini_path=None, file_manager=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    uce_path = os.path.abspath(uce_path)
    if not pre_flight(uce_path, replace_path, file_manager):
        return False
    temp_dir = common_utils.create_temp_dir(__name__)
    file_manager = file_manager if file_manager else 'thunar'
    # Split the UCE and store the two parts in byte-strings
    squashfs_etc, save_data = split_uce(uce_path)
    # Set paths
    img_path = os.path.join(temp_dir, 'save.img')
    # Write the save partition to file
    common_utils.write_file(img_path, save_data, 'wb')
    if extract_path:
        common_utils.copyfile(img_path, extract_path)
        return True
    if backup_uce:
        backup_path = uce_path + '.bak'
        common_utils.copyfile(uce_path, backup_path)
    # Read files from the save partition and create a replacement
    if replace_path:
        rebuild_uce(uce_path, squashfs_etc, replace_path)
        return True
    save_part_contents_path = os.path.join(temp_dir, 'save_part_contents')
    common_utils.make_dir(save_part_contents_path)
    if edit_save_part(temp_dir, img_path, save_part_contents_path, retro_ini_path, file_manager, mount_method):
        rebuild_uce(uce_path, squashfs_etc, img_path)
    common_utils.cleanup_temp_dir(__name__)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-u', '--uce', dest='uce_path', help="The UCE file you want to edit", default=None)
    parser.add_option('-e', '--extract', dest='extract_path', help="Extract the save partition to specified path and quit", default=None)
    parser.add_option('-B', '--backup', dest='backup_uce', action='store_true',
                      help="Backup the UCE before any write operations", default=False)
    parser.add_option('-r', '--replace', dest='replace_path', help="Replace the save partition with the specified save.img, ignore subsequent options", default=None)
    parser.add_option('-M', '--mount', dest='mount_method', action='store_true', help="Use mount method of editing UCE, Linux only", default=False)
    parser.add_option('-i', '--retroini', dest='retro_ini_path', help="The UCE file you want to edit", default=None)
    parser.add_option('-f', '--fileman', dest='file_manager', help="Specify a particular file manager on Linux", default=None)
    return parser


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = parser.parse_args()
    main(opts.uce_path,  extract_path=opts.extract_path, replace_path=opts.replace_path, backup_uce=opts.backup_uce,
         mount_method=opts.mount_method, retro_ini_path=opts.retro_ini_path, file_manager=opts.file_manager)
