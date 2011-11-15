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
from file_watcher import FileWatcher
from file_watcher import UpdateMode
from property import Property

class Disk:

	__fdiskstats = None
	__diskstat_lbl = ['maj', 'min', 'device', 'rd' ,'rd_merged', 'rc_sec', 'rd_ms', 'wr' ,'wr_merged', 'wr_sec', 'wr_ms', 'io_prog', 'io_ms', 'weighted_ms']
	__property = None
	__disks = 0
	__last_update = 0
	__elapsed = 0

	def __init__(self):
		disk = []
		self.__property = Property()
		for dirname in os.listdir('/sys/block'):
			for dirdev in os.listdir('/sys/block/' + dirname):
					if (dirdev=='device'):
						disk.append(dirname)
		self.__disks = len(disk)
		
		self.__fdiskstats = FileWatcher('/proc/diskstats')
		self.__fdiskstats.setLabel(self.__diskstat_lbl)
		self.__fdiskstats.setUpdateMode(UpdateMode.TABLE)
		self.__fdiskstats.setFilter({'col': 2, 'values': disk})
		
		self.__property.add('disk_perc', self.__property_callback)

	def __calc_disk_usage(self, devices):
		result = 0
		for dev in devices:
			result+=int(devices[dev]['io_ms'])
		return result
		
	def __property_callback(self, property):
		curr = self.__calc_disk_usage(self.__fdiskstats.getCurrent())
		prev = self.__calc_disk_usage(self.__fdiskstats.getPrevious())
		self.__property.set('disk_perc', utils.perc((curr-prev), self.__elapsed ))
	
	def getDiskPerc(self):
		return self.__property.get('disk_perc')
	
	def getDiskNum(self):
		return self.__disks

	def update(self):
		self.__fdiskstats.update()

		now = utils.get_msec()
		self.__elapsed = now - self.__last_update
		self.__last_update = now
		
		self.__property.invalidateAll()

	