#!/usr/bin/env python3

import math
import os
import hashlib
from zipfile import ZipFile, BadZipfile
import logging

from shared import common_utils, info_messages, uce_utils, error_messages
import operations

logger = logging.getLogger(__name__)


class UCEBuildPaths:

    def __init__(self):
        self.temp_dir = common_utils.create_temp_dir(__name__)
        self.cart_tmp_file = os.path.join(self.temp_dir, 'cart_tmp_file.img')
        self.cart_save_file = os.path.join(self.temp_dir, 'cart_save_file.img')
        self.md5_file = os.path.join(self.temp_dir, 'md5_file')
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.save_dir = os.path.join(self.temp_dir, 'data', 'save')
        self.save_workdir = os.path.join(self.temp_dir, 'save_workdir')

    def cleanup(self):
        common_utils.cleanup_temp_dir(__name__)


def check_os():
    if common_utils.get_platform() not in ('linux', 'win32'):
        logger.error(error_messages.INVALID_OS)
        return False
    return True


def validate_args(input_dir):
    valid = True
    if not common_utils.validate_existing_dir(input_dir, 'Input dir'):
        valid = False
    return valid


def relink_boxart(data_dir):
    title_png = os.path.join(data_dir, 'title.png')
    common_utils.delete_file(title_png)
    common_utils.create_symlink('boxart/boxart.png', title_png)


def prepare_save_files(ub_paths):
    if os.path.isdir(ub_paths.save_dir):
        logger.info(info_messages.SAVE_DATA_FOUND)
        common_utils.copytree(ub_paths.save_dir, ub_paths.save_workdir)
        common_utils.remove_dir(ub_paths.save_dir)
    # Does nothing and catches errors if the dirs already exist
    common_utils.make_dir(ub_paths.save_dir)
    common_utils.make_dir(ub_paths.save_workdir)


def prepare_source_files(input_dir, ub_paths):
    common_utils.copytree(input_dir, ub_paths.data_dir, symlinks=True)
    prepare_save_files(ub_paths)
    common_utils.set_755(os.path.join(ub_paths.data_dir, 'exec.sh'))
    relink_boxart(ub_paths.data_dir)


def call_mksquashfs(input_dir, target_file, app_root):
    mksquashfs_args = [
        input_dir,
        target_file,
        '-b', '262144',
        '-root-owned',
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


def extract_and_copy_save_zip(ub_paths):
    try:
        with ZipFile(os.path.join(ub_paths.save_workdir, 'save.zip'), 'r') as zfile:
            zfile.extract('save.img', ub_paths.save_workdir)
            common_utils.copyfile(os.path.join(ub_paths.save_workdir, 'save.img'), ub_paths.cart_save_file)
    except BadZipfile:
        logger.error(error_messages.SAVE_NOT_VALID_ZIP)
    except KeyError:
        logger.error(error_messages.ZIP_HAS_NO_SAVE_IMG)
    except OSError as e:
        logger.error(error_messages.zip_extract_failed(e))


def get_save_part(ub_paths):
    if os.listdir(ub_paths.save_workdir):
        save_img_path = os.path.join(ub_paths.save_workdir, 'save.img')
        if os.path.isfile(save_img_path):
            logger.info(info_messages.processing_save_file('save.img'))
            common_utils.copyfile(save_img_path, ub_paths.cart_save_file)
        elif os.path.isfile(os.path.join(ub_paths.save_workdir, 'save.zip')):
            logger.info(info_messages.processing_save_file('save.zip'))
            extract_and_copy_save_zip(ub_paths)
        else:
            logger.info(info_messages.processing_save_file('all save dir contents'))
            uce_utils.create_blank_file(ub_paths.cart_save_file)
            uce_utils.make_save_part_from_dir(ub_paths.save_workdir, ub_paths.cart_save_file)
    else:
        uce_utils.make_ext4_part(ub_paths.cart_save_file)
        uce_utils.create_save_part_base_dirs(ub_paths.temp_dir, ub_paths.cart_save_file)


def main(input_dir, output_path=None):    
    input_dir = input_dir if input_dir else os.getcwd()
    if not check_os() or not validate_args(input_dir):
        return
    if not output_path:
        output_path = os.path.join(input_dir, '{0}.uce'.format(os.path.split(os.path.abspath(input_dir))[-1]))
    logger.info('Building new UCE')
    app_root = common_utils.get_app_root()
    ub_paths = UCEBuildPaths()
    prepare_source_files(input_dir, ub_paths)
    make_squashfs_img(app_root, ub_paths)
    append_md5_to_img(ub_paths.cart_tmp_file, ub_paths.md5_file, ub_paths.cart_tmp_file)
    append_to_file(ub_paths.cart_tmp_file, bytearray(32))
    get_save_part(ub_paths)
    append_md5_to_img(ub_paths.cart_save_file, ub_paths.md5_file, ub_paths.cart_tmp_file)
    append_file_to_file(ub_paths.cart_tmp_file, ub_paths.cart_save_file)
    common_utils.copyfile(ub_paths.cart_tmp_file, output_path)
    logger.info('Built: {0}'.format(output_path))
    ub_paths.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(name)s : %(levelname)s : %(message)s",
                        datefmt="%H:%M:%S")
    parser = common_utils.get_cmd_line_args(operations.operations['build_single_uce_from_recipe']['options'])
    args = vars(parser.parse_args())
    main(args['input_dir'], output_path=args['output_path'])
