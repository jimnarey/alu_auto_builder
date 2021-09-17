#!/usr/bin/env python3

import os
import common_utils
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")

source_dir = common_utils.get_app_root()
logging.info('Source dir: {0}'.format(source_dir))
build_dir = os.path.join(source_dir, 'build')
logging.info('Build dir: {0}'.format(build_dir))
build_dirs = [os.path.join(build_dir, dir_) for dir_ in os.listdir(build_dir) if os.path.isdir(os.path.join(build_dir, dir_))]

source_bash_scripts = os.path.join(source_dir, 'bash_scripts')
source_common = os.path.join(source_dir, 'common')
source_windows = os.path.join(source_dir, 'windows')
source_linux_launch_sh = os.path.join(source_dir, 'linux_launch_script', 'aluautobuild_gui.sh')

for dir_ in build_dirs:
    logging.info('Processing: {0}'.format(dir_))
    common_utils.copytree(source_common, os.path.join(dir_, 'common'))
    if 'exe.win' in dir_:
        common_utils.copytree(source_windows, os.path.join(dir_, 'windows'))
    elif 'exe.linux' in dir_:
        common_utils.copytree(source_bash_scripts, os.path.join(dir_, 'bash_scripts'))
        common_utils.copyfile(source_linux_launch_sh, dir_)
