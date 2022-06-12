from shared import configs, help_messages
import runners

input_path_opt = {
    'name': 'input_path',
    'cli_short': 'i',
    'gui_required': True,
    'type': 'file_open',
    'help': help_messages.INPUT_PATH
    }

input_dir_opt = {
    'name': 'input_dir',
    'cli_short': 'i',
    'gui_required': True,
    'type': 'dir',
    'help': help_messages.INPUT_DIR
}

output_path_opt = {
    'name': 'output_path',
    'cli_short': 'o',
    'gui_required': False,
    'type': 'file_save',
    'help': help_messages.OUTPUT_PATH
}

output_dir_opt = {
    'name': 'output_dir',
    'cli_short': 'o',
    'gui_required': False,
    'type': 'dir',
    'help': help_messages.OUTPUT_DIR
}

extra_build_opts = (
    {
        'name': 'core_path',
        'cli_short': 'c',
        'gui_required': True,
        'type': 'file_open',
        'help': help_messages.CORE_PATH
    },
    {
        'name': 'bios_dir',
        'cli_short': 'b',
        'gui_required': False,
        'type': 'dir',
        'help': help_messages.BIOS_DIR
    }
)

platform_opt = {
        'name': 'platform',
        'cli_short': 'p',
        'gui_required': True,
        'type': 'text_selection',
        'help': help_messages.PLATFORM,
        'selections': configs.PLATFORMS.keys()
     }

other_scrape_opts = (
    {
        'name': 'scrape_module',
        'cli_short': 's',
        'gui_required': False,
        'type': 'text_selection',
        'help': help_messages.SCRAPE_MODULE,
        'selections': configs.SCRAPING_MODULES
     },
    {
        'name': 'user_name',
        'cli_short': 'u',
        'gui_required': False,
        'type': 'text',
        'help': help_messages.USER_NAME
     },
    {
        'name': 'password',
        'cli_short': 'q',
        'gui_required': False,
        'type': 'text',
        'help': help_messages.PASSWORD
    },
    {
        'name': 'scrape_videos',
        'cli_short': 'V',
        'gui_required': False,
        'gui_default': False,
        'type': 'bool',
        'help': help_messages.SCRAPE_VIDEOS
    },
    {
        'name': 'refresh_rom_data',
        'cli_short': 'R',
        'gui_required': False,
        'gui_default': False,
        'type': 'bool',
        'help': help_messages.REFRESH_ROM_DATA
    }
)

export_assets_opts = (
    {
        'name': 'export_cox_assets',
        'cli_short': 'C',
        'gui_required': False,
        'gui_default': False,
        'type': 'bool',
        'help': help_messages.EXPORT_COX_ASSETS
     },
    {
        'name': 'export_bitpixel_marquees',
        'cli_short': 'Q',
        'gui_required': False,
        'gui_default': False,
        'type': 'bool',
        'help': help_messages.EXPORT_BITPIXEL_MARQUEES
    }
)

do_bezel_scape_opt = {
    'name': 'do_bezel_scrape',
    'cli_short': 'B',
    'gui_required': False,
    'gui_default': True,
    'type': 'bool',
    'help': help_messages.DO_BEZEL_SCRAPE
}

do_summarise_gamelist_opt = {
    'name': 'do_summarise_gamelist',
    'cli_short': 'S',
    'gui_required': False,
    'gui_default': False,
    'type': 'bool',
    'help': help_messages.DO_SUMMARISE_GAMELIST
}

add_bezels_to_gamelist_opts = (
    {
        'name': 'min_match_score',
        'cli_short': 'm',
        'gui_required': False,
        'gui_default': True,
        'type': 'text',
        'help': help_messages.MIN_MATCH_SCORE
    },
    {
        'name': 'compare_filename',
        'cli_short': 'F',
        'gui_required': False,
        'gui_default': False,
        'type': 'bool',
        'help': help_messages.COMPARE_FILENAME
    },
    {
        'name': 'filter_unsupported_regions',
        'cli_short': 'U',
        'gui_required': False,
        'gui_default': True,
        'type': 'bool',
        'help': help_messages.FILTER_UNSUPPORTED_REGIONS
    }
)

replace_save_part_opt = {
    'name': 'part_path',
    'cli_short': 'p',
    'gui_required': True,
    'type': 'file_open',
    'help': help_messages.PART_PATH
}

edit_save_part_opts = (
    {
        'name': 'mount_method',
        'cli_short': 'M',
        'gui_required': False,
        'gui_default': False,
        'type': 'bool',
        'help': help_messages.MOUNT_METHOD
    },
    {
        'name': 'file_manager',
        'cli_short': 'f',
        'gui_required': False,
        'type': 'text',
        'help': help_messages.FILE_MANAGER}
)

backup_save_part_opt = {
    'name': 'backup_uce',
    'cli_short': 'B',
    'gui_required': False,
    'gui_default': False,
    'type': 'bool',
    'help': help_messages.BACKUP_UCE
}

scrape_and_build_opts = (input_dir_opt, output_dir_opt, *extra_build_opts, platform_opt, *other_scrape_opts)

build_from_game_list_opts = (input_path_opt, output_dir_opt, *extra_build_opts)

operations = {
    'scrape_to_uces': { #
        'options': (*scrape_and_build_opts, do_summarise_gamelist_opt, do_bezel_scape_opt, *add_bezels_to_gamelist_opts, *export_assets_opts),
        'runner': runners.scrape_and_build_uces,
        'help': help_messages.SCRAPE_TO_UCES,
        'gui_user_continue_check': False
    },
    'scrape_to_recipes': { #
        'options': (*scrape_and_build_opts, do_summarise_gamelist_opt, do_bezel_scape_opt, *add_bezels_to_gamelist_opts, *export_assets_opts),
        'runner': runners.scrape_and_make_recipes,
        'help': help_messages.SCRAPE_TO_RECIPES,
        'gui_user_continue_check': False
    },
    'scrape_to_gamelist': { #
        'options': (input_dir_opt, output_dir_opt, platform_opt, *other_scrape_opts, do_summarise_gamelist_opt, do_bezel_scape_opt, *add_bezels_to_gamelist_opts,),
        'runner': runners.scrape_and_make_gamelist,
        'help': help_messages.SCRAPE_TO_GAMELIST,
        'gui_user_continue_check': False
    },
    'gamelist_to_uces': {
        'options': (*build_from_game_list_opts, *export_assets_opts, do_summarise_gamelist_opt),
        'runner': runners.build_uces_from_gamelist,
        'help': help_messages.GAMELIST_TO_UCES,
        'gui_user_continue_check': False
    },
    'gamelist_to_recipes': {
        'options': (*build_from_game_list_opts, *export_assets_opts, do_summarise_gamelist_opt),
        'runner': runners.build_recipes_from_gamelist,
        'help': help_messages.GAMELIST_TO_RECIPES,
        'gui_user_continue_check': False
    },
    'export_gamelist_assets': {
        'options': (input_path_opt, output_dir_opt, *export_assets_opts, do_summarise_gamelist_opt),
        'runner': runners.export_assets_from_gamelist,
        'help': help_messages.EXPORT_GAMELIST_ASSETS,
        'gui_user_continue_check': False
    },
    'add_bezels_to_gamelist': { #
        'options': (input_path_opt, platform_opt, *add_bezels_to_gamelist_opts, do_summarise_gamelist_opt),
        'runner': runners.add_bezels_to_existing_gamelist,
        'help': help_messages.ADD_BEZELS_TO_GAMELIST,
        'gui_user_continue_check': False
    },
    'summarise_gamelist': {
        'options': (input_path_opt, output_dir_opt),
        'runner': runners.create_summary_of_gamelist,
        'help': help_messages.SUMMARISE_GAMELIST,
        'gui_user_continue_check': False
    },
    'recipes_to_uces': {
        'options': (input_dir_opt, output_dir_opt),
        'runner': runners.build_uces_from_recipes,
        'help': help_messages.RECIPES_TO_UCES,
        'gui_user_continue_check': False
    },
    'recipe_to_uce': {
        'options': (input_dir_opt, output_path_opt),
        'runner': runners.build_single_uce_from_recipe,
        'help': help_messages.RECIPE_TO_UCE,
        'gui_user_continue_check': False
    },
    'edit_save_partition': {
        'options': (input_path_opt, *edit_save_part_opts, backup_save_part_opt),
        'runner': runners.edit_uce_save_partition,
        'help': help_messages.EDIT_SAVE_PARTITION,
        'gui_user_continue_check': True
    },
    'extract_save_partition': {
        'options': (input_path_opt, output_path_opt),
        'runner': runners.extract_uce_save_partition,
        'help': help_messages.EXTRACT_SAVE_PARTITION,
        'gui_user_continue_check': False
    },
    'replace_save_partition': {
        'options': (input_path_opt, replace_save_part_opt, backup_save_part_opt),
        'runner': runners.replace_uce_save_partition,
        'help': help_messages.REPLACE_SAVE_PARTITION,
        'gui_user_continue_check': False
    }
}
