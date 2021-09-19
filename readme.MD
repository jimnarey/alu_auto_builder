# Arcade Legends Ultimate Auto UCE Builder

- [Arcade Legends Ultimate Auto UCE Builder](#arcade-legends-ultimate-auto-uce-builder)
  * [What it is](#what-it-is)
  * [Status and Safety](#status-and-safety)
  * [Input files](#input-files)
  * [How it works](#how-it-works)
  * [Requirements and Dependencies](#requirements-and-dependencies)
    + [Windows](#windows)
      - [GUI](#gui)
      - [Command Line](#command-line)
    + [Linux](#linux)
  * [Skyscraper](#skyscraper)
  * [Installation](#installation)
    + [Command line version](#command-line-version)
    + [GUI Version](#gui-version)
  * [Usage](#usage)
    + [General](#general)
    + [GUI](#gui-1)
    + [Command Line](#command-line-1)
      - [Linux](#linux-1)
      - [Windows](#windows-1)
      - [Examples](#examples)
      - [Command line options](#command-line-options)
    + [When things go wrong](#when-things-go-wrong)
    + [To do](#to-do)
    + [Credits](#credits)
    + [Licence](#licence)

  
## What it is

This tool allows you to batch-create UCE files for use on the ATGames Arcade Legends Ultimate arcade cabinet and
probably other ATGames systems based on the same hardware/software. It aims to improve on the ATGames Addon Tool by
allowing creation of an arbitrary number of UCEs in a single pass, doing all of the hard work of creating directories (
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

Whether using the GUI version the user does not need to provide anything else and in the case of Windows doesn't have to
provide anything at all.

### Windows

#### GUI

The Windows GUI release includes Skyscraper as the author only provides an (unsupported) Windows build in binary format
so this doesn't conflict with his preferred way of distribution. The current bundled version is 3.6.12.

If you already have Skyscraper installed **and** it is in your PATH then this tool will use that copy instead of the
bundled one. It's not impossible that running two versions of Skyscraper - each using the same cache - could cause
problems but since Skyscraper can be updated without re-building cached metadata this is probably unlikely. If you have
Skyscraper installed on Windows and are concerned then the simplest thing is to make sure it (the directory containing
it) is in your
PATH. [This tutorial](https://www.c-sharpcorner.com/article/add-a-directory-to-path-environment-variable-in-windows-10/)
takes you through the simple steps to take.

#### Command Line

You need to have Python 3 installed (this is packaged into the .exe with the GUI release but that is no help with the
command line version). This should work with the version of Python 3 from the Microsoft Store but that can cause other
problems (including for me when packaging the GUI version) so I recommend installing
from [python.org](https://www.python.org/downloads/windows/).

This has been tested on Python 3.8 and 3.9 but ought to work on lower versions of Python 3, up to a point. It will not
work with Python 2.

To use the command line version in Windows you must separately install Skyscraper as the binaries are not included in
this repo. Get it from the main Skyscraper page and either put it somewhere in your path or extract it into the '
windows' directory within the repo in a new directory called 'skyscraper'. The readme in the 'windows' directory of this
repo shows what the dir structure should look like.

### Linux

Please follow the instructions on the Skyscraper page for installing it on Linux. It's quick and straightforward but
since the author doesn't provide a binary release for Linux, neither have I.

Most, if not all, Linux distros include Python 3 so nothing else should be needed for the command line version. It isn't
needed for the GUI version as it's included in the executable.

## Skyscraper

It's a very powerful tool, run from the command line. I highly recommend giving it a go. This tool calls a small subset
of its functionality.

The [Skyscraper docs](https://github.com/muldjord/skyscraper/tree/master/docs) are comprehensive. If you're not
intending to use it more widely then the most relevant part is
the [readme on scraping modules](https://github.com/muldjord/skyscraper/blob/master/docs/SCRAPINGMODULES.md). You have
to select one of these when using this tool to scrape. I recommend the default, screenscraper, though it is slow without
an account. I have found the fastest module which doesn't need an account to be arcadedb, though as the name suggests it
covers a limited number of systems. For MAME it's great.

## Installation

### Command line version

Either clone this repo (you must have git installed) or download it as a zip file and extract somewhere on your system.
The command line tools (aluautobuild.py, create_gamelist.py, build_uces.py, build_uce_tool.py) only use the Python
standard library so do not need further Python packages installed on any system.

I suggest creating symlinks to any of the scripts you intend to use somewhere in your path. That way you can call them
without providing the full path to the script. Having to do this can be particularly annoying on Windows with its less
than ideal tab-completion.

### GUI Version

Get it from the releases page (right-hand side of this GitHub page) and unzip it somewhere on your system.

## Usage

### General

*Taking care with your input directory*

Make sure that when you specify an input directory (the directory containing your roms) it only contains roms - not
other file types - and only roms for a single system. If you want to build UCEs for two systems, e.g. a MAME set and a
Final Burn Alpha set, you need to run the tool twice.

The tool will pack any files it finds into UCEs, irrespective of whether metatdata/covers are found. Screenscraper in
particular is very comprehensive and it's rare that it won't find data for an actual rom file but to deal with edge
cases, everything is built. If you put a Microsft Excel file in with your roms it's going in UCE.

Sub-directories in the input directory are ignored, as are their contents.

*Providing a core file*

This is mandatory in the GUI and all the command line tools except create_gamelist.py. No sense checking is done at
present, so the tool will build the UCEs with whatever you point it to. At present the tool doesn't even check the
extension is right.

*The output directory/files are overwritten on each run*

Care needs to be taken here, especially if you don't specify an output directory (in which case a directory called '
output' is created in the input directory).

### GUI

On Windows, right-click the .exe file and choose 'Run as administrator'.

On Linux, run the aluautobuild_gui.sh script rather than the binary and select 'Execute in Terminal' (or just run it
from within a terminal window) to make sure you get the logging output.

You must supply the inputs specified in the GUI. The minimum inputs vary according to whether you scrape
metadata/covers, or provide a gamelist.xml.

When scraping metadata/covers against a directory or roms the minimum inputs are an input directory (where your roms
are) and a core file.

When building from a gamelist.xml the minimum inputs are a path to the gamelist and a core file.

If you don't provide an output directory, UCEs will be created in a new 'output' directory in the directory containing
your roms (the 'input directory'). This will be overwritten on each run, so move it/its contents between operations.

'Platform' refers to the system being emulated. The scraper needs to know this to get the right metadata. For MAME2003P
you would use 'mame-libretro'.

'Scraping module' refers to the source used to scrape metadata/cover images. The default is screenscraper but expect
this to be slow without an account. See the Skyscraper docs (linked above) for more information.

The GUI currently allows you to run the end-to-end process (from a gamelist *or* a roms directory) but not parts of it,
as the command line tools do. This means that the build-stages in between are deleted after each run. A more granular
set of options will be added in the near future.

*Notes on the GUI*

Bear the following in mind. These things will be fixed/improved wherever possible in future releases:

- The tool is at an early stage and it currently uses a console window (opened by the tool, if needed) for log output.
- There is no option to clear inputs. You'll have to restart the tool to clear them. You can, however, change them to
something else.
- Once you have chosen to run in scraping mode you can't switch to gamelist mode or vice versa. Restart the tool.


### Command Line

You can call the following scripts from the command line. In each case run with `--help` to get a description of the
options which can/must be used. There are some general notes on optiosn below.

- *aluautobuild.py*

This wraps the other scripts and mirrors the functionality of the GUI app.

- *create_gamelist.py*

Calls Skyscraper on a set of roms and creates a gamelist.xml which is then used by build_uces.py. You can get exactly
the same result with two Skyscraper commands. This script has the advantage of automatically using the right settings
for building cabinet UCEs, e.g. not downloading any more than is needed, but it's a thin wrapper. It's main purpose is
to support the end-to-end process and a command line interface is provided for completeness more than anything else.

- *build_uces.py*

Point this to a gamelist.xml and it will build a set of UCEs for each of the roms specified in the gamelist. It creates
a temporary directory and builds the correct directory structure for each game, copies the roms/bios/core files over,
sets up the exec.sh and cartridge.xml files needed to make the game run and then builds it all into a UCE.

- *build_uce_tool.py*

This creates an individual UCE from a directory set up in the 'recipe' format (
see [here](https://github.com/FalkensMaze1983/ultimate_addon)).

#### Linux

Assuming you have Python 3 installed you can just run the scripts without invoking `python` (or `python3` depending on
your environment).

#### Windows

You have to execute the scripts using `python`, e.g. -

```
python aluautobuild.py -p mame-libretro -c /path/to/mamelibretrocore.so
```

You need to run the scripts in an administrator shell.

#### Examples

The following example commands assume you are using Linux. In the case of Windows add `python` to the start of the
command as above and use back-slashes instead of forward-slashes in the paths.

*To build a set of UCEs from the roms in the current directory, where the core file is in the parent directory:*

```
aluautobuild.py -p mame-libretro -c ../mame2003P_libretro.so
```

*To create a gamelist.xml and scrape media from the roms in the current directory*

```
create_gamelist.py -p mame-libretro -o ../game_list_out
```

This will create a folder in the parent called 'game_list_out', scrape metadata for all the roms in the current
directory and create a gamelist and media folder in 'game_list_out' which can then be used in the next stage. This is
mostly useful for testing or if you want to edit/examine the gamelist before building UCEs.

*To build a set of UCEs from an existing gamelist.xml*

This can be done with aluautobuild.py or build_uces.py. Assuming the gamelist.xml is in the current directory and you
want to build the UCEs into a new directory called 'output' within the current directory, with the core you're using in
the parent:

```
aluautobuild.py -g gamelist.xml -c ../mame2003P_libretro.so
```

...or...

```
build_uces.py -g gamelist.xml -c ../mame2003P_libretro.so
```

*To build a single UCE from within a directory set up in recipe format*

```
build_uce_tool.py
```

With no options, as above, this will create a file called 'output.uce' in the current directory. More than likely you'll
want to specify an output file though, in which case:

```
build_uce_tool.py -o ../circus.UCE
```

#### Command line options

Run any of these scripts with `--help` to get a full description of the available options.

*Setting an input directory*

By default aluautobuild.py, build_uces.py and build_uce_tool.py will look for roms in the current directory. You can
specify a different directory with `-i`.

*Setting an output directory*

By default aluautobuild.py, build_uces.py and build_uce_tool.py will create a new directory called `output` in the
current directory and put UCEs there. You can specify a different directory with `-o`.

You must specify an output directory using '-o' when running create_gamelist.xml by itself (i.e. when it isn't called by
aluautobuild.py or the GUI), otherwise it will create a gamelist.xml and place media in a temporary directory, which it
will then delete. More sensible behaviour on the way!

*Choosing build type/operation with aluautobuild.py*

This is done by specifying a platform to scrape against (`-p`) or a gamelist.xml to build from (`-g`). If you specify
both it will ignore the platform option and build from the gamelist. If you specify neither it will complain.

*Choosing a scraping module*

For aluautobuild.py (when scraping) and create_gamelist.xml you can specify a scraping module. Run `Skyscraper --help`
for a list. By default the screenscraper will be used. Use `-s`.

*Specifying a platform to scrape against*

For aluautobuild.py (when scraping) and create_gamelist.xml you **must** specify a platform to scrape against, e.g. '
mame-libretro' or 'snes'. Run `Skyscraper --help` for a list. Use `-p`.

### When things go wrong

If running the tool results in an exception (error) which I haven't caught, it will quit. So you can see the logging 
output should this happen, re-run the GUI tool from the command line in an existing terminal window.

If the tool completes a build run but there is something wrong with your UCEs, check the logging output. If there are
any entries marked ERROR then this usually means something went sufficiently wrong to result in bad UCEs. The tool
currently keeps on going after encountering most errors which isn't hugely helpful but will continue to be the case
until it is out of beta.

Please raise an issue on GitHub if you get an unhandled exception or problems which it doesn't seem are down to user
input.

## Building

On either Linux or Windows 10 clone the repo.

From within the cloned directory run:

```
pip install -r requirements.txt

python setup.py build_exe

python build_copy.py
```

The first command installs python dependencies which are then built, along with the source code, by the second command.

The third command copies the right files for Windows/Linux into the newly created build directory. Look in the newly
created 'build' directory for your build.


## To do

In short, loads: 
- The GUI needs a some work
- The logging needs a little rationalisation
- Better handling of errors
- Catching when Skyscraper can't find metadata and informing the user before continuing
- It can be made to run a little faster  
- Adding the ability to use custom save images, to allow core customisation. A lot of work has gone into generating
  save images on the fly under Windows (it's straightforward in Linux) to enable this.
- A MacOS build. However, I'm unlikely to ever get custom save images working on MacOS as there is no (free) way to
mount writable ext4 partitions, which is what the save images are.
- The ability to build from pre-made 'recipe' directories, which people who've been building UCEs for a while probably
have stored

## Credits

- The [ultimate_addon repo](https://github.com/FalkensMaze1983/ultimate_addon) which has the Windows tool for creating
  addon roms and a Linux script for doing the same. All of the logic used to build this tool was ported from this repo
  and derived tools.
- dudemo from the Legends Ultimate Reddit for a huge amount of help in understanding the Legends Ultimate internals,
  UCEs and testing.

## Licence

Because this tool uses the GP3 licensed PyQT library it is also released under GPL3. If you breach this I may send
squirrels after you but the people behind (Py)QT probably have lawyers. I don't know anyone else who uses squirrels.