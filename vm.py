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
from reader.proc_file_reader import ProcFileReader

class Vm:

	__stat_cpu_lbl = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest']
	__avg_lbl = ['1m', '5m', '15m', 'running_threads', 'last_pid']
	__elapsed = -1
	__fstat = None
	__favg = None
	__fuptime = None
	__fmeminfo = None
	__fvmstat = None
	__property = None
	__kernel_release = None
	__hostname = None

	# constructor
	def __init__(self):
		self.__property = Property()
		# /proc/stat
		self.__fstat = FileWatcher('/proc/stat')
		self.__fstat.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fstat.setSeparator(' ')
		# /proc/loadavg
		self.__favg = FileWatcher('/proc/loadavg')
		self.__favg.setUpdateMode(UpdateMode.TABLE)
		self.__favg.setLabel(self.__avg_lbl)
		self.__favg.setSeparator(' ')
		# /proc/uptime
		self.__fuptime = FileWatcher('/proc/uptime')
		self.__fuptime.setUpdateMode(UpdateMode.TABLE)
		self.__fuptime.setSeparator(' ')
		# /proc/meminfo
		self.__fmeminfo = FileWatcher('/proc/meminfo')
		self.__fmeminfo.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fmeminfo.setSeparator(' ')
		# /proc/vmstat
		self.__fvmstat = FileWatcher('/proc/vmstat')
		self.__fvmstat.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fvmstat.setSeparator(' ')
		
		self.update()
		self.__property.add('cpu_details', self.__callbackCpu)
		self.__property.add('cpu_perc', self.__callbackCpu)
		self.__property.add('cpu_elapsed', self.__callbackCpu)
		self.__property.add('avg', self.__callbackAvg)
		self.__property.add('uptime', self.__callbackUptime)
		self.__property.add('meminfo', self.__callbackMeminfo)
		self.__property.add('delta_meminfo', self.__callbackMeminfo)
		self.__property.add('vmstat', self.__callbackVmstat)
		self.__property.add('delta_vmstat', self.__callbackVmstat)

		self.__get_kernel_values()

	def __callbackCpu(self, property):
		if (property=='cpu_elapsed'):
			prev = self.__calc_cpu_time(self.__fstat.getPrevious()['cpu'])
			curr = self.__calc_cpu_time(self.__fstat.getCurrent()['cpu'])
			self.__property.set('cpu_elapsed', curr-prev)
		if (property=='cpu_perc'):
			self.__property.set('cpu_perc', self.__calc_cpu_perc(self.__property.get('cpu_elapsed'), self.__fstat.getCurrent()['cpu'].split(), self.__fstat.getPrevious()['cpu'].split()))
		if (property=='cpu_details'):
			curr = self.__fstat.getCurrent()
			self.__property.set('cpu_details', reader.normalization.arrayToDict(curr['cpu'].split(), self.__stat_cpu_lbl))

	def __callbackUptime(self, property):
		curr = self.__fuptime.getCurrent()
		print "curr:",curr
		if curr:
			total_seconds = float(curr[0][0])
			minute = 60; hour = minute * 60; day = hour * 24
			days = int( total_seconds / day )
			hours = int( ( total_seconds % day ) / hour )
			minutes = int( ( total_seconds % hour ) / minute )
			seconds = int( total_seconds % minute )
			self.__property.set('uptime', '%dd:%dh:%dm:%ds' % (days, hours, minutes, seconds))

	def __callbackAvg(self, property):
		curr = self.__favg.getCurrent()[0]
		run_thr = curr['running_threads']
		if run_thr:
			tmp = run_thr.split('/')
			if tmp:
				curr['running'] = tmp[0]
				curr['threads'] = tmp[1]
			del curr['running_threads']
			
		self.__property.set('avg', curr)

	def __convert_to_byte(self, values):
		result = {}
		for (k,v) in values.iteritems():
			if (v[-3:]==' kB'):
				v=int(v[0:-3])*1024
			else:
				if (type(v)==type('') and v.isdigit()):
					v=int(v)
			result[k]=v
		return result

	def __callbackMeminfo(self, property):
		curr = self.__convert_to_byte(self.__fmeminfo.getCurrent())
		prev = self.__convert_to_byte(self.__fmeminfo.getPrevious())
		self.__property.set('meminfo', curr)
		self.__property.set('delta_meminfo', utils.calc_delta(curr, prev))

	def __callbackVmstat(self, property):
		curr = self.__fvmstat.getCurrent()
		prev = self.__fvmstat.getPrevious()
		self.__property.set('vmstat', curr)
		self.__property.set('delta_vmstat', utils.calc_delta(curr, prev))
		
	# private methods	
	def __get_kernel_values(self):
		f = ProcFileReader('/proc/sys/kernel/osrelease')
		if (f.open()):
			self.__kernel_release = f.readLine(False)
			f.close()
		f = ProcFileReader('/proc/sys/kernel/hostname')
		if (f.open()):
			self.__hostname = f.readLine(False)
			f.close()
		
	def __calc_cpu_time(self, cpu):
		sum = 0
		if cpu:
			for value in cpu.split():
				sum = sum + int(value)
		return sum
	
	def __calc_cpu_perc(self, total, curr, prev):
		cpu_perc = {}
		if (len(curr)!=len(prev) or len(curr)!=len(self.__stat_cpu_lbl)): return cpu_perc
		for i in range(0,len(curr)):
			cpu_perc[self.__stat_cpu_lbl[i]] = utils.perc(int(curr[i]) - int(prev[i]), total)
		return cpu_perc
	
	# getter/setter
	def getElapsed(self): 
		return self.__property.get('cpu_elapsed')
	
	def getCpuDetails(self):		
		return self.__property.get('cpu_details')
	
	def getCpuPerc(self): 
		return self.__property.get('cpu_perc')

	def getAvg(self): 
		return self.__property.get('avg')

	def getUptime(self): 
		return self.__property.get('uptime')

	def getMeminfo(self): 
		return self.__property.get('meminfo')

	def getMeminfoDelta(self): 
		return self.__property.get('delta_meminfo')

	def getVmstat(self): 
		return self.__property.get('vmstat')
	
	def getVmstatDelta(self):
		return self.__property.get('delta_vmstat')

	def getHostname(self): return self.__hostname
	def getKernelRelease(self): return self.__kernel_release
	
	# public methods
	def update(self):
		self.__fstat.update()
		self.__favg.update()
		self.__fuptime.update()
		self.__fmeminfo.update()
		self.__fvmstat.update()
		self.__property.invalidateAll()

	def eval(self):
		pass
