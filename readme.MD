# Purpose

The AtGames Arcade Legends Ultimate cabinet allows the addition of user-owned game roms to the cabinet. There are two chief difficulties with this:

- AtGames try to push users towards their new 'AddonX' tool which is good for batch-adding roms and allows the use of a custom-created version of CoinOps. Don't ask me how to use this. I have no idea, because...
- You can't use any roms installed via this method without being signed into an AtGames account. The process is cumbersome and unreliable. There's a lot of pressure on AtGames to opt for a more proportionate approach and hopefully this will win through. 
- The other method of adding games (simply 'Addon') doesn't allow for easy batch-creation of roms, at least using the AtGames tools.

This tool allows batch creation of rom files to add to the system with the minimum user input. For now, this means if you want to - for example - add 10 MAME roms to your cabinet you will need:
- A USB stick formatted to eXfat or Fat32
- An installation of [Skyscraper](https://github.com/muldjord/skyscraper) (just follow the instructions on that page)
- The 10 roms
- The MAME libreto core

All the fiddly bits to do with scraping artwork and metadata, creating an xml file and launch script etc are handled. In due course I'd like to make this a bit more user-friendly.

For now this only works on Linux and is designed with Debian derivatives in mind. It currently uses copies of two files from the saUCE factory repo (link below) but ideally I'll submodule this or similar to keep track of any improvements there.

# Sources and Inspiration

- The [ultimate_addon repo](https://github.com/FalkensMaze1983/ultimate_addon) which has the Windows tool for creating addon roms and a Linux script for doing the same.
- The [saUCE factory repo](https://github.com/wn2000/sauce_factory) which has an updated version of addon script for Linux and does the heavy lifting for this tool (this tool basically batch-runs the script and puts a few ease-of-use features around it).
