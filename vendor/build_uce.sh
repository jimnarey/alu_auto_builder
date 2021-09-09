#!/bin/bash

set -e

if (($# < 2)); then
  echo "Usage:"
  echo $0 /path/to/inputdata  output.uce
  exit 1
fi

inputdir="$1"
cart_file=$2

#mkdir -p out

workdir=$(mktemp -d)
trap "rm -R $workdir" 0 2 3 15

export BASEDIR="$PWD"
 
cart_tmp_file="$workdir/byog_cartridge_shfs_temp.img"
cart_save_file="$workdir/byog_cart_saving_ext4.img"
my_md5string_hex_file="$workdir/my_md5string_hex.bin"
 
cart_saving_size=4M
 
/bin/rm -f $cart_tmp_file
/bin/rm -f $cart_save_file

mkdir -p "$workdir/data"
cp -R "$inputdir"/* "$workdir/data/"
mkdir -p "$workdir/data/save"

find "$workdir/data" -name "*.lnk" -type f -print0 | xargs -0 -n1 ./resolve.sh
find "$workdir/data" -name "*.lnk" -type f -delete

chmod 755 "$workdir/data/exec.sh"

# resize box art
# convert "$1"/boxart/boxart.* -resize 223x307 boxart_resized.png
# /bin/rm -f "$1"/boxart/boxart.*
# /bin/mv boxart_resized.png "$1"/boxart/boxart.png

$(cd "$workdir/data" && rm -f title.png && ln -sf boxart/boxart.png title.png)

if [ -f "$workdir/data/save.zip" ]
then
  /bin/mv "$workdir/data/save.zip" "$workdir/"
fi

mksquashfs "$workdir/data" $cart_tmp_file -b 262144 -root-owned -nopad
 
SQIMGFILESIZE=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $SQIMGFILESIZE Bytes (before applying 4k alignment)"
 
REAL_BYTES_USED_DIVIDED_BY_4K=$((SQIMGFILESIZE/4096))
if  [ $((SQIMGFILESIZE % 4096)) != 0 ]
then
  REAL_BYTES_USED_DIVIDED_BY_4K=$((REAL_BYTES_USED_DIVIDED_BY_4K+1))
fi
REAL_BYTES_USED=$((REAL_BYTES_USED_DIVIDED_BY_4K*4096))
 
dd if=/dev/zero bs=1 count=$((REAL_BYTES_USED-SQIMGFILESIZE)) >> $cart_tmp_file
 
SQIMGFILESIZE=$(stat -c%s "$cart_tmp_file")

echo "*** Size of $cart_tmp_file: $SQIMGFILESIZE Bytes (after applying 4k alignment)"
 
# header padding 64 bytes
EXT4FILE_OFFSET=$((SQIMGFILESIZE+64));
echo "*** Offset of Ext4 partition for file saving would be: $EXT4FILE_OFFSET ($SQIMGFILESIZE + 64)"
 
md5=$(md5sum "$cart_tmp_file" | cut -d ' '  -f 1)
echo "*** SQFS Partition MD5 Hash: "$md5""
echo $md5 | xxd -r -p > $my_md5string_hex_file

echo "*** Appending 16 bytes of SQFS Partition MD5 to $cart_tmp_file"
dd if=$my_md5string_hex_file of=$cart_tmp_file ibs=16 count=1 obs=16 oflag=append conv=notrunc

filesize=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $filesize Bytes (after SQFS MD5)"

echo "*** Padding 32 bytes of zeros to $cart_tmp_file"
dd if=/dev/zero of=$cart_tmp_file ibs=16 count=2 obs=16 oflag=append conv=notrunc

filesize=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $filesize Bytes (after padding zeros)"
 
/bin/rm -f $my_md5string_hex_file
 
truncate -s $cart_saving_size $cart_save_file
mkfs.ext4 $cart_save_file
debugfs -R 'mkdir upper' -w $cart_save_file
debugfs -R 'mkdir work' -w $cart_save_file
 
md5=$(md5sum "$cart_save_file" | cut -d ' '  -f 1)
echo "*** Ext4 Partition MD5 Hash: "$md5""
echo $md5 | xxd -r -p > $my_md5string_hex_file

echo "*** Appending 16 bytes of Ext4 Partition MD5 to $cart_tmp_file"
dd if=$my_md5string_hex_file of=$cart_tmp_file ibs=16 count=1 obs=16 oflag=append conv=notrunc

filesize=$(stat -c%s "$cart_tmp_file")
echo "*** Size of $cart_tmp_file: $filesize Bytes (after Ext4 MD5)"
 
filesize=$(stat -c%s "$cart_save_file")
echo "*** Size of $cart_save_file: $filesize Bytes (save partition)"

bind files together
if [ -f "$workdir/save.zip" ]
then
  unzip "$workdir/save.zip" -d "$workdir"
  /bin/mv "$workdir/save.bin" $cart_save_file
fi

cat $cart_tmp_file $cart_save_file > "$cart_file"

filesize=$(stat -c%s "$cart_file")
echo "*** Final size ($cart_file): $filesize Bytes (cart + save)"
 
#/bin/rm -f $my_md5string_hex_file
#/bin/rm -f $cart_tmp_file
#/bin/rm -f $cart_save_file

