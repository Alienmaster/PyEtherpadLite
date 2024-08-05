#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='pyetherpadlite',
    version='1.2',
    description='Python bindings for Etherpad\'s HTTP API. (https://github.com/ether/etherpad-lite)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="Apache Software License 2.0",
    author='alienmaster, devjones',
    author_email='github@crpykng.de',
    url='https://github.com/Alienmaster/PyEtherpadLite',
    project_urls={
        'Bug Tracker': 'https://github.com/Alienmaster/PyEtherpadLite/issues',
        'Source Code': 'https://github.com/Alienmaster/PyEtherpadLite',
    },
    packages=find_packages('src'),
    package_dir={'': 'src'},
    options={'bdist_wheel': {'universal': True}},
    zip_safe=True,  # This package can safely be installed from a zip file
    platforms='any',
)
