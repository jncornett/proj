proj
====

Project initialization made easy. Language/framework agnostic.

Synopsis
--------

To initialize a new project in the current working directory:

    ~/devel $ proj.py my-chrome-foo chrome-ext-popup << EOF
    heredoc> {
    heredoc>    "description": "A foo extension",
    heredoc>    "author_email": "me@example.com"
    heredoc> }
    heredoc> EOF
    Created project from 'chrome-ext-popup' at ~/devel/my-chrome-foo

To see what's going on under the hood, do:

    ~/devel $ proj.py --verbose my-chrome-foo chrome-ext-popup < settings.json
    Created directory ~/devel/my-chrome-foo
    Created file my-chrome-foo/manifest.json from template 'manifest.html.template'
    Created file my-chrome-foo/popup.html from template 'popup.html.template'
    Created file my-chrome-foo/popup.js from template 'popup.js.template'
    Executed command 'git init' in my-chrome-foo
    Executed command 'git add -A' in my-chrome-foo
    Executed command 'git commit -m "initial commit"' in my-chrome-foo
    Created project from 'chrome-ext-popup' at ~/devel/my-chrome-foo

Project templates (the working term for these is "structures" to differentiate them from file templates)
are folders placed in `~/.proj/templates` which contain a `proj.json` file at a minimum.
Here's what the `chrome-ext-popup` JSON file looks like:

    [
        {
            "manifest.json": "@manifest.json.template",
            "popup.html": "@popup.html.template",
            "popup.js": "console.log('popup script loaded');",
        },
        {
            "git-init": "!git init",
            "git-add": "!git add -A",
            "git-commit": "!git commit -m {commit_message}"
        }
    ]
    
Here's what `popup.html.template` looks like:
    
    <!--Created by {author_name} <{author_email}>-->
    <!--Description: {description}-->
    <html>
        <head>
            <title>{name}</title>
            <script src="popup.js"></script>
        </head>
        <body>
            <h1>Hello, Foo</h1>
        </body>
    </html>

Plugins
-------
__proj__ comes with a lightweight plugin framework. To create a custom plugin (say for creating a jade template),
simply drop a python script with a subclass of `proj.Plugin` in `~/.proj/plugins`.
Here's what the jade templating plugin might look like:

    import json
    from subprocess import call
    from proj.core import Template
    from proj.plugin import Plugin
    
    class JadeTemplate(Template):
        def render(self):
            call([
                "jade", 
                "-o", self.file_path, 
                "-O", json.dumps(self.data)
                self.template
            ])

    class JadeTemplatePlugin(Plugin):
        def on_parse_structure(self, maker, key, value):
            try:
                if value[0] == "@":
                    template_file = value[1:]
                    if template_file.rsplit(".", 1)[-1] == "jade":
                        return JadeTemplate, (key,), {
                            "template": maker._get_template(template_file)
                            }
            except (AttributeError, IndexError):
                pass

More to come...

TODO
----
- Write console script (`proj/script.py`)
- Write example plugins for each hook
- Logging for all modules in package
- Documentation for all modules in package
- Complete unit tests
