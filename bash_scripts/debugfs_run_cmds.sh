#!/bin/bash

if (($# < 3)); then
  echo "Usage:"
  echo $0 save_part_contents_path cmd_file save_img
  exit 1
fi

STARTDIR=$(pwd)

cd "$1" || exit

debugfs  -w -f "$2" "$3"
#debugfs -R 'rdump / uce_contents' save.img 2> /dev/null

cd "$STARTDIR" || exit