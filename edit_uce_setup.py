import sys
from cx_Freeze import setup, Executable

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(
        name = 'uce_save_editor',
        version = "0.1",
        description = "Edit the save partition of a UCE file",
        # options = {"build_exe" : {"includes" : includes }},
        executables = [Executable('edit_uce.py', base = base)]
        )
