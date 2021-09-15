#!/usr/bin/env python3

import os
import sys
import functools

from PyQt5.QtCore import QDir, QFile
from PyQt5.QtGui import QFontMetrics, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QLabel, \
    QPushButton, QDialog, QWidget, QFileDialog, QComboBox, QRadioButton

import configs
import aluautobuild


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
        self.run_type = 'scrape'
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
        self._create_input_path_layout()
        self._create_output_path_layout()
        self._create_other_paths_layout()
        self._create_gamelist_opts_layout()
        self._create_scraping_opts_layout()
        self._create_main_buttons_widget()
        for widget_name in ('input_dir', 'output_dir', 'other_dir', 'gamelist', 'scrape', 'main_buttons'):
            self.layout_widgets[widget_name].hide()

    def _create_input_path_layout(self):
        input_dir_row = self._create_fs_select('input_dir', 'Choose Input Dir', 'Required')
        widget = self._create_vertical_layout_widget('input_dir', input_dir_row)
        self.main_layout.addWidget(widget)

    def _create_output_path_layout(self):
        output_dir_row = self._create_fs_select('output_dir', 'Choose Output Dir', 'Optional')
        widget = self._create_vertical_layout_widget('output_dir', output_dir_row)
        self.main_layout.addWidget(widget)

    def _create_other_paths_layout(self):
        core_path_row = self._create_fs_select('core_path', 'Choose Core', 'Required')
        bios_dir_row = self._create_fs_select('bios_dir', 'Choose Bios Dir', 'Optional')
        widget = self._create_vertical_layout_widget('other_dir', core_path_row, bios_dir_row)
        self.main_layout.addWidget(widget)

    def _create_gamelist_opts_layout(self):
        gamelist_path_row = self._create_fs_select('gamelist_path', 'Choose gamelist.xml', 'Required')
        widget = self._create_vertical_layout_widget('gamelist', gamelist_path_row)
        self.main_layout.addWidget(widget)

    def _create_scraping_opts_layout(self):
        platform_row = self._create_combo_select('platform', 'Choose Platform:', configs.GUI_PLATFORMS)
        scrape_module_row = self._create_combo_select('scrape_module', 'Choose Scraping Module:',
                                                      configs.SCRAPING_MODULES)
        user_name_row = self._create_text_input('user_name', 'Username:')
        password_row = self._create_text_input('password', 'Password:')
        widget = self._create_vertical_layout_widget('scrape', platform_row, scrape_module_row, user_name_row,
                                                     password_row)
        self.main_layout.addWidget(widget)

    def _create_operation_type_widget(self):
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        scrape = self._create_button('scrape_op', 'Scrape')
        gamelist = self._create_button('gamelist_op', 'Gamelist.xml')
        layout.addWidget(scrape)
        layout.addWidget(gamelist)
        widget.setLayout(layout)
        self.layout_widgets['op_type'] = widget
        self.main_layout.addWidget(widget)

    def _create_main_buttons_widget(self):
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        run = self._create_button('run', 'Run')
        exit_ = self._create_button('exit', 'Exit')
        layout.addWidget(run)
        layout.addWidget(exit_)
        widget.setLayout(layout)
        self.layout_widgets['main_buttons'] = widget
        self.main_layout.addWidget(widget)

    def _create_vertical_layout_widget(self, name, *args):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for arg in args:
            layout.addLayout(arg)
        widget = QWidget()
        widget.setLayout(layout)
        self.layout_widgets[name] = widget
        return widget

    def _create_title_label(self, label_text):
        title_label = QLabel()
        title_label.setFont(self.font)
        title_label.setFixedWidth(self.title_label_width_px)
        title_label.setText(label_text)
        return title_label

    def _create_text_input(self, name, label_text):
        layout = QHBoxLayout()
        title_label = self._create_title_label(label_text)
        text_input = QLineEdit()
        layout.addWidget(title_label)
        layout.addWidget(text_input)
        self.fields[name] = text_input
        return layout

    def _create_combo_select(self, name, label_text, items):
        layout = QHBoxLayout()
        title_label = self._create_title_label(label_text)
        option_select = QComboBox()
        option_select.addItems(items)
        layout.addWidget(title_label)
        layout.addWidget(option_select)
        self.combos[name] = option_select
        return layout

    def _create_fs_select(self, name, button_text, init_text):
        layout = QHBoxLayout()
        path_label = self._create_path_field(name, init_text)
        button = self._create_button(name, button_text)
        layout.addWidget(button)
        layout.addWidget(path_label)
        return layout

    def _create_radio_button(self, name, text, checked=False):
        radio = QRadioButton(text)
        radio.setChecked(checked)
        self.radios[name] = radio
        return radio

    def _create_button(self, name, text):
        button = QPushButton(text)
        button.setFont(self.font)
        button.setFixedHeight(30)
        self.buttons[name] = button
        return button

    def _create_path_field(self, name, init_text):
        label = QLabel()
        label.setFixedWidth(self.path_label_width_px)
        label.setFixedHeight(self.path_label_height_px)
        label.setFont(self.font)
        label.setStyleSheet("border: 1px solid black;")
        label.setText(init_text)
        self.fields[name] = label
        return label

    def get_elided_text(self, text):
        return self.font_metrics.elidedText(text, 0, self.path_label_width_px - 10, 0)


class RunOpts:

    def __init__(self):
        self.gamelist = None
        self.input_dir = None
        self.output_dir = None
        self.core_path = None
        self.bios_dir = None
        self.platform = None
        self.scrape_source = None
        self.user_name = None
        self.password = None
        self.user_creds = None


class Controller:

    def __init__(self, view, opts):
        self._view = view
        self._opts = opts
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
            for name in ('input_dir', 'output_dir', 'other_dir', 'scrape', 'main_buttons'):
                self._view.layout_widgets[name].show()
            self._view.run_type = 'scrape'
        else:
            for name in ('output_dir', 'other_dir', 'gamelist', 'main_buttons'):
                self._view.layout_widgets[name].show()
            self._view.run_type = 'gamelist'

    def _choose_dir(self, name):
        dir_name = QFileDialog.getExistingDirectory(self._view, 'Select Directory', '.')
        if dir_name:
            dir_name = QDir.toNativeSeparators(dir_name)
        if os.path.isdir(dir_name):
            self._view.fields[name].setText(self._view.get_elided_text(dir_name))
            setattr(self._opts, name, dir_name)

    def _choose_file(self, name):
        file_name = QFileDialog.getOpenFileName(self._view, 'Select File', '.')[0]
        if file_name:
            file_name = QDir.toNativeSeparators(file_name)
        if os.path.isfile(file_name):
            self._view.fields[name].setText(self._view.get_elided_text(file_name))
            setattr(self._opts, name, file_name)

    def _combo_select(self, name):
        setattr(self._opts, name, self._view.combos[name].currentText())

    def _text_field_edit(self, name):
        setattr(self._opts, name, self._view.fields[name].text())

    def _run(self):
        self._opts.user_creds = '{0}:{1}'.format(self._opts.user_name, self._opts.password)
        aluautobuild.main(self._opts)


if __name__ == '__main__':
    app_root = configs.APP_ROOT
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(app_root, 'common', 'title.png')))
    main_window = Window()
    run_opts = RunOpts()
    controller = Controller(main_window, run_opts)
    main_window.show()
    sys.exit(app.exec_())
