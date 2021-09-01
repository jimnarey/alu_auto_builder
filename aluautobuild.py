#!/usr/bin/env python3

import errno
import os
# import sys
from pprint import pp, pprint
from optparse import OptionParser
from configs import CONFIG, ARTWORK, FLAGS

# TODO - Add something to ignore existing Skyscraper config
# TODO - Ensure temp files are created in input dir, not in whatever dir the script is run in

def write_file(file_path, lines):
    with open(file_path, 'w') as target_file:
        target_file.writelines(lines)

def safe_make_dir(path):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    pass

def run_skyscraper(platform, input_dir, flags, config_path, art_xml_path=None, scrape_source=None, user_creds=None):
    cmd = 'Skyscraper -p {0} -i "{1}" --flags {2} -c "{3}"'.format(platform, input_dir, flags, config_path)
    if scrape_source:
        cmd = cmd + ' -s {0}'.format(scrape_source)
        cmd = cmd + ' -u {0}'.format(user_creds) if user_creds else cmd
    elif art_xml_path:
        cmd = cmd + ' -a "{0}"'.format(art_xml_path)
    os.system(cmd)
    # print(cmd)

def set_paths(input_dir, output_dir):
    this_dir = os.path.split(os.path.realpath(__file__))[0]
    paths = {}
    paths['input_dir'] = input_dir
    paths['output_dir'] = output_dir if output_dir else os.path.join(input_dir, 'output')
    paths['temp_dir'] = os.path.join(input_dir, 'temp')
    paths['config_file'] = os.path.join(paths['temp_dir'], 'config.ini')
    paths['art_xml_path'] = os.path.join(paths['temp_dir'], 'artwork.xml')
    paths['common_files'] = os.path.join(this_dir, 'common')
    paths['vendor_scripts'] = os.path.join(this_dir, 'vendor')
    return paths

def setup(paths):
    safe_make_dir(paths['temp_dir'])
    safe_make_dir(paths['output_dir'])
    write_file(paths['config_file'], CONFIG)
    write_file(paths['art_xml_path'], ARTWORK)

def run(platform, input_dir, flags, scrape_source, user_creds, output_dir):
    paths = set_paths(input_dir, output_dir)
    pprint(paths)
    setup(paths)
    # run_skyscraper(platform, input_dir, flags, paths['config_file'], scrape_source=scrape_source, user_creds=user_creds)
    # run_skyscraper(platform, input_dir, flags, paths['config_file'], art_xml_path=paths['art_xml_path'])


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-p', '--platform', dest='platform', help="Emulated platform. Run 'Skyscraper --help' to see available platforms.")
    parser.add_option('-i', '--inputdir', dest='input_dir', help="Location of input roms.")
    parser.add_option('-s', '--scraper', dest='scraper', help="Scraping source. Run 'Skyscraper --help' to see available scraping modules.")
    parser.add_option('-o', '--output', dest='output_dir', help="Output directory.")
    parser.add_option('-u', '--usercreds', dest='user_creds', help="User credentials for scraping module.")
    (options, args) = parser.parse_args()
    if options.platform is None:
        print(parser.usage)
        exit(0)
    
    flags=FLAGS
    input_dir = options.input_dir if options.input_dir else os.getcwd()
    scrape_source = options.scraper if options.scraper else 'screenscraper'
    user_creds = options.user_creds if options.user_creds else None
    output_dir = options.output_dir if options.output_dir else None
    run(options.platform, input_dir, flags, scrape_source, user_creds, output_dir)
