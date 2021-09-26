#!/usr/bin/env python3
import os
import logging


def validate_recipe_subdirs(dir_):
    valid = True
    for subdir in ('emu', 'roms'):
        subdir_path = os.path.join(dir_, subdir)
        if not os.path.isdir(subdir_path):
            logging.warning('Directory {0} does not contain {1} subdir'.format(dir_, subdir))
            valid = False
        if not os.listdir(subdir_path):
            logging.warning('Directory {0} in {1} is empty'.format(subdir, dir_))
            valid = False
    return valid


def validate_recipe_files(dir_):
    for file_name in ('exec.sh', 'cartridge.xml'):
        if not os.path.isfile(os.path.join(dir_, file_name)):
            logging.warning('Directory {0} does not contain a file named {1}'.format(dir_, file_name))
            return False
    return True


def validate_recipe_dir(dir_):
    if validate_recipe_subdirs(dir_) and validate_recipe_files(dir_):
        logging.info('Directory {0} has passed a cursory sense check and will be processed as a recipe'.format(dir_))
        return True
    logging.warning('Directory {0} failed basic checks and will be skipped'.format(dir_))
    return False


def get_recipe_dirs(input_dir):
    recipe_dirs = [item for item in os.listdir(input_dir) if os.path.isdir(item) and validate_recipe_dir(item)]


def main(input_dir, output_dir=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    output_dir = os.path.abspath(output_dir) if output_dir else os.path.join(input_dir, 'UCE')
