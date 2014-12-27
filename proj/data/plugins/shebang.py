from proj import ProjPlugin

DEFAULT_ENV_PATH = "/usr/bin/env"

class Shebang(object):
    def __init__(self, env_path):
        self.env_path = DEFAULT_ENV_PATH
    
    def __getattr__(self, attr):
        return "{} {}".format(self.env_path, attr)

class ShebangPlugin(ProjPlugin):
    def on_create_config(self, config):
        config["shebang"] = Shebang(
            config.get("env_path", DEFAULT_ENV_PATH)
        )
