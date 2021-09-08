#!/bin/bash

truncate -s 4M $cart_save_file
mkfs.ext4 $cart_save_file
debugfs -R 'mkdir upper' -w $cart_save_file
debugfs -R 'mkdir work' -w $cart_save_file