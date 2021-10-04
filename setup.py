import sys
from cx_Freeze import setup, Executable

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(
        name='aluautobuilder',
        version="0.2",
        description="Automatically builds UCE images",
        executables=[Executable('ucetool_gui.py', base=base),
                     Executable('ucetool.py', base=base)]
        )
