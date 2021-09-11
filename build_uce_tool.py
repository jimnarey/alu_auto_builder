#!/usr/bin/env python3
import math
import os
import shutil
import stat
import hashlib
import tempfile

import common_utils


def execute(cmd):
    print(cmd)
    cmd_out = os.popen(cmd).read()
    print(cmd_out)
    return cmd_out


def set_755(file_path):
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


# TODO - sort for Windows
def relink_boxart(data_dir):
    title_png = os.path.join(data_dir, 'title.png')
    os.remove(title_png)
    os.symlink('boxart/boxart.png', title_png)


# def call_mksquashfs(input_dir, target_file):
#     cmd = 'mksquashfs "{0}" "{1}" -b 262144 -root-owned -nopad'.format(input_dir, target_file)
#     cmd_out = os.popen(cmd).read()
#     print(cmd_out)

def call_mksquashfs(input_dir, target_file, this_dir):
    if common_utils.get_platform() == 'linux':
        cmd = 'mksquashfs "{0}" "{1}" -b 262144 -root-owned -nopad'.format(input_dir, target_file)
    elif common_utils.get_platform() == 'win32':
        exe_dir = os.path.join(this_dir, 'windows', 'cygwin_old')
        exe = os.path.join(exe_dir, 'mksquashfs.exe')
        cmd = '"{0}" "{1}" "{2}" -b 262144 -root-owned -nopad'.format(exe, input_dir, target_file)
    cmd_out = os.popen(cmd).read()
    print(cmd_out)


def get_sq_image_real_bytes_used(sq_img_file_size):
    real_bytes_used_divided_by_4K = math.floor(sq_img_file_size / 4096)
    if sq_img_file_size % 4096 != 0:
        real_bytes_used_divided_by_4K = real_bytes_used_divided_by_4K + 1
    return real_bytes_used_divided_by_4K * 4096


def get_md5(cart_temp_file):
    md5_hash = hashlib.md5()
    with open(cart_temp_file, 'rb') as input_file:
        content = input_file.read()
        md5_hash.update(content)
    return md5_hash.hexdigest()


def create_hex_file(md5_hex_digest, file_path):
    binary_md5 = bytearray.fromhex(md5_hex_digest)
    with open(file_path, 'wb') as hex_file:
        hex_file.write(binary_md5)


def append_file_to_file(start_file, end_file):
    with open(end_file, 'rb') as e_file:
        append_to_file(start_file, e_file.read())


def append_to_file(start_file, append_data):
    with open(start_file, 'ab') as s_file:
        s_file.write(append_data)


def make_ext4_part(cart_save_file, this_dir):
    if common_utils.get_platform() == 'linux':
        bash_script_dir = os.path.join(this_dir, 'bash_scripts')
        script = os.path.join(bash_script_dir, 'make_ext4_part.sh')
        cmd = '{0} {1}'.format(script, cart_save_file)
    elif common_utils.get_platform() == 'win32':
        exe_dir = os.path.join(this_dir, 'windows', 'cygwin_old')
        script = os.path.join(exe_dir, 'make_ext4_part.bat')
        cmd = '"{0}" "{1}"'.format(script, cart_save_file)
    execute(cmd)


def run(input_dir, output_file):

    this_dir = os.path.split(os.path.realpath(__file__))[0]
    # bash_script_dir = os.path.join(this_dir, 'bash_scripts')
    work_dir = tempfile.TemporaryDirectory()
    cart_tmp_file = os.path.join(work_dir.name, 'cart_tmp_file.img')
    cart_save_file = os.path.join(work_dir.name, 'cart_save_file.img')
    md5_file = os.path.join(work_dir.name, 'md5_file')
    data_dir = os.path.join(work_dir.name, 'data')
    save_dir = os.path.join(work_dir.name, 'data', 'save')
    # TODO Can we avoid the need for re-linking boxart here?
    shutil.copytree(input_dir, data_dir, symlinks=True)
    common_utils.safe_make_dir(save_dir)
    set_755(os.path.join(data_dir, 'exec.sh'))
    # relink_boxart(data_dir)
    call_mksquashfs(data_dir, cart_tmp_file, this_dir)
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
    # TODO - Reduce this
    # script = os.path.join(bash_script_dir, 'make_ext4_part.sh')
    # cmd = '{0} {1}'.format(script, cart_save_file)
    # execute(cmd)


    md5_string = get_md5(cart_save_file)
    create_hex_file(md5_string, md5_file)
    append_file_to_file(cart_tmp_file, md5_file)
    append_file_to_file(cart_tmp_file, cart_save_file)
    shutil.copy(cart_tmp_file, output_file)

