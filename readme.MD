## Arcade Legends Ultimate Auto UCE Builder

### Purpose

The AtGames Arcade Legends Ultimate cabinet allows the addition of user-owned game roms to the cabinet. There are two
chief difficulties with this:

- AtGames try to push users towards their new 'AddonX' tool which is good for batch-adding roms and allows the use of a
  custom-created version of CoinOps. Don't ask me how to use this. I have no idea, because...
- You can't use any roms installed via this method without being signed into an AtGames account. The process is not
  solid. There's a lot of pressure on AtGames to opt for a more proportionate approach and hopefully this will win
  through.
- The other method of adding games (simply 'Addon') doesn't allow for easy batch-creation of roms, at least using the
  AtGames tools.

This tool allows batch creation of rom files to add to the system with the minimum user input/work. For now, this means
if you want to - for example - add 10 Final Burn Alpha roms to your cabinet you will need:

- A Linux system. Making this platform-independent is a high priority.
- Python 3. There are no Python dependencies, only packages from the standard library are used. It has been tested on
  Python 3.8 but should work, within reason, with earlier versions of Python 3.
- A USB stick formatted to eXfat or Fat32
- An installation of [Skyscraper](https://github.com/muldjord/skyscraper) (just follow the instructions on that page)
- The 10 roms
- The Final Burn Alpha libreto core

All the fiddly bits to do with crating directories, scraping artwork and metadata, creating an xml file and launch
script etc are handled. In due course I'd like to make this a bit more user-friendly.

For now this only works on Linux and is designed with Debian derivatives in mind. It currently uses copies of several
files from the saUCE factory repo (link below) but ideally I'll submodule this or similar to keep track of any
improvements there.

### Status

This tool is at a **very** early stage of development and isn't really ready for public consumption. However, it does
work using the fbalpha_libretro.so core and Gunforce and Gunforce 2 from the 2.97.23 set. In early testing, it isn't
working with the Neo Geo games in that set. This is either a (lack of) bios issue or the wrong version of the core but
the process is sound.

### Usage

I suggest putting the script in your path so you can call it from within the directory containing your roms. You may
need to make the script executable by running

`chmod +x aluautobuild.py`

Create a directory and put your roms in it.

Put the right libretro core for your roms somewhere else.

For Final Burn Alpha, within the directory containing the roms, run:

`aluautobuilder.py -p fba -c path_to_libretro_core`

The platform argument is passed to Skyscraper to tell it what system it needs to be searching metadata for. To see a
list of supported platforms, run:

`Skyscraper --help`

### To do

In short, loads. See the top of the aluautobuilder.py file for a current, non-exhaustive list.

### Sources and Inspiration

- The [ultimate_addon repo](https://github.com/FalkensMaze1983/ultimate_addon) which has the Windows tool for creating
  addon roms and a Linux script for doing the same.
- The [saUCE factory repo](https://github.com/wn2000/sauce_factory) which has an updated version of addon script for
  Linux and builds the UCE files.

### Licence

Because this tool uses the GP3 licensed PyQT library it is also released under GPL3.