#!/bin/bash

echo "************* Start Build UCE Script **************"

inputdir="$1"
cart_file=$2

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

workdir=$(mktemp -d)

cart_tmp_file="$workdir/byog_cartridge_shfs_temp.img"
export cart_save_file="$workdir/byog_cart_saving_ext4.img"
my_md5string_hex_file="$workdir/my_md5string_hex.bin"

export cart_saving_size=4M

echo $cart_saving_size

mkdir -p "$workdir/data"
cp -R "$inputdir"/* "$workdir/data/"
mkdir -p "$workdir/data/save"

chmod 755 "$workdir/data/exec.sh"

#$(cd "$workdir/data" && rm -f title.png && ln -sf boxart/boxart.png title.png)

mksquashfs "$workdir/data" $cart_tmp_file -b 262144 -root-owned -nopad

export SQIMGFILESIZE=$(stat -c%s "$cart_tmp_file")

echo $SQIMGFILESIZE

REAL_BYTES_USED=$($SCRIPT_DIR/real_bytes_used.sh)

echo $REAL_BYTES_USED

dd if=/dev/zero bs=1 count=$((REAL_BYTES_USED-SQIMGFILESIZE)) >> $cart_tmp_file

md5=$(md5sum "$cart_tmp_file" | cut -d ' '  -f 1)
echo $md5 | xxd -r -p > $my_md5string_hex_file

dd if=$my_md5string_hex_file of=$cart_tmp_file ibs=16 count=1 obs=16 oflag=append conv=notrunc

dd if=/dev/zero of=$cart_tmp_file ibs=16 count=2 obs=16 oflag=append conv=notrunc

/bin/rm -f $my_md5string_hex_file

"$SCRIPT_DIR/make_ext4_part.sh"

md5=$(md5sum "$cart_save_file" | cut -d ' '  -f 1)
echo $md5 | xxd -r -p > $my_md5string_hex_file

dd if=$my_md5string_hex_file of=$cart_tmp_file ibs=16 count=1 obs=16 oflag=append conv=notrunc

cat $cart_tmp_file $cart_save_file > "$cart_file"

