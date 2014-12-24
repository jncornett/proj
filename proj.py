#!/usr/bin/env python

import json
import logging
import os
from subprocess import check_call

logger = logging.getLogger(__name__)

ROOT_TEMPLATE_NAME = "root.json"
CONFIG_FILENAME = ".proj.json"
USER_PATH = os.path.expanduser("~")
CONFIG_PATH = os.path.join(USER_PATH, CONFIG_FILENAME)
DEFAULT_TEMPLATE_DIR = os.path.join(USER_PATH, ".proj")
DEFAULTS = {
    "template_dir": DEFAULT_TEMPLATE_DIR
}

DOC = """\
Feel free to edit the configuration file at {CONFIG_PATH}
""".format(**vars())

def mkdirp(path):
    try:
        os.makedirs(path)
    except os.error:
        if not os.path.exists(path):
            raise


def touch(path):
    with open(path, "a"):
        os.utime(path)


class FSObject(object):
    def __init__(self, name, contents=None):
        self.name = name
        self.contents = list(contents or [])


class File(FSObject):
    def make(self, path, config, dry_run=False):
        path = os.path.join(path, self.name)
        logger.info("Creating file [%s]", path)
        if not dry_run:
            touch(path)


class Directory(FSObject):
    def make(self, path, config, dry_run=False):
        path = os.path.join(path, self.name)
        logger.info("Creating directory [%s]", path)
        if not dry_run:
            mkdirp(path)

        for item in self.contents:
            item.make(path, config, dry_run)


class TemplateFile(File):
    def __init__(self, name, template=""):
        super(TemplateFile, self).__init__(name)
        self.template = template


    def make(self, path, config, dry_run=False):
        path = os.path.join(path, self.name)
        text = self.template.format(**config)
        logger.info("Creating template file [%r]", path)
        logger.debug("Writing [%s]:\n%s", path, text)
        if not dry_run:
            with open(path, "w") as f:
                f.write(text)


class ShellCommand(object):
    def __init__(self, cmdline):
        self.cmdline = cmdline


    def format_cmdline(self, config):
        return [cmd.format(**config) for cmd in self.cmdline]
        

    def make(self, path, config, dry_run=False):
        cmdline = self.format_cmdline(config)
        logger.info("Running \"%s\" in [%s]", " ".join(cmdline), path)
        if not dry_run:
            check_call(self.format_cmdline(config), cwd=path)


    @staticmethod
    def sort_key(key):
        if key and key[0].isdigit():
            return int(key[0])

        return 0
        


class Project(object):
    def __init__(self, name, template_path):
        self.name = name
        self.template_path = template_path


    def get_root_template(self):
        path = os.path.join(self.template_path, ROOT_TEMPLATE_NAME)
        with open(path, "rb") as f:
            return json.load(f)


    def get_template(self, name):
        path = os.path.join(self.template_path, "{}.template".format(name))
        with open(path) as f:
            return f.read()


    def init(self, config, dry_run=False):
        root = Directory(
            self.name, 
            self.parse_template(self.get_root_template(), config)
            )

        root.make(config["root"], config, dry_run)


    def parse_template(self, template, config):
        shell_commands = {}
        for key, value in template.items():
            key = key.format(**config)
            if isinstance(value, dict):
                # We're creating a folder
                yield Directory(key, self.parse_template(value, config))
            elif key.startswith("!"):
                # It's a shell command
                shell_commands[key[1:]] = (ShellCommand(value))
            elif not value:
                # It's a blank file
                yield File(key)
            else:
                # It's a file from a template
                yield TemplateFile(key, self.get_template(value))

        for key in sorted(shell_commands, key=ShellCommand.sort_key):
            yield shell_commands[key]


def get_available_templates(template_dir):
    mkdirp(template_dir)
    return os.listdir(template_dir)


def get_parser(config):
    import argparse
    parser = argparse.ArgumentParser(epilog=DOC)
    parser.add_argument("-q", "--quiet", action="store_const",
                        dest="log_level", const=logging.WARNING,
                        default=logging.INFO, help="Suppress (most) logging")
    parser.add_argument("--debug", action="store_const", dest="log_level",
                        const=logging.DEBUG, help="Turn on debug messages")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Don't actually do anything")
    parser.add_argument("-j", "--json", action="append",
                        help="Specify additional configuration files")
    parser.add_argument("-r", "--root", default=os.getcwd(),
                        help="Specify a root directory for the project")
    parser.add_argument("template", 
                        choices=get_available_templates(config["template_dir"]),
                        help="Template to use")
    parser.add_argument("name", help="Name of project to create")
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
