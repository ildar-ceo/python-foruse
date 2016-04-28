#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""
Инструкции:

python setup.py sdist - Сборка пакета
python setup.py develop - Установка пакета для разработки
pip install dist/foruse-0.1.zip - Установка пакета
pip uninstall foruse - Удаление пакета
"""

from setuptools import setup, find_packages
from os.path import join, dirname

PACKAGE = "foruse"
NAME = "foruse"
DESCRIPTION = "Library For use on python"
URL = "https://github.com/vistoyn/python-foruse"
AUTHOR = __import__(PACKAGE).__author__
AUTHOR_EMAIL = __import__(PACKAGE).__email__
VERSION = __import__(PACKAGE).__version__

setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=open(join(dirname(__file__), 'README.md')).read(),
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	license='MIT License',
	url = URL,
	packages=find_packages(),
	include_package_data = True,
	install_requires=[
	],
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.5',
	],
)