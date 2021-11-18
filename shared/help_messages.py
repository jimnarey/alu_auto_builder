#!/usr/bin/env python3

import os

# Options

INPUT_PATH = 'Path to the input file. The type of file required varies according to the operation being performed.'

INPUT_DIR = 'Path to the input directory.'

OUTPUT_PATH = 'The output path for operations which create a file.'

OUTPUT_DIR = 'The output path for operations which create or populate a directory.'

CORE_PATH = "The path to a libretro core (a '.so' file) for the system being emulated."

BIOS_DIR = "A directory containing additional files (usually a bios) to be included with the rom(s)."

PLATFORM = "The name of the platform being emulated to enable scraping."

SCRAPE_MODULE = "The online source for scraping metadata."

USER_NAME = 'User account name for scraping module. This enables faster scraping with some modules (e.g. screenscraper).'

PASSWORD = 'Password for scraping module.'

REFRESH_ROM_DATA = 'Choose whether to refresh the metadata cache'

EXPORT_BITPIXEL_MARQUEES = 'Choose whether to export marquees, resized to fit the Bitpixel, to a filesystem folder'

EXPORT_COX_ASSETS = 'Choose whether to export assets for use with CoinOpsX'

SCRAPE_VIDEOS = 'Choose whether to scrape videos. Useful only if you choose to export these as part of a build for a frontend (COX)'

PART_PATH = "The path to a save partition to replace the UCE's existing save partition."

MOUNT_METHOD = 'Set this option to use the mount method for opening an existing save parition. Linux only.'

FILE_MANAGER = 'Optionally specify a file manager to open the save parition. Linux only.'

BACKUP_UCE = 'Set this option to create a backup of the UCE file before editing.'

DO_BEZEL_SCRAPE = 'Choose whether to scrape bezels in addition to other game data provided by Skyscraper'

DO_SUMMARISE_GAMELIST = 'Choose whether to sumamrise the gamelist (scraping results) on completion'

MIN_MATCH_SCORE = "The minimum percentage bezel name match to use before reverting to the platform's default bezel"

COMPARE_FILENAME = 'Use a filename instead of game title to scrape bezels'

FILTER_UNSUPPORTED_REGIONS = 'Use the default system bezel for Japanese games which are not supported by the bezel project'

# Operations

SCRAPE_TO_UCES = 'Provide a directory of roms, scrape cover images and metadata and generate UCEs in one step.'

SCRAPE_TO_RECIPES = "Provide a directory of roms, scrape cover images and metadata and build directories in 'recipe' format."

SCRAPE_TO_GAMELIST = 'Provide a directory of roms, scrape cover images and metadata and generate an EmulationStation format gamelist.xml, for later generation of recipes/UCEs'

GAMELIST_TO_UCES = 'Build UCEs from an existing gamelist.xml in EmulationStation format.'

GAMELIST_TO_RECIPES = "Build directories in 'recipe' format from an existing EmulationStation gamelist.xml."

RECIPES_TO_UCES = "Build UCEs from a directory containing multiple 'recipe' sub-directories."

RECIPE_TO_UCE = "Build a single UCE from a single 'recipe' directory."

EDIT_SAVE_PARTITION = 'Edit the save partition of an existing UCE file.'

EXTRACT_SAVE_PARTITION = 'Extract the save partition from an existing UCE file.'

REPLACE_SAVE_PARTITION = 'Replace the save parttion of an existing UCE file with a specified save.img file.'

EXPORT_GAMELIST_ASSETS = 'Export CoinOpsX assets from a specified gamelist.xml'

ADD_BEZELS_TO_GAMELIST = 'Add bezels to a previously created gamelist.xml'

SUMMARISE_GAMELIST = "Create summary files to assess the completeness of a gamelist's data"


