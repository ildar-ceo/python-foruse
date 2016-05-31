# -*- coding: utf-8 -*-

import os
import asyncio
import foruse.log as log


class AbstractFS(log.Log):
	SEEK_SET = 0
	SEEK_CUR = 1
	SEEK_END = 2
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.loop = kwargs.get('loop')
		if self.loop == None:
			self.loop = asyncio.get_event_loop()
		
	async def file_exists(self, file_name):
		pass
	
	async def file_open(self, file_name, mode):
		return None
	
	async def file_read(self, handle, max_size=1024):
		pass	
		
	async def file_write(self, handle, buf):
		pass
		
	async def file_close(self, handle):
		pass
	
	async def file_seek(self, seek):
		pass
	
	async def file_delete(self, file_name):
		pass
	
#!endclass AbstractFS

	

class LocalFS(AbstractFS):
	
	async def file_exists(self, file_name):
		return await self.loop.run_in_executor(None, os.path.exists, file_name)
	
	async def file_size(self, file_name):
		statinfo = await self.loop.run_in_executor(None, os.stat, file_name) 
		return statinfo.st_size
		
	async def file_delete(self):
		pass
	
	async def file_open(self, file_name, mode):
		return await self.loop.run_in_executor(None, open, file_name, mode)
	
	async def file_read(self, handle, max_size=1024):
		return await self.loop.run_in_executor(None, handle.read, max_size) 	
		
	async def file_write(self, handle, buf):
		await self.loop.run_in_executor(None, handle.write, buf) 
		
	async def file_close(self, handle):
		await self.loop.run_in_executor(None, handle.close) 
	
	async def file_pos(self, handle):
		return await self.loop.run_in_executor(None, handle.tell) 
	
	async def file_seek(self, handle):
		pass
	
#!endclass LocalFS