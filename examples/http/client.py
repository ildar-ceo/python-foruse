#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from foruse import *
from foruse.aio.http import *

	
async def connect():
	
	client = await HttpClient.connect('127.0.0.1', 8080)
	reader = client.get_reader()
	
	request = client.create_request()
	#request.set_header('Connection', 'close')
	request.set_header('Host', 'bayrell.org')
	
	await request.send()
	answer = await client.get_answer()
	
	if answer:
		body = answer.get_body_stream()
		
		#body._log.set_level('DEBUG3')
		while not await body.eof():
			data = await body.read()
			print (data)
	
	await request.parse_end()
	
	client.close()
	
	#create_connection
	
#enddef connect
	
log.set_level('DEBUG3')
	
tasks=[]
loop = asyncio.get_event_loop()
tasks.append(loop.create_task(connect()))

try:
	loop.run_until_complete(asyncio.wait(tasks))
	pass
except KeyboardInterrupt:
	loop.stop()
	pass