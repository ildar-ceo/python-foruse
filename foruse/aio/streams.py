# -*- coding: utf-8 -*-
import asyncio
import foruse.log as log
from .fs import LocalFS

_local_fs = LocalFS()


class EndLineException(Exception):
	def __str__(self):
		return "End of line excepted"
		
#!endclass EndLineException


class EofException(Exception):
	def __str__(self):
		return "End of stream"
		
#!endclass EndLineException


class AbstractStream(log.Log):
	
	SEEK_SET = 0
	SEEK_CUR = 1
	SEEK_END = 2
	
	MODE_READ = 'rb'
	MODE_READ_AND_WRITE = 'r+b'
	MODE_WRITE = 'wb'
	MODE_WRITE_AND_READ = 'w+b'
	MODE_APPEND = 'ab'
	MODE_APPEND_AND_READ = 'a+b'
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._loop = kwargs.get('loop')
		if self._loop == None:
			self._loop = asyncio.get_event_loop()
	
	
	async def open(self):
		pass
	
	async def read(self, max_size=1024):
		pass
	
	async def write(self, buf):
		pass
		
	async def close(self):
		pass

	async def flush(self):
		pass
	
	async def eof(self):
		return True
	
	async def get_size(self):
		return 0
	
	async def get_pos(self):
		return 0
	
	async def close(self):
		pass
	
#!endclass AbstreactStream



class FileStream(AbstractStream):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._file_name = kwargs.get('file_name')
		self._mode = kwargs.get('mode')
		self._handle = None
		self._fs = kwargs.get('fs')
		
		if self._fs is None:
			self._fs = _local_fs
		
		self._size = 0
		self._pos = 0
		
		self._size_dirty = True
		self._pos_dirty = True

		
	async def open(self):
		if self._handle is not None:
			await self.close()
	
		if await self._fs.file_exists(self._file_name):
			self._size = await self._fs.file_size(self._file_name)
			self._handle = await self._fs.file_open(self._file_name, self._mode)
		else:
			self._handle = None
		
		return self._handle is not None
	
	async def read(self, max_size=1024):
		data = await self._fs.file_read(self._handle, max_size)
		self._pos_dirty = True
		return data

	async def write(self, buf):
		await self._fs.file_write(self._handle, buf)
		self._pos_dirty = True
		self._size_dirty = True
		return data

	async def close(self):
		await self._fs.file_close(self._handle)
		self._handle = None
	
	async def eof(self):
		pos = await self.get_pos()
		size = await self.get_size()
		return pos >= size
	
	async def get_size(self):
		if self._size_dirty:
			await self.update_size()
		return self._size
	
	async def get_pos(self):
		if self._pos_dirty:
			await self.update_pos()
		return self._pos
	
	async def update_pos(self):
		self._pos = await self._fs.file_pos(self._handle)
		self._pos_dirty = False
		return self._pos
		
	async def update_size(self):
		self._size = await self._fs.file_size(self._file_name)
		self._size_dirty = False
		return self._size
	
#!endclass FileStream



class BufferStream(AbstractStream):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._max_size = kwargs.get('max_size', 3) # 16384
		self._min_size = kwargs.get('min_size', 1) # 1024
		self._is_eof = False
		self._is_close = False
		
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
	
	def is_close(self):
		return self._is_close
	
	def get_buffer(self):
		return self._buffer[self._cur:self._end]
	
	async def close(self):
		self._is_close = True
		self._is_eof = True
		await self._unlock_read()
		await self._unlock_write()
	
	async def get_pos(self):
		return self._count_readed
	#!enddef

	async def _try_lock_read(self):
		if self._end < self._min_size and not self._is_close and not self._is_eof and self._exception is None:
			await self._lock_read()
	
	async def _lock_read(self):
		self._read_waiter = asyncio.futures.Future(loop=self._loop)
		try:
			await self._read_waiter
		finally:
			self._read_waiter = None
	#!enddef
	
	
	async def _unlock_read(self):
		if self._read_waiter is not None:
			self._read_waiter.set_result(None)
		self._read_waiter = None
	#!enddef
	
	
	async def _lock_write(self):
		self._write_waiter = asyncio.futures.Future(loop=self._loop)
		try:
			await self._write_waiter
		finally:
			self._write_waiter = None
	#!enddef
	
	
	async def _unlock_write(self):
		if self._write_waiter is not None:
			self._write_waiter.set_result(None)
		self._write_waiter = None
	#!enddef
	
	
	async def read(self, count = -1):
	
		if count == 0:
			return []
			
		if count > 0:
			return await self.read_count(count)
	
		if await self.eof():
			return []
		
		await self._try_lock_read()
		
		if self._exception != None:
			raise self._exception

		cur = self._cur
		end = self._end
			
		self._count_readed += end - cur
		self._cur = 0
		self._end = 0
		
		await self._unlock_write()
		
		return self._buffer[cur:end]
	#!enddef
	
	
	async def read_all(self):
		data = bytearray()
		while not await self.eof():
			buf = await self.read()
			data.extend(buf)
		
		return data
	
	async def write(self, buff):
		
		if self.is_close():
			return
	
		buff_size = len(buff)
		buff_pos = 0
		
		while buff_size - buff_pos > 0 and not self._is_close:
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
		await self._unlock_read()
	#!enddef	
	
	
	async def eof(self):
		return self._is_eof and self._cur == 0
	#!enddef
	
	
	async def write_eof(self):
		await self.flush()
		await self._unlock_write()
		self._is_eof = True
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
		await out_stream.close()
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
				
				if cur + left < end:
					self.count_readed = self.count
					self.stream._cur = cur + left
					self.stream._end = end
					self.stream._count_readed += left
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
		await out_stream.close()
	#!enddef
	
	
	async def get_count_stream(self, count):
		stream = BufferStream()
		self._loop.create_task(self._loop_read_count(stream, count))
		return stream
	#!enddef
	
	
	async def read_count(self, count):
		buff = bytearray()
		async for data in self._read_count(count):
			buff.extend(data)
		return buff
	#!enddef
	
	
#!endclass BufferStream
