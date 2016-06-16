# -*- coding: utf-8 -*-
"""
Инструкции:

python setup.py sdist - Сборка пакета
sudo python setup.py develop - Установка пакета для разработки
sudo pip install foruse - Установка пакета
sudo pip uninstall foruse - Удаление пакета
python setup.py register - Зарегистрировать пакет в pypi
python setup.py sdist upload - Залить на сервер

Классификация https://pypi.python.org/pypi?%3Aaction=list_classifiers
"""

from setuptools import setup, find_packages
from os.path import join, dirname

PACKAGE = "foruse"
NAME = "foruse"
DESCRIPTION = "Library foruse on python"
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
	#platform = ["Any"],
	download_url = "https://github.com/vistoyn/python-foruse/releases/download/"+VERSION+"/foruse-"+VERSION+".tar.gz",
	packages=find_packages(),
	include_package_data = True,
	install_requires=[
		'python-dateutil',
	],
	keywords = [
		"foruse", "python foruse", "bayrell", "python library"
	],
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
	],
)