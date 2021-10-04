#!/usr/bin/env python3

# Options

INPUT_PATH = 'Path to the input file. The type of file required varies according to the operation being performed'

INPUT_DIR = 'Path to the input directory'

OUTPUT_PATH = 'The output path for operations which create a file'

OUTPUT_DIR = 'The output path for operations which create or populate a directory'

CORE_PATH = "The path to a libretro core (a '.so' file) for the system being emulated"

BIOS_DIR = "A directory containing additional files (usually a bios) to be included with the rom(s)"

PLATFORM = "The name of the platform being emulated to enable scraping. Run 'Skyscraper --help' to see available platforms."

SCRAPE_MODULE = "The source for scraping metadata. Run 'Skyscraper --help' to see available scraping modules."

USER_NAME = 'Passed to Skyscaper. User account name for scraping module.'

PASSWORD = 'Passed to Skyscaper. Password for scraping module.'

PART_PATH = "The path to a save partition to replace the UCE's existing save partition"

MOUNT_METHOD = 'Set this option to use the mount method for opening an existing save parition. Linux only'

FILE_MANAGER = 'Optionally specify a file manager to open the save parition. Linux only'

BACKUP_UCE = 'Set this option to create a backup of the UCE file before editing'

# Operations

SCRAPE_TO_UCES = 'Provide a directory of roms, scrape cover images and metadata and generate UCEs in one step'

SCRAPE_TO_RECIPES = "Provide a directory of roms, scrape cover images and metadata and build directories in 'recipe' format"

SCRAPE_TO_GAMELIST = 'Provide a directory of roms, scrape cover images and metadata and generate an EmulationStation format gamelist.xml. A thin wrapper for Skyscraper'

GAMELIST_TO_UCES = 'Build UCEs from an existing gamelist.xml in EmulationStation format'

GAMELIST_TO_RECIPES = "Build directories in 'recipe' format from an existing EmulationStation gamelist.xml"

RECIPES_TO_UCES = "Build UCEs from a directory containing multiple 'recipe' sub-directories"

RECIPE_TO_UCE = "Build a single UCE from a single 'recipe' directory"

EDIT_SAVE_PARTITION = 'Edit the save partition of an existing UCE file'

EXTRACT_SAVE_PARTITION = 'Extract the save parition from an existing UCE file'

REPLACE_SAVE_PARTITION = 'Replace the save parition of an existing UCE file with a specified save.img file'
