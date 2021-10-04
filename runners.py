#!/usr/bin/env python3

import build_from_recipes
import build_uce_tool
import create_gamelist
import build_recipes
import edit_uce
import extract_save_part
import replace_save_part


def scrape_and_build_uces(args):
    pass


def scrape_and_make_recipes(args):
    pass


def scrape_and_make_gamelist(args):
    create_gamelist.run_with_args(args)


def build_uces_from_gamelist(args):
    pass


def build_recipes_from_gamelist(args):
    build_recipes.run_with_args(args)


def build_uces_from_recipes(args):
    build_from_recipes.run_with_args(args)


def build_single_uce_from_recipe(args):
    build_uce_tool.run_with_args(args)


def edit_uce_save_partition(args):
    edit_uce.run_with_args(args)


def extract_uce_save_partition(args):
    extract_save_part.run_with_args(args)


def replace_uce_save_partition(args):
    replace_save_part.run_with_args(args)