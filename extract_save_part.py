#!/usr/bin/env python3

import os
import logging
import argparse

import common_utils
import uce_utils
import operations


def validate_args(input_path):
    return common_utils.validate_required_path(input_path)


def main(input_path, output_path=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    if not validate_args(input_path):
        return False
    output_path = os.path.abspath(output_path) if output_path else os.path.join(input_path, 'save.img')
    squashfs_etc, save_data = uce_utils.split_uce(input_path)
    common_utils.write_file(output_path, save_data, 'wb')


if __name__ == "__main__":
    opts_set = operations.operations['extract_uce_save_partition']
    parser = argparse.ArgumentParser(prog='extract_save_part')
    for opt in opts_set:
        long_opt = '--{0}'.format(opt['name']).replace('_', '')
        short_opt = '-{0}'.format(opt['short'])
        parser.add_argument(long_opt, short_opt, dest=opt['name'], default=None)
    args = vars(parser.parse_args())
    main(args['input_path'], args['output_path'])
