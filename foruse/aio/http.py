# -*- coding: utf-8 -*-
import asyncio
import foruse.log as log

from .streams import BufferStream, EndLineException


class HttpPacket:
	
	TYPE_REQUEST = 1
	TYPE_ANSWER = 2
	
	STATE_NONE = 0
	STATE_INIT = 1
	STATE_HEADER = 2
	STATE_BODY = 3
	
	MODE_PROXY = 1
	MODE_ANALYZE = 2	
	
	STATUS_CODES = {
		100:"Continue",
		101:"Switching Protocols",
		102:"Processing",
		200:"OK",
		201:"Created",
		202:"Accepted",
		203:"Non-Authoritative Information",
		204:"No Content",
		205:"Reset Content",
		206:"Partial Content",
		207:"Multi-Status",
		226:"IM Used",
		300:"Multiple Choices",
		301:"Moved Permanently",
		302:"Moved Temporarily",
		303:"See Other",
		304:"Not Modified",
		305:"Use Proxy",
		306:"Reserved",
		307:"Temporary Redirect",
		400:"Bad Request",
		401:"Unauthorized",
		402:"Payment Required",
		403:"Forbidden",
		404:"Not Found",
		405:"Method Not Allowed",
		406:"Not Acceptable",
		407:"Proxy Authentication Required",
		408:"Request Timeout",
		409:"Conflict",
		410:"Gone",
		411:"Length Required",
		412:"Precondition Failed",
		413:"Request Entity Too Large",
		415:"Unsupported Media Type",
		416:"Requested Range Not Satisfiable",
		417:"Expectation Failed",
		418:"I'm a teapot",
		422:"Unprocessable Entity",
		423:"Locked",
		424:"Failed Dependency",
		425:"Unordered Collection",
		426:"Upgrade Required",
		428:"Precondition Required",
		429:"Too Many Requests",
		431:"Request Header Fields Too Large",
		434:"Requested host unavailable",
		449:"Retry With",
		451:"Unavailable For Legal Reasons",
		500:"Internal Server Error",
		501:"Not Implemented",
		502:"Bad Gateway",
		503:"Service Unavailable",
		504:"Gateway Timeout",
		505:"HTTP Version Not Supported",
		506:"Variant Also Negotiates",
		507:"Insufficient Storage",
		509:"Bandwidth Limit Exceeded",
		510:"Not Extended",
		511:"Network Authentication Required",
	}
	
	def __init__(self):
		self.method = None
		self.path = None
		self.version = None
		self.code = None
		self.type = None
		self.headers = {}
	
	def parse_request(self, line):
		self.type = Const.TYPE_REQUEST
		try:
			(self.method, self.path, self.version) = line.split()
		except:
			pass
	
	def parse_answer(self, line):
		self.type = Const.TYPE_ANSWER
		try:
			arr = line.split()
			self.version = arr[0]
			self.code = arr[1]
		except:
			pass
	
	def parse_header(self, line):
		try:
			(key, value) = line.split(':')
			ukey = key.strip().lower()
			value = value.strip()
			self.headers[ukey]=(key,value)
		except:
			pass
	
	def get_raw_header(self):
		
		crlf = b"\r\n"
		data = b""
		
		if self.type == Const.TYPE_REQUEST:
			data += to_byte(self.method) + b" " +  to_byte(self.path) + b" " +  to_byte(self.version) + crlf
		elif self.type == Const.TYPE_ANSWER:
			data += to_byte(self.version) + b" " +  to_byte(self.code) + crlf
			
		for key,value in xvalues(self.headers):
			data += to_byte(key) + b": " + to_byte(value) + crlf
		
		data += crlf
		
		return data
	
	def get_header(self, key, default=None):
		key = key.lower()
		val = self.headers.get(key)
		if val is None:
			return default
		return val[1]
	
#!endclass HttpPacket



class HttpStream(BufferStream):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._state = HttpPacket.STATE_NONE
		self._header_line_limit = 8192
		self._content_length = 10
		
	
	async def read_header(self):
		header = ""
		while not await self.eof():
			try:
				data = await self.readline(self._header_line_limit)
				data = data.decode('utf-8').strip()
				
			except EndLineException as e:
				self.drain_line()
				return None
			
			except Exception as e:
				return None
			
			if len(data) == 0:
				break
			
			header += data + "\n"
			
		return header

	
	def get_body_stream(self):
		if self._content_length is not None:
			return self.read_count_stream(self._content_length)
		return None
	
	
#!endclass HttpStream	