#!/usr/bin/env python3
import os.path

import requests
import pprint

from shared import configs, common_utils

BASE_URL = 'https://api.github.com/repos/thebezelproject/{0}/git/trees/master?recursive=1'


def get_available_bezels(platform):
    data = requests.get(BASE_URL.format('bezelproject-GameGear'))
    tree = data.json()['tree']
    pngs = []
    for item in tree:
        if item['type'] == 'blob':
            if os.path.splitext(item['path'])[-1] == '.png':
                pngs.append({os.path.basename(item['path']): item['url']})
    pprint.pprint(pngs)

    # print(data.status_code)
    # pprint.pprint(data.json())
    # common_utils.write_file('out.json', str(data.json()), 'w')


get_available_bezels('')
# No 'if name == __main__' as this can't be run as a distinct operation
