#!/usr/bin/env python3
import os
import logging
from optparse import OptionParser

import build_uce_tool
import common_utils


def validate_args(input_dir, output_dir):
    valid = True
    for dir_ in (input_dir, output_dir):
        if not os.path.isdir(dir_):
            logging.error('Directory {0} is not a valid dir'.format(dir_))
            valid = False
    return valid


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
    return [item for item in os.listdir(input_dir) if os.path.isdir(item) and validate_recipe_dir(item)]


def make_recipes(recipe_dirs, output_dir):
    for dir_ in recipe_dirs:
        output_path = os.path.join(output_dir, '{0}.uce'.format(os.path.split(dir_)[-1]))
        build_uce_tool.main(dir_, output_path)


def main(input_dir, output_dir=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    input_dir = input_dir if input_dir else os.getcwd()
    output_dir = os.path.abspath(output_dir) if output_dir else os.path.join(input_dir, 'UCE')
    common_utils.make_dir(output_dir)
    if not validate_args(input_dir, output_dir):
        return False
    recipe_dirs = get_recipe_dirs(input_dir)
    make_recipes(recipe_dirs, output_dir)


def get_opts_parser():
    parser = OptionParser()
    parser.add_option('-i', '--inputdir', dest='input_dir', help="Dir containing recipe dirs", default=None)
    parser.add_option('-o', '--outputdir', dest='output_dir', help="Dir to save UCE files", default=None)
    return parser


def validate_opts(parser):
    (opts, args) = parser.parse_args()
    return opts, args


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = validate_opts(parser)

    main(opts.input_dir, opts.output_dir)
