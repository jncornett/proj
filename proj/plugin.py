from abc import ABCMeta, abstractmethod, abstractproperty
from os import walk

# ### General Usage 
# - In (a/the) plugins directory, create a python script:
#   - import and subclass plugin.Plugin
#   - Voila! That plugin will automatically be imported
# 
#  Basic Plugin:
#
#       from plugin import Plugin
#       class FooPlugin(Plugin):
#           def initialize(self, config, data):
#               print("Initializing")
#
#
#           def finish(self, config, data):
#               print("Cleaning up")
#
#
#           def register(self, manager):
#               pass
#
# That's it! 

HOOKS = {}

class Plugin(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def register(self, manager):
        pass


class ApiPlugin(Plugin):
    pass


class TemplatePlugin(Plugin):

    def initialize(self):
        class TemplateClass(Template):
            pass


    def register(self, manager):
        pass


class PluginManager(object):
    def __init__(self, project):
        pass


    def _find_plugins(self, path):
        pass
    

    def register_plugins(self, path):
        pass


    def initialize(self, **config):
        pass


    def finish(self, **config):
        pass
