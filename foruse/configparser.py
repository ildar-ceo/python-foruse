# -*- coding: utf-8 -*- 

import re
import json
from . import log
from .error import *
from .lib import *

IS_PYTHON2 = sys.version_info < (3,0)
if IS_PYTHON2:
	from urlparse import urlsplit
else:
	from urllib.parse import urlsplit

class ConfigParser(log.Log):
	
	def __init__(self, *args, **kwargs):
		log.Log.__init__(self, *args, **kwargs)
		
		self._config_type = kwargs.get('_config_type', 'ini')
		self._config_path = ""
		
		self._init = {}
		self._original = None
		self._settings = None
		
	#!enddef __init__
	
	def set_init(self, init):
		self._init = init

	def get_settings(self):
		return self._settings
	
	
	@classmethod
	def read_ini(self, config_path, init={}):
		
		# Читает построчно файл и возравщает частично проанализированные строки
		def read_file(config_path):
			
			settings = {}
			
			def add_settings(settings, section, key, val):
				if section is None or key is None or val is None:	
					return
				
				if settings.get(section) is None:
					settings[section] = {}
				
				section = section.strip()
				key = key.strip()
				val = val.strip('\r\n')
				
				if len(section) == 0:
					return
				if len(key) == 0:
					return
				
				try:
					j = json.loads(val)
					val = j
				except:
					pass
				
				#print ("[%s] %s=%s" % (section, key, val))
				settings[section][key] = val
			#!enddef add_settings
			
			try:
				if file_exists(config_path):
					with open(config_path) as f:
						
						section = None
						key = None
						val = None
						
						for line in f:
							#line = line.strip('\r\n')
							
							if len(line) == 0:
								continue
							if line[0] == '#':
								add_settings(settings, section, key, val)
								key = None
								val = None
								continue
							
							if line[0] in ['\t', '\s']:
								if val is not None:
									val += line 
								continue
							
							if line[0] == '[':
								add_settings(settings, section, key, val)
								
								line = line.strip('\r\n')
								line = line[1:]
								if line[len(line) - 1] == ']':
									line = line[:-1]
								
								line = line.strip()
								if len(line) == 0:
									continue
								
								section = line
								key = None
								val = None
								continue
							
							add_settings(settings, section, key, val)
							key = None
							val = None
							
							arr = line.split('=', 1)
							if len(arr) > 1:
								key = arr[0]
								val = arr[1]
								
							pass
						#!endfor 
						
						add_settings(settings, section, key, val)
						f.close()
					#!endwith
				#!endif
			except:
				print (get_traceback())
				pass
			
			return settings
		
		#!enddef read
		
		original = init
		
		# Читаем конфиг построчно
		data = read_file(config_path)
		
		# Анализируем полученные данные
		for key, value in xitems(data):
			section = original
			arr = key.split(':')
			f = True
			sz0 = len(arr)-1
			for i, key in xitems(arr):
				key = str(key).strip()
				if len(key) == 0:
					f = False
					break
				
				if i < sz0:
					res = section.get(key)
					if res is None or not (type(res) is dict):
						section[key] = {}
					section = section[key]
				else:
					# Последний элемент
					section[key] = value
			#!endfor
			
			if f == False:
				continue
			
			#section = value
		#!endfor
		
		return original
	#!enddef read ini file
	
	
	# Рекурсивно форматируем все строки
	def _format_all(self, arr):
		for key in xkeys(arr):
			val = arr[key]
			t = type(val)
			if (t is dict) or (t is list):
				self._format_all(arr[key])
			
			if t is str:
				arr[key] = self.format(val)
			
			elif IS_PYTHON2:
				if t is unicode:
					arr[key] = self.format(val)
					
		#!endfor
	#!enddef _format_all
	
	
	# Форматируем строку на основе self._settings
	def format(self, val):
		
		# если на входе строка вида %str1%/%str2%/%str3:str4%
		# то в res будет ['str1', 'str2', 'str3:str4']
		res = re.findall(r"%([^%]+)%", val)
		
		for name in res:
			arr = name.split(':')
			
			if len(arr) == 0:
				continue
			
			s = ""
			try:
				s = self._settings
				for i, key in xitems(arr):
					s = s[key]
			except:
				s = ""
			
			s = str(s)
			
			val = val.replace('%'+name+'%', s)
		#!endfor
			
		return val
	#!enddef format
	
	
	def read(self, config_path):
		
		if self._config_type == 'ini':
			self._config_path = config_path
			self._original = ConfigParser.read_ini(config_path, init=self._init)
			
		self._settings = clone(self._original)
		self._format_all(self._settings)
	#!enddef read
	
	
	"""
	def __init__(self, *args, **kwargs):
		Parser.__init__(self, *args, **kwargs)
		self.format_params={}
	
	def add_format(self, key, value):
		self.format_params[key] = value
	
	def format(self, s):
		s = str(s)
		for key, value in xitems(self.format_params):
			s = s.replace('%'+key+'%', str(value))
			
		return s
	
	def get_data(self, *args, **kwargs):
		
		default = kwargs.get('default')
		type = kwargs.get('type')
		res = None
		try:
			res = self
			for i in args:
				if IS_PYTHON2:
					if isinstance(res, ConfigParser):
						res = res.items(i)
						#print (res)
					else:
						res = res[i]
				else:
					if isinstance(res, SectionProxy):
						res = res.get(i, raw=True)
					else:
						res = res[i]
		except Exception as e:
			#print (get_traceback())
			res = default
		
		if type == 'array':
			res = str(res)
			try:
				res = json.loads(res)
			except:
				res = []
				
		return res
	
	def get_value(self, *args, **kwargs):
		val = self.get(*args, **kwargs)
		return self.format(val)
	"""