#!/usr/bin/env python3

# GUI

def required_option_not_set(option_name):
    readable_name = option_name.replace('_', ' ').title()
    return 'Option {0} is required but not set'.format(readable_name)

# Scraping

SCRAPE_INVALID_PLATFORM = 'You must provide a valid platform (emulated system) to enable scraping'
SCRAPE_INVALID_MODULE = 'You must provide a valid scraping module (metadata source) when scraping'


# UCE Building

SAVE_NOT_VALID_ZIP = 'save.zip is not a valid zipfile'

ZIP_HAS_NO_SAVE_IMG = 'save.zip does not contain a file named save.img'


def zip_extract_failed(exception_message):
    return 'Unable to extract and copy save.img file from zip: {0}'.format(exception_message)


# OS Errors

INVALID_OS = 'This tool requires either Linux or Windows'


# Edit UCE

INVALID_MOUNT_CONFIG = 'Mount option is only available under Linux and when running as root'

FILEMAN_NOT_LINUX = 'File manager option can only be used on Linux'

INVALID_FILEMAN = 'The specified file manager does not appear to be a valid executable'

NO_FILE_MAN_FOUND = 'No filemanager was found. This tool does not have a complete list. Specify one explicitly'


# Recipe dir warnings

def no_required_subdir(dir_, subdir):
    return 'Directory {0} does not contain {1} subdir'.format(dir_, subdir)


def no_required_file(dir_, file_name):
    return 'Directory {0} does not contain a file named {1}'.format(dir_, file_name)


def dir_is_empty(dir_, subdir):
    return 'Directory {0} in {1} is empty'.format(subdir, dir_)


# Common Utils

def failed_to_create_temp_dir(exception_message):
    return 'Failed to create temp dir: '.format(exception_message)


def command_exited_non_zero(code, cmd):
    return 'Last command exited with error code {0}: {1}'.format(code, ' '.join(cmd))


def command_failed_with_exception(cmd, exception_message):
    return 'Command {0} failed to run: {1}'.format(' '.join(cmd), exception_message)


def access_failure(access_type, path, exception_message):
    return 'Failed to {0} data to/from {1}: {2}'.format(access_type, path, exception_message)


def make_dir_failure(path, exception_message):
    return 'Failed to create directory {0}: {1}'.format(path, exception_message)


def delete_failure(item_type, path, exception_message):
    return 'Failed to remove {0} {1}: {2}'.format(item_type, path, exception_message)


def copy_failure(item_type, source, dest, exception_message):
    return 'Error copying {0} {1} to {2}: {3}'.format(item_type, source, dest, exception_message)


def symlink_failure(symlink, target, exception_message):
    return 'Failed to create symlink {0} to target {1}: {2}'.format(symlink, target, exception_message)


# Shared

def invalid_path(option_name, path, path_type):
    return '{0} {1} is not a valid {2}'.format(option_name, path, path_type)

