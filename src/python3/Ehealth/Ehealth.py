import threading
import logging
import EhealthSerial
from EhealthException import EhealthException


class Ehealth:

	def __init__(port,baud,timeout,callbacks = None):
		self.__port = port
		self.__baud = baud
		self.__timeout = timeout
		try:
			self__connection = EhealthSerial.EhealthSerial(port,baud,timeout = timeout)
		except:
			raise EhealthException('Could not Make Serial Connection')
		else:
			if callbacks is None:
				self.__callbacks = []
			else:
				self.__callbacks = callbacks
