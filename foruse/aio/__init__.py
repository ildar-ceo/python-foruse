# -*- coding: utf-8 -*-

import asyncio

from .fs import *
from .streams import *
from .connection import *


def call_later(time, func):
	return asyncio.get_event_loop().call_later(time, func)