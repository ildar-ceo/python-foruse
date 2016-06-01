# -*- coding: utf-8 -*-

import asyncio
import datetime
import asyncio.streams
from foruse import *
from foruse.aio import *


class HTTPServer(log.Log, asyncio.Protocol):

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)
		
		self._close = False
		self._transport = None
		
		self._buffer = QueueStream()
		
		self._loop = kwargs.get('loop')
		
		if self._loop == None:
			self._loop = asyncio.get_event_loop()

			
	def __del__(self):
		self._log.debug2 ('--------------')
	
	
	def close(self):
		self._close = True
		self._buffer.feed_eof()
		self._transport.close()
		
	def connection_made(self, transport):
		self._log.debug2 ('connection_made')
		self._transport = transport
		self._start = datetime.datetime.now()
		self._loop.create_task(self.start())
		
		
	def connection_lost(self, exc):
		self._log.debug2 ('connection_lost')
		self._close = True
		self._buffer.feed_eof()
		
		
	def eof_received(self):
		self._log.debug2 ('eof_received')
		self._buffer.feed_eof()
	
	
	def data_received(self, data):
		self._log.debug2 ('data_received')
		self._buffer.feed_data(data)
		self._buffer.feed_flush()
		
	
	async def handle_request(self, request):
		self._log.debug2 ('handle_request')
		
		answer = request.create_answer()
		answer.set_header('Content-type', 'text/html')
		answer.write(b'Hello world!!!')
		
		return answer
		
	
	async def handle_error(self, request, status_code):
		answer = request.create_answer()
		answer.set_header('Connection', 'close')
		answer.set_header('Content-type', 'text/html')
		
		status_str = HttpPacket.STATUS_CODES.get(status_code, '')
		answer.write(status_str)
		
		await answer.send()
		self.close()
	
	
	async def start(self):
		
		while not await self._buffer.eof():
			request = HttpRequest(input_stream=self._buffer, transport=self._transport)
			if await request.parse():	
				try:
					answer = await self.handle_request(request)
					
					await answer.send()
					
					length = answer.get_header('Content-Length')
					if length is None:
						self.close()
					
					self._end = datetime.datetime.now()
					self._log.debug('Request = %sms' % ( (self._end - self._start).microseconds / 1000 ))
					
					if self._close == False:
						await request.end()

						
				except Exception as e:
					print (get_traceback())
					await self.handle_error(request, 502)
			