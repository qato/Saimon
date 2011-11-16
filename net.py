#!/usr/bin/env python
#
#    This file is part of SAIMON.
#
#    Saimon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Saimon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Saimon.  If not, see <http://www.gnu.org/licenses/>.
#       
#       Copyright (C) 2011  qato@qatoproject.it
#       

import utils
import reader.normalization
from file_watcher import FileWatcher
from file_watcher import UpdateMode
from property import Property
from reader.proc_file_reader import ProcFileReader

class Net:

	__net_lbl = ['rxbytes', 'rxpackets', 'rxerrs', 'rxdrop', 'rxfifo', 'rxframe', 'rxcompressed', 'rxmulticast', \
				'txbytes', 'txpackets', 'txerrs', 'txdrop', 'txfifo', 'txcolls', 'txcarrier', 'txcompressed']
	__fnet = None
	__property = None
	
	def __init__(self):
		self.__property = Property()
		# /proc/stat
		self.__fnet = FileWatcher('/proc/net/dev')
		self.__fnet.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fnet.setSeparator(':')
		self.__fnet.setLabel(self.__net_lbl)
		self.__property.add('net', self.__callback)
		self.__property.add('net_delta', self.__callback)

	# private methods
	def __normalize(self, data):
		result = {}
		values = reader.normalization.arrayToDict(data.split(), self.__net_lbl)
		result= utils.convert_values_to_byte(values)
		return result

	def __callback(self, property):
		delta = {}
		current = {}
		curr, prev = self.__fnet.getCurrent(), self.__fnet.getPrevious()
		for k in curr.keys():
			c = self.__normalize(curr[k])
			p = self.__normalize(prev[k])
			delta[k] = utils.calc_delta(c, p)
			current[k] = c
		self.__property.set('net', current)
		self.__property.set('net_delta', delta)

	def getStatus(self): return self.__property.get('net')
	def getDelta(self): return self.__property.get('net_delta')
	
	# public methods
	def update(self):
		self.__fnet.update()
		self.__property.invalidateAll()

	def eval(self):
		pass
