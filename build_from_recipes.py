#!/usr/bin/env python3
import os
import logging
from optparse import OptionParser

import build_uce_tool
import common_utils
import errors
import operations


def validate_args(input_dir, output_dir):
    valid = True
    if not common_utils.validate_existing_dir(input_dir):
        valid = False
    if not common_utils.validate_parent_dir(output_dir):
        valid = False
    return valid


def validate_recipe_subdirs(dir_):
    valid = True
    for subdir in ('emu', 'roms'):
        subdir_path = os.path.join(dir_, subdir)
        if not os.path.isdir(subdir_path):
            logging.warning('Directory {0} does not contain {1} subdir'.format(dir_, subdir))
            valid = False
        elif not os.listdir(subdir_path):
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
    sub_dirs = [os.path.join(input_dir, item) for item in os.listdir(input_dir)]
    recipe_dirs = [dir_ for dir_ in sub_dirs if validate_recipe_dir(dir_)]
    return recipe_dirs


def make_recipes(recipe_dirs, output_dir):
    for dir_ in recipe_dirs:
        output_path = os.path.join(output_dir, '{0}.uce'.format(os.path.split(dir_)[-1]))
        build_uce_tool.main(dir_, output_path)


def main(input_dir, output_dir=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    input_dir = os.path.abspath(input_dir) if input_dir else os.getcwd()
    if not validate_args(input_dir, output_dir):
        return False
    output_dir = os.path.abspath(output_dir) if output_dir else os.path.join(input_dir, 'UCE')
    common_utils.make_dir(output_dir)
    recipe_dirs = get_recipe_dirs(input_dir)
    make_recipes(recipe_dirs, output_dir)


if __name__ == "__main__":
    parser = common_utils.get_cmd_line_args(operations.operations['build_uces_from_recipes'])
    args = vars(parser.parse_args())
    main(args['input_dir'], output_dir=args['output_dir'])
