import imp
import logging
import os
from itertools import chain

dbg = logging.getLogger("debug")

class PluginManager(object):

    HOOKS = set() # A set of hook names to register

    def __init__(self, app, plugin_paths, 
                 debug=False, logger=None):

        if logger is None:
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = logger.getChild(self.__class__.__name__)

        self.app = app
        self.debug = debug # Determine whether to fail on error
        self.modules = list(self._load_plugins(plugin_paths))
        self.plugins = list(self._init_plugins())
        self.hooks = self._register_hooks()
    

    def _init_plugins(self):
        for module in self.modules:
            plugin_classes = []
            for obj_name in dir(module):
                obj = getattr(module, obj_name)
                try:
                    if issubclass(obj, Plugin):
                        plugin_classes.append(obj)
                except TypeError:
                    pass

            for cls in plugin_classes:
                try:
                    yield cls(self.app)
                except Exception as e:
                    self._log_plugin_exception(e, **{"class": cls})
                    if self.debug:
                        raise


    def _register_hooks(self):
        for plugin in self.plugins:
            for key in plugin.hooks:
                if key in self.HOOKS:
                    self.hooks.setdefault(key, []).append(plugin.hooks[key])


    def _get_modules(self, path):
        for entry in os.listdir(path):
            base, ext = os.path.splitext(entry)
            if not ext or ext == ".py":
                mod_info = (_, _, mod_file, _) = imp.find_module(base, path)
                if mod_info:
                    try:
                        yield imp.load_module(base, *mod_info)
                    except Exception as e:
                        self._log_plugin_exception(e, module_info=mod_info)
                        if self.debug:
                            raise
                    finally:
                        mod_file.close()


    def _load_plugins(self, plugin_paths):
         return chain(
            *(self._get_modules(path) 
                for path in plugin_paths)
            )


    def _log_plugin_exception(self, e, **kwargs):
        self.logger.error("Exception: %s, Kwargs: %s", e, kwargs)


    def trigger(self, hook, *args, **kwargs):
        hook_fns = self.hooks[hook]
        rv = None
        for fn in hook_fns:
            try:
                rv = fn(self.app, rv, *args, **kwargs)
            except Exception as e:
                self._log_plugin_exception(e, hook=hook, fn=fn)
                if self.debug:
                    raise

        return rv


class Plugin(object):

    hooks = {}

    def __init__(self, app):
        self.app = app


    @classmethod
    def hook(cls, hook_name):
        def inner(fn):
            cls.hooks.setdefault(hook_name, []).append(fn.__name__)
            return fn

        return inner



