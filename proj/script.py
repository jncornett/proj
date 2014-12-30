import argparse
import json
import logging
import os
from pkg_resources import resource_filename

from .plugin import PluginManager
from .core import Maker
from .util import find_dirs_containing, expand_join

STRUCTURE_ROOT_NAME = "proj.json"
USER_ROOT_DIR = expand_join("~", "." + __name__)
STRUCTURE_ROOT_DIR = resource_filename(__name__, "data/templates")
USER_STRUCTURE_ROOT_DIR = os.path.join(USER_ROOT_DIR, "templates")
PLUGIN_ROOT_DIR = resource_filename(__name__, "data/plugins")
USER_PLUGIN_ROOT_DIR = os.path.join(USER_ROOT_DIR, "plugins")

def find_structure_dir(name, paths):
    for path in paths:
        structure = find_dirs_containing(path, STRUCTURE_ROOT_NAME, False)
        for structure_dir in structure:
            if structure_dir == name:
                return path, structure_dir


def get_parser(config):
    parser = argparse.ArgumentParser()
    parser.add_argument("name", 
                        help=("The name of the project folder to create "
                              "in the current working directory"))
    parser.add_argument("template", 
                        help=("Template to use. This can be an absolute path "
                              "or a relative path for a template located in "
                              "the package or user template directory. (The "
                              "user template directory is located at {!r})"
                              ).format(USER_STRUCTURE_ROOT_DIR))
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Simulate project creation")
    return parser


def configure_logger(options):
    log_level = logging.WARNING
    if options["debug"]:
        log_level = logging.DEBUG
    elif options["verbose"]:
        log_level = logging.INFO

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(log_level)
    return logger


def main():
    config = {}
    options = vars(get_parser(config).parse_args())
    logger = configure_logger(options)
    if options["debug"]:
        logger.debug(options)

    structure_dir = find_structure_dir(
        options["template"], 
        filter(os.path.isdir, [STRUCTURE_ROOT_DIR, USER_STRUCTURE_ROOT_DIR])
        )

    if not structure_dir:
        logger.error("Template %r not found", options["template"])
        exit(2)

    with open(os.path.join(*(structure_dir + (STRUCTURE_ROOT_NAME,))), "rb") as f:
        structure = json.load(f)

    plugin_manager = PluginManager(
        None, # TODO: <- fix this reference issue
        filter(os.path.isdir, [PLUGIN_ROOT_DIR, USER_PLUGIN_ROOT_DIR]),
        debug=options["debug"],
        logger=logger
        )

    # TODO: ^^ Weird dependency thing going on here with PluginManager + Maker
    #       Need to make more modularized and agnostic.

    maker = Maker(options["name"], structure, os.path.join(*structure_dir),
                  **dict(
                      plugin_manager=plugin_manager,
                      logger=logger
                      )
                  )

    maker.make(dry_run=options["dry_run"]) # TODO: Enable passing data from cl


    

