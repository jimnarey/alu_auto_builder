import configs

input_path_opt = {'name': 'input_path', 'short': 'i', 'required': True}

input_dir_opt = {'name': 'input_dir', 'short': 'i', 'required': True}

output_path_opt = {'name': 'output_path', 'short': 'o', 'required': False}

output_dir_opt = {'name': 'output_dir', 'short': 'o', 'required': False}


extra_build_opts = (
    {'name': 'core_path', 'short': 'c', 'required': True},
    {'name': 'bios_dir', 'short': 'b', 'required': False}
)

scrape_opts = (
    {'name': 'platform', 'short': 'p', 'required': True, 'selections': configs.PLATFORMS},
    {'name': 'scrape_module', 'short': 's', 'required': False, 'selections': configs.SCRAPING_MODULES},
    {'name': 'user_name', 'short': 'u', 'required': False},
    {'name': 'password', 'short': 'q', 'required': False}
)

edit_uce_extra_opts = (
    {'name': 'extract_path', 'short': 'e', 'required': False},
    {'name': 'backup_uce', 'short': 'B', 'required': False},
    {'name': 'replace_path', 'short': 'r', 'required': False},
    {'name': 'mount_method', 'short': 'M', 'required': False},
    {'name': 'retro_ini_path', 'short': 'n', 'required': False},
    {'name': 'file_manager', 'short': 'f', 'required': False}
)

scrape_and_build_opts = (input_dir_opt, output_dir_opt, *extra_build_opts, *scrape_opts)

build_from_game_list_opts = (input_path_opt, output_dir_opt, *extra_build_opts)

operations = {
    'scrape_and_build_uces': scrape_and_build_opts,
    'scrape_and_make_recipes': scrape_and_build_opts,
    'scrape_and_make_gamelist': (input_dir_opt, output_dir_opt, *scrape_opts),
    'build_uces_from_gamelist': build_from_game_list_opts,
    'build_recipes_from_gamelist': build_from_game_list_opts,
    'build_uces_from_recipes': (input_dir_opt, output_dir_opt),
    'edit_uce_save_partition': (input_path_opt,)
}

