#!/usr/bin/env python
from setuptools import setup

setup(
    name="Proj",
    version="0.1.dev1",
    description="Project Creation Tool",
    author="Joel Cornett",
    author_email="joel.cornett@gmail.com",
    url="https://github.com/jncornett/proj",
    install_requires=["pyaml", "gitpython"],
    entry_points={"console_scripts": ["proj = proj:main"]},
    package_data={"proj": ["templates"]},
    py_modules=["proj"]
)
