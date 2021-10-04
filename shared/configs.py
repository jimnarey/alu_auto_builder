import os

CONFIG = [
    '[main]\n',
    'videos="false"\n',
    'unattend="true"\n',
    'verbosity="1"\n'
]

ARTWORK = [
    '<?xml version="1.0" encoding="UTF-8"?>\n',
    '<artwork>\n',
    '\t<output type="cover" resource="cover">\n'
    '\t</output>\n'
    '</artwork>\n'
]

CARTRIDGE_XML = [
    '<?xml version="1.0" encoding="UTF-8"?>\n',
    '<byog_cartridge version="1.0">\n',
    '\t<title>GAME_TITLE</title>\n',
    '\t<desc>GAME_DESCRIPTION</desc>\n',
    '\t<boxart file="boxart\\boxart.png" ext="png">\n',
    '</byog_cartridge>\n',
]

EXEC_SH = [
    '#!/bin/sh\n',
    'set -x\n',
    '/emulator/retroplayer ./emu/CORE_FILE_NAME "./roms/GAME_FILE_NAME"\n'
]

SCRAPE_FLAGS = ['onlymissing', 'nosubdirs', 'noscreenshots', 'nomarquees']

GAME_LIST_FLAGS = ['nobrackets', 'skipped']

PLATFORMS = ['', '3do', '3ds', 'amiga', 'amigacd32', 'amstradcpc', 'apple2', 'arcade', 'arcadia', 'astrocde',
                 'atari800', 'atari2600', 'atari5200', 'atari7800', 'atarijaguar', 'atarilynx', 'atarist', 'c16', 'c64',
                 'c128', 'coco', 'coleco', 'daphne', 'dragon32', 'dreamcast', 'fba', 'fds', 'gameandwatch', 'gamegear',
                 'gb', 'gba', 'gbc', 'genesis', 'intellivision', 'mame-advmame', 'mame-libretro', 'mame-mame4all',
                 'mastersystem', 'megacd', 'megadrive', 'msx', 'n64', 'nds', 'neogeo', 'neogeocd', 'nes', 'ngp', 'ngpc',
                 'oric', 'pc', 'pc88', 'pc98', 'pcfx', 'pcengine', 'pokemini', 'psp', 'psx', 'saturn',
                 'scummvm', 'sega32x', 'segacd', 'sg-1000', 'snes', 'ti99', 'trs-80', 'vectrex', 'vic20',
                 'videopac', 'virtualboy', 'wonderswan', 'wonderswancolor', 'x68000', 'x1', 'zmachine',
                 'zx81', 'zxspectrum']


SCRAPING_MODULES = ['', 'screenscraper', 'arcadedb', 'igdb', 'mobygames', 'openretro', 'thegamesdb',
                    'worldofspectrum']

