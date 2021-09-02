#!/bin/bash

if (($# < 1)); then
  echo "Usage:"
  echo $0 save_part.img
  exit 1
fi

echo "Filepath passed to make_save_partition.sh"
echo "$1"

truncate -s 4M "$1"
mkfs.ext4 "$1"
debugfs -R 'mkdir upper' -w "$1"
debugfs -R 'mkdir work' -w "$1"