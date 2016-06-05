# -*- coding: utf-8 -*-

import asyncio
from foruse import *
from .streams import *


class TCPConnection(log.Log, asyncio.Protocol):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._close = False
		self._transport = None
		
		self._read_buffer = QueueStream()
		self._read_buffer._log.set_name('QueueStream_read_buffer')
		
		self._loop = kwargs.get('loop')
		if self._loop == None:
			self._loop = asyncio.get_event_loop()
		
		self._start_request = None
		self._end_request = None
	
	def __del__(self):
		self._log.debug3 ('------ DEL ------')
	
	
	def get_reader(self):
		return self._read_buffer
	
	
	def get_transport(self):
		return self._transport
	
	
	def close(self):
		self._close = True
		self._read_buffer.feed_eof()
		self._transport.close()
	
	
	@classmethod
	async def connect(cls, host, port, *args, loop=None, **kwargs):
		
		if loop == None:
			loop = asyncio.get_event_loop()
		
		transport, client = await loop.create_connection(lambda: cls(), host, port, **kwargs)
		return client
	
	
	@classmethod
	async def connect_unix(cls, filename, *args, loop=None, **kwargs):
		
		if loop == None:
			loop = asyncio.get_event_loop()
		
		transport, client = await loop.create_unix_connection(lambda: cls(), filename, **kwargs)
		return client
	
		
	def connection_made(self, transport):
		self._log.debug3 ('connection_made')
		self._transport = transport
		self._start_request = datetime.datetime.now()
		
		
	def connection_lost(self, exc):
		self._log.debug3 ('connection_lost')
		self._close = True
		self._read_buffer.feed_eof()
		
		
	def eof_received(self):
		self._log.debug3 ('eof_received')
		self._read_buffer.feed_eof()
	
	
	def data_received(self, data):
		self._log.debug3 ('data_received')
		self._read_buffer.feed_data(data)
		self._read_buffer.feed_flush()
		
#!endclass TCPConnection


	