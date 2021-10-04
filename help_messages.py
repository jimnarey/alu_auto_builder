

# Scraping/Gamelist generation opts

INPUT_DIR = "Location of input roms."

GAME_LIST_TARGET_DIR = "Directory to save the generated gamelist.xml"

# Scraping only

PLATFORM = "Emulated platform. Passed to Skyscaper. Run 'Skyscraper --help' to see available platforms."

SCRAPE_MODULE = "Scraping source. Passed to Skyscaper. Run 'Skyscraper --help' to see available scraping modules."

USER_NAME = "Passed to Skyscaper. User account name for scraping module."

PASSWORD = "Passed to Skyscaper. Password for scraping module."

# Gamelist generation only

KEEP_BRACKETS = "Passed to Skyscaper. Can be 'true' or 'false', default 'false'. If set to 'true' then rom notes in () or [] such as (U) or [!] will be kept in the rom's title when generating the UCE."

ALL_ROMS = "Passed to Skyscaper. Can be 'true' or 'false', default 'true' in which case roms without any scraped data will be included in the gamelist.xml and made into UCEs. If 'false' then only roms for which at least some data is scraped will be made into UCEs"

# Build only

OUTPUT_DIR = "Output directory."

CORE = "Libretro core compatible with input roms"

BIOS_DIR = "Path to directory containing common files (e.g. bios files) to be included with EVERY game"

# Combined only

GAME_LIST = "Specify existing gamelist.xml in EmulationStation format."
