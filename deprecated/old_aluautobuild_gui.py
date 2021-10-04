#!/usr/bin/env python3

import os
import sys
import functools
from pathlib import Path
import logging

from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontMetrics, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QHBoxLayout, QLabel, \
    QPushButton, QWidget, QFileDialog, QComboBox

import common_utils
import configs
import aluautobuild
import error_messages


class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.font = QFont('Arial', 10)
        self.font_metrics = QFontMetrics(self.font)
        self.path_label_width_px = 300
        self.path_label_height_px = 30
        self.title_label_width_px = 250
        self.setWindowTitle('Auto UCE Builder')
        self.setStyleSheet("background-color: grey")
        self.layout_widgets = {}
        self.fields = {}
        self.combos = {}
        self.buttons = {}
        self.main_layout = self._create_main_layout()
        self.init_ui()

    def _create_main_layout(self):
        main_layout = QVBoxLayout()
        layout_container = QWidget()
        layout_container.setLayout(main_layout)
        self.setCentralWidget(layout_container)
        return main_layout

    def init_ui(self):
        self._create_operation_type_widget()
        for path_widget_params in (
                ('input_dir', 'Choose Input Dir', 'Required'),
                ('output_dir', 'Choose Output Dir', ''),
                ('core_path', 'Choose Core', 'Required'),
                ('bios_dir', 'Choose Bios Dir', 'Optional'),
                ('gamelist_path', 'Choose gamelist.xml', 'Required')
        ):

            self._create_path_select_widget(path_widget_params[0], path_widget_params[1], path_widget_params[2])

        for combo_widget_params in (
                ('platform', 'Choose Platform:', configs.PLATFORMS),
                ('scrape_module', 'Choose Scraping Module:', configs.SCRAPING_MODULES)
        ):
            self._create_combo_select_widget(combo_widget_params[0], combo_widget_params[1], combo_widget_params[2])

        for text_widget_params in (
                ('user_name', 'Username:'),
                ('password', 'Password:')
        ):
            self._create_text_input_widget(text_widget_params[0], text_widget_params[1])

        self._create_main_buttons_widget()
        for widget_name in ('input_dir', 'output_dir', 'bios_dir', 'core_path', 'gamelist_path', 'platform', 'scrape_module', 'user_name', 'password',  'main_buttons'):
            self.layout_widgets[widget_name].hide()

    def _create_user_input_widget(self, *args):
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        for arg in args:
            layout.addWidget(arg)
        return widget

    def _create_path_select_widget(self, name, button_text, init_text):
        path_label = self._create_path_field(name, init_text)
        button = self._create_button(name, button_text)
        widget = self._create_user_input_widget(path_label, button)
        self.layout_widgets[name] = widget
        self.main_layout.addWidget(widget)

    def _create_combo_select_widget(self, name, label_text, items):
        title_label = self._create_title_label(label_text)
        option_select = QComboBox()
        option_select.addItems(items)
        widget = self._create_user_input_widget(title_label, option_select)
        self.layout_widgets[name] = widget
        self.combos[name] = option_select
        self.main_layout.addWidget(widget)

    def _create_text_input_widget(self, name, label_text):
        title_label = self._create_title_label(label_text)
        text_input = QLineEdit()
        widget = self._create_user_input_widget(title_label, text_input)
        self.layout_widgets[name] = widget
        self.fields[name] = text_input
        self.main_layout.addWidget(widget)

    def _create_operation_type_widget(self):
        scrape = self._create_button('scrape_op', 'Scrape')
        gamelist = self._create_button('gamelist_op', 'Gamelist.xml')
        widget = self._create_user_input_widget(scrape, gamelist)
        self.layout_widgets['op_type'] = widget
        self.main_layout.addWidget(widget)

    def _create_main_buttons_widget(self):
        run = self._create_button('run', 'Run')
        exit_ = self._create_button('exit', 'Exit')
        widget = self._create_user_input_widget(run, exit_)
        self.layout_widgets['main_buttons'] = widget
        self.main_layout.addWidget(widget)

    def _create_path_field(self, name, init_text):
        label = QLabel()
        label.setFixedWidth(self.path_label_width_px)
        label.setFixedHeight(self.path_label_height_px)
        label.setFont(self.font)
        label.setStyleSheet("border: 1px solid black;")
        label.setText(init_text)
        self.fields[name] = label
        return label

    def _create_title_label(self, label_text):
        title_label = QLabel()
        title_label.setFont(self.font)
        title_label.setFixedWidth(self.title_label_width_px)
        title_label.setText(label_text)
        return title_label

    def _create_button(self, name, text):
        button = QPushButton(text)
        button.setFont(self.font)
        button.setFixedHeight(30)
        self.buttons[name] = button
        return button

    def get_elided_text(self, text):
        return self.font_metrics.elidedText(text, 0, self.path_label_width_px - 10, 0)


class RunOpts:

    def __init__(self):
        self.gamelist_path = None
        self.input_dir = None
        self.output_dir = None
        self.core_path = None
        self.bios_dir = None
        self.platform = None
        self.scrape_module = None
        self.user_name = None
        self.password = None
        self.user_creds = None
        self.run_type = 'scrape'

    def _validate_gamelist_opts(self):
        valid = True
        if not self.gamelist_path:
            logging.error(error_messages.NO_INPUT_GAMELIST)
            valid = False
        if not self.output_dir:
            logging.error(error_messages.GAMELIST_NO_OUTPUT_DIR)
            valid = False
        return valid

    def _validate_scrape_opts(self):
        valid = True
        if not self.platform:
            logging.error(error_messages.SCRAPE_NO_PLATFORM)
            valid = False
        if not self.input_dir:
            logging.error(error_messages.SCRAPE_NO_INPUT_DIR)
            valid = False
        return valid

    def validate_opts(self):
        valid = True
        if not self.core_path:
            logging.error(error_messages.NO_CORE_FILE)
            valid = False
        if self.run_type == 'gamelist':
            valid = self._validate_gamelist_opts()
        elif self.run_type == 'scrape':
            valid = self._validate_scrape_opts()
        return valid

    def set_derived_opts(self):
        if not self.output_dir:
            self.output_dir = os.path.join(self.input_dir, 'output')
        self.user_creds = '{0}:{1}'.format(self.user_name, self.password)


class Controller:

    def __init__(self, view, opts):
        self._view = view
        self._opts = opts
        self.dialog_dir = str(Path.home())
        self._connect_signals()

    def _connect_signals(self):
        for name in ('gamelist_op', 'scrape_op'):
            self._view.buttons[name].clicked.connect(functools.partial(self._toggle_layout, name))
        for name in ('input_dir', 'output_dir', 'bios_dir'):
            self._view.buttons[name].clicked.connect(functools.partial(self._choose_dir, name))
        for name in ('core_path', 'gamelist_path'):
            self._view.buttons[name].clicked.connect(functools.partial(self._choose_file, name))
        for name in ('platform', 'scrape_module'):
            self._view.combos[name].currentIndexChanged.connect(functools.partial(self._combo_select, name))
        for name in ('user_name', 'password'):
            self._view.fields[name].textChanged.connect(functools.partial(self._text_field_edit, name))

        self._view.buttons['run'].clicked.connect(self._run)
        self._view.buttons['exit'].clicked.connect(sys.exit)

    def _toggle_layout(self, button_name):
        self._view.layout_widgets['op_type'].hide()
        if button_name == 'scrape_op':
            for name in ('input_dir', 'output_dir', 'bios_dir', 'core_path', 'platform', 'scrape_module', 'user_name', 'password', 'main_buttons'):
                self._view.layout_widgets[name].show()
                self._view.fields['output_dir'].setText('Optional')
            self._opts.run_type = 'scrape'
        else:
            for name in ('output_dir', 'bios_dir', 'core_path', 'gamelist_path', 'main_buttons'):
                self._view.layout_widgets[name].show()
                self._view.fields['output_dir'].setText('Required')
            self._opts.run_type = 'gamelist'

    def _choose_dir(self, name):
        dir_name = QFileDialog.getExistingDirectory(self._view, 'Select Directory', self.dialog_dir)
        if dir_name:
            dir_name = QDir.toNativeSeparators(dir_name)
        if os.path.isdir(dir_name):
            self._view.fields[name].setText(self._view.get_elided_text(dir_name))
            setattr(self._opts, name, dir_name)
            self.dialog_dir = dir_name

    def _choose_file(self, name):
        file_name = QFileDialog.getOpenFileName(self._view, 'Select File', self.dialog_dir)[0]
        if file_name:
            file_name = QDir.toNativeSeparators(file_name)
        if os.path.isfile(file_name):
            self._view.fields[name].setText(self._view.get_elided_text(file_name))
            setattr(self._opts, name, file_name)
            self.dialog_dir = os.path.split(file_name)[0]

    def _combo_select(self, name):
        setattr(self._opts, name, self._view.combos[name].currentText())

    def _text_field_edit(self, name):
        setattr(self._opts, name, self._view.fields[name].text())

    def _run(self):
        if self._opts.validate_opts():
            self._opts.set_derived_opts()
            aluautobuild.main(self._opts)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    app_root = common_utils.get_app_root()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(app_root, 'common', 'title.png')))
    main_window = Window()
    run_opts = RunOpts()
    Controller(main_window, run_opts)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
