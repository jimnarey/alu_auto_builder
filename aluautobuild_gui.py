#!/usr/bin/env python3

import os
import sys
import functools
from pathlib import Path
import logging

from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontMetrics, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QHBoxLayout, QLabel, \
    QPushButton, QWidget, QFileDialog, QComboBox, QDialog, QFormLayout, QDialogButtonBox

import common_utils
import configs
import aluautobuild
import errors


scrape_opts = (
    {'name': 'input_dir'},
    {'name': 'output_dir'},
    {'name': 'bios_dir'},
    {'name': 'core_path'},
    {'name': 'platform', 'selections': configs.PLATFORMS},
    {'name': 'scrape_module', 'selections': configs.SCRAPING_MODULES},
    {'name': 'user_name', },
    {'name': 'password', },
)


def get_opt_type(name):
    name_parts = name.split('_')
    try:
        suffix = name_parts[1]
        if suffix in ('dir', 'path'):
            return suffix
    except IndexError:
        pass
    return 'text'


def label_text_from_name(name):
    return name.replace('_', ' ').title()


class Dialog(QDialog):

    def __init__(self, title, opts, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.dialog_layout = QVBoxLayout()
        self.buttons = {}
        for opt in opts:
            self._create_select_widget(opt)
        self._create_user_input_widget(self._create_button('ok', 'OK'), self._create_button('cancel', 'Cancel'))
        self.setLayout(self.dialog_layout)

    def _create_user_input_widget(self, *args):
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        for arg in args:
            layout.addWidget(arg)
        self.dialog_layout.addWidget(widget)

    def _create_title_label(self, label_text):
        title_label = QLabel()
        title_label.setFixedWidth(100)
        title_label.setText(label_text)
        return title_label

    def _create_button(self, name, text):
        button = QPushButton(text)
        button.setFixedHeight(30)
        self.buttons[name] = button
        return button

    def _create_select_widget(self, opts):
        widgets = [self._create_title_label(label_text_from_name(opts['name']))]
        field = QComboBox()
        field.addItems(opts.get('selections', []))
        field.setFixedWidth(200)
        field.setEditable(True)
        widgets.append(field)
        if get_opt_type(opts['name']) in ('dir', 'path'):
            widgets.append(self._create_button(opts['name'], 'Select'))
        self._create_user_input_widget(*widgets)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = Dialog('Scrape and Build', scrape_opts)
    dlg.show()
    sys.exit(app.exec_())
