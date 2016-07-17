#! /usr/bin/env python

from setuptools import setup
from redshirt import  __version__

setup(name="redshirt",
      version=__version__,
      scripts=['redshirt.py'],
      author="Jack Laxson",
      author_email="jack@getpizza.cat",
      description="A HTTP management api for taskwarrior's taskd",
      license="GPL v3",
      install_requires=["bottle", "baker==1.3",],
      url="https://github.com/jrabbit/taskd-redshirt",
      classifiers=[])
