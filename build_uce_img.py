#!/usr/bin/env python3
import hashlib
import os
import stat
import sys
import shutil
import errno
import pickle
from optparse import OptionParser


# TODO 1 - Consider something to clear any existing dir/files
# /bin/rm -f $cart_tmp_file
# /bin/rm -f $cart_save_file

# TODO 2 - Consider re-adding handling of any links
# find "$workdir/data" -name "*.lnk" -type f -print0 | xargs -0 -n1 ./resolve.sh
# find "$workdir/data" -name "*.lnk" -type f -delete

# TODO 3 - Does anything need doing with this?
# header padding 64 bytes
# EXT4FILE_OFFSET=$((SQIMGFILESIZE+64));
# echo "*** Offset of Ext4 partition for file saving would be: $EXT4FILE_OFFSET ($SQIMGFILESIZE + 64)"

# TODO 4 - Consider as part of more general output (x6)

# SQIMGFILESIZE=$(stat -c%s "$cart_tmp_file")
# echo "*** Size of $cart_tmp_file: $SQIMGFILESIZE Bytes (after applying 4k alignment)"

# filesize=$(stat -c%s "$cart_tmp_file")
# echo "*** Size of $cart_tmp_file: $filesize Bytes (after SQFS MD5)"

# filesize=$(stat -c%s "$cart_tmp_file")
# echo "*** Size of $cart_tmp_file: $filesize Bytes (after padding zeros)"

# filesize =$(stat - c % s "$cart_tmp_file")
# echo
# "*** Size of $cart_tmp_file: $filesize Bytes (after Ext4 MD5)"

# filesize =$(stat - c % s "$cart_save_file")
# echo
# "*** Size of $cart_save_file: $filesize Bytes (save partition)"

# filesize=$(stat -c%s "$cart_file")
# echo "*** Final size ($cart_file): $filesize Bytes (cart + save)"

# TODO 5 - Some cleanup
# /bin/rm -f $my_md5string_hex_file

# TODO 6 - Handle custom save.zips
# #bind files together
# if [ -f "$workdir/save.zip" ]
# then
#   unzip "$workdir/save.zip" -d "$workdir"
#   /bin/mv "$workdir/save.bin" $cart_save_file
# fi

# TODO ESSENTIAL
# TODO - Handle file (dir) exists error from copytree
# TODO - Sort superfluous copy of inputdir to workdir/data
# TODO - Sensibly brigade functions by job

# TODO - Sense check and improve user output
# TODO - Consider sense check on input_dir contents
# TODO - Work out how to batch process save.zip files (more for aluautobuilder.py)


def get_platform():
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform in ('win32', 'darwin'):
        return sys.platform
    return None


def safe_make_dir(path):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    pass


def make_dirs(*args):
    for new_dir in args:
        safe_make_dir(new_dir)


# TODO Make this generic (error message!)
def move_file(source, dest):
    try:
        shutil.move(source, dest)
    except FileNotFoundError:
        print('No save.zip included')


def data_dir_path(root_work_dir):
    return os.path.join(root_work_dir, 'data')


def save_dir_path(root_work_dir):
    return os.path.join(root_work_dir, 'data', 'save')


def set_image_file_paths(root_work_dir):
    return os.path.join(root_work_dir, 'cart_temp_file.img'),\
           os.path.join(root_work_dir, 'cart_save_file.img'),\
           os.path.join(root_work_dir, 'md5_temp_file.bin')
        

def set_755(file_path):
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def relink_boxart(data_dir):
    title_png = os.path.join(data_dir, 'title.png')
    os.remove(title_png)
    os.symlink(os.path.abspath(os.path.join(data_dir, 'boxart', 'boxart.png')), title_png)


def call_mksquashfs(data_dir, target_file):
    cmd = 'mksquashfs "{0}" "{1}" -b 262144 -root-owned -nopad'.format(data_dir, target_file)
    cmd_out = os.popen(cmd).read()
    print(cmd_out)


# TODO - Understand logic here
def get_sq_image_real_bytes_used(sq_img_file_size):
    real_bytes_used_divided_by_4K = sq_img_file_size / 4096
    if sq_img_file_size % 4096 != 0:
        real_bytes_used_divided_by_4K = real_bytes_used_divided_by_4K + 1
    return real_bytes_used_divided_by_4K * 4096


def get_sq_image_padding(sq_img_file_size):
    sq_img_real_bytes_used = get_sq_image_real_bytes_used(sq_img_file_size)
    return int(sq_img_real_bytes_used - sq_img_file_size)


def append_file_to_file(start_file, end_file):
    with open(end_file, 'rb') as e_file:
        append_to_file(start_file, e_file.read())


def append_to_file(start_file, data):
    with open(start_file, 'ab') as s_file:
        pickle.dump(data, s_file)


def get_md5(cart_temp_file):
    md5_hash = hashlib.md5()
    with open(cart_temp_file, 'rb') as input_file:
        content = input_file.read()
        md5_hash.update(content)
    return md5_hash.hexdigest()


# TODO - append this without creating separate file
def create_hex_file(md5_hex_digest, file_path):
    binary_md5 = bytearray.fromhex(md5_hex_digest)
    with open(file_path, 'wb') as hex_file:
        hex_file.write(binary_md5)


def make_save_partition(file_path):
    this_dir = os.path.split(os.path.realpath(__file__))[0]
    script = os.path.join(this_dir, 'bash_scripts', 'make_save_partition.sh')
    cmd = '{0} "{1}"'.format(script, file_path)
    cmd_out = os.popen(cmd).read()
    print(cmd_out)


def run(input_dir, output_file, root_work_dir):
    data_dir = data_dir_path(root_work_dir)
    save_dir = save_dir_path(root_work_dir)
    cart_temp_file, cart_save_file, md5string_hex_file = set_image_file_paths(root_work_dir)
    shutil.copytree(input_dir, data_dir, symlinks=True)
    make_dirs(data_dir, save_dir)
    set_755(os.path.join(data_dir, 'exec.sh'))
    relink_boxart(data_dir)
    move_file(os.path.join(data_dir, 'save.zip'), root_work_dir)
    call_mksquashfs(data_dir, cart_temp_file)
    sq_img_file_size = os.path.getsize(cart_temp_file)
    append_to_file(cart_temp_file, bytearray(get_sq_image_padding(sq_img_file_size)))
    sq_img_file_md5 = get_md5(cart_temp_file)
    create_hex_file(sq_img_file_md5, md5string_hex_file)
    append_file_to_file(cart_temp_file, md5string_hex_file)
    # TODO - Ask what the 32 bytes are for
    append_to_file(cart_temp_file, bytearray(32))
    make_save_partition(md5string_hex_file)
    save_part_md5 = get_md5(md5string_hex_file)
    create_hex_file(save_part_md5, md5string_hex_file)
    append_file_to_file(cart_temp_file, md5string_hex_file)
    append_file_to_file(cart_temp_file, md5string_hex_file)
    shutil.copy(cart_temp_file, output_file)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-i', '--inputdir', dest='input_dir', help="Input directory.")
    parser.add_option('-o', '--outfile', dest='out_file', help="Output file.")
    return parser


def validate_opts(parser):
    (options, args) = parser.parse_args()
    if None in (options.input_dir, options.out_file):
        parser.print_help()
        exit(0)
    return options, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (options, args) = validate_opts(parser)
    run(options.input_dir, options.out_file, './buildtemp')
