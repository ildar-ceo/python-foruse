# -*- coding: utf-8 -*- 

import string
import random
import sys
import os
import copy
import re
import shutil
import distutils.dir_util
import distutils.file_util
from urllib.parse import urlsplit

def is_exists(a):
	return a != None and a != "" and a != 0 and a != False

# -----------------------------------------------------------------------------
# Функции для работы с массивами
# -----------------------------------------------------------------------------

def clone(var):
	t = type(var)
	if (t is list or t is dict):
		return copy.deepcopy(var)
	return var


# Получить значение из массива или списка по его ключам
def xarr(arr, *args, default=None):
	res=arr
	for key in args:
		try:
			res=res[key]
		except:
			res=default
			break
	
	if res is None:
		res=default
	
	return res


# Получить значение из массива или списка по его ключам и сделаем копию
def xclone(arr, *args, **kwargs):	
	return clone(xarr(arr, *args, **kwargs))

	
# Добавить значение	в список по ключам
def xadd(arr, *args, value=None):
	size = len(args)
	res = arr
	for index, key in xitems(args):
		if index == size - 1:
			res[key] = value
		else:
			try:
				res=res[key]
			except:
				res[key] = {}
				res = res[key]
		#!endif
	#!endfor	
	
	
# Возвращает пару ключ->значение в зависимости от типа Dict или List
def xitems(arr):
	t = type(arr)
	if t is list or t is tuple:
		return enumerate(arr)
	elif t is dict:
		return arr.items()
	return []
	
# Возвращает ключи в зависимости от типа Dict или List
def xkeys(arr):
	t = type(arr)
	if t is list or t is tuple:
		return range(len(arr))
	elif type(arr) is dict:
		return arr.keys()
	return []
	
# Возвращает значения в зависимости от типа Dict или List
def xvalues(arr):
	t = type(arr)
	if t is list or t is tuple:
		return arr
	elif t is dict:
		return arr.values()
	return []

# -----------------------------------------------------------------------------
# Функции для преобразования типов
# -----------------------------------------------------------------------------

def xint(val, default=0):
	try:
		val = int(val)
	except:
		try:
			val = int(default)
		except:
			val = 0
	
	return val

def xbool(val, default=None):
	t = type(val)
	if t is bool:
		return val
	
	if t is str:
		val = val.lower()
		if val == 'false' or val == '0':
			return False
		
		if val == 'true' or val == '1':
			return True
		
		if val.isdigit():
			return True
		
	if t is int:
		if val == 0:
			return False
		
		return True
	
	return default
	
def to_str(b, encoding="utf-8", errors="strict"):
	if type(b) is byte:
		return b.decode(encoding=encoding, errors=errors)
	return ""
	
def to_byte(s, encoding="utf-8", errors="strict"):
	if type(s) is str:
		return s.encode(encoding=encoding, errors=errors)
	return b""
	
# -----------------------------------------------------------------------------
# Функции для работы с файловой системой
# -----------------------------------------------------------------------------

# Функция возвращает имя файла или папки
def getfilename(name):
	try:
		arr = basename(name).split('.')
		return arr[0]
	except:
		return ""

# Функция возвращает имя файла или папки
def getfileext(name):
	try:
		arr = basename(name).split('.')
		return arr[1]
	except:
		return ""
	
# Функция возвращает имя вместе с расширением файла или папки
def basename(filename):
	return os.path.basename(filename)

# Функция возвращает путь файла или папки
def dirname(filename):
	return os.path.dirname(filename)

# Функция возвращает текущую папку
def get_current_dir():
	return os.getcwd()

# Функция возвращает текущую папку
def get_current_dirrectory():
	return os.getcwd()
	
# Функция проверяет есть ли файл или нет
def file_exists(file_name):
	return os.path.exists(file_name) 

# Функция проверяет существует ли папка file_name
def dir_exists(file_name):
	return os.path.isdir(file_name) 
	
# Функция проверяет является ли file_name папкой
def is_dir(file_name):
	return os.path.isdir(file_name) 

# Функция проверяет является ли file_name файлом
def is_file(file_name):
	return os.path.isfile(file_name) 
	
def mkdir(dirname):
	if not is_dir(dirname):
		os.makedirs(dirname)

def unlink(filename):
	os.remove(filename)
		
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
	

# -----------------------------------------------------------------------------
# Улучшенная реализация функции urlparse2
# -----------------------------------------------------------------------------
	
class UrlSplitResult:
	def __init__(self, *args, **kwargs):
		self.scheme = xarr(args, 0)
		self.netloc = xarr(args, 1)
		self.path = xarr(args, 2)
		self.query = xarr(args, 3)
		self.fragment = xarr(args, 4)
		self.hostname = None
		self.port = None
		self.username = None
		self.password = None
	#!enddef __init__
	
	def init(self):
		netloc = self.netloc
		netloc = netloc.split(':')
		if len(netloc) >= 3:
			self.hostname = netloc[1]
			self.port = netloc[2]
			arr = netloc[0].split('@')
			self.username = xarr(arr, 0, default=None)
			self.password = xarr(arr, 1, default=None)
		else:
			self.hostname = xarr(netloc, 0, default=None)
			self.port = xarr(netloc, 1, default=None)
	
	def __str__(self):
		res = ""
		
		netloc = None
		if is_exists(self.hostname):
			user_password = None
			if is_exists(self.username):
				user_password = str(self.username) + "@" + str(self.password)
			
			netloc = self.hostname
			if is_exists(self.port):
				netloc = netloc + ":" + str(self.port)
			
			if is_exists(user_password):
				netloc = str(user_password) + ":" + str(netloc)
			
			res = str(netloc)
		
		if is_exists(self.scheme):
			res = str(self.scheme) + "://" + str(res)
		
		if is_exists(self.path):
			res = res + str(self.path)
		
		if is_exists(self.query):
			res = res + '?' + str(self.query)
		
		if is_exists(self.fragment):
			res = res + '#' + str(self.fragment)
		
		return res
	#!enddef __str__
	
#!endclass UrlSplitResult


def urlparse2(path, *args, **kwargs):
	res = urlsplit(path, *args, **kwargs)
	url = UrlSplitResult(*res)
	url.init()
	return url
	
	
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