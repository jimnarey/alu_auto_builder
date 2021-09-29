#!/usr/bin/env python3

NO_INPUT_GAMELIST = 'You must specify a gamelist.xml when building from a gamelist'

GAMELIST_NO_OUTPUT_DIR = 'You must specify an output dir when building from a gamelist.xml'

SCRAPE_NO_INPUT_DIR = 'You must specify an input dir when scraping'



SCRAPE_INVALID_MODULE = 'You must provide a valid scraping module (metadata source) when scraping'

NO_CORE_FILE = 'You must specify an emulator core file'

NO_GAMELIST_OR_PLATFORM = 'You must provide either a gamelist.xml to build from or a platform to scrape'

INVALID_OS = 'This tool requires either Linux or Windows'


def invalid_path(path, path_type):
    return '{0} is not a valid {1}'.format(path, path_type)


# Deprecated
# The two checks for this pair were merged, re-draft:
# SCRAPE_NO_PLATFORM = 'You must provide a platform (i.e. emulated system) when scraping'
# SCRAPE_INVALID_PLATFORM = 'You must specify a valid platform (i.e. emulated system) when scraping'
