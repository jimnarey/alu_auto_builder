#!/usr/bin/env python3

# Runners

def start_operation(operation_name):
    return 'Starting {} operation'.format(operation_name)


def end_operation(operation_name):
    return 'Operation {0} complete'.format(operation_name)


# Create gamelist

ATTEMPTING_WIN_SKYSCRAPER_SETUP = 'Attempting to copy required .skyscraper and RetroPie dirs to user home dir'

USING_PACKAGED_SKYSCRPAER_WIN = 'Using packaged copy of Skyscraper for Windows'

USING_EXTERNAL_SKYSCRPAER = 'Attempting to use external copy of Skyscraper'


# Building recipes

NO_BOXART_FOUND = 'No boxart file found, using default'


# Build from recipes

def recipe_dir_check(dir_, result_text):
    return 'Directory {0} was checked and {1}'.format(dir_, result_text)


# Build from recipe

SAVE_DIR_DATA_FOUND = 'Custom save data found in save dir'

CREATING_BLANK_SAVE_PART = 'Creating blank save partition'


def processing_save_file(source_type):
    return 'Processing {0} as new save partition'.format(source_type)


def copying_extracted_save_file(save_file, save_zip):
    return 'Copying save file {0} extracted from {1}'.format(save_file, save_zip)


def creating_save_from_files(dir_path):
    return 'Creating save partition from contents of {0}'.format(dir_path)


# Edit UCE

def file_manager_not_found(file_manager):
    return 'File manager {0} was not found on the system'.format(file_manager)


FILEMAN_NOT_LINUX = 'File manager option can only be used on Linux, ignoring'

CONSOLE_WAIT_FOR_USER_INPUT = 'Press enter when ready'

GUI_WAIT_FOR_USER_INPUT = 'Press OK when finished editing'


# Common Utils

def created_temp_dir(calling_module):
    return 'Created temp dir for module {0}'.format(calling_module)


def ran_command(cmd):
    return 'Successfully ran command: {0}'.format(' '.join(cmd))


def access_success(access_type, path):
    prep = 'to' if access_type == 'wrote' else 'from'
    return 'Successfully {0} data {1} {2}'.format(access_type, prep, path)


def dir_already_exists(dir_):
    return 'Directory {0} already exists'.format(dir_)


def make_dir_success(dir_):
    return 'Dir {0} successfully created or already exists'.format(dir_)


def remove_success(item_type, path):
    return 'Successfully removed {0} {1}'.format(item_type, path)


def copy_success(item_type, source, dest):
    return 'Successfully copied {0} {1} to {2}'.format(item_type, source, dest)


def symlink_success(symlink, target):
    return 'Successfully created symlink {0} to target {1}'.format(symlink, target)


# UCE Utils

def split_uce(uce_path):
    return 'Splitting UCE file {0} into main section and save partition'.format(uce_path)


def rebuild_uce(uce_path):
    return 'Rebuilding UCE file {0}'.format(uce_path)


def modifying_save_part_perms(img_path):
    return 'Modifying save partition permissions in {0}'.format(img_path)


# Shared

def starting_new_process(name):
    return 'Starting new {0} build run'.format(name)


# GUI

def dialog_opened(operation_name):
    return "Opened dialog for '{0}'".format(operation_name)
