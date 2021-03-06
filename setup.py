#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
from iotapp import version

file_name = os.path.join('requirements', 'common.txt')
with open(file_name, 'r') as r:
    requirements = [l for l in r.read().splitlines()]

setup(
    name='iotapp',
    version=version,
    description='Iot Applications',

    author='Massimiliano Ravelli',
    author_email='massimiliano.ravelli@gmail.com',
    url='http://github.com/madron/iotapp',

    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: System :: Automation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='iot mqtt',

    packages=find_packages(),
    install_requires=requirements,
    entry_points = dict(
        console_scripts=['iotapp=iotapp.__main__:main'],
    )
)
