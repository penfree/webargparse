#!/usr/bin/env python
# coding=utf8
"""
# Author: penfree
# Created Time : 03 Mar 2022 07:23:45 PM CST

# File Name: setup.py
# Description:

"""
from setuptools import setup, find_packages
import os

if os.path.exists('requirements.txt'):
    requirements = [x.strip() for x in open("requirements.txt").readlines()]
else:
    requirements = []

version = "0.1"

# Create build meta
setup(
    name="webargparse",
    version=version,
    author="penfree",
    url="https://github.com/penfree/webargparse",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    description="",
    long_description=open("README.md").read(),
)
