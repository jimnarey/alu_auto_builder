from shared import configs
import runners


input_path_opt = {'name': 'input_path', 'short': 'i', 'gui_required': True}

input_dir_opt = {'name': 'input_dir', 'short': 'i', 'gui_required': True}

output_path_opt = {'name': 'output_path', 'short': 'o', 'gui_required': False}

output_dir_opt = {'name': 'output_dir', 'short': 'o', 'gui_required': False}


extra_build_opts = (
    {'name': 'core_path', 'short': 'c', 'gui_required': True},
    {'name': 'bios_dir', 'short': 'b', 'gui_required': False}
)

scrape_opts = (
    {'name': 'platform', 'short': 'p', 'gui_required': True, 'selections': configs.PLATFORMS},
    {'name': 'scrape_module', 'short': 's', 'gui_required': False, 'selections': configs.SCRAPING_MODULES},
    {'name': 'user_name', 'short': 'u', 'gui_required': False},
    {'name': 'password', 'short': 'q', 'gui_required': False}
)

replace_save_part_opt = {'name': 'part_path', 'short': 'p', 'gui_required': True}

edit_save_part_opts = (
    {'name': 'mount_method', 'short': 'M', 'gui_required': False},
    {'name': 'file_manager', 'short': 'f', 'gui_required': False}
)

backup_save_part_opt = {'name': 'backup_uce', 'short': 'B', 'gui_required': False}

scrape_and_build_opts = (input_dir_opt, output_dir_opt, *extra_build_opts, *scrape_opts)

build_from_game_list_opts = (input_path_opt, output_dir_opt, *extra_build_opts)


operations = {
    'scrape_and_build_uces': {'options': scrape_and_build_opts, 'runner': runners.scrape_and_build_uces},
    'scrape_and_make_recipes': {'options': scrape_and_build_opts, 'runner': runners.scrape_and_make_recipes},
    'scrape_and_make_gamelist': {'options': (input_dir_opt, output_dir_opt, *scrape_opts), 'runner': runners.scrape_and_make_gamelist},
    'build_uces_from_gamelist': {'options': build_from_game_list_opts, 'runner': runners.build_uces_from_gamelist},
    'build_recipes_from_gamelist': {'options': build_from_game_list_opts, 'runner': runners.build_recipes_from_gamelist},
    'build_uces_from_recipes': {'options': (input_dir_opt, output_dir_opt), 'runner': runners.build_uces_from_recipes},
    'build_single_uce_from_recipe': {'options': (input_dir_opt, output_path_opt), 'runner': runners.build_single_uce_from_recipe},
    'edit_uce_save_partition': {'options': (input_path_opt, *edit_save_part_opts, backup_save_part_opt), 'runner': runners.edit_uce_save_partition},
    'extract_uce_save_partition': {'options': (input_path_opt, output_path_opt), 'runner': runners.extract_uce_save_partition},
    'replace_uce_save_partition': {'options': (input_path_opt, replace_save_part_opt, backup_save_part_opt), 'runner': runners.replace_uce_save_partition}
}
