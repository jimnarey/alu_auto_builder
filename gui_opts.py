import configs

input_path_opt = {'name': 'input_path', 'required': True}


input_dir_opt = {'name': 'input_dir', 'required': True}


output_dir_opt = {'name': 'output_dir', 'required': False}


extra_build_opts = (
    {'name': 'core_path', 'required': True},
    {'name': 'bios_dir', 'required': False}
)

scrape_opts = (
    {'name': 'platform', 'required': True, 'selections': configs.PLATFORMS},
    {'name': 'scrape_module', 'required': True, 'selections': configs.SCRAPING_MODULES},
    {'name': 'user_name', 'required': False},
    {'name': 'password', 'required': False}
)

scrape_and_build_opts = (input_dir_opt, output_dir_opt, *extra_build_opts, *scrape_opts)

build_from_game_list_opts = (input_path_opt, output_dir_opt, *extra_build_opts)

operations = {
    'scrape_and_build_uces': scrape_and_build_opts,
    'scrape_and_make_recipes': scrape_and_build_opts,
    'scrape_and_make_gamelist': (input_dir_opt, output_dir_opt, *scrape_opts),
    'build_uces_from_game_list': build_from_game_list_opts,
    'build_recipes_from_game_list': build_from_game_list_opts,
    'build_from_recipes': (input_dir_opt, output_dir_opt),
    'edit_uce_save_partition': (input_path_opt,)
}

