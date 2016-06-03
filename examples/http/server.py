#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import asyncio
import uvloop
from foruse import *
from foruse.aio.http import *


class MyServer(HTTPServer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._log.set_level('DEBUG3')
		
		
	async def handle_request(self, request):
		self._log.debug3 ('handle_request')
		
		answer = request.create_answer()
		answer.set_header('Content-type', 'text/html')
		#answer.set_header('Connection', 'close')
		answer.write(b'Hello world!!!')
		answer.write_eof()
		
		return answer
#!MyServer


loop = asyncio.get_event_loop()
print ('Start server on 0.0.0.0:8080')
asyncio.ensure_future(loop.create_server(
	lambda: MyServer(),
	'0.0.0.0', 8080
))
try:
	loop.run_forever()
	pass
except KeyboardInterrupt:
	loop.stop()
	pass
