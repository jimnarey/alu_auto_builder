#!/usr/bin/env python3

import os
import logging
import shutil

from shared import common_utils, info_messages, uce_utils, error_messages
import operations

logger = logging.getLogger(__name__)


class EditUCEConfig:

    def __init__(self, input_path, file_manager):
        self.temp_dir = common_utils.create_temp_dir(__name__)
        self.input_path = os.path.abspath(input_path)
        self.img_path = os.path.join(self.temp_dir, 'save.img')
        self.save_part_contents_path = os.path.join(self.temp_dir, 'save_part_contents')
        self.backup_path = input_path + '.bak'
        self.file_manager = None
        self.set_file_manager(file_manager)

    def set_file_manager(self, file_manager):
        if common_utils.get_platform() == 'linux':
            self.set_file_manager_linux(file_manager)
        elif common_utils.get_platform() == 'win32':
            if file_manager:
                logger.info(info_messages.FILEMAN_NOT_LINUX)
            self.file_manager = 'explorer.exe'

    def set_file_manager_linux(self, file_manager):
        for check_manager in (str(file_manager), 'thunar', 'dolphin', 'pcmanfm', 'nautilus', 'nemo', 'konqueror'):
            if shutil.which(check_manager):
                self.file_manager = check_manager
                return
            logger.info(info_messages.file_manager_not_found(check_manager))
        logger.error(error_messages.NO_FILE_MAN_FOUND)

    def cleanup(self):
        common_utils.cleanup_temp_dir(__name__)


def validate_args(input_path):
    valid = True
    if not common_utils.validate_required_path(input_path, 'Input path'):
        valid = False
    return valid


def open_file_manager(path, file_manager):
    common_utils.execute_with_output([file_manager, path])


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
        logger.error(error_messages.INVALID_MOUNT_CONFIG)
        return False


def edit_save_part_with_cmds(temp_dir, img_path, save_part_contents_path, file_manager, continue_check):
    extract_img_contents(temp_dir)
    set_all_755(save_part_contents_path)
    edit_contents(save_part_contents_path, file_manager)
    # input(info_messages.WAIT_FOR_USER_INPUT)
    continue_check()
    common_utils.delete_file(img_path)
    # uce_utils.create_blank_file(img_path)
    uce_utils.make_save_part_from_dir(save_part_contents_path, img_path)
    return True


def edit_save_part(temp_dir, img_path, save_part_contents_path, file_manager, mount_method, continue_check):
    if mount_method:
        return edit_save_part_with_mount(img_path, save_part_contents_path, file_manager)
    else:
        return edit_save_part_with_cmds(temp_dir, img_path, save_part_contents_path, file_manager, continue_check)


def console_continue_check():
    input(info_messages.CONSOLE_WAIT_FOR_USER_INPUT)


def main(input_path, backup_uce=False, mount_method=False, file_manager=None, continue_check=None):
    if not validate_args(input_path):
        return False
    ec_config = EditUCEConfig(input_path, file_manager)
    if not ec_config.file_manager:
        return False
    continue_check = continue_check if continue_check else console_continue_check
    squashfs_etc_data, save_data = uce_utils.split_uce(input_path)
    common_utils.write_file(ec_config.img_path, save_data, 'wb')
    if backup_uce:
        backup_path = input_path + '.bak'
        common_utils.copyfile(input_path, backup_path)
    common_utils.make_dir(ec_config.save_part_contents_path)
    if edit_save_part(ec_config.temp_dir, ec_config.img_path, ec_config.save_part_contents_path,
                      ec_config.file_manager, mount_method, continue_check):
        uce_utils.rebuild_uce(ec_config.input_path, squashfs_etc_data, ec_config.img_path)
    ec_config.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(asctime)s : %(message)s", datefmt="%H:%M:%S")
    parser = common_utils.get_cmd_line_args(operations.operations['edit_save_partition']['options'])
    args = vars(parser.parse_args())
    main(args['input_path'], backup_uce=args['backup_uce'], mount_method=args['mount_method'],
         file_manager=args['file_manager'])
