#!/usr/bin/env python3

import os
from optparse import OptionParser

CONFIG = [  '[main]',
            'videos="false"',
            'unattend="true"',
            'verbosity="1"',
            '[screenscraper]',
            'userCreds="{0}"'.format(os.getenv('SCCREDS'))
        ]

FLAGS = 'onlymissing,nosubdirs,noscreenshots,nomarquees'

def write_config(path='.'):
    with open(os.path.join(path, 'conf.ini'), 'w') as config_file:
        config_file.write('\n'.join(CONFIG) + '\n')

TEMP_DIR = os.path.join('.', 'temp')

def download_rom_data(platform, roms_dir, config_file, flags, scrape_source):
    os.system('Skyscraper -p {0} -i {1} -c "{2}" --flags {3} -s {4}'.format(platform, roms_dir, config_file, flags, scrape_source))

def write_gamelist(platform, roms_dir, config_file, flags):
    os.system('Skyscraper -p {0} -i {1} -c {2} --flags {3}'.format(platform, roms_dir, config_file, flags))

def run(platform, roms_dir, config, flags, scrape_source, output_dir):
    write_config()
    # os.mkdir(output_dir)
    download_rom_data(platform, roms_dir, config, flags, scrape_source)
    # write_gamelist(platform, roms_dir, config, flags)


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help="Emulated platform. Run 'Skyscraper --help' to see available platforms.")
    parser.add_option('-i', '--inputdir', dest='roms_dir', help="Location of input roms.")
    parser.add_option('-s', '--scraper', dest='scraper', help="Scraping source. Run 'Skyscraper --help' to see available scraping modules.")
    parser.add_option('-o', '--output', dest='output_dir', help="Output directory.")
    (options, args) = parser.parse_args()
    if options.platform is None:
        print(parser.usage)
        exit(0)
    roms_dir = options.roms_dir if options.roms_dir else os.getcwd()
    config='./conf.ini'
    flags=FLAGS
    scrape_source = options.scraper if options.scraper else 'screenscraper'
    output_dir = options.output_dir if options.output_dir else os.path.join(os.getcwd(), 'output')
    run(options.platform, roms_dir, config, flags, scrape_source, output_dir)
