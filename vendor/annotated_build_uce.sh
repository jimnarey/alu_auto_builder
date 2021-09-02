#!/bin/bash

set -e

if (($# < 2)); then
  echo "Usage:"
  echo $0 /path/to/inputdata  output.uce
  exit 1
fi

inputdir="$1"
cart_file=$2

# Not needed, at least when called from auto script
#mkdir -p out

# Created as via shutil.copytree call
workdir=$(mktemp -d)

# This isn't needed
trap "rm -R $workdir" 0 2 3 15

# This doesn't appear to do anything!
export BASEDIR="$PWD"

# Handled in set_image_file_paths
cart_tmp_file="$workdir/byog_cartridge_shfs_temp.img"
cart_save_file="$workdir/byog_cart_saving_ext4.img"
my_md5string_hex_file="$workdir/my_md5string_hex.bin"

# Set in global const CART_SAVING_FILE
cart_saving_size=4M

# Parked in TO_DO 1
/bin/rm -f $cart_tmp_file
/bin/rm -f $cart_save_file

# Handled in run (copytree, make_dirs)
mkdir -p "$workdir/data"
cp -R "$inputdir"/* "$workdir/data/"
mkdir -p "$workdir/data/save"

# Parked in TO_DO 2
#find "$workdir/data" -name "*.lnk" -type f -print0 | xargs -0 -n1 ./resolve.sh
#find "$workdir/data" -name "*.lnk" -type f -delete

# Handled in set_755
chmod 755 "$workdir/data/exec.sh"

# resize box art
# convert "$1"/boxart/boxart.* -resize 223x307 boxart_resized.png
# /bin/rm -f "$1"/boxart/boxart.*
# /bin/mv boxart_resized.png "$1"/boxart/boxart.png

# Handled in relink_boxart
$(cd "$workdir/data" && rm -f title.png && ln -sf boxart/boxart.png title.png)

# Handled in call to move_file
if [ -f "$workdir/data/save.zip" ]
then
  /bin/mv "$workdir/data/save.zip" "$workdir/"
fi

# Handled by call_mksquashfs
mksquashfs "$workdir/data" $cart_tmp_file -b 262144 -root-owned -nopad

# Handled by call to get_sq_img_file_size
SQIMGFILESIZE=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $SQIMGFILESIZE Bytes (before applying 4k alignment)"

# Handled by call to get_sq_image_real_bytes_used
REAL_BYTES_USED_DIVIDED_BY_4K=$((SQIMGFILESIZE/4096))
if  [ $((SQIMGFILESIZE % 4096)) != 0 ]
then
  REAL_BYTES_USED_DIVIDED_BY_4K=$((REAL_BYTES_USED_DIVIDED_BY_4K+1))
fi
REAL_BYTES_USED=$((REAL_BYTES_USED_DIVIDED_BY_4K*4096))

# Handled by call to pad_sq_img_file
dd if=/dev/zero bs=1 count=$((REAL_BYTES_USED-SQIMGFILESIZE)) >> $cart_tmp_file

# Parked in TO_DO 4
SQIMGFILESIZE=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $SQIMGFILESIZE Bytes (after applying 4k alignment)"

# Parked in TO_DO 3
# header padding 64 bytes
EXT4FILE_OFFSET=$((SQIMGFILESIZE+64));
echo "*** Offset of Ext4 partition for file saving would be: $EXT4FILE_OFFSET ($SQIMGFILESIZE + 64)"

# Handled by call to get_md5
md5=$(md5sum "$cart_tmp_file" | cut -d ' '  -f 1)
echo "*** SQFS Partition MD5 Hash: "$md5""

# Handled by call to create_hex_file
echo $md5 | xxd -r -p > $my_md5string_hex_file

# Handled by call to append_md5_to_img
echo "*** Appending 16 bytes of SQFS Partition MD5 to $cart_tmp_file"
dd if=$my_md5string_hex_file of=$cart_tmp_file ibs=16 count=1 obs=16 oflag=append conv=notrunc

# Parked in TO_DO 4
filesize=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $filesize Bytes (after SQFS MD5)"

# Handled by append_32_bytes
echo "*** Padding 32 bytes of zeros to $cart_tmp_file"
dd if=/dev/zero of=$cart_tmp_file ibs=16 count=2 obs=16 oflag=append conv=notrunc

# Parked in TO_DO 4
filesize=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $filesize Bytes (after padding zeros)"

# Parked in TO_DO 5
/bin/rm -f $my_md5string_hex_file

# Handled in bash_scripts/make_save_partition.sh
truncate -s $cart_saving_size $cart_save_file
mkfs.ext4 $cart_save_file
debugfs -R 'mkdir upper' -w $cart_save_file
debugfs -R 'mkdir work' -w $cart_save_file

# Handled by call to get_md5
md5=$(md5sum "$cart_save_file" | cut -d ' '  -f 1)
echo "*** Ext4 Partition MD5 Hash: "$md5""

# Handled by call to create_hex_file
echo $md5 | xxd -r -p > $my_md5string_hex_file

# Handled by call to append_md5_to_img
echo "*** Appending 16 bytes of Ext4 Partition MD5 to $cart_tmp_file"
dd if=$my_md5string_hex_file of=$cart_tmp_file ibs=16 count=1 obs=16 oflag=append conv=notrunc

# Parked in TO_DO 4
filesize=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $filesize Bytes (after Ext4 MD5)"

# Parked in TO_DO 4
filesize=$(stat -c%s "$cart_save_file")
echo "*** Size of $cart_save_file: $filesize Bytes (save partition)"

# Parked in TO_DO 6
#bind files together
if [ -f "$workdir/save.zip" ]
then
  unzip "$workdir/save.zip" -d "$workdir"
  /bin/mv "$workdir/save.bin" $cart_save_file
fi

cat $cart_tmp_file $cart_save_file > "$cart_file"

# Parked in TO_DO 4
filesize=$(stat -c%s "$cart_file")
echo "*** Final size ($cart_file): $filesize Bytes (cart + save)"
 
#/bin/rm -f $my_md5string_hex_file
#/bin/rm -f $cart_tmp_file
#/bin/rm -f $cart_save_file

