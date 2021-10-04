#!/usr/bin/env python3

import os
import logging

from shared import common_utils, uce_utils
import operations


def validate_args(input_path):
    valid = True
    if not common_utils.validate_required_path(input_path, 'Input path'):
        valid = False
    return valid


def main(input_path, output_path=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    if not validate_args(input_path):
        return False
    output_path = os.path.abspath(output_path) if output_path else os.path.join(os.getcwd(), 'save.img')
    _, save_data = uce_utils.split_uce(input_path)
    common_utils.write_file(output_path, save_data, 'wb')


if __name__ == "__main__":
    parser = common_utils.get_cmd_line_args(operations.operations['extract_uce_save_partition']['options'])
    args = vars(parser.parse_args())
    main(args['input_path'], output_path=args['output_path'])
