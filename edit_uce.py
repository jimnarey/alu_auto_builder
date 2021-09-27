#!/usr/bin/env python3
import pprint
import sys
import os
import logging
from optparse import OptionParser

import common_utils


# APP_ROOT = common_utils.get_app_root()

def pre_flight(uce_path, file_manager):
    valid = True
    if not uce_path or not os.path.isfile(uce_path):
        logging.error('You must provide a path to a UCE file to edit')
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


#
# START Mount method functions
#


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

#
# END mount method functions
#

#
# START debugfs method functions
#


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


# def run_debugfs_cmd_file(save_part_contents_path, cmd_file, img_path, return_dir=os.getcwd()):
#     bin_ = common_utils.get_platform_bin('debugfs.exe', 'debugfs')
#     os.chdir(save_part_contents_path)
#     cmd = [
#         bin_,
#         '-w',
#         '-f',
#         cmd_file,
#         img_path
#     ]
#     common_utils.execute_with_output(cmd)
#     os.chdir(return_dir)


def copy_into_save_img(temp_dir, save_part_contents_path, img_path):
    dirs, files = get_save_contents(save_part_contents_path)
    pprint.pprint(dirs)
    pprint.pprint(files)
    # dirs = common_utils.remove_run_dir_prefixes(dirs, save_part_contents_path)
    # files = common_utils.remove_run_dir_prefixes(files, save_part_contents_path)
    pprint.pprint(dirs)
    pprint.pprint(files)
    mkdir_cmd_file_path = common_utils.create_debugfs_mkdir_cmd_file(temp_dir, dirs, save_part_contents_path)
    write_cmd_file_path = common_utils.create_debugfs_write_cmd_file(temp_dir, files, save_part_contents_path)
    common_utils.run_debugfs_cmd_file(mkdir_cmd_file_path, img_path)
    common_utils.run_debugfs_cmd_file(write_cmd_file_path, img_path)


#
# END debugfs method functions
#


def access_save_contents(temp_dir, img_path, save_part_contents_path, retro_ini_path, file_manager, do_mount):
    if do_mount:
        if common_utils.get_platform() == 'linux' and os.getuid() == 0:
            mount_image(img_path, save_part_contents_path)
            edit_contents(save_part_contents_path, retro_ini_path, file_manager)
            unmount_image(save_part_contents_path)
            common_utils.remove_dir(save_part_contents_path)
            return True
        else:
            logging.error('Mount option is only available under Linux and when running as root')
            return False
    else:
        extract_img_contents(temp_dir)
        set_all_755(save_part_contents_path)
        edit_contents(save_part_contents_path, retro_ini_path, file_manager)
        # logging.info('Files available at {0}'.format(save_part_contents_path))
        input('Press enter when ready')
        common_utils.delete_file(img_path)
        common_utils.make_ext4_part(img_path)
        copy_into_save_img(temp_dir, save_part_contents_path, img_path)
        return True


# def main(opts):
def main(uce_path, do_backup=False, do_mount=False, retro_ini_path=None, file_manager=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    uce_path = os.path.abspath(uce_path)
    if not pre_flight(uce_path, file_manager):
        return False
    temp_dir = common_utils.create_temp_dir(__name__)
    file_manager = file_manager if file_manager else 'thunar'
    if do_backup:
        backup_path = uce_path + '.bak'
        common_utils.copyfile(uce_path, backup_path)
    # Split the UCE and store the two parts in byte-strings
    squashfs_etc, save_data = split_uce(uce_path)
    # Set paths
    img_path = os.path.join(temp_dir, 'save.img')
    save_part_contents_path = os.path.join(temp_dir, 'save_part_contents')
    # Write the save partition to file and create dir for contents
    common_utils.write_file(img_path, save_data, 'wb')
    common_utils.make_dir(save_part_contents_path)
    # Read files from the save partition and create a replacement
    if access_save_contents(temp_dir, img_path, save_part_contents_path, retro_ini_path, file_manager, do_mount):
        rebuild_uce(uce_path, squashfs_etc, img_path)
    common_utils.cleanup_temp_dir(__name__)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-u', '--uce', dest='uce_path', help="The UCE file you want to edit", default=None)
    parser.add_option('-B', '--backup', dest='do_backup', action='store_true', help="Create a backup of the UCE before editing", default=False)
    parser.add_option('-M', '--mount', dest='do_mount', action='store_true', help="Use mount method of editing UCE, Linux only", default=False)
    parser.add_option('-r', '--retroini', dest='retro_ini_path', help="The UCE file you want to edit", default=None)
    parser.add_option('-f', '--fileman', dest='file_manager', help="Specify a particular file manager on Linux", default=None)

    return parser


# def validate_opts(parser):
#     (opts, args) = parser.parse_args()
#     if not opts.uce_path:
#         parser.print_help()
#         sys.exit(0)
#     return opts, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = parser.parse_args()
    main(opts.uce_path, do_backup=opts.do_backup, do_mount=opts.do_mount, retro_ini_path=opts.retro_ini_path,
         file_manager=opts.file_manager)
