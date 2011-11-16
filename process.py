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
from reader.normalization import procStatNormFn
from file_watcher import FileWatcher
from file_watcher import UpdateMode
from property import Property

class Process:

	__pid = 0
	__fstat = None
	__fstatus = None
	__fio = None
	__stat_lbl = ['pid', 'cmd','state','ppid','pgrp','sid','tty_nr','tty_pgrp','flags','min_flt','cmin_flt','maj_flt','cmaj_flt','utime','stime','cutime','cstime','priority','nice','num_threads','it_real_value','start_time','vsize','rss','rsslim','start_code','end_code','start_stack','esp','eip','pending','blocked','sigign','sigcatch','wchan','exit_signal','task_cpu','rt_priority','policy','blkio_ticks','gtime','cgtime']
	__property = None

	def __init__(self, pid):
		self.__property = Property()
		self.__pid = pid
		self.__property.add("pid_%d" % pid, None)
		
		# /proc/%d/stat
		self.__fstat = FileWatcher('/proc/%d/stat' % pid)
		self.__fstat.setLabel(self.__stat_lbl)
		self.__fstat.setLineNormalizationFunc(procStatNormFn)
		self.__fstat.setUpdateMode(UpdateMode.TABLE)
		
		# /proc/%d/status
		self.__fstatus = FileWatcher('/proc/%d/status' % pid)
		self.__fstatus.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fstatus.setSeparator(':')

		# /proc/%d/io
		self.__fio = FileWatcher('/proc/%d/io' % pid)
		self.__fio.setUpdateMode(UpdateMode.DICTIONARY)
		self.__fio.setSeparator(':')
		
		self.__property.add('cpu_usr', self.__property_callback)
		self.__property.add('cpu_sys', self.__property_callback)
		self.__property.add('cpu_delta', self.__property_callback)
		self.__property.add('status', self.__property_callback)
		self.__property.add('io', self.__property_callback)
		self.__property.add('io_delta', self.__property_callback)
		self.__property.add('delta', None)

	def __property_callback(self, property):
		if (property[0:2]=='io'):
			curr, prev = self.__fio.getCurrent(), self.__fio.getPrevious()
			self.__property.set('io_delta', self.__calc_delta(curr, prev))
			self.__property.set('io', utils.convert_values_to_byte(curr))
		if (property[0:3]=='cpu'):
			curr, prev = self.__fstat.getCurrent(), self.__fstat.getPrevious()
			usr, sys = self.__calc_cpu(curr, prev, self.__property.get('delta'))
			self.__property.set('cpu_usr', usr)
			self.__property.set('cpu_sys', sys)
			self.__property.set('cpu_delta', self.__calc_delta(curr[0], prev[0]))
			self.__property.set('status', utils.convert_values_to_byte(curr[0]))
		
#	def __del__(self):
#		print "kill %d" % self.__pid

	# getter/setter
	def getCpuDetails(self): return { "usr" : self.__property.get('cpu_usr'), "sys" : self.__property.get('cpu_sys') }
	def getCpu(self): return self.__property.get('cpu_usr') + self.__property.get('cpu_sys')
	
	def getPID(self): return self.__pid

	def getStatus(self): return self.__property.get('status')
	def getStatusDelta(self): return self.__property.get('status_delta')

	def getIO(self): return self.__property.get('io')
	def getIOSysCall(self): 
		v = self.__property.get('io_delta')
		return v['syscr'] + v['syscw']
	def getIOBytes(self): 
		v = self.__property.get('io_delta')
		return v['rchar'] + v['wchar']
	def getIODelta(self): return self.__property.get('io_delta')

	# private methods	
	def __calc_delta(self, curr, prev):
		curr = utils.convert_values_to_byte(curr)
		prev = utils.convert_values_to_byte(prev)
		return utils.calc_delta(curr, prev)
	
	def __calc_cpu(self, curr, prev, delta):
		if (not curr or not prev or not delta): return 0,0
		if (delta > 0):
			return utils.perc(int(curr[0]['utime']) - int(prev[0]['utime']), delta), utils.perc(int(curr[0]['stime']) - int(prev[0]['stime']), delta)
		return 0,0
	
	def update(self):
		# stat
		self.__fstat.update()
		# status
		self.__fstatus.update()
		# io
		self.__fio.update()
		self.__property.invalidateAll()
		
	def eval(self, delta):
		self.__property.set('delta', delta)
