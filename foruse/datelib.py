# -*- coding: utf-8 -*- 

import datetime, dateutil.tz

DATETIME_FORMAT='%Y-%m-%d %H:%M:%S'
DATE_FORMAT='%Y-%m-%d'
TIME_FORMAT='%H:%M:%S'

def gmdbtime(t):
	res = datetime.datetime.utcfromtimestamp(t)
	res = res.replace(tzinfo=datetime.timezone.utc)
	return res.strftime('%Y-%m-%d %H:%M:%S')

def gmfromtimestamp(t):
	res = datetime.datetime.utcfromtimestamp(t)
	res = res.replace(tzinfo=datetime.timezone.utc)
	return res

def gmstrptime(s, format='%Y%m%d%H%M%S'):
	res = datetime.datetime.strptime(s, format)
	res = res.replace(tzinfo=datetime.timezone.utc)
	return res
	
def tzutc():
	return dateutil.tz.tzutc()
	
def tzlocal():
	return dateutil.tz.tzlocal()
	
def localtime():
	tz = tzlocal()
	return datetime.datetime.now(tz)

def gmtime():
	tz = tzutc()
	return datetime.datetime.now(tz)
	
def utctime():
	tz = tzutc()
	return datetime.datetime.now(tz)
	
def change_timezone(dt, tz):
	offset = dt.utcoffset()
	if offset == None:
		tz2 = tzlocal()
		offset = tz2.utcoffset(fromtimestamp(0))
	utc = (dt - offset).replace(tzinfo=tz)
	return tz.fromutc(utc)