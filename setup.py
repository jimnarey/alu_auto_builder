import sys
from cx_Freeze import setup, Executable

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(
        name = 'aluautobuilder',
        version = "0.1",
        description = "Automatically builds UCE images",
        # options = {"build_exe" : {"includes" : includes }},
        executables = [Executable('aluautobuild_gui.py', base = base)]
        )
