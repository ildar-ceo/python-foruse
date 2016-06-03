# -*- coding: utf-8 -*- 

import sys
from .colors import colorf, COLORS
from .datelib import *
from .lib import *

DEBUG3=7
DEBUG2=6
DEBUG1=5
DEBUG=5
INFO=4
WARNING=3
ERROR=2
CRITICAL=1

LOG_LEVEL = INFO
LOG_FORMAT = "%(date)s %(color)s%(level)-8s %(module)+20s: %(message)s%(nc)s"
#LOG_FORMAT = "%(date)s [%(color)s%(module)-20s] %(level)+8s: %(message)s%(nc)s"
LOG_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

TO_STR={
	DEBUG3: 'DEBUG3',
	DEBUG2: 'DEBUG2',
	DEBUG: 'DEBUG',
	INFO: 'INFO',
	WARNING: 'WARNING',
	ERROR: 'ERROR',
	CRITICAL: 'CRITICAL',
}

FROM_STR={
	'DEBUG3': DEBUG3,
	'DEBUG2': DEBUG2,
	'DEBUG1': DEBUG,
	'DEBUG': DEBUG,
	'INFO': INFO,
	'WARNING': WARNING,
	'ERROR': ERROR,
	'CRITICAL': CRITICAL,
}

LOG_COLORS = {
	DEBUG3: 'b_cyan',
	DEBUG2: 'b_cyan',
	DEBUG: 'b_cyan',
	INFO: 'b_blue',
	WARNING: 'b_yellow',
	ERROR: 'b_red',
	CRITICAL: 'b_red',
}

def get_level(level):
	if type(level) is str:
		return FROM_STR.get(level, LOG_LEVEL)
	elif TO_STR.get(level) is not None:
		return level
		
	return LOG_LEVEL

	
class Logging:
	
	def __init__(self, *args, **kwargs):
		self.log_colors = clone(LOG_COLORS)
		self.log_level = None
		self.log_module = kwargs.get('log_module', 'Main')
	
	def set_module(self, name):
		self.log_module = name
	
	def set_name(self, name):
		self.log_module = name
	
	def set_level(self, level):
		self.log_level = get_level(level)
	
	def set_color(self, level, color):
		level = get_level(level)
		self.log_colors[level] = color
	
	def log(self, s, *args, **kwargs):
		
		#print (self.log_colors)
		
		level_num = kwargs.get('level')
		level_str = TO_STR.get(level_num)
		level_color = self.log_colors.get(level_num)
		
		if level_str is None:
			level_num = INFO
			level_str = TO_STR.get(level_num)
			level_color = self.log_colors.get(level_num)
		
		if self.log_level is None:
			if level_num > LOG_LEVEL:
				return
		else:
			if level_num > self.log_level:
				return
		
		time = localtime()
		
		params = {
			'module': self.log_module[0:20],
			'message': s,
			'level': level_str,
			'date': time.strftime(LOG_DATETIME_FORMAT),
			'color': COLORS.get(level_color),
			'nc': COLORS.get('nc'),
		}
		
		print (LOG_FORMAT % params)
		sys.stdout.flush()
	
	def debug(self, s, *args, **kwargs):
		self.log(s, *args, level=DEBUG, **kwargs)
		
	def debug2(self, s, *args, **kwargs):
		self.log(s, *args, level=DEBUG2, **kwargs)
	
	def debug3(self, s, *args, **kwargs):
		self.log(s, *args, level=DEBUG3, **kwargs)
	
	def info(self, s, *args, **kwargs):
		self.log(s, *args, level=INFO, **kwargs)
		
	def warn(self, s, *args, **kwargs):
		self.log(s, *args, level=WARNING, **kwargs)
		
	def error(self, s, *args, **kwargs):
		self.log(s, *args, level=ERROR, **kwargs)
		
	def critical(self, s, *args, **kwargs):
		self.log(s, *args, level=CRITICAL, **kwargs)
	
	def crit(self, s, *args, **kwargs):
		self.log(s, *args, level=CRITICAL, **kwargs)
	
#!endclass Logging


class Log:
	def __init__(self, *args, **kwargs):
		self._log = Logging(log_module=self.__class__.__name__)
		

logging = Logging(log_module='Main')

def log(s, *args, **kwargs):
	logging.log(s, *args, **kwargs)
	
def set_module(name):
	logging.set_module(name)
	
def set_level(level):
	global LOG_LEVEL
	
	if type(level) is str:
		LOG_LEVEL = FROM_STR.get(level, INFO)
	elif TO_STR.get(level) is not None:
		LOG_LEVEL = level
	
def debug(s, *args, **kwargs):
	logging.log(s, *args, level=DEBUG, **kwargs)
	
def info(s, *args, **kwargs):
	logging.log(s, *args, level=INFO, **kwargs)
	
def warn(s, *args, **kwargs):
	logging.log(s, *args, level=WARNING, **kwargs)
	
def error(s, *args, **kwargs):
	logging.log(s, *args, level=ERROR, **kwargs)
	
def critical(s, *args, **kwargs):
	logging.log(s, *args, level=CRITICAL, **kwargs)