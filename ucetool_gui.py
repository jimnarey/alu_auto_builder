#!/usr/bin/env python3

import os
import sys
import functools
from pathlib import Path
import logging
from pprint import pprint

import dearpygui.dearpygui as dpg

from shared import common_utils, error_messages, info_messages
import operations

logger = logging.getLogger(__name__)

LOG_PATH = os.path.join(common_utils.get_app_root(), 'log.txt')

LAST_DIR = common_utils.get_app_root()

# def reset_logging():
#     logging.basicConfig(filename=LOG_PATH,
#                         filemode='w',
#                         level=logging.INFO,
#                         format="%(levelname)s : %(asctime)s : %(message)s",
#                         datefmt="%H:%M:%S")
#
#

def testing():
    pass



def title_from_name(name):
    return name.replace('_', ' ').title()


def show_fs_dialog(sender, app_data, user_data):
    dpg.configure_item(user_data, default_path=LAST_DIR)
    dpg.show_item(user_data)


def fs_select_callback(sender, app_data, user_data):
    global LAST_DIR
    LAST_DIR = app_data.get('file_path_name')
    dpg.set_value(user_data, list(app_data.get('selections', ['']).values())[0])


def get_item_aliases_by_type(item_type):
    return [item for item in dpg.get_aliases() if item_type in item]


def run_operation_callback(sender, app_data, user_data):
    runopts = {}
    for item_alias in get_item_aliases_by_type('runopt'):
        runopts[item_alias.split('__runopt__')[0]] = dpg.get_value(item_alias)
    pprint(runopts)


def unique_item_name(name, item_type='runopt'):
    return '{0}__{1}__{2}'.format(name, item_type, dpg.generate_uuid())


def add_filesystem_selector(label, option_name, dir_select=False):
    dialog_tag = dpg.generate_uuid()
    input_text_tag = unique_item_name(option_name)
    dpg.add_file_dialog(tag=dialog_tag, directory_selector=dir_select, show=False, callback=fs_select_callback, user_data=input_text_tag)
    if not dir_select:
        dpg.add_file_extension(".*", parent=dialog_tag)
    with dpg.group(horizontal=True):
        dpg.add_input_text(tag=input_text_tag)
        dpg.add_button(label=label, callback=show_fs_dialog, user_data=dialog_tag)


def add_input_widget(option):
    if option.get('type') == 'bool':
        dpg.add_checkbox(tag=unique_item_name(option.get('name')), default_value=option.get('gui_default', False))
    elif option.get('type') == 'text':
        dpg.add_input_text(tag=unique_item_name(option.get('name', '')))
    elif option.get('type') == 'text_selection':
        dpg.add_combo(list(option.get('selections', [])), tag=unique_item_name(option.get('name')))
    elif option.get('type') == 'dir':
        add_filesystem_selector('Choose Dir', option.get('name'), dir_select=True)
    elif option.get('type') == 'file_open':
        add_filesystem_selector('Choose File', option.get('name'))
    elif option.get('type') == 'file_save':
        add_filesystem_selector('Target File', option.get('name'))


def create_operation_window(sender, app_data, user_data):
    dpg.delete_item("control_window", children_only=True)
    dpg.add_child_window(tag="operation_window", parent="control_window")
    dpg.add_table(tag="options_table", parent="operation_window", header_row=False)
    dpg.add_table_column(parent="options_table")
    dpg.add_table_column(parent="options_table")
    for option in user_data.get('options'):
        with dpg.table_row(parent="options_table"):
            dpg.add_text(title_from_name(option.get('name')))
            add_input_widget(option)
    with dpg.group(horizontal=True, parent="operation_window"):
        dpg.add_button(tag="run_button", label="Run", callback=run_operation_callback, user_data=user_data)
        dpg.add_button(tag="close_button", label="Close",  callback=lambda: dpg.delete_item("control_window", children_only=True))


def setup_menu():
    dpg.add_menu_bar(tag="menu_bar", parent="primary_window")
    dpg.add_menu(tag="operations_menu", label="Operations", parent="menu_bar")
    for key, operation in operations.operations.items():
        dpg.add_menu_item(label=title_from_name(key), parent="operations_menu", callback=create_operation_window,
                          user_data=operation)


if __name__ == '__main__':
    # reset_logging()
    dpg.create_context()

    with dpg.window(tag="primary_window"):
        dpg.add_child_window(tag="control_window", autosize_x=True, height=450)
        dpg.add_child_window(tag="log_window", autosize_x=True, height=150, horizontal_scrollbar=True)

    dpg.create_viewport(title='Custom Title')
    # dpg.create_viewport(title='Custom Title', autosize_y=True, autosize_x=True)
    dpg.setup_dearpygui()
    dpg.set_primary_window("primary_window", True)
    setup_menu()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
