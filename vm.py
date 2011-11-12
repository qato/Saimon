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

import os

import utils
import reader.normalization
from file_watcher import FileWatcher
from file_watcher import UpdateMode
from property import Property

class Vm:

	__stat_cpu_lbl = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest']
	__cpu_perc = dict()
	__elapsed = -1
	__property = None

	# constructor
	def __init__(self):
		self.__property = Property()
		# /proc/%d/stat
		self.__fstat = FileWatcher('/proc/stat')
		self.__fstat.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fstat.setSeparator(' ')
		self.update()
		self.__property.add('cpu_details', self.__callbackCpu)
		self.__property.add('cpu_perc', self.__callbackCpu)
		self.__property.add('cpu_elapsed', self.__callbackCpu)

	def __callbackCpu(self, property):
		if (property=='cpu_elapsed'):
			prev = self.__calc_cpu_time(self.__fstat.getPrevious()['cpu'])
			curr = self.__calc_cpu_time(self.__fstat.getCurrent()['cpu'])
			self.__property.set('cpu_elapsed', curr-prev)
		if (property=='cpu_perc'):
			self.__calc_cpu_perc(self.__property.get('cpu_elapsed'), self.__fstat.getCurrent()['cpu'].split(), self.__fstat.getPrevious()['cpu'].split())
			self.__property.set('cpu_perc', self.__cpu_perc)
		if (property=='cpu_details'):
			curr = self.__fstat.getCurrent()
			self.__property.set('cpu_details', reader.normalization.arrayToDict(curr['cpu'].split(), self.__stat_cpu_lbl))

	# private methods	
	def __calc_cpu_time(self, cpu):
		sum = 0
		if cpu:
			for value in cpu.split():
				sum = sum + int(value)
		return sum
	
	def __calc_cpu_perc(self, total, curr, prev):
		if (len(curr)!=len(prev) or len(curr)!=len(self.__stat_cpu_lbl)): return
		result = dict()
		for i in range(0,len(curr)):
			self.__cpu_perc[self.__stat_cpu_lbl[i]] = utils.perc(int(curr[i]) - int(prev[i]), total)
	
	# getter/setter
	def getElapsed(self): 
		return self.__property.get('cpu_elapsed')
	
	def getCpuDetails(self):		
		return self.__property.get('cpu_details')
	
	def getCpuPerc(self): 
		return self.__property.get('cpu_perc')
	
	# public methods
	def update(self):
		self.__fstat.update()
		self.__property.invalidateAll()

	def eval(self):
		pass
