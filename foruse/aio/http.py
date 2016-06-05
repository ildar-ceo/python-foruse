# -*- coding: utf-8 -*-
import asyncio
from foruse import *
from .connection import TCPConnection
from .streams import AbstractStream, EndLineException, QueueStream


class HttpPacket(log.Log):
	
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
	
	def is_status_code_body_exists(self):
		return self._status_code in [200, 206, 207, 226]
	
	def is_status_code_success(self):
		return self._status_code>=200 and self._status_code<=299
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._body = None
		self._headers = {}
		self._transport = kwargs.get('transport')
		self._input_stream = kwargs.get('input_stream')
		self._body_stream = None
		self._type = None
		self._state = HttpPacket.STATE_NONE
		self._header_line_limit = 8192
		self._method = None
		self._path = None
		self._http_version = None
		self._status_code = None
		
		self.headers = {}
	#!enddef __init__
	
	def set_input_stream(self, input_stream):
		self._input_stream = input_stream
		
	def get_input_stream(self):
		return self._input_stream
	
	def set_transport(self, transport):
		self._transport = transport
		
	def get_transport(self):
		return self._transport
	
	def set_body_stream(self, stream):
		self._body_stream = stream
	
	def get_body_stream(self):
		return self._body_stream
		
	def get_path(self):
		return self._path
	
	def set_path(self, value):
		self._path = value
	
	def get_method(self):
		return self._method
	
	def set_method(self, value):
		self._method = value
	
	def get_http_version(self):
		return self._http_version
	
	def set_http_version(self, value):
		self._http_version = value
	
	def get_version(self):
		return self._http_version
	
	def set_version(self, value):
		self._http_version = value
	
	def get_status_code(self):
		return self._status_code
	
	def set_status_code(self, value):
		self._status_code = int(value)
	
	async def close(self):
		if self._body_stream is not None:
			await self._body_stream.skip()
			await self._body_stream.close()
	
	def set_header(self, key, value):
		ukey = key.lower()
		self._headers[ukey] = (key, value)
	
	def get_header(self, key, default=None):
		key = key.lower()
		val = self._headers.get(key)
		if val is None:
			return default
		return val[1]
	
	def remove_header(self, key):
		key = key.lower()
		if key in self._headers:
			del self._headers[key]
	
	def delete_header(self, key):
		self.remove_header(key)
	
	def del_header(self, key):
		self.remove_header(key)
	
	def get_headers(self):
		return self._headers
	
	def get_body(self):
		return self._body_stream
	
	
	def parse_request(self, line):
		self._type = HttpPacket.TYPE_REQUEST
		try:
			(self._method, self._path, self._http_version) = line.split()
		except:
			return False
		
		if self._method in ['GET', 'PUT', 'POST', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'TRACE', 'CONNECT']:
			return True
			
		return False
	#!enddef parse_request
	
	
	def parse_answer(self, line):
		self.type = HttpPacket.TYPE_ANSWER
		try:
			arr = line.split()
			self._http_version = arr[0]
			self._status_code = int(arr[1])
		except:
			return False
		
		return True
	#!enddef parse_answer
	
	
	def parse_header(self, line):
		try:
			(key, value) = line.split(':', 1)
			ukey = key.strip().lower()
			value = value.strip()
			self._headers[ukey]=(key,value)
		except Exception as e:
			#print (e)
			return False
		
		return True
	#!enddef parse_header
	
	
	def get_raw_header(self):
		
		crlf = "\r\n"
		str = ""
		
		if self._type == HttpPacket.TYPE_REQUEST:
			str += "%s %s %s%s" % (self._method, self._path, self._http_version, crlf)
		
		elif self._type == HttpPacket.TYPE_ANSWER:
			str += "%s %s" % (self._http_version, self._status_code)
			status_str = HttpPacket.STATUS_CODES.get(self._status_code)
			
			if status_str is not None:
				str += " " + status_str
			
			str += crlf
			
		for key,value in xvalues(self._headers):
			str += "%s: %s%s" % (key, value, crlf)
		
		str += crlf
		
		return to_byte(str)
		
	#!enddef get_raw_header
	
	
	def write(self, data):
		if isinstance(self._body_stream, QueueStream):
			self._body_stream.feed_data(data)
	#!enddef write
	
	
	def write_eof(self):
		if isinstance(self._body_stream, QueueStream):
			self._body_stream.feed_eof()
	#!enddef write_eof
	
	
	async def send(self):
		
		if self._transport is not None:
			
			addr = self._transport.get_extra_info('peername')
			#print (addr)
			self._log.debug3('Send packet to {} ' . format(addr))
				
			self.remove_header('Content-Length')
			if self._body_stream is not None:
				size = await self._body_stream.size()
				if size != None:
					self.set_header('Content-Length', size)
			
			self._transport.write(self.get_raw_header())
			
			#print ('_body_stream = ' + str(self._body_stream))
			if self._body_stream is not None:
				while not await self._body_stream.eof():
					data = await self._body_stream.read(8192)
					#print (data)
					self._transport.write(data)
				await self._body_stream.close()
			#!endif
			
		#!endif
	#!enddef send
	
	
	async def parse(self):
		
		self._body_stream = None
		
		if self._input_stream is None:
			return False
		
		if self._state != HttpPacket.STATE_NONE:
			return False
		
		self._state = HttpPacket.STATE_INIT
		
		while not await self._input_stream.eof():
			
			try:
				line = await self._input_stream.readline(self._header_line_limit)
				line = line.decode('utf-8').strip()
				
			except EndLineException as e:
				await self.skipline()
				return False
			
			except Exception as e:
				return False
			
			if len(line) == 0:
				break
			
			if self._state == HttpPacket.STATE_INIT:
				
				if self._type == HttpPacket.TYPE_REQUEST:
					if not self.parse_request(line):
						return False
						
				if self._type == HttpPacket.TYPE_ANSWER:
					if not self.parse_answer(line):
						return False
						
				self._state = HttpPacket.STATE_HEADER
			
			elif self._state == HttpPacket.STATE_HEADER:
				if not self.parse_header(line):
					return False
			
		#!endwhile
		
		if self._state == HttpPacket.STATE_INIT:
			return False
		
		length = self.get_header('Content-Length')
		self._log.debug3('Content-Length: %s' % (length))
		
		if isinstance(self, HttpAnswer):
			
			if self.is_status_code_body_exists():
				# Todo: здесь нужен http body stream на основе input stream
				# Также нужно проверить код, что body Идет по частям
				# В противном случае, _body_stream создавать, если packet является ответом
				if length is not None:
					self._body_stream = self._input_stream.get_count_stream(length)
				else:
					self._body_stream = self._input_stream
			
		else:
			if length is not None:
				self._body_stream = self._input_stream.get_count_stream(length)
		
		
		return True
	#!enddef parse
	
	
	async def parse_stop():
		if self._body_stream is not None:
			await self._body_stream.stop()
	#!enddef parse_stop
	
	
	async def parse_end(self):
		if self._body_stream is not None:
			if self._body_stream != self._input_stream:
				#print ('parse_end')
				await self._body_stream.skip()
				await self._body_stream.stop()
	#!enddef parse_end	
	
#!endclass HttpPacket



class HttpRequest(HttpPacket):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._type = HttpPacket.TYPE_REQUEST
		self._method = 'GET'
		self._path = '/'
		self._http_version = 'HTTP/1.1'
	
	
	def create_answer(self,):
		answer = HttpAnswer(transport=self._transport)
		return answer
	
	
#!endclass HttpRequest



class HttpAnswer(HttpPacket):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._type = HttpPacket.TYPE_ANSWER
		self._http_version = 'HTTP/1.1'
		self._status_code = 200
		
		self._body_stream = QueueStream()
		
#!endclass HttpAnswer



class HTTPServer(TCPConnection):
	
	async def create_error_answer(self, code):
	
		answer = self.create_answer()
		answer.set_header('Content-type', 'text/html')
		#answer.set_header('Connection', 'close')
		
		if code in HttpPacket.STATUS_CODES:
			message = str(code) + ' ' + HttpPacket.STATUS_CODES.get(code)
		else:
			message = str(code)
		
		answer.write(to_byte('<h1><center>' + message + '</center></h1>'))
		answer.write_eof()
		
		return answer
	
	
	async def handle_error(self, code):
		answer = self.create_error_answer(code)
		answer.set_transport(self._transport)
		await answer.send()
		self.close()
		
	
	async def handle_request_end(self, request, answer):
		self._log.debug('Request = %sms' % ( (self._end_request - self._start_request).microseconds / 1000 ))
		
	
	async def handle_request(self, request):
		self._log.debug3 ('handle_request')
		
		answer = request.create_answer()
		answer.set_header('Content-type', 'text/html')
		answer.set_header('Connection', 'close')
		answer.write(b'Hello world!!!')
		
		return answer
	
	def connection_made(self, transport):
		super().connection_made(transport)
		self._loop.create_task(self.start())
	
	async def start(self):
		
		while not await self._read_buffer.eof():
			
			await self._read_buffer._try_lock_read()
			self._start_request = datetime.datetime.now()
			
			request = HttpRequest(input_stream=self._read_buffer, transport=self._transport)
			if await request.parse():	
				try:
					answer = await self.handle_request(request)
					
					if answer != None:
						answer.set_transport(self._transport)
						await answer.send()
						
						self._end_request = datetime.datetime.now()
						await self.handle_request_end(request, answer)
						
						length = answer.get_header('Content-Length')
						if length is None:
							self.close()
							return 
						
						if not answer.is_status_code_success():
							self.close()
							return 
						
						if self._close == False:
							await request.parse_end()
						
					else:
						await self.handle_error(502)
						
					
				except Exception as e:
					print (get_traceback())
					await self.handle_error(502)
			
			else:
				self.close()
				return
			
			#!endif
		#!endwhile
		
	#!enddef
	
	def create_answer(self):
		request = HttpAnswer()
		request.set_transport(self._transport)
		return request
	
	async def send_answer(self, answer):
		#print (answer)
		answer.set_transport(self._transport)
		await answer.send()
	#!enddef
	
#!endclass HTTPServer


class HttpClient(TCPConnection):
	
	async def get_answer(self):
		
		await self._read_buffer._try_lock_read()
		self._start_request = datetime.datetime.now()
		answer = HttpAnswer(input_stream=self._read_buffer)
		if await answer.parse():
			return answer
			
		return None
			
	def create_request(self):
		request = HttpRequest()
		request.set_transport(self._transport)
		return request
	
	async def send_request(self, request):
		request.set_transport(self._transport)
		await request.send()
	#!enddef
	
	
	def data_received(self, data):
		super().data_received(data)
		#print (data)
	
#!endclass HttpClient