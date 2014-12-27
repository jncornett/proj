from proj import ProjApi, ShellCommand

COMMANDS = [
    ["git", "init"],
    ["git", "add", "-A"],
    ["git", "commit", "initial commit"]
    ]

class GitSetupApi(ProjApi):
    method_name = "git-setup"
    
    def call(self, config, *args, **kwargs):
        for cmd in COMMANDS:
            yield ShellCommand(cmd)
