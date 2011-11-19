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

from process import Process

class ProcessList:
	__plist = {}
	__pids = set()

	# private methos
	def __getProcByPid(self, pid):
		proc = None
		if self.__plist.has_key(pid):
			proc = self.__plist[pid]
		else:
			proc = Process(pid)
			self.__plist[pid] = proc
		return proc

	def __sort_process_by(self, keys):
		sorted_plist = []
		if self.__plist:
			sorted_plist = [(k, v) for k, v in self.__plist.iteritems()]
			for key in reversed(keys):
				sorted_plist = sorted(sorted_plist, cmp=lambda x, y: cmp(x[1].get(key), y[1].get(key)), reverse=True)
		return sorted_plist

	# getter/setter
	def getProcessList(self): return self.__plist
	def getSortedProcessList(self, keys = ['cpu']): return self.__sort_process_by(keys)
	def getPids(self): return self.__pids
	def getProcessByPid(self, pid):
		if self.__plist.has_key(pid):
			return self.__plist[pid]
		return None
		
	# public methods
	def update(self):
		pids=set()

		# Retrieve pid list
		for dirname in os.listdir('/proc'):
			if dirname[0]>='0' and dirname[0]<='9':
				pid=int(dirname)
				pids.add(pid)
				self.__getProcByPid(pid).update()

		# Process started
		for pid in (pids - self.__pids):
			self.__pids.add(pid)

		# Process terminated
		for pid in (self.__pids - pids):
			self.__pids.remove(pid)
			del self.__plist[pid]

	def eval(self, delta):
		for pid in self.__pids:
			self.__plist[pid].eval(delta)
