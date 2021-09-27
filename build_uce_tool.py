#!/usr/bin/env python3

import math
import os
import hashlib
from zipfile import ZipFile, BadZipfile
from optparse import OptionParser
import logging

import edit_uce
import cmd_help
import common_utils
import errors


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


PLATFORM = common_utils.get_platform()


def pre_flight(input_dir):
    if PLATFORM not in ('linux', 'win32'):
        logging.error(errors.INVALID_OS)
        return False
    if not os.path.isdir(input_dir):
        logging.error(errors.invalid_path(input_dir, 'directory'))
    return True


# This doesn't appear to be needed.
# When not called as part of Windows development all worked anyway
# Subsequently tested on Linux, same result.
def relink_boxart(data_dir):
    title_png = os.path.join(data_dir, 'title.png')
    common_utils.delete_file(title_png)
    common_utils.create_symlink('boxart/boxart.png', title_png)


def prepare_save_files(ub_paths):
    if os.path.isdir(ub_paths.save_dir):
        logging.info('Custom save data found')
        common_utils.copytree(ub_paths.save_dir, ub_paths.save_workdir)
        common_utils.remove_dir(ub_paths.save_dir)
    common_utils.make_dir(ub_paths.save_dir)


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
    if PLATFORM == 'win32':
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
    logging.info('Appending {0} bytes to {1}'.format(count, ub_paths.cart_tmp_file))
    append_to_file(ub_paths.cart_tmp_file, bytearray(count))


def get_md5(cart_temp_file):
    md5_hash = hashlib.md5()
    content = common_utils.get_file_content(cart_temp_file, 'rb')
    md5_hash.update(content)
    md5_hex_digest = md5_hash.hexdigest()
    logging.info('md5 of {0} is {1}'.format(cart_temp_file, md5_hex_digest))
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
        logging.error('save.zip is not a valid zipfile')
    except KeyError:
        logging.error('save.zip does not contain a file named save.img')
    except OSError as e:
        logging.error('Unable to extract and copy save.img file from zip: {0}'.format(e))


def get_save_part(ub_paths):
    if os.listdir(ub_paths.save_workdir):
        save_img_path = os.path.join(ub_paths.save_workdir, 'save.img')
        if os.path.isfile(save_img_path):
            logging.info('Processing save.img as new save partition, ignoring any other contents of save dir')
            common_utils.copyfile(save_img_path, ub_paths.cart_save_file)
        elif os.path.isfile(os.path.join(ub_paths.save_workdir, 'save.zip')):
            logging.info('Processing save.zip as new save partition, ignoring any other contents of save dir')
            extract_and_copy_save_zip(ub_paths)
        # else:
        #     logging.info('Creating save partition from contents of save dir')
        #     common_utils.make_ext4_part(ub_paths.cart_save_file)
        #     edit_uce.copy_into_save_img(ub_paths.temp_dir, ub_paths.save_workdir, ub_paths.cart_save_file)
    else:
        common_utils.make_ext4_part(ub_paths.cart_save_file)
        # TODO - add base dir generation
        common_utils.create_save_part_base_dirs(ub_paths.temp_dir, ub_paths.cart_save_file)


# # TODO - Use common utils version
# def make_ext4_part(cart_save_file, app_root):
#     if PLATFORM == 'win32':
#         bin = os.path.join(app_root, 'windows', 'make_ext4_part.bat')
#     else:
#         bin = os.path.join(app_root, 'bash_scripts', 'make_ext4_part.sh')
#     cmd = [bin, cart_save_file]
#     common_utils.execute_with_output(cmd)


def main(input_dir, output_file):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    if not pre_flight(input_dir):
        return
    logging.info('Building new UCE')
    app_root = common_utils.get_app_root()
    ub_paths = UCEBuildPaths()
    prepare_source_files(input_dir, ub_paths)
    make_squashfs_img(app_root, ub_paths)
    append_md5_to_img(ub_paths.cart_tmp_file, ub_paths.md5_file, ub_paths.cart_tmp_file)
    append_to_file(ub_paths.cart_tmp_file, bytearray(32))


    # make_ext4_part(ub_paths.cart_save_file, app_root)
    get_save_part(ub_paths)

    append_md5_to_img(ub_paths.cart_save_file, ub_paths.md5_file, ub_paths.cart_tmp_file)


    append_file_to_file(ub_paths.cart_tmp_file, ub_paths.cart_save_file)
    common_utils.copyfile(ub_paths.cart_tmp_file, output_file)
    logging.info('Built: {0}\n\n\n'.format(output_file))
    ub_paths.cleanup()


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-i', '--inputdir', dest='input_dir', help=cmd_help.INPUT_DIR, default=os.getcwd())
    parser.add_option('-o', '--output', dest='output_file', help=cmd_help.OUTPUT_DIR, default=os.path.join(os.getcwd(), 'output.uce'))
    return parser


def validate_opts(parser):
    (opts, args) = parser.parse_args()
    return opts, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = validate_opts(parser)

    main(opts.input_dir, opts.output_file)

