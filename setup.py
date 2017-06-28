#! /usr/bin/env python

from setuptools import setup

setup(name="redshirt",
      version="0.1.0a2",
      scripts=['redshirt.py'],
      author="Jack Laxson",
      author_email="jack@getpizza.cat",
      description="A HTTP management api for taskwarrior's taskd",
      keywords=["taskd", "taskwarrior", "api", "management"],
      license="GPL v3",
      zip_safe=False,
      install_requires=["bottle", "baker==1.3", "psutil", "packaging", "requests"],
      url="https://github.com/jrabbit/taskd-redshirt",
      classifiers=["Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
                   "Topic :: System :: Monitoring",
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.5",
                   ])
