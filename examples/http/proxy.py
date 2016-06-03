#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import asyncio
import uvloop
from foruse import *
from foruse.aio.http import *

class MyClient(HttpClient):
	
	def data_received(self, data):
		super().data_received(data)
		#print (data)

#!MyClient
		
		
class ProxyServer(HTTPServer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	
	async def handle_request_end(self, request, answer):
		await super().handle_request_end(request, answer)
		self.client.close()
		
		
	async def handle_request(self, request):
		self._log.debug3 ('handle_request')
		
		try:
			#request.set_header('Connection', 'close')
			request.set_header('Host', 'bayrell.org')
			
			self.client = await MyClient.connect('bayrell.org', 80)
			
			reader = self.client.get_reader()
			#reader._log.set_level('DEBUG3');
			
			await self.client.send_request(request)
			answer = await self.client.get_answer()
			
			if answer != None:
				answer.delete_header('Connection')
				return answer
			
		except:
			return await self.create_error_answer(504)

		return None		

#!ProxyServer


log.set_level('DEBUG3')

loop = asyncio.get_event_loop()
print ('Start server on 0.0.0.0:8080')
asyncio.ensure_future(loop.create_server(
	lambda: ProxyServer(),
	'0.0.0.0', 8080
))
try:
	loop.run_forever()
	pass
except KeyboardInterrupt:
	loop.stop()
	pass
