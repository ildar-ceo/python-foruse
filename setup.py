#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""
Инструкции:

python3 setup.py sdist - Сборка пакета
sudo python3 setup.py develop - Установка пакета для разработки
sudo pip3 install dist/foruse-0.2.zip - Установка пакета
sudo pip3 uninstall foruse - Удаление пакета
python3 setup.py register - Зарегистрировать пакет в pypi
python3 setup.py sdist upload - Залить на сервер
"""

from setuptools import setup, find_packages
from os.path import join, dirname

PACKAGE = "foruse"
NAME = "foruse"
DESCRIPTION = "Library For use on python"
URL = "https://github.com/vistoyn/python-foruse"
LICENSE = 'MIT License'
AUTHOR = __import__(PACKAGE).__author__
AUTHOR_EMAIL = __import__(PACKAGE).__email__
VERSION = __import__(PACKAGE).__version__

setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=open(join(dirname(__file__), 'DESCRIPTION.rst')).read(),
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	license=LICENSE,
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