proj
====

Project Initialization made easy

Synopsis
--------

    /home/joel/devel $ proj.py --verbose python-package foo
    Created directory /home/joel/devel/foo
    Created directory ./foo
    Touched file ./foo/__init__.py
    Created directory ./tests
    Created file from template ./foo/test_foo.py
    
    ./foo/test_foo.py
    =================
    > from unittest import TestCase
    > import foo
    > 
    > class TestFoo(TestCase):
    >     def test_main(self):
    >         pass
    
    Created file from template ./setup.py
    
    ./setup.py
    ==========
    > from setuptools import setup, find_packages
    > setup(
    >     name="foo",
    >     version="0.1.dev1",
    >     author="Joel Cornett",
    >     author_email="joel.cornett@example.com",
    >     packages=find_packages(),
    >     )
    
    Created file from template ./.gitignore
    
    ./.gitignore
    ============
    > *.pyc
    > *.egg-info/
    > __pycache__/
    
    Ran shell command "git init" at ./
    Ran shell command "git add -A" at ./
    Ran shell command "git commit -m \"initial commit\"" at ./
    
Details
-------

`proj.py` read project template information from a folder titled `python-package`. The folder's contents are:

- `python-package`
  - `root.json`: main project template file
  - `setup.py.template`: template for setup.py
  - `test.py.template`: template for test script
  - `gitignore.template`: template for gitignore
  
`python-package/root.json` reads like this:

    {
      "{name}": {
        "__init__.py": ""
        },
      "tests": {
        "test_{name}.py": "test.py.template",
        },
      "setup.py": "setup.py.template",
      ".gitignore": "gitignore.template",
      "!": [
        ["git", "init"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", "initial commit for {name}"]
      ]
    }
    
  More to come...
