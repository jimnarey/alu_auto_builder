#!/usr/bin/env python3

import os
import logging
import argparse

import common_utils
import uce_utils
import operations


def validate_args(input_path, part_path):
    valid = True
    for file_path in (input_path, part_path):
        valid = common_utils.validate_required_path(file_path)
    return valid


def main(input_path, part_path, backup_uce=False):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    if not validate_args(input_path, part_path):
        return False
    squashfs_etc_data, save_data = uce_utils.split_uce(input_path)
    if backup_uce:
        backup_path = input_path + '.bak'
        common_utils.copyfile(input_path, backup_path)
    uce_utils.rebuild_uce(input_path, squashfs_etc_data, part_path)


if __name__ == "__main__":
    opts_set = operations.operations['replace_uce_save_partition']
    parser = argparse.ArgumentParser(prog='replace_save_part')
    for opt in opts_set:
        long_opt = '--{0}'.format(opt['name']).replace('_', '')
        short_opt = '-{0}'.format(opt['short'])
        if opt['short'].islower():
            action = 'store'
            default = None
        else:
            action = 'store_true'
            default = False
        parser.add_argument(long_opt, short_opt, dest=opt['name'], default=default, action=action)
    args = vars(parser.parse_args())
    main(args['input_path'], args['part_path'], args['backup_uce'])
