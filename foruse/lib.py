# -*- coding: utf-8 -*- 

import string
import random
import sys
import os
import re
import shutil
import distutils.dir_util
import distutils.file_util

# -----------------------------------------------------------------------------
# Функции для работы с файловой системой
# -----------------------------------------------------------------------------

# Функция возвращает текущую папку
def get_current_dir():
	return os.getcwd()

# Функция возвращает текущую папку
def get_current_dirrectory():
	return os.getcwd()
	
# Функция проверяет есть ли файл или нет
def file_exists(file_name):
	return os.path.exists(file_name) 
	
# Функция проверяет является ли file_name папкой
def is_dir(file_name):
	return os.path.isdir(file_name) 

# Функция проверяет является ли file_name файлом
def is_file(file_name):
	return os.path.isfile(file_name) 
	
def mkdir(dirname):
	if not is_dir(dirname):
		os.makedirs(dirname)
	
def remove_dir(dirname):
	if is_dir(dirname):
		#https://docs.python.org/3.5/distutils/apiref.html#distutils.dir_util.remove_tree
		distutils.dir_util.remove_tree(dirname)
	
def copy_dir(src, dest, *args, **kwargs):
	if is_dir(src):
		#https://docs.python.org/3.5/distutils/apiref.html#distutils.dir_util.copy_tree
		distutils.dir_util.copy_tree(src, dest, *args, **kwargs)
		return True
	return False
	
def copy_file(src, dest, *args, **kwargs):
	if is_file(src):
		#https://docs.python.org/3.5/distutils/apiref.html#distutils.file_util.copy_file
		distutils.file_util.copy_file(src, dest, *args, **kwargs)
		return True
	return False
	
# -----------------------------------------------------------------------------
# Функции для работы со строками
# -----------------------------------------------------------------------------
	
# Добавляем первый слэш у строки
def add_first_slash(s):
	try:
		if s[0] != '/':
			return "/" + s
		return s
	except:
		return ''
		
# Добавляем последний слэш у строки
def add_last_slash(s):
	try:
		if s[-1] != '/':
			return s + "/"
		return s
	except:
		return ''
		
# Удаляем первый слэш у строки
def delete_first_slash(s):
	try:
		if s[0] == '/':
			return s[1:]
		return s
	except:
		return ''
		
# Удаляем последний слэш у строки
def delete_last_slash(s):
	try:
		if s[-1] == '/':
			return s[:-1]
		return s
	except:
		return ''
	
# Функция соединяет пути
def join_paths(*args, **kwargs):
	arr = [""] * (len(args) * 2)
	i = 0
	for p in args:
		if p == "":
			continue
		if p[0] != '/':
			arr[i] = '/'
		arr[i+1] = p
		i = i + 2
	s = "".join(arr)
	s = re.sub('/+','/',s)
	return delete_last_slash(s)
	
# Возвращает пару ключ->значение в зависимости от типа Dict или List
def xitems(arr):
	if type(arr) == list:
		return enumerate(arr)
	if type(arr) == dict:
		return arr.items()
	return []
	
# Возвращает ключи в зависимости от типа Dict или List
def xkeys(arr):
	if type(arr) == list:
		return range(len(arr))
	if type(arr) == dict:
		return arr.keys()
	return []
	
# Возвращает значения в зависимости от типа Dict или List
def xvalues(arr):
	if type(arr) == list:
		return arr
	if type(arr) == dict:
		return arr.values()
	return []


# -----------------------------------------------------------------------------
# Функции var_dump
# -----------------------------------------------------------------------------

def var_dump_output(var, level, space, crl, outSpaceFirst=True, outLastCrl=True):
	res = ''
	if outSpaceFirst: res = res + space * level
	
	typ = type(var)
	
	if typ in [list]:
		res = res + "[" + crl
		for i in var:
			res = res + var_dump_output(i, level + 1, space, crl, True, False) + ',' + crl
		res = res + space * level + "]" 
		
	elif typ in [dict]:
		res = res + "{" + crl 
		for i in var:
			res = res + space * (level+1) + i + ": " + var_dump_output(var[i], level + 1, space, crl, False, False)  + ',' + crl
		res = res + space * level  + "}"
	
	elif typ in [str]:
		res = res + "'"+str(var)+"'"
	
	elif typ in [None]:
		res = res + "None"
	
	elif typ in (int, float, bool):
		res = res + typ.__name__ + "("+str(var)+")"
		
	elif isinstance(typ, object):
		res = res + typ.__name__ + "("+str(var)+")"
		
	if outLastCrl == True:
		res = res + crl
		
	return res
	
def var_dump(*obs):
	"""
	  shows structured information of a object, list, tuple etc
	"""
	i = 0
	for x in obs:
		
		str = var_dump_output(x, 0, '  ', '\n', True)
		print (str.strip())
		
		#dump(x, 0, i, '', object)
		i += 1

def gen_random_string(size=6, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


# from http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="yes"):
	"""Ask a yes/no question via input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is True for "yes" or False for "no".
	"""
	valid = {"yes": True, "y": True, "ye": True,
			 "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' "
							 "(or 'y' or 'n').\n")