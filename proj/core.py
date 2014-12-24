import json
import logging
import os
from subprocess import check_call, CalledProcessError
from .util import mkdirp, touch

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


