# -*- coding: utf-8 -*-
import asyncio
import foruse.log as log
from .fs import LocalFS
from .buffer import BufferStream
from foruse import *


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
			
		self._chunk_size = kwargs.get('chunk_size', 8192)
		self._read_loop_waiter = None
		self._start_seek = 0
		
		self._create_buffer(*args, **kwargs)
		
	def set_min_size(self, size):
		if size <= self._buffer._max_size:
			self._buffer._min_size = size
	
	
	def _create_buffer(self, *args, **kwargs):
		self._buffer = BufferStream(max_size=kwargs.get('max_size'), min_size=kwargs.get('min_size'))
		
		
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
		await self._buffer.stop()
		await self._stop_read_loop()
		await self._close()
	
	async def eof(self):
		if self._read_loop_waiter is not None:
			pos = await self.tell()
			size = await self.size()
			return pos >= size
		else:
			return await self._eof()
	
	async def flush(self):
		await self._flush()
	
	async def size(self):
		return await self._size()
	
	async def seek(self, offset, whence = SEEK_SET):
		await self._stop_read_loop()
		await self._seek(offset, whence)
		self._start_seek = await self._tell()
	
	async def tell(self):
		if self._read_loop_waiter is not None:
			return self._start_seek + self._buffer._count_readed
		else:
			return await self._tell()
		
	# -----------------------------------------------------------------------------
	#                               Write To Stream
	# -----------------------------------------------------------------------------
	
	async def write(self, buff):
		if self.writable():
			await self._stop_read_loop()
			await self._write(buff)
		
		else:
			raise IOException("Write to unwritable stream")
	#!enddef write
	
	
	# -----------------------------------------------------------------------------
	#                               Read From Stream
	# -----------------------------------------------------------------------------
	
	async def _loop_read(self):
		self._read_loop_waiter = asyncio.futures.Future(loop=self._loop)
		#print ('Start loop!')
		
		try:
			#print (await self._eof())
			while not self._buffer.is_stop() and not await self._eof():
				data = await self._read(self._chunk_size)
				if len(data) > 0:
					await self._buffer.write(data)
				
		except Exception as e:
			print (e)
			self._buffer.set_exception(e)
		
		#print ('Stop loop!')
		await self._buffer.stop()
		self._read_loop_waiter.set_result(None)
		self._read_loop_waiter = None
	#!enddef
	
	
	async def _try_start_read_loop(self):
		if self._read_loop_waiter is None:
			await self._buffer.clear()
			self._loop.create_task(self._loop_read())
	#!enddef
	
	
	async def _stop_read_loop(self):
		if self._read_loop_waiter is not None:
			await self._read_loop_waiter
			self._read_loop_waiter = None
	#!enddef
	
	
	async def get_read_buffer():
		if self.readable():
			await self._try_start_read_loop()
			return self._buffer
			
		else:
			raise IOException("Read from unreadable stream")
		
		return None
	#!enddef
	
		
	async def read(self, count = -1):
		try:
			count = int(count)
		except:
			count = -1
		
		if self.readable():
			await self._try_start_read_loop()
			return await self._buffer.read(count)
			
		else:
			raise IOException("Read from unreadable stream")
	#!enddef read
	
	
	async def skip(self):
		if self.readable():
			await self._try_start_read_loop()
			await self._buffer.skip()
		else:
			raise IOException("Read from unreadable stream")
	#!enddef skip
	
	
	async def skip_line(self):
		if self.readable():
			await self._try_start_read_loop()
			await self._buffer.skip_line()
		else:
			raise IOException("Read from unreadable stream")
	#!enddef skip_line
	
	
	async def get_line_stream(self):
		if self.readable():
			await self._try_start_read_loop()
			return await self._buffer.get_line_stream()
		else:
			raise IOException("Read from unreadable stream")
	#!enddef get_line_stream
	
	
	async def readline(self, maxlen = -1):
		if self.readable():
			await self._try_start_read_loop()
			return await self._buffer.readline(maxlen)
		else:
			raise IOException("Read from unreadable stream")
	#!enddef readline
	
	
	async def readline_skip(self):
		if self.readable():
			await self._try_start_read_loop()
			return await self._buffer.readline_skip()
		else:
			raise IOException("Read from unreadable stream")
	#!enddef readline_skip
	
	
	async def get_count_stream(self):
		if self.readable():
			await self._try_start_read_loop()
			return await self._buffer.get_count_stream()
		else:
			raise IOException("Read from unreadable stream")
	#!enddef get_count_stream
	

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
		self._list = []
		
	
	def seekable(self):
		return True
	
	def writable(self):
		return False
	
	def readable(self):
		return True
	
	
	async def _try_lock_read(self):
		if len(self._list) == 0 and not self._is_stop and not self._is_eof:
			await self._lock_read()
	
	async def _lock_read(self):
		if self._read_waiter is None:
			self._read_waiter = asyncio.futures.Future(loop=self._loop)
		try:
			await self._read_waiter
		finally:
			self._read_waiter = None
	#!enddef
	
	def _unlock_read(self):
		if self._read_waiter is not None:
			self._read_waiter.set_result(None)
		self._read_waiter = None
	#!enddef
	
	
	async def stop(self):
		self._is_stop = True
		self._unlock_read()
		
	async def _open(self):
		return True
	
	async def _close(self):
		self._list = []
		self._is_eof = True
		self._is_stop = True
		self._unlock_read()
	
	async def _read(self, count=-1):
		await self._try_lock_read()
		if len(self._list) == 0:
			return []
		
		data = self._list[0]
		del self._list[0]
		
		return data
	
	def feed_data(self, buf):
		if not self._is_stop:
			self._list.append(buf)
			self._unlock_read()
	
	def feed_flush(self):
		asyncio.ensure_future(self._buffer.flush())
	
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
		return len(self._list) == 0 and self._is_eof == True
	
	async def eof(self):
		return len(self._list) == 0 and self._is_eof == True
	
	async def _flush(self):
		pass
		
#!endclass MemoryStream	