#!/usr/bin/env python3

import os
import logging
import shutil

from shared import common_utils, info_messages, uce_utils, error_messages
import operations


def validate_file_manager(file_manager):
    valid = True
    if common_utils.get_platform() == 'linux':
        if file_manager:
            if common_utils.get_platform() != 'linux':
                logging.error(error_messages.FILEMAN_NOT_LINUX)
                valid = False
            else:
                if not shutil.which(file_manager):
                    logging.error(error_messages.INVALID_FILEMAN)
                    valid = False
    return valid


def validate_args(input_path, file_manager):
    valid = True
    if not common_utils.validate_required_path(input_path, 'Input path'):
        valid = False
    if not validate_file_manager(file_manager):
        valid = False
    return valid


def select_linux_file_manager():
    for file_manager in ('thunar', 'dolphin', 'pcmanfm', 'nautilus', 'nemo', 'konqueror'):
        if shutil.which(file_manager):
            return file_manager
    logging.error(error_messages.NO_FILE_MAN_FOUND)
    return False


def open_file_manager(path, file_manager):
    if common_utils.get_platform() == 'win32':
        bin_ = 'explorer.exe'
    else:
        bin_ = file_manager
    common_utils.execute_with_output([bin_, path])


# Keep this in its own function in case we want to add direct folder copy later
def edit_contents(save_part_contents_path, file_manager):
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


def edit_save_part_with_mount(img_path, save_part_contents_path, file_manager):
    if common_utils.get_platform() == 'linux' and os.getuid() == 0:
        mount_image(img_path, save_part_contents_path)
        edit_contents(save_part_contents_path, file_manager)
        unmount_image(save_part_contents_path)
        common_utils.remove_dir(save_part_contents_path)
        return True
    else:
        logging.error(error_messages.INVALID_MOUNT_CONFIG)
        return False


def edit_save_part_with_cmds(temp_dir, img_path, save_part_contents_path, file_manager):
    extract_img_contents(temp_dir)
    set_all_755(save_part_contents_path)
    edit_contents(save_part_contents_path, file_manager)
    input(info_messages.WAIT_FOR_USER_INPUT)
    common_utils.delete_file(img_path)
    uce_utils.create_blank_file(img_path)
    uce_utils.make_save_part_from_dir(save_part_contents_path, img_path)
    return True


def edit_save_part(temp_dir, img_path, save_part_contents_path, file_manager, mount_method):
    if mount_method:
        return edit_save_part_with_mount(img_path, save_part_contents_path, file_manager)
    else:
        return edit_save_part_with_cmds(temp_dir, img_path, save_part_contents_path, file_manager)


def main(input_path, backup_uce=False, mount_method=False, file_manager=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    if not validate_args(input_path, file_manager):
        return False
    file_manager = file_manager if file_manager else select_linux_file_manager()
    if not file_manager:
        return False
    input_path = os.path.abspath(input_path)
    temp_dir = common_utils.create_temp_dir(__name__)
    file_manager = file_manager if file_manager else 'thunar'
    squashfs_etc_data, save_data = uce_utils.split_uce(input_path)
    img_path = os.path.join(temp_dir, 'save.img')
    common_utils.write_file(img_path, save_data, 'wb')
    if backup_uce:
        backup_path = input_path + '.bak'
        common_utils.copyfile(input_path, backup_path)
    save_part_contents_path = os.path.join(temp_dir, 'save_part_contents')
    common_utils.make_dir(save_part_contents_path)
    if edit_save_part(temp_dir, img_path, save_part_contents_path, file_manager, mount_method):
        uce_utils.rebuild_uce(input_path, squashfs_etc_data, img_path)
    common_utils.cleanup_temp_dir(__name__)


if __name__ == "__main__":
    parser = common_utils.get_cmd_line_args(operations.operations['edit_uce_save_partition']['options'])
    args = vars(parser.parse_args())
    main(args['input_path'], backup_uce=args['backup_uce'], mount_method=args['mount_method'],
         file_manager=args['file_manager'])