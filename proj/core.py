import logging
import os
from abc import ABCMeta, abstractmethod, abstractproperty
from subprocess import check_call

from .util import touch, mkdirp

logger = logging.getLogger(__name__)

# ## Base Components
# ### Node
# The most basic project component
class Node(object):

    __metaclass__ = ABCMeta
    log_info_string = ""

    def __init__(self, **config):
        self.config = config or {}
        self.data = {}


    def __getattr__(self, attr):
        return self.config.get(attr, None)


    def _to_path(self, *keys):
        components = (self.data[key] 
                      for key in keys if key in self.data)

        return os.path.join(*components)


    def _log_messages(self):
        if self.logger:
            for level, fn in ((logging.INFO, "log_info"), 
                              (logging.DEBUG, "log_debug")):
                if self.logger.isEnabledFor(level):
                    args = getattr(self, fn)()
                    if args:
                        self.logger.log(level, *args)


    def make(self, dry_run=False, **data):
        self.data = dict(data, **self.data)
        self._log_messages()
        if not dry_run:
            self.render()


    @property
    def root_path(self):
        return self._to_path("root")


    @property
    def module_path(self):
        return self._to_path("root", "module")


    @property
    def file_path(self):
        return self._to_path("root", "module", "name")


    def log_info(self):
        return self.log_info_string, self.data


    def log_debug(self):
        pass


    @abstractmethod
    def render(self, data):
        pass


# ### Branch
# A project component with children
class Branch(Node):
    def __init__(self, contents=None, **config):
        super(Branch, self).__init__(**config)
        self.contents = list(contents) if contents else []


    def make(self, dry_run=False, **kwargs):
        super(Branch, self).make(dry_run=dry_run, **kwargs)
        _data = dict(
            self.data,
            module=self._to_path("module", "name")
            )

        for node in self.contents:
            node.make(dry_run=dry_run, **_data)


# ## Additional components
class File(Node):

    log_info_string = "Creating file: %(module)s/%(name)s"

    def __init__(self, name, **config):
        super(File, self).__init__(**config)
        self.data["name"] = name


    def render(self):
        touch(self.file_path)


class Directory(Branch):

    log_info_string = "Creating directory: %(module)s/%(name)s"
    
    def __init__(self, name, contents=None, **config):
        super(Directory, self).__init__(
            contents=contents, 
            **config
            )

        self.data["name"] = name


    def render(self):
        mkdirp(self.file_path)


class Template(File):
    
    log_info_string = "Rendering template: %(module)s/%(name)s"

    def __init__(self, name, template="", **config):
        super(Template, self).__init__(name, **config)
        self.template = template


    def render(self):
        with open(self.file_path, "w") as f:
            f.write(self.template.format(**self.data))


class ShellCommand(Node):

    log_info_string = "Running shell: %(cmd)s"

    def __init__(self, cmd, **config):
        super(ShellCommand, self).__init__(**config)
        self.data["cmd"] = cmd


    def _format_cmd(self):
        return [arg.format(**self.data) for arg in self.data["cmd"]]


    def render(self):
        check_call(self._format_cmd(), cwd=self.module_path)
