import logging
import os
import shlex
from abc import ABCMeta, abstractmethod
from itertools import chain
from subprocess import check_call

from .util import touch, mkdirp

logger = logging.getLogger(__name__)

HOOKS = {
    "augment_data",
    "parse_structure"
    }

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

    def __init__(self, name, text=None, **config):
        super(File, self).__init__(**config)
        self.text = text
        self.name = self.data["name"] = name


    def __repr__(self):
        return "{}({!r}, text={!r})".format(
            self.__class__.__name__,
            self.name,
            self.text
            )


    def render(self):
        touch(self.file_path, self.text)


class Directory(Branch):

    log_info_string = "Creating directory: %(module)s/%(name)s"
    
    def __init__(self, name, contents=None, **config):
        super(Directory, self).__init__(
            contents=contents, 
            **config
            )

        self.name = self.data["name"] = name


    def __repr__(self):
        return "{}({!r}, contents={!r})".format(
            self.__class__.__name__,
            self.name,
            self.contents
            )


    def render(self):
        mkdirp(self.file_path)


class Template(File):
    
    log_info_string = "Rendering template: %(module)s/%(name)s"

    def __init__(self, name, template="", **config):
        super(Template, self).__init__(name, **config)
        self.template = template


    def __repr__(self):
        return "{}({!r}, template={!r})".format(
            self.__class__.__name__,
            self.name,
            self.template
            )


    def render(self):
        with open(self.file_path, "w") as f:
            f.write(self.template.format(**self.data))


class ShellCommand(Node):

    log_info_string = "Running shell: %(cmd)s"

    def __init__(self, cmd, **config):
        super(ShellCommand, self).__init__(**config)
        self.cmd = self.data["cmd"] = cmd


    def __repr__(self):
        return "{}({!r})".format(
            self.__class__.__name__,
            self.cmd
            )


    def _format_cmd(self):
        return [arg.format(**self.data) for arg in self.data["cmd"]]


    def render(self):
        check_call(self._format_cmd(), cwd=self.module_path)


class Maker(object):
    # TODO: Add logger to Maker
    def __init__(self, name, structure, templates, **config):
        self.data = config.pop("data", {})
        self.hooks = config.pop("plugin_manager", None)
        parentLogger = config.pop("logger", logging)
        self.logger = parentLogger.getChild(self.__class__.__name__)
        self.template_path = templates
        self.config = config
        self.root = Directory(name, contents=self._build(structure))

    
    def _get_template(self, name):
        self.logger.debug("Fetching template for %r", name)
        template_filename = os.path.abspath(os.path.join(self.template_path, name))
        with open(template_filename) as f:
            return f.read()


    def _build(self, structure):
        self.logger.debug("Parsing structure %s", structure)
        if hasattr(structure, "items"):
            for key, value in structure.items():
                rv = self.hooks.trigger("parse_structure", key, value)
                if rv:
                    cls, args, kwargs = rv
                else:
                    cls, args, kwargs = File, (key,), {}
                    if value is not None:
                        if isinstance(value, (unicode, str)):
                            if value.startswith("@"):
                                cls = Template
                                args += (self._get_template(value[1:]),)
                            elif value.startswith("!"):
                                cls = ShellCommand
                                args = (shlex.split(value[1:]),)
                            else:
                                kwargs = {"text": value}
                        else:
                            cls = Directory
                            kwargs = {"contents": self._build(value)}
                
                yield cls(*args, **dict(self.config, **kwargs))
        else:
            for node in chain.from_iterable(map(self._build, structure)):
                yield node
            

    def make(self, dry_run=False, **data):
        data = dict(self.data, **data)
        self.hooks.trigger("augment_data", data, self.config)
        self.root.make(dry_run=dry_run, **data)
