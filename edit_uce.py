#!/usr/bin/env python3
import sys
import os

from optparse import OptionParser
import tempfile

import common_utils

PLATFORM = common_utils.get_platform()

APP_ROOT = common_utils.get_app_root()


def split_uce(uce_path):
    data = common_utils.get_file_content(uce_path, 'rb')

    squashfs_etc = data[:-4194304]
    save_data = data[-4194304:]
    return squashfs_etc, save_data


def mount_image(img_path, save_data, mount_path):
    common_utils.write_file(img_path, save_data, 'wb')
    common_utils.make_dir(mount_path)
    if PLATFORM == 'win32':
        bin_ = os.path.join(APP_ROOT, 'windows', 'mount')
    else:
        bin_ = 'mount'
    cmd = [
        bin_,
        '-o',
        'loop',
        img_path,
        mount_path
    ]
    common_utils.execute_with_output(cmd)


def edit_image(mount_path, opts):
    if opts.retro_ini_path:
        common_utils.copyfile(opts.retro_ini_path, os.path.join(mount_path, 'upper', 'retroplayer.ini'))
    else:
        if PLATFORM == 'win32':
            bin_ = os.path.join('explorer.exe')
        else:
            bin_ = opts.file_manager
        common_utils.execute_with_output([bin_, mount_path])


def unmount_image(mount_path):
    if PLATFORM == 'win32':
        bin_ = os.path.join(APP_ROOT, 'windows', 'umount')
    else:
        bin_ = 'umount'
    cmd = [
        bin_,
        mount_path
    ]
    common_utils.execute_with_output(cmd)


def rebuild_uce(uce_path, squashfs_etc, img_path):
    save_data = common_utils.get_file_content(img_path, 'rb')
    common_utils.write_file(uce_path, squashfs_etc + save_data, 'wb')


def main(opts):
    temp_dir_obj = tempfile.TemporaryDirectory()
    temp_dir = temp_dir_obj.name
    common_utils.make_dir(temp_dir)
    if opts.do_backup:
        backup_path = opts.uce_path + '.bak'
        common_utils.copyfile(opts.uce_path, backup_path)
    squashfs_etc, save_data = split_uce(opts.uce_path)
    img_path = os.path.join(temp_dir, 'save.img')
    mount_path = os.path.join(temp_dir, 'mnt')
    mount_image(img_path, save_data, mount_path)
    edit_image(mount_path, opts)
    unmount_image(mount_path)
    rebuild_uce(opts.uce_path, squashfs_etc, img_path)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-u', '--uce', dest='uce_path', help="The UCE file you want to edit")
    parser.add_option('-r', '--retroini', dest='retro_ini_path', help="The UCE file you want to edit", default=None)
    parser.add_option('-f', '--fileman', dest='file_manager', help="Specify a particular file manager on Linux", default='thunar')
    parser.add_option('-B', '--backup', dest='do_backup', action='store_true', default=False)
    return parser


def validate_opts(parser):
    (opts, args) = parser.parse_args()
    if not opts.uce_path:
        parser.print_help()
        sys.exit(0)
    return opts, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = validate_opts(parser)
    main(opts)
