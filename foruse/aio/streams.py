# -*- coding: utf-8 -*-
import asyncio
from foruse import *
from .fs import LocalFS
from .const import Aio


_local_fs = LocalFS()


class EndLineException(Exception):
	def __str__(self):
		return "End of line excepted"
		
#!endclass EndLineException


class IOException(Exception):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return self.value
		
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
		
		self._read_loop_waiter = None
		self._start_seek = 0
		self._chunk_size = kwargs.get('chunk_size', Aio.chunk_size)
		self._buffer_start = 0
		
		self._buffer = None
		self._log.set_level(kwargs.get('log_level', 'ERROR'))
		
	def set_min_size(self, size):
		if size <= self._buffer._max_size:
			self._buffer._min_size = size
		
	def _clear_buffer(self):
		self._buffer_start = 0
		self._buffer = None
		
	def seekable(self):
		return False
	
	def writable(self):
		return False
	
	def readable(self):
		return False
	
	# -----------------------------------------------------------------------------
	#                           Abstract Stream Functions
	# -----------------------------------------------------------------------------
	
	async def _open(self):
		return False
	
	async def _close(self):
		pass
	
	async def _read(self, count=-1):
		pass
	
	async def _write(self, buf):
		pass
	
	async def _seek(self, offset, whence):
		pass
	
	async def _tell(self):
		return 0
	
	async def _size(self):
		return None
	
	async def _eof(self):
		return True
	
	async def _flush(self):
		pass
	
	# -----------------------------------------------------------------------------
	#                               Stream Functions
	# -----------------------------------------------------------------------------
	
	async def open(self):
		return await self._open()
	
	async def stop(self):
		await self.close()
		
	async def close(self):
		await self._close()
	
	async def eof(self):
		if self._buffer is None:
			return await self._eof()
		
		return False
	
	async def flush(self):
		await self._flush()
	
	async def size(self):
		return await self._size()
	
	async def seek(self, offset, whence = SEEK_SET):
		self._clear_buffer()
		await self._seek(offset, whence)
	
	async def tell(self):
		sz = await self._tell()
		
		if self._buffer is None:
			return sz
			
		return sz - len(self._buffer) + self._buffer_start
	
	# -----------------------------------------------------------------------------
	#                               Write To Stream
	# -----------------------------------------------------------------------------
	
	async def write(self, buff):
		self._clear_buffer()
		await self._write(buff)
	#!enddef write
	
	
	# -----------------------------------------------------------------------------
	#                               Read From Stream
	# -----------------------------------------------------------------------------
	
	def _can_read(self):
		if not self.readable():
			raise IOException("Read from unreadable stream")
	
	
	async def read(self, count = -1):
		try:
			count = int(count)
		except:
			count = -1
		
		self._can_read()
		
		if count == 0:
			return b""
		
		if self._buffer != None:
			sz_buffer = len(self._buffer)
			
			if sz_buffer == self._buffer_start:
				self._clear_buffer()
				return await self._read(count)
			
			if count < 0:
				data = self._buffer[self._buffer_start:]
				self._clear_buffer()
				return data
			
			#print ('--------')
			#print ('count = %s' % (count))
			#print ('sz_buffer = %s' % (sz_buffer))
			#print ('_buffer_start = %s' % (self._buffer_start))
			#print ('free = %s' % (sz_buffer - self._buffer_start))
			
			if count > sz_buffer - self._buffer_start:
				data = self._buffer[self._buffer_start:]
				self._clear_buffer()
				return data
				
			data = self._buffer[self._buffer_start:self._buffer_start + count]
			self._buffer_start += count
			
			#print ('--------')
			#print ('count = %s' % (self._buffer_start))
			#print ('free = %s' % (sz_buffer))
			
			return data
			
		return await self._read(count)
	#!enddef read
	
	
	async def _loop_read_count(self, stream, count):
		
		left = count
		while not await self.eof() and left > 0 and not stream._is_stop:
			sz = left
			if sz > self._chunk_size:
				sz = self._chunk_size
			
			data = await self.read(sz)
			data_len = len(data)
			
			stream.feed_data(data)
			
			while not await stream._try_feed_data():
				pass
			
			left -= data_len
		#!endwhile
		
		stream.feed_eof()
	#!enddef
	
	
	def get_count_stream(self, count, max_size=Aio.max_size):
		count = int(count)
		stream = QueueStream(max_size=max_size)
		self._loop.create_task(self._loop_read_count(stream, count))
		return stream
	
	
	
	def readline_iter(self, maxlen = -1):
		
		self._can_read()
		
		class f:
			def __init__(self, stream, maxlen):
				self.stream = stream
				self.maxlen = maxlen
				
				self.sz_buffer = 0
				if self.stream._buffer is not None:
					self.sz_buffer = len(self.stream._buffer)
					
				self.count_readed = 0
				self.stop = False
			
			async def __aiter__(self):
				return self
			
			
			async def __anext__(self):
				
				if self.stop:
					raise StopAsyncIteration
				
				if await self.stream.eof():
					raise StopAsyncIteration
				
				if self.sz_buffer == self.stream._buffer_start:
					self.stream._clear_buffer()
				
				if self.stream._buffer is None:
					self.stream._buffer = await self.stream._read(self.stream._chunk_size)
					self.sz_buffer = len(self.stream._buffer)
				
				pos_n = self.stream._buffer.find(b'\n', self.stream._buffer_start)

				"""
				self.stream._log.debug2('----------')
				self.stream._log.debug2("pos_n = %s" % (pos_n))
				self.stream._log.debug2("count_readed = %s" % (self.count_readed))
				self.stream._log.debug2("sz_buffer = %s" % (self.sz_buffer))
				self.stream._log.debug2("stream._buffer = %s" % (self.stream._buffer))
				self.stream._log.debug2("stream._buffer_start = %s" % (self.stream._buffer_start))
				#print (self.count_readed)
				"""
				
				if pos_n == -1:
					self.count_readed += self.sz_buffer
				else:
					self.count_readed += pos_n - self.stream._buffer_start
				
				
				#self.stream._log.debug2("count_readed = %s" % (self.count_readed))
				
				
				if self.count_readed > self.maxlen and self.maxlen != -1:
					raise EndLineException
					
				
				if pos_n != -1:
					data = self.stream._buffer[self.stream._buffer_start:pos_n]
					self.stream._buffer_start = pos_n + 1
					self.count_readed += 1
					self.stop = True
					return data
					
				
				data = self.stream._buffer[self.stream._buffer_start:]
				self.stream._clear_buffer()
				return data
		
		return f(self, maxlen)
	
	
	async def readline(self, maxlen = -1):
		data=bytearray()
		async for buf in self.readline_iter(maxlen):
			data.extend(buf)
		return data
	
	async def skip(self):
		while not await self.eof():
			await self.read()
	#!enddef
	
	
	async def skipline(self):
		async for buf in self.readline_iter(maxlen = -1):
			pass
	#!enddef

	
#!endclass AbstractStream



class FileStream(AbstractStream):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._file_name = kwargs.get('file_name')
		self._mode = kwargs.get('mode')
		self._handle = None
		self._fs = kwargs.get('fs')
		
		if self._fs is None:
			self._fs = _local_fs
		
		self._size_hash = 0
		self._pos_hash = 0
		
		self._size_dirty = True
		self._pos_dirty = True
	
	def seekable(self):
		return True
	
	def writable(self):
		return True
	
	def readable(self):
		return True
	
	async def _open(self):
		if self._handle is not None:
			await self.close()
	
		if await self._fs.file_exists(self._file_name):
			self._size_hash = await self._fs.file_size(self._file_name)
			self._handle = await self._fs.file_open(self._file_name, self._mode)
		else:
			self._handle = None
		
		return self._handle is not None
	
	async def _close(self):
		if self._handle is not None:
			await self._fs.file_close(self._handle)
		self._handle = None
	
	async def _read(self, count=-1):
		data = []
		if self._handle is not None:
			data = await self._fs.file_read(self._handle, count)
			self._pos_dirty = True
		return data
	
	async def _write(self, buf):
		if self._handle is not None:
			await self._fs.file_write(self._handle, buf)
			self._pos_dirty = True
			self._size_dirty = True
	
	async def _seek(self, offset, whence):
		pass
	
	async def _eof(self):
		if self._handle is not None:
			pos = await self._tell()
			size = await self._size()
			return pos >= size
		
		return True
		
	async def _flush(self):
		pass
	
	async def _tell(self):
		if self._pos_dirty:
			await self._update_pos()
		return self._pos_hash
	
	async def _size(self):
		if self._size_dirty:
			await self._update_size()
		return self._size_hash
	
	async def _update_pos(self):
		if self._handle is not None:
			self._pos_hash = await self._fs.file_pos(self._handle)
			self._pos_dirty = False
		return self._pos_hash
		
	async def _update_size(self):
		if self._handle is not None:
			self._size_hash = await self._fs.file_size(self._file_name)
			self._size_dirty = False
		return self._size_hash
	
#!endclass FileStream



class QueueStream(AbstractStream):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._is_eof = False
		self._is_stop = False
		self._read_waiter = None
		self._feed_waiter = None
		self._list = []
		self._current_size = 0
		self._max_size = kwargs.get('max_size', Aio.max_size)
		
		
	def seekable(self):
		return True
	
	def writable(self):
		return False
	
	def readable(self):
		return True
	
	
	async def seek(self, offset, whence = AbstractStream.SEEK_SET):
		pass
	
	
	async def _try_feed_data(self):
		
		if self._current_size > self._max_size and not self._is_stop and not self._is_eof:
			self._log.debug3('Try %s = %s' % (self._current_size, self._max_size))
			await self._lock_feed()
			return False
			
		return True
	
	async def _lock_feed(self):
		if self._feed_waiter is None:
			self._feed_waiter = asyncio.Event()
		try:
			self._log.debug3('lock feed')
			await self._feed_waiter.wait()
			self._log.debug3('unlock feed')
		finally:
			self._feed_waiter.clear()
	
	def _unlock_feed(self):
		if self._feed_waiter is not None:
			self._feed_waiter.set()
		
		
	
	async def _try_lock_read(self):
		if len(self._list) == 0 and not self._is_stop and not self._is_eof:
			await self._lock_read()
	
	async def _lock_read(self):
		if self._read_waiter is None:
			self._read_waiter = asyncio.Event()
		try:
			self._log.debug3('lock read')
			await self._read_waiter.wait()
			self._log.debug3('unlock read')
		finally:
			self._read_waiter.clear()
			#self._read_waiter = None
			pass
	#!enddef
	
	def _unlock_read(self):
		if self._read_waiter is not None:
			self._read_waiter.set()
	#!enddef
	
	
	
	def is_stop(self):
		return self._is_stop
	
	async def stop(self):
		self._is_stop = True
		self._unlock_read()
		self._unlock_feed()
		
	async def _open(self):
		return True
	
	async def _close(self):
		self._list = []
		self._is_eof = True
		self._is_stop = True
		self._unlock_read()
	
	async def _read(self, count=-1):
	
		self._unlock_feed()
		await self._try_lock_read()
		if len(self._list) == 0:
			return b''
		
		if count == 0:
			return b''
		
		sz = len(self._list[0])
		if sz > count and count > 0:
			data = self._list[0][0:count]
			self._list[0] = self._list[0][count:]
			self._current_size -= count
			return data
		
		self._current_size -= sz
		data = self._list[0]
		del self._list[0]
		
		self._unlock_feed()
		
		return data
	
	def feed_data(self, buf):
		self._log.debug3('feed_data')
		if not self._is_stop:
			self._current_size += len(buf)
			self._list.append(buf)
			self._unlock_read()
	
	def feed_flush(self):
		self._log.debug3('feed_flush')
		self._unlock_read()
	
	def feed_eof(self):
		self._is_eof = True
		self._unlock_read()
	
	async def _seek(self, offset, whence):
		pass
	
	async def _tell(self):
		return None
	
	async def _size(self):
		return None
	
	async def _eof(self):
		return len(self._list) == 0 and (self._is_eof == True or self._is_stop == True)
	
	async def eof(self):
		return len(self._list) == 0 and (self._is_eof == True or self._is_stop == True)
	
	async def _flush(self):
		pass
		
#!endclass QueueStream	