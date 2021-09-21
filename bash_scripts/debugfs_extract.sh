#!/bin/bash

if (($# < 1)); then
  echo "Usage:"
  echo $0 source_img target_dir
  exit 1
fi

STARTDIR=$(pwd)

cd "$1" || exit

debugfs -R 'rdump / save_part_contents' save.img
#debugfs -R 'rdump / uce_contents' save.img 2> /dev/null

cd "$STARTDIR" || exit
