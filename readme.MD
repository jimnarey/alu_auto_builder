# Arcade Legends Ultimate Auto UCE Builder

## What it is

This tool allows you to batch-create UCE files for use on the ATGames Arcade Legends Ultimate arcade cabinet and
probably other ATGames systems based on the same hardware/software. It aims to improve on the ATGames Addon Tool by
allowing creation of an aribtrary number of UCEs in a single pass, doing all of the hard work of creating directories (
roms, emu, core etc) and automatically scraping for metadata/cover images.

The tool has a GUI and can be used on the command line. It works on Windows (must be run as administrator, see below)
and Linux. It is written in Python.

Note that this creates the same kind of UCEs as the 'Addon' tool, not the 'AddonX' tool. One advantage of this is there
is no need to be logged in to use them.

## Status and Safety

This is the first release and it's a beta. It works but it's a touch clunky. The GUI is not going to win any design
awards or, indeed, any awards. For now, the tool opens a console window to display logging output.

The tool has been tested using a number of cores on Windows 10, Windows 11 and Ubuntu by me and my army of beta testers.
Just this evening the army told me he'd also run it successfully on Slackware.

This is - it should go without saying - offered without warranty of any kind and used entirely at the user's own risk.

It is designed to write into only two places, a temp dir created by Python's built-in tempfile library (so in '/tmp' on
Linux) and to an output directory provided by the user. However, it will write to whatever output directory you give it
so some care should be taken when providing this. This is especially the case on Windows where it must be run as an
administrator because otherwise it can't create the internal symlinks needed by the UCE file.

See 'To Do' below for more information.

## Input files

Game files must be provided by the user, and the user is responsible for the legality of any files used. There is no
shortage of legally-available roms for several old systems, for example those provided by
the [MAME Project](https://www.mamedev.org/roms/).

The only other files you need are libretro emulator cores (.so files), compiled for the RK3328 SoC used in the Arcade
Legends Ultimate.

## How it works

In one of two ways:

- By providing the tool with a directory containing an arbitrary number of roms for a single emulator core, e.g.
  MAME2003Plus and pointing it to a core (.so) file. The tool will then scrape metadata and cover images for each rom
  using Skyscraper (see below)
  and build a separate UCE file for each game.
- By pointing the tool to an existing EmulationStation gamelist.xml file - e.g. one used in RetroPie. The tool will then
  use the roms, metadata and cover images specified in the gamelist to create a UCE file for each game.

UCE files are then added to a USB drive (formatted as FAT32 or exFat) as normal.

So to create 10 MAME2003Plus UCEs you really do just need the 10 roms (zip files) in a single directory and a core. No
creating 'recipe' directories for each game as required, for example, by
the [ultimate_addon tool](https://github.com/FalkensMaze1983/ultimate_addon) or clicking through a GUI app for every
single game. Before this sounds like I'm trashing ultimate_addon, please see the
'Credits' section below!

## Requirements and Dependencies

The tool uses [Skyscraper](https://github.com/muldjord/skyscraper) for scraping and gamelist generation. However, this
it is not needed if the user provides their own gamelist.xml and cover images (specified in the gamelist, as normal).

Whether using the command line version or the GUI version the user does not need to provide anything else and in the
case of Windows doesn't have to provide anything at all.

### Windows

#### GUI

The Windows GUI release includes Skyscraper as the author only provides an (unsupported) Windows build in binary format
so this doesn't conflict with his preferred way of distribution. The current bundled version is 3.6.12.

If you already have Skyscraper installed **and** it is in your PATH then this tool will use that. It's not impossible
that running two versions of Skyscraper - each using the same cache - could cause problems but since Skyscraper can be
updated without re-building cached metadata this is probably unlikely. If have Skyscraper installed on Windows and are
concerned then the simplest thing is to make sure it (the directory containing it) is in your
PATH. [This tutorial](https://www.c-sharpcorner.com/article/add-a-directory-to-path-environment-variable-in-windows-10/)
takes you through the simple steps to take.

#### Command Line

You need to have Python 3 installed (this is packaged into the .exe with the GUI release but is no help with the command
line version). This should work with the version of Python 3 from the Microsoft Store but it can cause other problems (
including for me when packaging the GUI version) so I recommend installing
from [python.org](https://www.python.org/downloads/windows/).

This has been tested on Python 3.8 and 3.9 but ought to work on lower versions of Python 3, up to a point. It will not
work with Python 2.

To use the command line version in Windows you must separately install Skyscraper as the binaries are not included in
this repo. Get it from the main Skyscraper page and either put it somewhere in your path or extract it into the '
windows' directory within the repo (see the readme.MD in that directory).

#### Linux

Please follow the instructions on the Skyscraper page for installing Skyscraper on Linux. It's quick and straightforward
but since the author doesn't provide a binary release for Linux, neither have I.

Most, if not all, Linux distros include Python 3 so nothing else should be needed for the command line version.

### Skyscraper

It's a very powerful tool, run from the command line. I highly recommend giving it a go. This tool calls a small subset
of its functionality.

The [Skyscraper docs](https://github.com/muldjord/skyscraper/tree/master/docs) are comprehensive. If you're not
intending to use it more widely then the most relevant part is
the [readme on scraping modules](https://github.com/muldjord/skyscraper/blob/master/docs/SCRAPINGMODULES.md). You have
to select one of these when using this tool to scrape. I highly recommend the default, screenscraper, though it is slow
without an account. I have found the fasted module which doesn't need an account to be arcadedb, though as the name
suggests it covers a limited number of systems. For MAME it's great.

### Installation

#### Command line version

Either clone this repo (you must have git installed) or download it as a zip file and extract somewhere on your system.
The command line tools (aluautobuild.py, create_gamelist.py, build_uces.py, build_uce_tool.py) only use the Python
standard library so do not need further Python packages installed.

I suggest creating symlinks to any of the scripts you intend to use somewhere in your path.

#### GUI Version

Get it from the releases page (right hand side of this Github page) and unzip it somewhere on your system.

### Usage

More to follow...

#### GUI

On Windows, right click the .exe file and choose 'Run as administrator'.

On Linux, run the aluautobuild_gui.sh rather than the binary and select 'Execute in Terminal' (or just run it from 
within a terminal window) to make sure you get the logging output.

You must supply the inputs specified in the GUI. The minimum inputs vary according to whether you scrape metadata/covers,
or provide a gamelist.xml.

If you don't provide an output directory, UCEs will be created in a new 'output' directory in the directory containing your roms
(the 'input directory'). This will be overwritten on each run, so move it between operations.

#### Command Line

...instructions to follow but for now, run the relevant Python script with --help...

Under Windows you need to run the scripts in an administrator shell.

### To do

In short, loads. The GUI needs some work but the immediate priority is allowing the use of custom images for the save
partition so core settings can be customised.

### Credits

- The [ultimate_addon repo](https://github.com/FalkensMaze1983/ultimate_addon) which has the Windows tool for creating
  addon roms and a Linux script for doing the same. All of the logic used to build this tool was ported from this repo
  and derived tools.
- dudemo from the Legends Ultimate Reddit for a huge amount of help in understanding the Legends Ultimate internals, UCEs
  and testing.
  
### Licence

Because this tool uses the GP3 licensed PyQT library it is also released under GPL3. If you breach this I may send squirrels
after you but the people behind (Py)QT probably have lawyers. I don't know anyone else who uses squirrels.