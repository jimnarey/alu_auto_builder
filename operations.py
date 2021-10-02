import configs

# TODO consider changing 'required' to 'gui_required' given command line can auto generate some opts based on cwd

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

replace_save_part_opt = {'name': 'part_path', 'short': 'p', 'required': True}

edit_save_part_opts = (
    {'name': 'mount_method', 'short': 'M', 'required': False},
    {'name': 'file_manager', 'short': 'f', 'required': False}
)

backup_save_part_opt = {'name': 'backup_uce', 'short': 'B', 'required': False}

scrape_and_build_opts = (input_dir_opt, output_dir_opt, *extra_build_opts, *scrape_opts)

build_from_game_list_opts = (input_path_opt, output_dir_opt, *extra_build_opts)

operations = {
    'scrape_and_build_uces': scrape_and_build_opts,
    'scrape_and_make_recipes': scrape_and_build_opts,
    'scrape_and_make_gamelist': (input_dir_opt, output_dir_opt, *scrape_opts),
    'build_uces_from_gamelist': build_from_game_list_opts,
    'build_recipes_from_gamelist': build_from_game_list_opts,
    'build_uces_from_recipes': (input_dir_opt, output_dir_opt),
    'build_single_uce_from_recipe': (input_dir_opt, output_path_opt),
    'edit_uce_save_partition': (input_path_opt, *edit_save_part_opts, backup_save_part_opt),
    'extract_uce_save_partition': (input_path_opt, output_path_opt),
    'replace_uce_save_partition': (input_path_opt, replace_save_part_opt, backup_save_part_opt)
}

