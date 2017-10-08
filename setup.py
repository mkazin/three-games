# -*- coding: utf-8 -*-

# Based on: https://github.com/kennethreitz/setup.py
# TODO: fully implement https://github.com/kennethreitz/setup.py/blob/master/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sample',
    version='0.1.0',
    description='Steam game exploration library',
    long_description=readme,
    author='Michael J. Kazin',
    author_email='mkazin@gmail.com',
    url='https://github.com/mkazin/three-games',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
