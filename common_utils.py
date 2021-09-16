#!/usr/bin/env python3

import os
import sys
import shutil
import logging
from subprocess import Popen, PIPE


def execute_with_output(cmd):
    logging.info('Running command: {0}'.format(' '.join(cmd)))
    with Popen(cmd, stdout=PIPE, bufsize=1,
               universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')
        return_code = p.wait()
    if return_code:
        logging.error('Last command does not appear to have completed successfully')


def write_file(file_path, file_content, write_type):
    logging.info('Writing data to {0}'.format(file_path))
    try:
        with open(file_path, write_type) as target_file:
            target_file.write(file_content)
    except OSError as e:
        logging.error('Unable to write to {0}: {1}'.format(file_path, e))


def get_file_content(file_path, read_type):
    logging.info('Reading data from {0}'.format(file_path))
    try:
        with open(file_path, read_type) as read_file:
            content = read_file.read()
    except OSError as e:
        logging.error('Unable to read from file {0}: {1}'.format(file_path, e))
    return content


def make_dir(path):
    logging.info('Attempting to make new dir {0}'.format(path))
    try:
        os.mkdir(path)
    except FileExistsError:
        logging.info('Directory {0} already exists'.format(path))
    except OSError as e:
        logging.error('Failed to create directory {0}: {1}'.format(path, e))


def copyfile(source, dest):
    logging.info('Copying file {0} to {1}'.format(source, dest))
    try:
        shutil.copy(source, dest)
    except OSError as e:
        logging.error('Error copying {0} to {1}: {2}'.format(source, dest, e))


def copytree(source, dest, symlinks=False):
    logging.info('Copying whole directory {0} to new parent {1}'.format(source, dest))
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

