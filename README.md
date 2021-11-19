# UCE Tool

An automatic UCE builder for the Arcade Legends Ultimate arcade cabinet

## Important!

- Some of the operations performed by this tool require administrator privileges on Windows. Look in the help sections
  of the GUI for more info.
- When running the GUI tool in Linux, use the included sh file if running from the Desktop (i.e not in a console window)
  to get the logging output.

## Contents

- [What's New!](#what-s-new-)
- [What it is](#what-it-is)
- [Status and Safety](#status-and-safety)
- [Input files](#input-files)
    * [What on Earth is a 'recipe'](#what-on-earth-is-a--recipe-)
- [How it works](#how-it-works)
- [Requirements and Dependencies](#requirements-and-dependencies)
    * [Windows](#windows)
        + [GUI](#gui)
        + [Command Line](#command-line)
    * [Linux](#linux)
- [Skyscraper](#skyscraper)
- [Installation](#installation)
- [Usage](#usage)
    * [General](#general)
    * [GUI](#gui-1)
    * [Command Line](#command-line-1)
    * [When things go wrong](#when-things-go-wrong)
- [Building](#building)
- [To do](#to-do)
- [Credits](#credits)
- [Licence](#licence)

## What's New!

New in Beta 3:

- The tool scrapes bezels and adds them to UCEs/Recipes.
- Exporting of CoinOpsX assets. Videos can be scraped for the first time in order to support this
- Exporting of marquees resized for the BitPixel.
- Gamelists can be summarised so it's clear what data/assets were found for each recipe/UCE.
- The logging output is now included in the GUI rather than a separate console window.
- Help is included in each GUI dialog rather than a separate one.
- The tool is more tolerant of different ways of including a custom save partition in recipes.
- Various bug fixes.

Beta 2 introduced the following:

- UCE Building: in addition to building UCEs from roms or a gamelist, the tool can now: build a gamelist from roms,
  build recipes from a gamelist, build recipes from roms, build a single recipe into a UCE and build multiple UCEs from
  a directtory of recipes.
- UCE Editing: you can extract the save partition from a UCE, replace the save partition in a UCE with a new one or edit
  a UCE save partition in your OS's file manager.
- Custom save paritions: when building UCEs from recipes (multiple or single) you can include a custom save partition by
  populating the 'save' subdir of the recipe. Include a save.zip, a save.img or simply the files you want to make up the
  partition (with the right internal folder structure).
- GUI: it has had a complete overhaul to accommodate managing a broader set of operations/functions.
- Command line: simplified with a single entry-point (`ucetool`) which has several subcommands, exactly mirroring the
  functionality of the GUI tool.
- Help: the command line help is a little clearer. The GUI includes comprehensive help for each operation.
- Structure: much of the work since the last beta involved turning what was a prototype into a more extensible app.
  Adding new functionality is now easier and quicker.

## What it is

This tool allows you to batch-create UCE files for use on the ATGames Arcade Legends Ultimate arcade cabinet and
probably other ATGames systems based on the same hardware/software. It aims to improve on the ATGames Addon Tool by
allowing creation of an arbitrary number of UCEs in a single pass, doing all of the hard work of creating directories (
roms, emu, core etc) and automatically scraping for metadata/cover images.

The tool has a GUI and can be used on the command line. It works on Windows (some functions require administrator, see
below)
and Linux. It is written in Python.

Note that this creates the same kind of UCEs as the 'Addon' tool, not the 'AddonX' tool. One advantage of this is there
is no need to be logged in to use them.

## Status and Safety

The tool has been tested using a number of cores on Windows 10, Windows 11 and several Linux distros. Nonetheless, it is
offered without warranty of any kind and is used entirely at the user's own risk.

It is designed to write into only three places, temporary directories created by Python's built-in tempfile library (so
in '/tmp' on Linux),an output directory provided by the user and a '.bezels' folder in the user's homedir when scraping
bezels. However, it will write to whatever output directory you give , so some care should be taken when providing
this. 

## Input files

Game files must be provided by the user, and the user is responsible for the legality of any files used. There is no
shortage of legally-available roms for several old systems, for example those provided by
the [MAME Project](https://www.mamedev.org/roms/).

The only other files you need are libretro emulator cores (.so files), compiled for the RK3328 SoC used in the Arcade
Legends Ultimate.

### What on Earth is a 'recipe'

See [this](https://github.com/FalkensMaze1983/ultimate_addon). Not only does this repo have a good explanation of the
recipe format, but the logic in this tool is ported from the bash scripts there.

## How it works

You can provide the tool with roms, a gamelist (which points to roms) or recipe dirs, and it will create UCEs from them.
Alternatively, you can create the intermediary steps such as a gamelist.xml or recipe dirs if you need to tweak the
final UCEs in some way.

UCE files are then added to a USB drive (formatted as FAT32 or exFat) as normal.

To create 10 MAME2003Plus UCEs - with covers, titles and descriptions - you really do just need the 10 roms (zip files)
in a single directory and a core.

The tool has several other functions described in the help sections within the tool itself.

## Requirements and Dependencies

The tool uses [Skyscraper](https://github.com/muldjord/skyscraper) for scraping and gamelist generation. However, this
it is not needed if the user provides their own gamelist.xml and cover images (specified in the gamelist, as normal).

### Windows

#### GUI

The Windows release includes Skyscraper as the author only provides an (unsupported) Windows build in binary format so
this doesn't conflict with his preferred way of distribution. The current bundled version is 3.6.12.

If you already have Skyscraper installed **and** it is in your PATH then this tool will use that copy instead of the
bundled one. It's not impossible that running two versions of Skyscraper - each using the same cache - could cause
problems but since Skyscraper can be updated without re-building cached metadata this is probably unlikely. If you have
Skyscraper installed on Windows and are concerned then the simplest thing is to make sure it (the directory containing
it) is in your
PATH. [This tutorial](https://www.c-sharpcorner.com/article/add-a-directory-to-path-environment-variable-in-windows-10/)
takes you through the simple steps to take.

#### Command Line

The command line version now includes a python interpreter (thank
you [cx_freeze](https://cx-freeze.readthedocs.io/en/latest/))
so on Windows has no external dependencies.

### Linux

You will need QT installed. On Ubuntu < 20:

`sudo apt install qt5-default`

On Ubuntu 20:

`apt install build-essential qtbase5-dev qt5-qmake qtbase5-dev-tools`

Please follow the instructions on the Skyscraper page for installing it on Linux. It's quick and straightforward but
since the author doesn't provide a binary release for Linux, neither have I.

## Skyscraper

It's a very powerful tool, run from the command line. I highly recommend giving it a go. This tool calls a small subset
of its functionality.

The [Skyscraper docs](https://github.com/muldjord/skyscraper/tree/master/docs) are comprehensive. If you're not
intending to use it more widely then the most relevant part is
the [readme on scraping modules](https://github.com/muldjord/skyscraper/blob/master/docs/SCRAPINGMODULES.md). You have
to select one of these when using this tool to scrape. I recommend screenscraper, though it is slow without an account.
I have found the fastest module which doesn't need an account to be arcadedb, though as the name suggests it covers a
limited number of systems. For MAME it's great.

## Installation

Get a package containing the GUI and command line versions for Windows or Linux from the releases page
(right-hand side of this GitHub page) and unzip it somewhere on your system.

It's a good idea to symlink the command line version to somewhere in your path, so you can run it from within source
directories for whatever you are doing. As much as anything, this usually involves passing fewer arguments on the
command line.

## Usage

### General

*Taking care with your input directory*

Make sure that when you specify an input directory (the directory containing your roms) it only contains roms - not
other file types - and only roms for a single system. If you want to build UCEs for two systems, e.g. a MAME set and a
Final Burn Alpha set, you need to run the tool twice.

The tool will pack any files it finds into UCEs, irrespective of whether metatdata/covers are found. Screenscraper in
particular is very comprehensive and it's rare that it won't find data for an actual rom file but to deal with edge
cases, everything is built. If you put a Microsft Excel file in with your roms, it's going in UCE.

Sub-directories in the input directory are ignored, as are their contents.

*Providing a core file*

This is mandatory in the GUI and all the command line tools for building recipes or UCEs. No sense checking is done at
present, so the tool will build the UCEs with whatever you point it to. At present the tool doesn't even check the
extension is right.

*The output directory/files are overwritten on each run*

Care needs to be taken here, especially if you don't specify an output directory (in which case a directory is created
automatically in the input directory).


### Command Line

The command line includes useful information on the options but it's less comprehensive than that provided in the GUI.
You may want a look at the GUI to get more info. The command line is there
for users already reasonably au fait with the UCE format etc

There is one entry-point (changed from the first beta): `ucetool`.

Run `ucetool --help` to get a list of subcommands.

Run `ucetool subcommand --help` to get information on the options for each subcommand. The tool will complain if it
doesn't get something it needs, though there's a bit of work to do on usability here.

### When things go wrong

If running the tool results in an exception (error) which I haven't caught, it will quit. So you can see the logging
output should this happen, re-run the GUI tool from the command line in an existing terminal window.

If the tool completes a build run but there is something wrong with your UCEs, check the logging output. If there are
any entries marked ERROR then this *usually* means something went sufficiently wrong to result in bad UCEs. The tool
currently keeps on going after encountering most errors, though this will be adapted.

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

A huge amount has been done since the last beta but the following are outstanding:

- The logging needs a little rationalisation, including removing some errant special characters
- Better handling of errors
- Catching when Skyscraper can't find metadata and informing the user before continuing
- It can be made to run a little faster, especially when building UCEs
- A MacOS build, which I now expect to have exactly the same functionality as the Windows/Linux versions.
- General GUI refinements
- Improve the help and documentation

## Credits

- The [ultimate_addon repo](https://github.com/FalkensMaze1983/ultimate_addon) which has the Windows tool for creating
  addon roms and a Linux script for doing the same. All of the logic used to build this tool was ported from this repo
  and derived tools.
- dudemo from the Legends Ultimate Reddit for a huge amount of help in understanding the Legends Ultimate internals,
  UCEs and testing.
- One or two others too modest to be named!

## Licence

Because this tool uses the GP3 licensed PyQT library it is also released under GPL3. If you breach this I may send
squirrels after you but the people behind (Py)QT probably have lawyers. I don't know anyone else who uses squirrels.