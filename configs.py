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

FLAGS = 'onlymissing,nosubdirs,noscreenshots,nomarquees'

CARTRIDGE_XML = [
    '<?xml version="1.0" encoding="UTF-8"?>\n',
    '<byog_cartridge version="1.0">\n',
    '\t<title>GAME_TITLE</title>\n',
    '\t<desc>GAME_DESCRIPTION</desc>\n',
    '\t<boxart file="boxart\BOXART_FILE_NAME" ext="png">\n',
    '</byog_cartridge>\n',
]

EXEC_SH = [
    '#!/bin/sh\n',
    'set -x\n',
    '/emulator/retroplayer ./emu/CORE_FILE_NAME "./roms/GAME_FILE_NAME"\n'
]