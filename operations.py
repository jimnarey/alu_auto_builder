from shared import configs, help_messages
import runners

input_path_opt = {
    'name': 'input_path',
    'short': 'i',
    'gui_required': True,
    'type': 'file_open',
    'help': help_messages.INPUT_PATH
    }

input_dir_opt = {
    'name': 'input_dir',
    'short': 'i',
    'gui_required': True,
    'type': 'dir',
    'help': help_messages.INPUT_DIR
}

output_path_opt = {
    'name': 'output_path',
    'short': 'o',
    'gui_required': False,
    'type': 'file_save',
    'help': help_messages.OUTPUT_PATH
}

output_dir_opt = {
    'name': 'output_dir',
    'short': 'o',
    'gui_required': False,
    'type': 'dir',
    'help': help_messages.OUTPUT_DIR
}

extra_build_opts = (
    {
        'name': 'core_path',
        'short': 'c',
        'gui_required': True,
        'type': 'file_open',
        'help': help_messages.CORE_PATH
    },
    {
        'name': 'bios_dir',
        'short': 'b',
        'gui_required': False,
        'type': 'dir',
        'help': help_messages.BIOS_DIR
    }
)

scrape_opts = (
    {
        'name': 'platform',
        'short': 'p',
        'gui_required': True,
        'type': 'text',
        'help': help_messages.PLATFORM,
        'selections': configs.PLATFORMS
     },
    {
        'name': 'scrape_module',
        'short': 's',
        'gui_required': False,
        'type': 'text',
        'help': help_messages.SCRAPE_MODULE,
        'selections': configs.SCRAPING_MODULES
     },
    {
        'name': 'user_name',
        'short': 'u',
        'gui_required': False,
        'type': 'text',
        'help': help_messages.USER_NAME
     },
    {
        'name': 'password',
        'short': 'q',
        'gui_required': False,
        'type': 'text',
        'help': help_messages.PASSWORD
     }
)

replace_save_part_opt = {
    'name': 'part_path',
    'short': 'p',
    'gui_required': True,
    'type': 'file_open',
    'help': help_messages.PART_PATH
}

edit_save_part_opts = (
    {
        'name': 'mount_method',
        'short': 'M',
        'gui_required': False,
        'type': 'bool',
        'help': help_messages.MOUNT_METHOD
    },
    {
        'name': 'file_manager',
        'short': 'f',
        'gui_required': False,
        'type': 'text',
        'help': help_messages.FILE_MANAGER}
)

backup_save_part_opt = {
    'name': 'backup_uce',
    'short': 'B',
    'gui_required': False,
    'type': 'bool',
    'help': help_messages.BACKUP_UCE
}

scrape_and_build_opts = (input_dir_opt, output_dir_opt, *extra_build_opts, *scrape_opts)

build_from_game_list_opts = (input_path_opt, output_dir_opt, *extra_build_opts)

operations = {
    'scrape_to_uces': {
        'options': scrape_and_build_opts,
        'runner': runners.scrape_and_build_uces,
        'help': help_messages.SCRAPE_TO_UCES
    },
    'scrape_to_recipes': {
        'options': scrape_and_build_opts,
        'runner': runners.scrape_and_make_recipes,
        'help': help_messages.SCRAPE_TO_RECIPES
    },
    'scrape_to_gamelist': {
        'options': (input_dir_opt, output_dir_opt, *scrape_opts),
        'runner': runners.scrape_and_make_gamelist,
        'help': help_messages.SCRAPE_TO_GAMELIST
    },
    'gamelist_to_uces': {
        'options': build_from_game_list_opts,
        'runner': runners.build_uces_from_gamelist,
        'help': help_messages.GAMELIST_TO_UCES
    },
    'gamelist_to_recipes': {
        'options': build_from_game_list_opts,
        'runner': runners.build_recipes_from_gamelist,
        'help': help_messages.GAMELIST_TO_RECIPES
    },
    'recipes_to_uces': {
        'options': (input_dir_opt, output_dir_opt),
        'runner': runners.build_uces_from_recipes,
        'help': help_messages.RECIPES_TO_UCES
    },
    'recipe_to_uce': {
        'options': (input_dir_opt, output_path_opt),
        'runner': runners.build_single_uce_from_recipe,
        'help': help_messages.RECIPE_TO_UCE
    },
    'edit_save_partition': {
        'options': (input_path_opt, *edit_save_part_opts, backup_save_part_opt),
        'runner': runners.edit_uce_save_partition,
        'help': help_messages.EDIT_SAVE_PARTITION
    },
    'extract_save_partition': {
        'options': (input_path_opt, output_path_opt),
        'runner': runners.extract_uce_save_partition,
        'help': help_messages.EXTRACT_SAVE_PARTITION
    },
    'replace_save_partition': {
        'options': (input_path_opt, replace_save_part_opt, backup_save_part_opt),
        'runner': runners.replace_uce_save_partition,
        'help': help_messages.REPLACE_SAVE_PARTITION
    }
}
