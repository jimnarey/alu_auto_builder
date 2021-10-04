#!/usr/bin/env python3

import logging

from shared import common_utils, uce_utils
import operations


def validate_args(input_path, part_path):
    valid = True
    for file_path in (input_path, part_path):
        if not common_utils.validate_required_path(file_path, 'Specified file'):
            valid = False
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


def run_with_args(args):
    main(args['input_path'], args['part_path'], backup_uce=args['backup_uce'])


if __name__ == "__main__":
    parser = common_utils.get_cmd_line_args(operations.operations['replace_uce_save_partition']['options'])
    args = vars(parser.parse_args())
    run_with_args(args)
