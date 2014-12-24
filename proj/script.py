#!/usr/bin/env python

import os
from pkg_resources import resource_filename
from .core import *
import logging

logger = logging.getLogger(__name__)

ROOT_TEMPLATE_NAME = "root.json"
CONFIG_FILENAME = ".proj.json"
USER_PATH = os.path.expanduser("~")
CONFIG_PATH = os.path.join(USER_PATH, CONFIG_FILENAME)
PACKAGE_TEMPLATE_DIR = "data/templates"
DEFAULT_USER_TEMPLATE_DIR = os.path.join(USER_PATH, ".proj")
DEFAULTS = {
    "template_dir": DEFAULT_USER_TEMPLATE_DIR
}

DOC = """\
To set user defaults, create/edit a JSON file at {CONFIG_PATH}.
To add custom project templates, create/edit the subfolder under
{{template_dir}}. 
Each template must contain a {ROOT_TEMPLATE_NAME}.
For information on the JSON structure of {ROOT_TEMPLATE_NAME},
see [TODO: Add {ROOT_TEMPLATE_NAME} documentation].
""".format(**vars())


def _get_templates(path):
    templates = {}
    for dirpath, dirnames, filenames in os.walk(path):
        if ROOT_TEMPLATE_NAME in filenames:
            template_key = os.path.relpath(dirpath, path)
            templates[template_key] = dirpath
            dirnames[:] = [] # Stop recursing in this tree

    return templates


def get_available_templates(user_template_path):
    pkg_template_path = resource_filename(
        __name__,
        PACKAGE_TEMPLATE_DIR
        )

    templates = _get_templates(pkg_template_path)
    
    if os.path.isdir(user_template_path):
        templates.update(_get_templates(user_template_path))
    elif os.path.exists(user_template_path):
        logger.warn("User template path [%s] is a file",
                user_template_path)

    return templates


def get_parser(config):
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=DOC
        )

    parser.add_argument(
        "-q", "--quiet", action="store_const",
        dest="log_level", const=logging.WARNING,
        default=logging.INFO, help="Suppress (most) logging"
        )

    parser.add_argument(
        "--debug", action="store_const", dest="log_level",
        const=logging.DEBUG, help="Turn on debug messages"
        )

    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Don't actually do anything")

    parser.add_argument(
        "-j", "--json", action="append",
        help="Specify additional configuration files"
        )

    parser.add_argument(
        "-r", "--root", default=os.getcwd(),
        help="Specify a root directory for the project"
        )

    parser.add_argument(
        "template", 
        choices=get_available_templates(
            config["template_dir"]
            ),
        help="Template to use"
        )

    parser.add_argument(
        "name", help="Name of project to create")

    return parser


def get_config(*filenames):
    master = {}
    for filename in filenames:
        try:
            with open(filename, "rb") as f:
                config = json.load(f)
        except (OSError, IOError):
            config = {}
        
        master.update(config)

    return master


def main():
    config = dict(DEFAULTS, **get_config(CONFIG_PATH))
    cmdline_config = vars(get_parser(config).parse_args())
    
    if cmdline_config["json"]:
        config.update(get_config(*cmdline_config["json"]))

    config.update(cmdline_config)

    logging.basicConfig(level=config["log_level"])

    project = Project(
        config["name"], 
        os.path.join(config["template_dir"], config["template"])
        )

    project.init(config, config["dry_run"])

if __name__ == "__main__":
    main()
