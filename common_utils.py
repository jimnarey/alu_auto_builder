#!/usr/bin/env python3

import os
import sys
import shutil
import logging


def write_file(file_path, file_content, write_type):
    try:
        with open(file_path, write_type) as target_file:
            target_file.write(file_content)
    except OSError as e:
        logging.error('Unable to write to {0}: {1}'.format(file_path, e))


def get_file_content(file_path, read_type):
    try:
        with open(file_path, read_type) as read_file:
            content = read_file.read()
    except OSError as e:
        logging.error('Unable to read from file {0}: {1}'.format(file_path, e))
    return content


def make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        logging.info('Directory {0} already exists'.format(path))
    except OSError as e:
        logging.error('Failed to create directory {0}: {1}'.format(path, e))


def copyfile(source, dest):
    try:
        shutil.copy(source, dest)
    except OSError as e:
        logging.error('Error copying {0} to {1}: {2)'.format(source, dest, e))


def copytree(source, dest, symlinks=False):
    try:
        shutil.copytree(source, dest, symlinks=symlinks)
    except OSError as e:
        logging.error('Error copying whole directory {0} to new parent {1}: {2}'.format(source, dest, e))


def get_platform():
    if sys.platform.startswith('linux'):
        return 'linux'
    # if sys.platform in ('darwin', 'win32'):    
    if sys.platform in ('win32'):
        return sys.platform
    return False

