#!/usr/bin/env python3
import math
import os
import stat
import hashlib
import tempfile
from optparse import OptionParser
import logging

import cmd_help
import common_utils
import configs

PLATFORM = common_utils.get_platform()


def pre_flight(input_dir):
    if PLATFORM not in ('linux', 'win32'):
        logging.error('This tool requires either Linux or Windows')
        return False
    if not os.path.isdir(input_dir):
        logging.error('{0} is not a directory'.format(input_dir))
    return True


def set_755(file_path):
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


# This doesn't appear to be needed.
# When not called as part of Windows development all worked anyway
# Subsequently tested on Linux, same result.
def relink_boxart(data_dir):
    title_png = os.path.join(data_dir, 'title.png')
    os.remove(title_png)
    os.symlink('boxart/boxart.png', title_png)


def call_mksquashfs(input_dir, target_file, app_root):
    if PLATFORM == 'win32':
        exe_dir = os.path.join(app_root, 'windows')
        exe = os.path.join(exe_dir, 'mksquashfs.exe')
        cmd = '"{0}" "{1}" "{2}" -b 262144 -root-owned -nopad'.format(exe, input_dir, target_file)
    else:
        cmd = 'mksquashfs "{0}" "{1}" -b 262144 -root-owned -nopad'.format(input_dir, target_file)
    logging.info('Running command: {0}'.format(cmd))
    cmd_out = os.popen(cmd).read()


def get_sq_image_real_bytes_used(sq_img_file_size):
    real_bytes_used_divided_by_4K = math.floor(sq_img_file_size / 4096)
    if sq_img_file_size % 4096 != 0:
        real_bytes_used_divided_by_4K = real_bytes_used_divided_by_4K + 1
    return real_bytes_used_divided_by_4K * 4096


def get_md5(cart_temp_file):
    md5_hash = hashlib.md5()
    content = common_utils.get_file_content(cart_temp_file, 'rb')
    md5_hash.update(content)
    return md5_hash.hexdigest()


def create_hex_file(md5_hex_digest, file_path):
    binary_md5 = bytearray.fromhex(md5_hex_digest)
    common_utils.write_file(file_path, binary_md5, 'wb')


def append_file_to_file(start_file, end_file):
    end_content = common_utils.get_file_content(end_file, 'rb')
    append_to_file(start_file, end_content)


def append_to_file(start_file, append_data):
    common_utils.write_file(start_file, append_data, 'ab')


def make_ext4_part(cart_save_file, app_root):
    if PLATFORM == 'win32':
        exe_dir = os.path.join(app_root, 'windows')
        script = os.path.join(exe_dir, 'make_ext4_part.bat')
    else:
        bash_script_dir = os.path.join(app_root, 'bash_scripts')
        script = os.path.join(bash_script_dir, 'make_ext4_part.sh')
    cmd = '"{0}" "{1}"'.format(script, cart_save_file)
    logging.info('Running command: {0}'.format(cmd))
    cmd_out = os.popen(cmd).read()


def main(input_dir, output_file):
    logging.basicConfig(level=logging.INFO)
    if not pre_flight(input_dir):
        return
    logging.info('Building new UCE')
    app_root = configs.APP_ROOT
    temp_dir_obj = tempfile.TemporaryDirectory()
    temp_dir = temp_dir_obj.name
    cart_tmp_file = os.path.join(temp_dir, 'cart_tmp_file.img')
    cart_save_file = os.path.join(temp_dir, 'cart_save_file.img')
    md5_file = os.path.join(temp_dir, 'md5_file')
    data_dir = os.path.join(temp_dir, 'data')
    save_dir = os.path.join(temp_dir, 'data', 'save')
    # TODO Can we avoid the need for re-linking boxart here?
    logging.info('Copying from input directory to temp directory')
    common_utils.copytree(input_dir, data_dir, symlinks=True)
    common_utils.make_dir(save_dir)
    set_755(os.path.join(data_dir, 'exec.sh'))
    relink_boxart(data_dir)
    call_mksquashfs(data_dir, cart_tmp_file, app_root)
    sq_img_file_size = os.path.getsize(cart_tmp_file)
    real_bytes_used = get_sq_image_real_bytes_used(sq_img_file_size)
    count = int(real_bytes_used) - int(sq_img_file_size)
    append_to_file(cart_tmp_file, bytearray(count))
    md5_string = get_md5(cart_tmp_file)
    create_hex_file(md5_string, md5_file)
    append_file_to_file(cart_tmp_file, md5_file)
    append_to_file(cart_tmp_file, bytearray(32))
    # TODO - Is this next line needed?
    os.remove(md5_file)
    make_ext4_part(cart_save_file, app_root)
    md5_string = get_md5(cart_save_file)
    create_hex_file(md5_string, md5_file)
    append_file_to_file(cart_tmp_file, md5_file)
    append_file_to_file(cart_tmp_file, cart_save_file)
    common_utils.copyfile(cart_tmp_file, output_file)
    logging.info('Built: {0}\n\n\n'.format(output_file))


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-i', '--inputdir', dest='input_dir', help=cmd_help.INPUT_DIR, default=os.getcwd())
    parser.add_option('-o', '--output', dest='output_file', help=cmd_help.OUTPUT_DIR, default=os.path.join(os.getcwd(), 'output.uce'))
    return parser


def validate_opts(parser):
    (options, args) = parser.parse_args()
    if options.input_dir is None:
        parser.print_help()
        exit(0)
    return options, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = validate_opts(parser)

    main(opts.input_dir, opts.output_file)

