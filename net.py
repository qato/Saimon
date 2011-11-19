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
import ethtools
import reader.normalization
from file_watcher import FileWatcher
from file_watcher import UpdateMode
from property import Property
from reader.proc_file_reader import ProcFileReader

# /sys/class/net/eth0/features

class Net:

	__net_lbl = ['rxbytes', 'rxpackets', 'rxerrs', 'rxdrop', 'rxfifo', 'rxframe', 'rxcompressed', 'rxmulticast', \
				'txbytes', 'txpackets', 'txerrs', 'txdrop', 'txfifo', 'txcolls', 'txcarrier', 'txcompressed']
	__net_speed = {}
	__net_speed_max = 0
	__fnet = None
	__property = None
	__rxmax = 0
	__txmax = 0
	__last_update = 0
	__elapsed = 0
	
	
	def __init__(self):
		self.__property = Property()
		# /proc/stat
		self.__fnet = FileWatcher('/proc/net/dev')
		self.__fnet.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fnet.setSeparator(':')
		self.__fnet.setLabel(self.__net_lbl)
		self.__property.add('net', self.__callback)
		self.__property.add('net_delta', self.__callback)
		self.__property.add('net_usage', self.__callback)

	# private methods
	def __get_speed(self, flag):
		speed = 10
		v = flag & 0xC0
		if (v==0x80): speed=1000
		if (v==0x40): speed=100
		return speed

	def __get_net_features(self, i):
		speed = 0
		f = ProcFileReader('/sys/class/net/%s/features' % i)
		if (f.open()):
			feature = int(f.readLine(False),0)
			speed = self.__get_speed(feature)
			f.close()
		return speed
	
	def __get_net_speed(self, device):
		speed = 0
		try:
			speed = ethtools.ethtool_get_speed(device)
		except IOError:
			speed =  self.__get_net_features(device)
		self.__net_speed[device] = (speed*1024*1024/8)
		self.__net_speed_max += self.__net_speed[device] 
		
	def __normalize(self, data):
		result = {}
		values = reader.normalization.arrayToDict(data.split(), self.__net_lbl)
		result= utils.convert_values_to_byte(values)
		return result

	def __sum_field(self, data, field):
		result = 0
		for k in data.keys():
			result+=data[k][field]
		return result

	def __callback(self, property):
		delta = {}
		current = {}
		curr, prev = self.__fnet.getCurrent(), self.__fnet.getPrevious()
		for k in curr.keys():
			if (k=='lo'): continue
			if (k not in self.__net_speed): self.__get_net_speed(k)
			c = self.__normalize(curr[k])
			p = self.__normalize(prev[k])
			delta[k] = utils.calc_delta(c, p)
			current[k] = c
		self.__property.set('net', current)
		self.__property.set('net_delta', delta)
		rmax = self.__sum_field(delta, 'rxbytes')
		tmax = self.__sum_field(delta, 'txbytes')
		if (rmax>self.__rxmax): self.__rxmax = rmax
		if (tmax>self.__txmax): self.__txmax = tmax
		self.__property.set('net_usage', { 'tot': utils.perc(rmax+tmax, self.__net_speed_max * self.__elapsed / 1000), 'rx' : utils.perc(rmax, self.__rxmax), 'tx' : utils.perc(tmax, self.__txmax)})

	def getStatus(self): return self.__property.get('net')
	def getDelta(self): return self.__property.get('net_delta')
	def getUsage(self): return self.__property.get('net_usage')
	
	# public methods
	def update(self):
		self.__fnet.update()
		
		now = utils.get_msec()
		self.__elapsed = now - self.__last_update
		self.__last_update = now
		
		self.__property.invalidateAll()

	def eval(self):
		pass
