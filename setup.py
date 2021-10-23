#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
 
setup(
    name='pyetherpadlite',
    version='1.0',
    description='Python bindings for Etherpad\'s HTTP API. (https://github.com/ether/etherpad-lite)',
    author='alienmaster, devjones',
    url='https://github.com/Alienmaster/PyEtherpadLite',
    packages=find_packages('src'),
    package_dir={'': 'src'},
)

