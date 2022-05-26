#!/usr/bin/env python3

import os
import sys
import functools
from pathlib import Path
import logging

from PyQt5.QtCore import QDir, pyqtRemoveInputHook, pyqtSignal, QThread, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QWidget, QFileDialog, QComboBox, QDialog, QCheckBox, QMessageBox, QPlainTextEdit, QSizePolicy

import tailhead

from shared import common_utils, error_messages, info_messages
import operations

logger = logging.getLogger(__name__)

LOG_PATH = os.path.join(common_utils.get_app_root(), 'log.txt')


def reset_logging():
    logging.basicConfig(filename=LOG_PATH,
                        filemode='w',
                        level=logging.INFO,
                        format="%(levelname)s : %(asctime)s : %(message)s",
                        datefmt="%H:%M:%S")


def title_from_name(name):
    return name.replace('_', ' ').title()


class MainWindow(QMainWindow):

    def __init__(self, operations, parent=None):
        super().__init__(parent)
        self.setWindowTitle('UCE Tool')
        self.welcome_html = self._get_welcome_html()
        self.op_buttons = {}
        self.op_descriptions = {}
        self.op_buttons_layout = QVBoxLayout()
        self.help_box = QPlainTextEdit()
        self._setup_help_box()
        self.main_layout = QHBoxLayout()
        self._setup_main_layout()
        self._create_operation_buttons(operations)
        self.exit_button = QPushButton('Exit')
        self.exit_button.installEventFilter(self)
        self.op_buttons_layout.addWidget(self.exit_button)
        self.setCentralWidget(self.main_layout_container)

    def _setup_help_box(self):
        self.help_box.setReadOnly(True)
        self.help_box.appendHtml(self.welcome_html)

    def _setup_main_layout(self):
        self.main_layout_container = QWidget()
        self.main_layout_container.setLayout(self.main_layout)
        self.main_layout.addWidget(self.help_box)
        self.main_layout.addLayout(self.op_buttons_layout)

    def _get_welcome_html(self):
        welcome_html_source = os.path.join(common_utils.get_app_root(), 'html', 'welcome.html')
        return common_utils.get_file_content(welcome_html_source, 'r')

    def _create_operation_buttons(self, operations):
        for operation_name in operations:
            self._create_button(operation_name)

    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverMove:
            self.help_box.clear()
            self.help_box.appendHtml(self.op_descriptions.get(object, self.welcome_html))
            self.help_box.verticalScrollBar().setValue(self.help_box.verticalScrollBar().minimum())
            return True
        return False

    def _create_button(self, operation_name):
        button = QPushButton(title_from_name(operation_name))
        button.installEventFilter(self)
        self.op_buttons[operation_name] = button
        html_help_desc_source = os.path.join(common_utils.get_app_root(), 'html',
                                             '{0}_desc.html'.format(operation_name))
        self.op_descriptions[button] = common_utils.get_file_content(html_help_desc_source, 'r')
        self.op_buttons_layout.addWidget(button)


class OperationDialog(QDialog):

    def __init__(self, name, opts, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title_from_name(name))
        # Setup layouts
        self.dialog_layout = QHBoxLayout()
        self.help_box = QPlainTextEdit()
        self.input_layout = QVBoxLayout()
        self.input_layout_container = QWidget()
        self.log_box = QPlainTextEdit()
        # Control containers parsed by Controller
        self.check_boxes = {}
        self.combo_selects = {}
        self.opt_buttons = []
        # Create controls and populate input_layout
        self._create_opt_inputs(opts)
        self._setup_input_layout()
        self.run_button = QPushButton('Run')
        self.close_button = QPushButton('Close')
        self._create_user_input_widget(self.run_button, self.close_button)
        self._setup_help_box()
        self._setup_log_box()
        self._setup_dialog_layout()
        self.setLayout(self.dialog_layout)

    def _setup_help_box(self):
        self.help_box.setReadOnly(True)
        self.help_box.setMinimumWidth(400)
        self.help_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def _setup_dialog_layout(self):
        self.dialog_layout.addWidget(self.help_box)
        self.dialog_layout.addWidget(self.input_layout_container)
        self.dialog_layout.addWidget(self.log_box)

    def _setup_input_layout(self):
        self.input_layout_container.setLayout(self.input_layout)
        self.input_layout_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.input_layout.addStretch()

    def _setup_log_box(self):
        self.log_box.setMinimumWidth(600)
        self.log_box.setMinimumHeight(500)
        self.log_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_box.setReadOnly(True)
        self.log_box.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.log_box.setStyleSheet("background-color: black; color: white")

    def _create_user_input_widget(self, *args):
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        for arg in args:
            layout.addWidget(arg)
        layout.addStretch()
        self.input_layout.addWidget(widget)

    def _create_opt_inputs(self, opts):
        for opt in opts:
            if opt['type'] == 'bool':
                self._create_checkbox_widget(opt)
            else:
                self._create_select_widget(opt)

    def _create_title_label(self, opt):
        title_label = QLabel()
        title_label.setToolTip(opt['help'])
        title_label.setFixedWidth(160)
        title_label.setText(title_from_name(opt['name']))
        return title_label

    def _create_opt_button(self, opt, button_text):
        button = QPushButton(button_text)
        button.setFixedHeight(30)
        self.opt_buttons.append({
            'name': opt['name'],
            'type': opt['type'],
            'button': button
        })
        return button

    def _create_checkbox_widget(self, opt):
        widgets = [self._create_title_label(opt)]
        checkbox = QCheckBox()
        self.check_boxes[opt['name']] = checkbox
        widgets.append(checkbox)
        self._create_user_input_widget(*widgets)

    def _create_select_widget(self, opt):
        widgets = [self._create_title_label(opt)]
        combo = QComboBox()
        if opt.get('selections', False):
            combo.addItem('')
            combo.addItems(opt.get('selections', []))
        combo.setFixedWidth(200)
        combo.setEditable(True)
        self.combo_selects[opt['name']] = combo
        widgets.append(combo)
        if opt['type'] in ('dir', 'file_open', 'file_save'):
            widgets.append(self._create_opt_button(opt, 'Select'))
        self._create_user_input_widget(*widgets)


class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, operation, args_dict, parent=None):
        super(Worker, self).__init__(parent)
        self.operation = operation
        self.args_dict = args_dict

    def run(self):
        self.operation(self.args_dict)


class LogWatcher(QThread):
    newLine = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        for line in tailhead.follow_path(self.path):
            if line is not None:
                self.newLine.emit(line)
            else:
                self.msleep(10)


class Controller:

    def __init__(self, operations):
        self.dialog_dir = str(Path.home())
        self.current_view = None
        self.args = {}
        self.operations = operations
        self.current_operation_name = None
        self.log_watcher = LogWatcher(LOG_PATH)
        self.log_watcher.newLine.connect(self._update_text_box)
        self.log_watcher.start()

    def _close_current_view(self):
        if self.current_view:
            self.current_view.close()

    def _show_view(self, view):
        self.current_view = view
        view.show()

    def connect_dialog_opt_button_signals(self, view):
        for button in view.opt_buttons:
            if button['type'] == 'dir':
                button['button'].clicked.connect(functools.partial(self._choose_dir, view, button['name']))
            elif button['type'] == 'file_open':
                button['button'].clicked.connect(functools.partial(self._open_file, view, button['name']))
            elif button['type'] == 'file_save':
                button['button'].clicked.connect(functools.partial(self._save_file, view, button['name']))

    def connect_dialog_main_button_signals(self, view):
        view.run_button.clicked.connect(self._run)
        view.close_button.clicked.connect(self.show_main_window)

    def _connect_dialog_combo_signals(self, view):
        for name, combo in view.combo_selects.items():
            combo.currentTextChanged.connect(functools.partial(self._change_combo_content, view, name))
            combo.currentIndexChanged.connect(functools.partial(self._change_combo_content, view, name))

    def _connect_dialog_checkbox_signals(self, view):
        for name, checkbox in view.check_boxes.items():
            checkbox.toggled.connect(functools.partial(self._change_checkbox_value, view, name))

    def _connect_dialog_signals(self, view):
        self.connect_dialog_opt_button_signals(view)
        self.connect_dialog_main_button_signals(view)
        self._connect_dialog_combo_signals(view)
        self._connect_dialog_checkbox_signals(view)

    def _show_dialog_help(self, operation_name, view):
        html_help_desc_source = os.path.join(common_utils.get_app_root(), 'html', '{0}_desc.html'.format(operation_name))
        html_help_opts_source = os.path.join(common_utils.get_app_root(), 'html',
                                             '{0}_opts.html'.format(operation_name))
        view.help_box.appendHtml(common_utils.get_file_content(html_help_desc_source, 'r'))
        view.help_box.appendHtml(common_utils.get_file_content(html_help_opts_source, 'r'))

    def _show_dialog(self, name):
        self.args = {}
        self._close_current_view()
        self.current_operation_name = name
        view = OperationDialog(name, operations.operations[name]['options'])
        self._show_dialog_help(name, view)
        self._connect_dialog_signals(view)
        self._show_view(view)
        view.help_box.verticalScrollBar().setValue(view.help_box.verticalScrollBar().minimum())
        logger.info(info_messages.dialog_opened(self.current_operation_name))

    def show_main_window(self):
        self._close_current_view()
        view = MainWindow(self.operations)
        for name, button in view.op_buttons.items():
            button.clicked.connect(functools.partial(self._show_dialog, name))
        view.exit_button.clicked.connect(sys.exit)
        self._show_view(view)

    def _choose_dir(self, view, name):
        dir_name = QFileDialog.getExistingDirectory(view, 'Select Directory', self.dialog_dir)
        if dir_name:
            dir_name = QDir.toNativeSeparators(dir_name)
        if os.path.isdir(dir_name):
            view.combo_selects[name].setCurrentText(dir_name)
            self.dialog_dir = dir_name

    def _open_file(self, view, name):
        file_name = QFileDialog.getOpenFileName(view, 'Open File', self.dialog_dir)[0]
        if file_name:
            file_name = QDir.toNativeSeparators(file_name)
        if os.path.isfile(file_name):
            view.combo_selects[name].setCurrentText(file_name)
            self.dialog_dir = os.path.split(file_name)[0]

    def _save_file(self, view, name):
        file_name = QFileDialog.getSaveFileName(view, 'Save File', self.dialog_dir)[0]
        if file_name:
            file_name = QDir.toNativeSeparators(file_name)
            view.combo_selects[name].setCurrentText(file_name)
            self.dialog_dir = os.path.split(file_name)[0]

    def _change_combo_content(self, view, name):
        self.args[name] = view.combo_selects[name].currentText()

    def _change_checkbox_value(self, view, name):
        self.args[name] = view.check_boxes[name].isChecked()

    def _validate_args(self):
        valid = True
        for option in self.operations[self.current_operation_name]['options']:
            if option['gui_required']:
                if option['name'] not in self.args:
                    logging.error(error_messages.required_option_not_set(option['name']))
                    valid = False
            else:
                if option['name'] not in self.args:
                    self.args[option['name']] = None
        return valid

    def gui_continue_check(self):
        dialog = QMessageBox()
        dialog.setWindowTitle('Edit save partition')
        dialog.setText(info_messages.GUI_WAIT_FOR_USER_INPUT)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()
        dialog.destroy()

    def _update_text_box(self, str_):
        if hasattr(self.current_view, 'log_box'):
            self.current_view.log_box.appendPlainText(str_)
            self.current_view.log_box.verticalScrollBar().setValue(self.current_view.log_box.verticalScrollBar().maximum())

    def _run(self):
        if not self._validate_args():
            return False
        self.current_view.log_box.clear()
        if self.operations[self.current_operation_name]['gui_user_continue_check']:
            self.args['continue_check'] = self.gui_continue_check
            self.operations[self.current_operation_name]['runner'](self.args)
        else:
            self.worker = Worker(self.operations[self.current_operation_name]['runner'], self.args)
            self.worker.start()


if __name__ == '__main__':
    reset_logging()
    pyqtRemoveInputHook()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(common_utils.get_app_root(), 'data', 'title.png')))
    controller = Controller(operations.operations)
    controller.show_main_window()
    sys.exit(app.exec_())
