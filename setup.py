#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="Proj",
    version="0.1.dev1",
    description="Project Creation Tool",
    author="Joel Cornett",
    author_email="joel.cornett@gmail.com",
    url="https://github.com/jncornett/proj",
    packages=find_packages(),
    entry_points={"console_scripts": ["proj = proj.script:main"]},
    package_data={"proj": ["data/templates"]},
)
