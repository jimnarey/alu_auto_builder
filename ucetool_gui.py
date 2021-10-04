#!/usr/bin/env python3

import os
import sys
import functools
from pathlib import Path
import logging

from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QWidget, QFileDialog, QComboBox, QDialog

import common_utils
# import configs
from shared import operations


def get_opt_type(name):
    name_parts = name.split('_')
    try:
        suffix = name_parts[-1]
        if suffix in ('dir', 'path'):
            return suffix
    except IndexError:
        pass
    return 'text'


def title_from_name(name):
    return name.replace('_', ' ').title()


class OptionSet:

    def __init__(self):
        pass


class MainWindow(QMainWindow):

    def __init__(self, operations, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Auto UCE Builder')
        self.main_layout = self._create_main_layout()
        self.op_buttons = {}
        self._create_operation_buttons(operations.keys())
        self.exit_button = QPushButton('Exit')
        self.main_layout.addWidget(self.exit_button)

    def _create_main_layout(self):
        main_layout = QVBoxLayout()
        layout_container = QWidget()
        layout_container.setLayout(main_layout)
        self.setCentralWidget(layout_container)
        return main_layout

    def _create_operation_buttons(self, op_names):
        for op_name in op_names:
            self._create_button(op_name)

    def _create_button(self, op_name):
        button = QPushButton(title_from_name(op_name))
        self.op_buttons[op_name] = button
        self.main_layout.addWidget(button)


class OperationDialog(QDialog):

    def __init__(self, name, opts, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title_from_name(name))
        self.dialog_layout = QVBoxLayout()
        self.fields = {}
        self.select_buttons = {}
        for opt in opts:
            self._create_select_widget(opt)
        self.ok_button = QPushButton('OK')
        self.close_button = QPushButton('Close')
        self._create_user_input_widget(self.ok_button, self.close_button)
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

    def _create_select_button(self, name):
        button = QPushButton('Select')
        button.setFixedHeight(30)
        self.select_buttons[name] = button
        return button

    def _create_select_widget(self, opts):
        widgets = [self._create_title_label(title_from_name(opts['name']))]
        field = QComboBox()
        field.addItems(opts.get('selections', []))
        field.setFixedWidth(200)
        field.setEditable(True)
        self.fields[opts['name']] = field
        widgets.append(field)
        if get_opt_type(opts['name']) in ('dir', 'path'):
            widgets.append(self._create_select_button(opts['name']))
        self._create_user_input_widget(*widgets)


class Controller:

    def __init__(self, option_set, operations):
        self.dialog_dir = str(Path.home())
        self.option_set = option_set
        self.current_view = None
        self.operations = operations

    def _close_current_view(self):
        if self.current_view:
            self.current_view.close()

    def _show_view(self, view):
        self.current_view = view
        view.show()

    def _connect_dialog_signals(self, view):
        for name, button in view.select_buttons.items():
            if get_opt_type(name) == 'dir':
                button.clicked.connect(functools.partial(self._choose_dir, view, name))
            elif get_opt_type(name) == 'path':
                button.clicked.connect(functools.partial(self._choose_file, view, name))
        view.ok_button.clicked.connect(self._run)
        view.close_button.clicked.connect(self.show_main_window)

    def _show_dialog(self, name):
        self._close_current_view()
        view = OperationDialog(name, operations.operations[name])
        self._connect_dialog_signals(view)
        self._show_view(view)

    def show_main_window(self):
        self._close_current_view()
        view = MainWindow(self.operations)
        for name, button in view.op_buttons.items():
            button.clicked.connect(functools.partial(self._show_dialog, name))
        view.exit_button.clicked.connect(sys.exit)
        self._show_view(view)


    # TODO - choose dir in combo box if valid
    def _choose_dir(self, view, name):
        dir_name = QFileDialog.getExistingDirectory(view, 'Select Directory', self.dialog_dir)
        if dir_name:
            dir_name = QDir.toNativeSeparators(dir_name)
        if os.path.isdir(dir_name):
            view.fields[name].setCurrentText(dir_name)
            self.dialog_dir = dir_name

    def _choose_file(self, view, name):
        file_name = QFileDialog.getOpenFileName(view, 'Select File', self.dialog_dir)[0]
        if file_name:
            file_name = QDir.toNativeSeparators(file_name)
        if os.path.isfile(file_name):
            view.fields[name].setCurrentText(file_name)
            self.dialog_dir = os.path.split(file_name)[0]

    def _run(self):
        pass

    # def _combo_select(self, name):
    #     setattr(self._opts, name, self._view.combos[name].currentText())
    #
    # def _text_field_edit(self, name):
    #     setattr(self._opts, name, self._view.fields[name].text())
    #
    # def _run(self):
    #     if self._opts.validate_opts():
    #         self._opts.set_derived_opts()
    #         aluautobuild.main(self._opts)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(common_utils.get_app_root(), 'data', 'title.png')))
    option_set = OptionSet()
    controller = Controller(option_set, operations.operations)
    controller.show_main_window()
    sys.exit(app.exec_())
