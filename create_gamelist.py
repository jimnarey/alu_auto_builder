#!/usr/bin/env python3

import os


def scrape(platform, scrape_flags, data_paths, scrape_source, user_creds=None):
    opts = '-s {0}'.format(scrape_source)
    opts = opts + ' -u {0}'.format(user_creds) if user_creds else opts
    run_skyscraper(platform, scrape_flags, data_paths, opts)


def create_gamelist(platform, game_list_flags, data_paths):
    opts = '-a "{0}" -g "{1}"'.format(data_paths['art_xml_path'], data_paths['temp_dir'])
    run_skyscraper(platform, game_list_flags, data_paths, opts)


def run_skyscraper(platform, flags, data_paths, opts):
    cmd = 'Skyscraper -p {0} -i "{1}" -c "{2}" {3}'.format(platform, data_paths['input_dir'], data_paths['config_file'], opts)
    cmd = cmd + ' --flags {0}'.format(','.join(flags)) if flags else cmd
    print(cmd)
    cmd_out = os.popen(cmd).read()
    print(cmd_out)