#!/bin/bash

if (($# < 1)); then
  echo "Usage:"
  echo $0 save_part.img
  exit 1
fi

echo "Filepath passed to make_save_partition.sh:"
echo "$1"

cart_save_file="$1"

truncate -s 4M "$cart_save_file"
mkfs.ext4 "$cart_save_file"
debugfs -R 'mkdir upper' -w "$cart_save_file"
debugfs -R 'mkdir work' -w "$cart_save_file"
