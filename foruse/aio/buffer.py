# -*- coding: utf-8 -*-
import asyncio
import foruse.log as log
from .fs import LocalFS
from .streams import *
from foruse import *


class BufferStream:
	
	def __init__(self, *args, **kwargs):
		
		self._loop = kwargs.get('loop')
		if self._loop == None:
			self._loop = asyncio.get_event_loop()
		
		self._max_size = xint(kwargs.get('max_size'), 16384)
		self._min_size = xint(kwargs.get('min_size'), 1)
		
		if self._max_size < self._min_size:
			self._max_size = 16384
			self._min_size = 1024
		
		self._is_eof = False
		self._is_stop = False
		self._is_flushed = False
		
		self._buffer = bytearray(self._max_size)
		self._cur = 0
		self._end = 0
		self._count_readed = 0
		
		self._write_waiter = None
		self._read_waiter = None
		self._exception = None
	#!enddef
	
	def set_exception(self, e):
		self._exception = e
	
	def is_stop(self):
		return self._is_stop
	
	def get_buffer(self):
		return self._buffer[self._cur:self._end]
	
	async def clear(self):
		self._exception = None
		self._count_readed = 0
		self._cur = 0
		self._end = 0
		self._is_stop = False
		self._is_eof = False
		self._is_flushed = False
		await self._unlock_read()
		await self._unlock_write()
	
	async def close(self):
		await self.stop()
	
	async def stop(self):
		self._is_stop = True
		self._is_eof = True
		await self._unlock_read()
		await self._unlock_write()
		
	async def get_pos(self):
		return self._count_readed
	#!enddef

	async def _try_lock_read(self):
		#print ('_try_lock_read')
		
		if self._is_flushed:
			self._is_flushed = False
			return
		
		if self._end < self._min_size and not self._is_stop and not self._is_eof and self._exception is None:
			await self._lock_read()
	
	async def _lock_read(self):
		if self._read_waiter is None:
			self._read_waiter = asyncio.Event()
		try:
			#print ('Lock Read')
			await self._read_waiter.wait()
			#print ('Unlock Read')
		finally:
			self._read_waiter.clear()
	#!enddef
	
	
	async def _unlock_read(self):
		if self._read_waiter is not None:
			self._read_waiter.set()
			#self._read_waiter = None
	#!enddef
	
	
	async def _lock_write(self):
		if self._write_waiter is None:
			self._write_waiter = asyncio.Event()
		try:
			await self._write_waiter.wait()
		finally:
			self._write_waiter.clear()
	#!enddef
	
	
	async def _unlock_write(self):
		if self._write_waiter is not None:
			self._write_waiter.set()
	#!enddef
	
	
	async def read(self, count = -1):
		#await asyncio.sleep(0.5)
		
		if self._exception != None:
			raise self._exception
		
		if count == 0:
			return bytearray([])
			
		if count > 0:
			return await self.read_count(count)
		
		if await self.eof():
			return bytearray([])
		
		await self._try_lock_read()
		
		#print (count)

		cur = self._cur
		end = self._end
		sz = end - cur
		if sz > 0:
			self._count_readed += end - cur
			self._cur = 0
			self._end = 0
		
		await self._unlock_write()
		self._is_flushed = False
		
		return self._buffer[cur:end]
	#!enddef
	
	
	async def read_all(self):
		data = bytearray()
		while not await self.eof():
			buf = await self.read()
			data.extend(buf)
		
		return data
	
	async def write(self, buff):
		
		if self.is_stop():
			return
	
		buff_size = len(buff)
		buff_pos = 0
		
		while buff_size - buff_pos > 0 and not self._is_stop:
			free_size = self._max_size - self._end
			count = buff_size - buff_pos
			
			if count > free_size:
				count = free_size
			
			if count > 0:
				self._buffer[self._end:self._end+count] = buff[buff_pos:buff_pos+count]
				
				buff_pos += count
				self._end += count
			
			if self._end >= self._min_size:
				await self._unlock_read()
			
			if self._end >= self._max_size:
				await self._lock_write()
			
		#!endwhile		
	#!enddef

	
	async def skip(self):
		while not await self.eof():
			await self.read()
	#!enddef
	
	
	async def skip_line(self):
		if self._exception != None:
			raise self._exception
		
		while not await self.eof():
			
			await self._try_lock_read()
			
			cur = self._cur
			end = self._end
			
			pos_n = self._buffer.find(b'\n', self._cur)
			
			if pos_n == -1 or pos_n >= end:
				self._count_readed += end - cur
				self._cur = 0
				self._end = 0
				await self._unlock_write()
			
			else:
				self._count_readed += pos_n - cur + 1
				self._cur = pos_n + 1
				self._end = end
				break
				
		#!endwhile
	#!enddef
	
	
	async def flush(self):
		self._is_flushed = True
		await self._unlock_read()
	#!enddef
	
	
	async def eof(self):
		return self._is_eof and self._end == 0
	#!enddef
	
	
	async def write_eof(self):
		self._is_eof = True
		await self._unlock_read()
		await self._unlock_write()
	#!enddef
	
	
	def _readline(self, maxlen = -1):
		
		class f:
			def __init__(self, stream, maxlen):
				self.stop = False
				self.stream = stream
				self.maxlen = maxlen
				self.count_readed = 0
		
			async def __aiter__(self):
				return self

			async def __anext__(self):
				if self.stop:
					raise StopAsyncIteration
				
				if await self.stream.eof():
					raise StopAsyncIteration
				
				if self.count_readed > self.maxlen and self.maxlen != -1:
					raise EndLineException
				
				await self.stream._try_lock_read()
				
				cur = self.stream._cur
				end = self.stream._end
				pos_n = self.stream._buffer.find(b'\n', self.stream._cur)
				
				if pos_n >= self.maxlen and self.maxlen != -1:
					raise EndLineException
				
				if pos_n == -1 or pos_n >= end:
					self.count_readed += end - cur
					self.stream._count_readed += end - cur
					self.stream._cur = 0
					self.stream._end = 0
					await self.stream._unlock_write()
					return (cur, end)
				
				else:
					self.count_readed += pos_n - cur + 1
					self.stream._count_readed += pos_n - cur + 1
					self.stream._cur = pos_n+1
					self.stream._end = end
					self.stop = True
					return (cur, pos_n)
			
			#!enddef __anext__
			
		#!endclass f
		
		return f(self, maxlen)
	#!enddef
	
	
	async def _loop_read_line(self, out_stream, maxlen = -1):
		try:
			async for cur, end in self._readline(maxlen = -1):
				await out_stream.write(self._buffer[cur:end])
		except Exception as e:
			out_stream.set_exception(e)
		await out_stream.stop()
	#!enddef
	
	
	async def get_line_stream(self, maxlen = -1):
		stream = BufferStream()
		self._loop.create_task(self._loop_read_line(stream, maxlen = -1))
		return stream
	#!enddef
	
	
	async def readline(self, maxlen = -1):
		data = bytearray()
		async for cur, end in self._readline(maxlen):
			data.extend(self._buffer[cur:end])
		return data
	#!enddef
	
	
	async def readline_skip(self, maxlen = -1):
		data = bytearray()
		try:
			async for cur, end in self._readline(maxlen):
				data.extend(self._buffer[cur:end])
		except EndLineException:
			await self.skip_line()
			return bytearray()
		return data
	#!enddef
	
	
	def _read_count(self, count):
		class f:
			def __init__(self, stream, count):
				self.stop = False
				self.stream = stream
				self.count = count
				self.count_readed = 0
		
			async def __aiter__(self):
				return self

			async def __anext__(self):
				if self.stop:
					raise StopAsyncIteration
				
				if await self.stream.eof():
					raise StopAsyncIteration
				
				if self.count_readed >= self.count:
					raise StopAsyncIteration
				
				await self.stream._try_lock_read()
				
				cur = self.stream._cur
				end = self.stream._end
				left = self.count - self.count_readed
				
				if left == 0:
					raise StopAsyncIteration
				
				if cur + left < end:
					self.count_readed = self.count
					self.stream._cur = cur + left
					self.stream._end = end
					self.stream._count_readed += left
					self.stop = True
					return self.stream._buffer[cur:cur + left]
					
				else:
					self.count_readed += end - cur
					self.stream._count_readed += end - cur
					self.stream._cur = 0
					self.stream._end = 0
					await self.stream._unlock_write()
					return self.stream._buffer[cur:end]
			#!enddef __anext__
			
		#!endclass f
		
		return f(self, count)
	#!enddef
	
	
	async def _loop_read_count(self, out_stream, count):
		try:
			async for data in self._read_count(count):
				await out_stream.write(data)
		except Exception as e:
			out_stream.set_exception(e)
		await out_stream.stop()
	#!enddef
	
	
	async def get_count_stream(self, count):
		try:
			count = int(count)
			stream = BufferStream()
			self._loop.create_task(self._loop_read_count(stream, count))
			return stream
		except:
			return None
	#!enddef
	
	
	async def read_count(self, count):
		buff = bytearray()
		async for data in self._read_count(count):
			buff.extend(data)
		return buff
	#!enddef
	
	
#!endclass BufferStream