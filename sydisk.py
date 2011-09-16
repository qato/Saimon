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
#	Copyright (C) 2011  qato@qatoproject.it
#	
from decimal import *
from time import *
import os
import sys
import getopt
import time

from systat import * 

class DiskStat:
	__ticks_per_disk = {}
	__disk = []
	__perc = 0
	__num_mon = 0

	def __init__(self):
		for dirname in os.listdir('/sys/block'):
			for dirdev in os.listdir(os.path.join('/sys/block', dirname)):
					if (dirdev=='device'):
						self.__disk.append(dirname)
		
	def check(self):	
		sys_delta_time=getSysDeltaTime()
		self.__perc=0
		self.__num_mon=0
		fname='/proc/diskstats'
		fin = open(fname, 'r')
		for line in fin:
			line = line.strip()
			field = line.split()
			device=field[2]
			if (len(field)>12) and (device in self.__disk):
				self.__num_mon+=1
				tot_ticks=int(field[12])
				prev_ticks = 0
				if device in self.__ticks_per_disk:
					prev_ticks=self.__ticks_per_disk[device]
					delta=float(tot_ticks-prev_ticks)/sys_delta_time*10
					if delta>100: delta=100
					self.__perc+=delta
				self.__ticks_per_disk[device] = tot_ticks
			
		fin.close()	
		self.__perc=float(self.__perc/len(self.__ticks_per_disk))

	def get_perc(self):
		return self.__perc

	def get_num_mon(self):
		return len(self.__ticks_per_disk)	

	def get_disks(self):
		return self.__ticks_per_disk

class Disk:
	def __init__(self, disk):
		self.__disk=disk
		self.__rd_ios=0
		self.__rd_merges_or_rd_sec=0
		self.__rd_sec_or_wr_ios=0
		self.__rd_ticks_or_wr_sec=0
		self.__wr_ios=0
		self.__wr_merges=0
		self.__wr_sec=0
		self.__wr_ticks=0
		self.__ios_pgr=0
		self.__tot_ticks=0
		self.__rq_ticks=0
		self.__delta_rd_ios=0
		self.__delta_rd_merges_or_rd_sec=0
		self.__delta_rd_sec_or_wr_ios=0
		self.__delta_rd_ticks_or_wr_sec=0
		self.__delta_wr_ios=0
		self.__delta_wr_merges=0
		self.__delta_wr_sec=0
		self.__delta_wr_ticks=0
		self.__delta_ios_pgr=0
		self.__delta_tot_ticks=0
		self.__delta_rq_ticks=0

	def check(self):
		sys_delta_time=getSysDeltaTime()
		fname='/proc/diskstats'
		if os.path.exists(fname):
			fin = open(fname, 'r')
			for line in fin:
				line = line.strip()
				field = line.split()
				if field[2]==self.__disk:
					rd_ios=int(field[3])
					rd_merges_or_rd_sec=int(field[4])
					rd_sec_or_wr_ios=int(field[5])
					rd_ticks_or_wr_sec=int(field[6])
					wr_ios=int(field[7])
					wr_merges=int(field[8])
					wr_sec=int(field[9])
					wr_ticks=int(field[10])
					ios_pgr=int(field[11])
					tot_ticks=int(field[12])
					rq_ticks=int(field[13])
			fin.close()
			if self.__rd_ios!=0:				
				self.__delta_rd_ios=(rd_ios-self.__rd_ios)/sys_delta_time*100
				self.__delta_rd_merges_or_rd_sec=(rd_merges_or_rd_sec-self.__rd_merges_or_rd_sec)/sys_delta_time*100
				self.__delta_rd_sec_or_wr_ios=(rd_sec_or_wr_ios-self.__rd_sec_or_wr_ios)/sys_delta_time*100
				self.__delta_rd_ticks_or_wr_sec=(rd_ticks_or_wr_sec-self.__rd_ticks_or_wr_sec)/sys_delta_time*100
				self.__delta_wr_ios=(wr_ios-self.__wr_ios)/sys_delta_time*100
				self.__delta_wr_merges=(wr_merges-self.__wr_merges)/sys_delta_time*100
				self.__delta_wr_sec=(wr_sec-self.__wr_sec)/sys_delta_time*100
				self.__delta_wr_ticks=(wr_ticks-self.__wr_ticks)/sys_delta_time*100
				self.__delta_ios_pgr=(ios_pgr-self.__ios_pgr)/sys_delta_time*100
				self.__delta_tot_ticks=(tot_ticks-self.__tot_ticks)/sys_delta_time*100
				self.__delta_rq_ticks=(rq_ticks-self.__rq_ticks)/1000
				#'''self.__delta_rq_ticks=((rq_ticks-self.__rq_ticks)/sys_delta_time*100)/1000'''
			self.__rd_ios=rd_ios
			self.__rd_merges_or_rd_sec=rd_merges_or_rd_sec
			self.__rd_sec_or_wr_ios=rd_sec_or_wr_ios
			self.__rd_ticks_or_wr_sec=rd_ticks_or_wr_sec
			self.__wr_ios=wr_ios
			self.__wr_merges=wr_merges
			self.__wr_sec=wr_sec
			self.__wr_ticks=wr_ticks
			self.__ios_pgr=ios_pgr
			self.__tot_ticks=tot_ticks
			self.__rq_ticks=rq_ticks

	def show(self):
		sys_delta_time=getSysDeltaTime()
		if sys_delta_time!=0:
			print '%s\t%s r/s:%.2f w/s:%.2f tot:%.2f rq/s:%.2f' % ( strftime("%H:%M:%S", gmtime()), self.__disk, self.__delta_rd_ios, self.__delta_wr_ios, self.__delta_tot_ticks, self.__delta_rq_ticks)
		'''if self.__rd_ios!=0:				
			print '\t%s\t'''

