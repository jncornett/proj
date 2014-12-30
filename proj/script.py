import argparse
import logging
import os
from pkg_resources import resource_filename

logger = logging.getLogger(__name__)

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
    return parser


def main(config):
    options = vars(get_parser(config).parse_args())
    logging.debug(options)

