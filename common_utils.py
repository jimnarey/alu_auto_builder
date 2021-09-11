#!/usr/bin/env python3

import os
import sys
import errno


def write_file(file_path, file_content):
    with open(file_path, 'w') as target_file:
        target_file.write(file_content)


def safe_make_dir(path):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    pass


def get_platform():
    if sys.platform.startswith('linux'):
        return 'linux'
    # if sys.platform in ('darwin', 'win32'):    
    if sys.platform in ('win32'):
        return sys.platform
    return False

