#!/usr/bin/env python3

import math
import os
import hashlib
import zipfile
import logging

from shared import common_utils, info_messages, uce_utils, error_messages
import operations

logger = logging.getLogger(__name__)


class UCEBuildPaths:

    def __init__(self):
        self.temp_dir = common_utils.create_temp_dir(__name__)
        self.cart_tmp_file = os.path.join(self.temp_dir, 'cart_tmp_file.img')
        self.cart_save_file = os.path.join(self.temp_dir, 'data/blank_save_part.img')
        self.md5_file = os.path.join(self.temp_dir, 'md5_file')
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.save_dir = os.path.join(self.temp_dir, 'data', 'save')
        self.save_workdir = os.path.join(self.temp_dir, 'save_workdir')
        self.blank_save_workdir = os.path.join(self.temp_dir, 'blank_save_workdir')
        self.zip_workdir = os.path.join(self.temp_dir, 'zip_workdir')

    def cleanup(self):
        common_utils.cleanup_temp_dir(__name__)


def check_os():
    if common_utils.get_platform() not in ('linux', 'win32'):
        logger.error(error_messages.INVALID_OS)
        return False
    return True


def validate_args(input_dir):
    logger.info('Validating arguments for build_uce_tool')
    valid = True
    if not common_utils.validate_existing_dir(input_dir, 'Input dir'):
        valid = False
    return valid


def relink_boxart(data_dir):
    title_png = os.path.join(data_dir, 'title.png')
    common_utils.delete_file(title_png)
    if not common_utils.create_symlink('boxart/boxart.png', title_png):
        logger.info(info_messages.COPY_SYMLINK_FAILED)
        common_utils.copyfile(os.path.join(data_dir, 'boxart', 'boxart.png'), title_png)


def call_mksquashfs(input_dir, target_file, app_root):
    mksquashfs_args = [
        input_dir,
        target_file,
        '-b', '262144',
        '-force-uid', '12',
        '-force-gid', '12',
        '-noappend',
        '-nopad'
    ]
    if common_utils.get_platform() == 'win32':
        cmd = [os.path.join(app_root, 'windows', 'mksquashfs.exe')]
    else:
        cmd = ['mksquashfs']
    cmd += mksquashfs_args
    common_utils.execute_with_output(cmd)


def get_sq_image_real_bytes_used(sq_img_file_size):
    real_bytes_used_divided_by_4K = math.floor(sq_img_file_size / 4096)
    if sq_img_file_size % 4096 != 0:
        real_bytes_used_divided_by_4K = real_bytes_used_divided_by_4K + 1
    return real_bytes_used_divided_by_4K * 4096


def make_squashfs_img(app_root, ub_paths):
    call_mksquashfs(ub_paths.data_dir, ub_paths.cart_tmp_file, app_root)
    sq_img_file_size = os.path.getsize(ub_paths.cart_tmp_file)
    real_bytes_used = get_sq_image_real_bytes_used(sq_img_file_size)
    count = int(real_bytes_used) - int(sq_img_file_size)
    logger.info('Appending {0} bytes to {1}'.format(count, ub_paths.cart_tmp_file))
    append_to_file(ub_paths.cart_tmp_file, bytearray(count))


def get_md5(cart_temp_file):
    md5_hash = hashlib.md5()
    content = common_utils.get_file_content(cart_temp_file, 'rb')
    md5_hash.update(content)
    md5_hex_digest = md5_hash.hexdigest()
    logger.info('md5 of {0} is {1}'.format(cart_temp_file, md5_hex_digest))
    return md5_hex_digest


def create_hex_file(md5_hex_digest, file_path):
    binary_md5 = bytearray.fromhex(md5_hex_digest)
    common_utils.write_file(file_path, binary_md5, 'wb')


def append_to_file(start_file, append_data):
    common_utils.write_file(start_file, append_data, 'ab')


def append_file_to_file(start_file, end_file):
    end_content = common_utils.get_file_content(end_file, 'rb')
    append_to_file(start_file, end_content)


def append_md5_to_img(md5_source, md5_file, append_target):
    md5_string = get_md5(md5_source)
    create_hex_file(md5_string, md5_file)
    append_file_to_file(append_target, md5_file)


def prepare_source_files(input_dir, ub_paths):
    common_utils.copytree(input_dir, ub_paths.data_dir, symlinks=True)
    common_utils.set_755(os.path.join(ub_paths.data_dir, 'exec.sh'))
    relink_boxart(ub_paths.data_dir)


def get_first_save_file_in_dir(dir_path):
    try:
        save_files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)
                      if os.path.isfile(os.path.join(dir_path, file)) and os.path.splitext(file)[0] == 'save']
        if save_files:
            return save_files[0]
    except FileNotFoundError:
        pass
    return None


def look_for_save_file(ub_paths):
    save_file = get_first_save_file_in_dir(ub_paths.save_dir)
    if not save_file:
        save_file = get_first_save_file_in_dir(ub_paths.data_dir)
    return save_file


def extract_save_from_zip(save_zip, ub_paths):
    try:
        with zipfile.ZipFile(save_zip, 'r') as zfile:
            zfile.extractall(path=ub_paths.zip_workdir)
            return get_first_save_file_in_dir(ub_paths.zip_workdir)
    except zipfile.BadZipfile:
        logger.error(error_messages.SAVE_NOT_VALID_ZIP)
    except KeyError:
        logger.error(error_messages.ZIP_HAS_NO_SAVE_IMG)
    except OSError as e:
        logger.error(error_messages.zip_extract_failed(e))
    return None


def save_img_from_save_file(save_file, ub_paths):
    if zipfile.is_zipfile(save_file):
        extr_save_file = extract_save_from_zip(save_file, ub_paths)
        if extr_save_file:
            logger.info(info_messages.copying_extracted_save_file(extr_save_file, save_file))
            common_utils.copyfile(os.path.join(extr_save_file), ub_paths.cart_save_file)
    else:
        common_utils.copyfile(save_file, ub_paths.cart_save_file)


# def prepare_files_based_save_contents(ub_paths):
#     common_utils.make_dir(ub_paths.save_workdir)
#     save_dir_upper = os.path.join(ub_paths.save_dir, 'upper')
#     save_workdir_upper = os.path.join(ub_paths.save_workdir, 'upper')
#     hiscore_dat_path = os.path.join(ub_paths.save_workdir, 'upper', 'hiscore.dat')
#     if os.path.isdir(save_dir_upper):
#         common_utils.copytree(save_dir_upper, save_workdir_upper)
#     else:
#         common_utils.copytree(ub_paths.save_dir, save_workdir_upper)
#     if not os.path.isfile(hiscore_dat_path):
#         common_utils.write_file(hiscore_dat_path, '', 'w')
#     common_utils.make_dir(os.path.join(ub_paths.save_workdir, 'work'))


def prepare_save_contents(ub_paths):
    save_file = look_for_save_file(ub_paths)
    if save_file:
        logger.info(info_messages.processing_save_file(save_file))
        save_img_from_save_file(save_file, ub_paths)
        uce_utils.modify_inodes(ub_paths.cart_save_file)
        # TODO - delete save_file
        common_utils.delete_file(save_file)
        # if os.path.isdir(ub_paths.save_dir):
        #     common_utils.remove_dir(ub_paths.save_dir)
        # common_utils.make_dir(ub_paths.save_dir)
        return

    # Intent - keep the save contents where they are and build into squashfs
    if os.path.isdir(ub_paths.save_dir) and os.listdir(ub_paths.save_dir):
        logger.info(info_messages.including_save_files_in_squashfs(ub_paths.save_dir))
        hiscore_dat_path = os.path.join(ub_paths.save_dir, 'hiscore.dat')
        if not os.path.isfile(os.path.join(hiscore_dat_path)):
            common_utils.write_file(os.path.join(hiscore_dat_path), '', 'w')

        # prepare_files_based_save_contents(ub_paths)
        # uce_utils.make_save_part_from_dir(ub_paths.save_workdir, ub_paths.cart_save_file)

    # Intent - use a stock, prepared save file

    logger.info(info_messages.USING_STOCK_BLANK_SAVE_PART)
    common_utils.copyfile(os.path.join(common_utils.get_app_root(), 'data', 'blank_save_part.img'), ub_paths.cart_save_file)
    # if os.path.isdir(ub_paths.save_dir):
    #     common_utils.remove_dir(ub_paths.save_dir)
    common_utils.make_dir(ub_paths.save_dir)
    # uce_utils.modify_inodes(ub_paths.cart_save_file)


def main(input_dir, output_path=None):    
    input_dir = input_dir if input_dir else os.getcwd()
    if not check_os() or not validate_args(input_dir):
        return
    if not output_path:
        # TODO - Use os.path.basename
        output_path = os.path.join(input_dir, '{0}.uce'.format(os.path.split(os.path.abspath(input_dir))[-1]))
    logger.info('Building new UCE')
    app_root = common_utils.get_app_root()
    ub_paths = UCEBuildPaths()
    prepare_source_files(input_dir, ub_paths)
    prepare_save_contents(ub_paths)
    make_squashfs_img(app_root, ub_paths)
    append_md5_to_img(ub_paths.cart_tmp_file, ub_paths.md5_file, ub_paths.cart_tmp_file)
    append_to_file(ub_paths.cart_tmp_file, bytearray(32))
    append_md5_to_img(ub_paths.cart_save_file, ub_paths.md5_file, ub_paths.cart_tmp_file)
    append_file_to_file(ub_paths.cart_tmp_file, ub_paths.cart_save_file)
    common_utils.copyfile(ub_paths.cart_tmp_file, output_path)
    logger.info('Built: {0}'.format(output_path))
    ub_paths.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(asctime)s : %(message)s", datefmt="%H:%M:%S")
    parser = common_utils.get_cmd_line_args(operations.operations['recipe_to_uce']['options'])
    args = vars(parser.parse_args())
    main(args['input_dir'], output_path=args['output_path'])
