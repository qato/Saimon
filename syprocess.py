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

class Process:
	__pid=0
	__prev_wchar=0
	__prev_rchar=0
	__prev_syscr=0
	__prev_syscw=0
	__prev_read_bytes=0
	__prev_write_bytes=0
	__prev_cancelled_write_bytes=0
	__delta_wchar=0
	__delta_rchar=0
	__delta_syscr=0
	__delta_syscw=0
	__delta_read_bytes=0
	__delta_write_bytes=0
	__delta_cancelled_write_bytes=0
	__cmdline=''
	__prev_utime=0
	__prev_stime=0
	__tcomm=''
	__state=''
	__ppid=0
	__pgrp=0
	__sid=0
	__tty_nr=0
	__tty_pgrp=0
	__flags=0
	__min_flt=0
	__cmin_flt=0
	__maj_flt=0
	__cmaj_flt=0
	__utime=0
	__stime=0
	__cutime=0
	__cstime=0
	__priority=0
	__nice=0
	__num_threads=0
	__it_real_value=0
	__start_time=0
	__vsize=0
	__rss=0
	__rsslim=0
	__start_code=0
	__end_code=0
	__start_stack=0
	__esp=0
	__eip=0
	__pending=0
	__blocked=0
	__sigign=0
	__sigcatch=0
	__wchan=0
	__0=0
	__0=0
	__exit_signal=0
	__task_cpu=0
	__rt_priority=0
	__policy=0
	__blkio_ticks=0
	__gtime=0
	__cgtime=0
	__perc_cpu_user=0
	__perc_cpu_sys=0
	
	def __init__(self, id):
		self.__pid=id
		self.__prev_wchar=0
		fname='/proc/%d/cmdline' % self.__pid
		if os.path.exists(fname) and os.access(fname, os.R_OK):
			fin = open(fname, 'r')
			self.__cmdline=fin.readline()
			fin.close()	

	def check_stat(self):

		fname='/proc/%d/stat' % self.__pid
		if os.path.exists(fname) and os.access(fname, os.R_OK):
			fin = open(fname, 'r')
			line=fin.readline()
			fin.close()	
			line = line.strip()
			field = line.split()

			cmd=field[1]
			cmd=cmd.replace('(','')
			cmd=cmd.replace(')','')

			self.__tcomm=cmd
			self.__state=field[2]
			self.__ppid=float(field[3])
			self.__pgrp=float(field[4])
			self.__sid=float(field[5])
			self.__tty_nr=float(field[6])
			self.__tty_pgrp=float(field[7])
			self.__flags=float(field[8])
			self.__min_flt=float(field[9])
			self.__cmin_flt=float(field[10])
			self.__maj_flt=float(field[11])
			self.__cmaj_flt=float(field[12])
			self.__utime=float(field[13])
			self.__stime=float(field[14])
			self.__cutime=float(field[15])
			self.__cstime=float(field[16])
			self.__priority=float(field[17])
			self.__nice=float(field[18])
			self.__num_threads=float(field[19])
			self.__it_real_value=float(field[20])
			self.__start_time=float(field[21])
			self.__vsize=float(field[22])
			self.__rss=float(field[23])
			self.__rsslim=float(field[24])
			self.__start_code=float(field[25])
			self.__end_code=float(field[26])
			self.__start_stack=float(field[27])
			self.__esp=float(field[28])
			self.__eip=float(field[29])
			self.__pending=float(field[30])
			self.__blocked=float(field[31])
			self.__sigign=float(field[32])
			self.__sigcatch=float(field[33])
			self.__wchan=float(field[34])
			self.__exit_signal=float(field[37])
			self.__task_cpu=float(field[38])
			self.__rt_priority=float(field[39])
			
			if len(field)>40:
				self.__policy=float(field[40])
				self.__blkio_ticks=float(field[41])
				self.__gtime=float(field[42])
				self.__cgtime=float(field[43])

			delta = float(getSysDeltaTime())
			if delta>0:
				self.__perc_cpu_user=float(self.__utime - self.__prev_utime)/delta*100
				self.__perc_cpu_sys=float(self.__stime - self.__prev_stime)/delta*100
			self.__prev_utime = self.__utime
			self.__prev_stime = self.__stime

	def check_io(self):

		fname='/proc/%d/io' % self.__pid
		if os.path.exists(fname) and os.access(fname, os.R_OK):
			fin = open(fname, 'r')
			for line in fin:
				line = line.strip()
				field = line.split(' ')
				if field[0]=='wchar:':
					wchar=int(field[1])
				if field[0]=='rchar:':
					rchar=int(field[1])
				if field[0]=='syscr:':
					syscr=int(field[1])
				if field[0]=='syscw:':
					syscw=int(field[1])
				if field[0]=='read_bytes:':
					read_bytes=int(field[1])
				if field[0]=='write_bytes:':
					write_bytes=int(field[1])
				if field[0]=='cancelled_write_bytes:':
					cancelled_write_bytes=int(field[1])
			if self.__prev_wchar!=0:
				self.__delta_wchar=wchar-self.__prev_wchar
				self.__delta_rchar=rchar-self.__prev_rchar
				self.__delta_syscr=syscr-self.__prev_syscr
				self.__delta_syscw=syscw-self.__prev_syscw
				self.__delta_read_bytes=read_bytes-self.__prev_read_bytes
				self.__delta_write_bytes=write_bytes-self.__prev_write_bytes
				self.__delta_cancelled_write_bytes=cancelled_write_bytes-self.__prev_cancelled_write_bytes	 			 
			self.__prev_wchar=wchar
			self.__prev_rchar=rchar
			self.__prev_syscr=syscr
			self.__prev_syscw=syscw
			self.__prev_read_bytes=read_bytes
			self.__prev_write_bytes=write_bytes
			self.__prev_cancelled_write_bytes=cancelled_write_bytes
			fin.close()	

	def check(self):
		self.check_stat()
		self.check_io()

	def get_pid(self):
		return self.__pid

	def show(self,threshold):
#if ((self.__delta_syscw + self.__delta_syscr) > threshold) or ((self.__perc_cpu_user + self.__perc_cpu_sys) > 0):
		if ((self.__perc_cpu_user + self.__perc_cpu_sys) > 0):
			print '%s\tpid:%d (u:%.2f s:%.2f) wchar:%d rchar:%d syscr:%d syscw:%d read:%d write:%d canc:%d (%s)' % ( strftime("%H:%M:%S", gmtime()), self.__pid, self.__perc_cpu_user, self.__perc_cpu_sys, self.__delta_wchar, self.__delta_rchar, self.__delta_syscr, self.__delta_syscw, self.__delta_read_bytes, self.__delta_write_bytes, self.__delta_cancelled_write_bytes, self.__tcomm)

