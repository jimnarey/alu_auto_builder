import os
from pathlib import Path

SKYSCRAPER_CONFIG = [
    '[main]\n',
    'unattend="true"\n',
    'verbosity="1"\n'
]

ARTWORK = [
    '<?xml version="1.0" encoding="UTF-8"?>\n',
    '<artwork>\n',
    '\t<output type="cover" resource="cover">\n'
    '\t</output>\n'
    '\t<output type="screenshot" resource="wheel">\n'
    '\t</output>\n'
    '\t<output type="marquee" resource="marquee">\n'
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

SCRAPE_FLAGS = ['nosubdirs', 'noscreenshots']

GAME_LIST_FLAGS = ['nobrackets', 'skipped', 'symlink', 'videos']

PLATFORMS = {'3do': {'bezel_repo': 'bezelproject-3DO', 'default_bezel': 'retroarch/overlay/Panasonic-3DO.png'},
             'amiga': {'bezel_repo': 'bezelprojectSA-Amiga', 'default_bezel': 'retroarch/overlay/Commodore-Amiga.png'},
             'amigacd32': {'bezel_repo': 'bezelproject-CD32', 'default_bezel': 'retroarch/overlay/Commodore-Amiga-CD32.png'},
             'amstradcpc': {'bezel_repo': 'bezelprojectSA-AmstradCPC', 'default_bezel': 'retroarch/overlay/Amstrad-CPC.png'},
             'arcade': {'bezel_repo': 'bezelproject-MAME', 'default_bezel': 'retroarch/overlay/MAME-Horizontal.png', 'use_filename': True},
             'atari800': {'bezel_repo': 'bezelprojectSA-Atari800', 'default_bezel': 'retroarch/overlay/Atari-800.png'},
             'atari2600': {'bezel_repo': 'bezelproject-Atari2600', 'default_bezel': 'retroarch/overlay/Atari-2600.png'},
             'atari5200': {'bezel_repo': 'bezelproject-Atari5200', 'default_bezel': 'retroarch/overlay/Atari-5200.png'},
             'atari7800': {'bezel_repo': 'bezelproject-Atari7800', 'default_bezel': 'retroarch/overlay/Atari-7800.png'},
             'atarijaguar': {'bezel_repo': 'bezelproject-AtariJaguar', 'default_bezel': 'retroarch/overlay/Atari-Jaguar.png'},
             'atarilynx': {'bezel_repo': 'bezelproject-AtariLynx', 'default_bezel': 'retroarch/overlay/Atari-Lynx-Horizontal.png'},
             'atarist': {'bezel_repo': 'bezelprojectSA-AtariST', 'default_bezel': 'retroarch/overlay/Atari-ST.png'},
             'c64': {'bezel_repo': 'bezelproject-C64', 'default_bezel': 'retroarch/overlay/Commodore-64.png'},
             'coleco': {'bezel_repo': 'bezelproject-ColecoVision', 'default_bezel': 'retroarch/overlay/Colecovision.png'},
             'daphne': {'bezel_repo': 'bezelproject-Daphne', 'default_bezel': 'retroarch/overlay/Daphne.png'},
             'dreamcast': {'bezel_repo': 'bezelproject-Dreamcast', 'default_bezel': 'retroarch/overlay/Dreamcast.png'},
             'fba': {'bezel_repo': 'bezelproject-MAME', 'default_bezel': 'retroarch/overlay/MAME-Horizontal.png', 'use_filename': True},
             'fds': {'bezel_repo': 'bezelproject-FDS', 'default_bezel': 'retroarch/overlay/Nintendo-Famicom-Disk-System.png'},
             'gamegear': {'bezel_repo': 'bezelproject-GameGear', 'default_bezel': 'retroarch/overlay/Sega-Game-Gear.png'},
             'gb': {'bezel_repo': 'bezelproject-GB', 'default_bezel': 'retroarch/overlay/Nintendo-Game-Boy.png'},
             'gba': {'bezel_repo': 'bezelproject-GBA', 'default_bezel': 'retroarch/overlay/Nintendo-Game-Boy-Advance.png'},
             'gbc': {'bezel_repo': 'bezelproject-GBC', 'default_bezel': 'retroarch/overlay/Nintendo-Game-Boy-Color.png'},
             'genesis': {'bezel_repo': 'bezelproject-MegaDrive', 'default_bezel': 'retroarch/overlay/Sega-Mega-Drive.png'},
             'intellivision': {'bezel_repo': 'bezelproject-Intellivision', 'default_bezel': 'retroarch/overlay/Intellivision.png'},
             'mame-libretro': {'bezel_repo': 'bezelproject-MAME', 'default_bezel': 'retroarch/overlay/MAME-Horizontal.png',  'use_filename': True},
             'mastersystem': {'bezel_repo': 'bezelproject-MasterSystem', 'default_bezel': 'retroarch/overlay/Sega-Master-System.png'},
             'megacd': {'bezel_repo': 'bezelproject-SegaCD', 'default_bezel': 'retroarch/overlay/Sega-CD.png'},
             'megadrive': {'bezel_repo': 'bezelproject-MegaDrive', 'default_bezel': 'retroarch/overlay/Sega-Mega-Drive.png'},
             'msx': {'bezel_repo': 'bezelprojectSA-MSX', 'default_bezel': 'retroarch/overlay/Microsoft-MSX.png'},
             'n64': {'bezel_repo': 'bezelproject-N64', 'default_bezel': 'retroarch/overlay/Nintendo-64.png'},
             'nds': {'bezel_repo': 'bezelproject-NDS', 'default_bezel': 'retroarch/overlay/Nintendo-DS.png'},
             'neogeo': {'bezel_repo': 'bezelproject-MAME', 'default_bezel': 'retroarch/overlay/MAME-Horizontal.png',  'use_filename': True},
             'neogeocd': {'bezel_repo': 'bezelproject-NG-CD', 'default_bezel': 'retroarch/overlay/SNK-Neo-Geo-CD.png'},
             'nes': {'bezel_repo': 'bezelproject-NES', 'default_bezel': 'retroarch/overlay/Nintendo-Entertainment-System.png'},
             'ngp': {'bezel_repo': 'bezelproject-NGP', 'default_bezel': 'retroarch/overlay/SNK-Neo-Geo-Pocket.png'},
             'ngpc': {'bezel_repo': 'bezelproject-NGPC', 'default_bezel': 'retroarch/overlay/SNK-Neo-Geo-Pocket-Color.png'},
             'pc': {'bezel_repo': 'bezelprojectSA-PC', 'default_bezel': 'retroarch/overlay/Microsoft-MS-DOS.png'},
             'pcfx': {'bezel_repo': 'bezelproject-PCFX', 'default_bezel': 'retroarch/overlay/NEC-PC-FX.png'},
             'pcengine': {'bezel_repo': 'bezelproject-PCEngine', 'default_bezel': 'retroarch/overlay/NEC-PC-Engine.png'},
             'psp': {'bezel_repo': 'bezelprojectSA-PSP', 'default_bezel': 'retroarch/overlay/Sony-PSP.png'},
             'psx': {'bezel_repo': 'bezelproject-PSX', 'default_bezel': 'retroarch/overlay/Sony-PlayStation.png'},
             'saturn': {'bezel_repo': 'bezelproject-Saturn', 'default_bezel': 'retroarch/overlay/Sega-Saturn.png'},
             'scummvm': {'bezel_repo': 'bezelproject-ScummVM', 'default_bezel': 'retroarch/overlay/ScummVM.png'},
             'sega32x': {'bezel_repo': 'bezelproject-Sega32X', 'default_bezel': 'retroarch/overlay/Sega-32X.png'},
             'segacd': {'bezel_repo': 'bezelproject-SegaCD', 'default_bezel': 'retroarch/overlay/Sega-CD.png'},
             'sg-1000': {'bezel_repo': 'bezelproject-SG-1000', 'default_bezel': 'retroarch/overlay/Sega-SG-1000.png'},
             'snes': {'bezel_repo': 'bezelproject-SNES', 'default_bezel': 'retroarch/overlay/Super-Nintendo-Entertainment-System.png'},
             'videopac': {'bezel_repo': 'bezelproject-Videopac', 'default_bezel': 'retroarch/overlay/Magnavox-Odyssey-2.png'},
             'virtualboy': {'bezel_repo': 'bezelproject-Virtualboy', 'default_bezel': 'retroarch/overlay/Nintendo-Virtual-Boy.png'},
             'wonderswan': {'bezel_repo': 'bezelproject-WonderSwan', 'default_bezel': 'retroarch/overlay/Bandai-WonderSwan-Horizontal.png'},  # Has vertical
             'wonderswancolor': {'bezel_repo': 'bezelproject-WonderSwanColor', 'default_bezel': 'retroarch/overlay/Bandai-WonderSwan—Color-Horizontal.png'}, # Has vertical
             'x68000': {'bezel_repo': 'bezelprojectSA-X68000', 'default_bezel': 'retroarch/overlay/Sharp-X68000.png'},
             'zx81': {'bezel_repo': 'bezelprojectSA-ZX81', 'default_bezel': 'retroarch/overlay/Sinclair-ZX-81.png'},
             'zxspectrum': {'bezel_repo': 'bezelprojectSA-ZXSpectrum', 'default_bezel': 'retroarch/overlay/Sinclair-ZX-Spectrum.png'},
             }

SCRAPING_MODULES = ['screenscraper', 'arcadedb', 'igdb', 'mobygames', 'openretro', 'thegamesdb',
                    'worldofspectrum']

UNSUPPORTED_REGION_STRINGS = (
    'Japan',
    '(J)'
)

BASE_TREE_URL = 'https://api.github.com/repos/thebezelproject/{0}/git/trees/master?recursive=1'

BASE_BEZEL_RAW_URL = 'https://raw.githubusercontent.com/thebezelproject/{0}/master/{1}'

BEZEL_ROOT_DIR = os.path.join(str(Path.home()), '.bezels')
