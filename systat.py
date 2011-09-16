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

sys_delta_time=0

def getSysDeltaTime():
	global sys_delta_time
	return sys_delta_time

class SyStat:
	__delta=0
	__prev_uptime=0
	__prev_cpu_user=0
	__prev_cpu_nice=0
	__prev_cpu_sys=0
	__prev_cpu_idle=0
	__prev_cpu_iowait=0
	__prev_cpu_hardirq=0
	__prev_cpu_softirq=0
	__prev_cpu_steal=0
	__prev_ctxt=0
	__perc_cpu_user=0
	__perc_cpu_nice=0
	__perc_cpu_sys=0
	__perc_cpu_idle=0
	__perc_cpu_iowait=0
	__perc_cpu_hardirq=0
	__perc_cpu_softirq=0
	__perc_cpu_steal=0
	__ctxt_per_delta=0
	__mem_total=0
	__mem_free=0
	__mem_buffers=0
	__mem_cached=0
	__swp_cached=0
	__swp_total=0
	__swp_free=0
	__avg_1m=0
	__avg_5m=0
	__avg_15m=0
	__nr_running=0
	__nr_threads=0
	__last_pid=0
	__prev_page_in = 0
	__prev_page_out = 0
	__prev_swap_in = 0
	__prev_swap_out = 0
	__delta_page_in = 0
	__delta_page_out = 0
	__delta_swap_in = 0
	__delta_swap_out = 0

	def __init__(self):
		fin = open('/proc/sys/kernel/osrelease', 'r')
		self.__kernel_release=fin.readline()
		if self.__kernel_release[-1]=='\n': self.__kernel_release=self.__kernel_release[:-1]
		fin.close()
		fin = open('/proc/sys/kernel/hostname', 'r')
		self.__hostname=fin.readline()
		if self.__hostname[-1]=='\n': self.__hostname=self.__hostname[:-1]
		fin.close()

	def show(self):
		if self.__delta!=0:
			print '%s usr:%.2f sys:%.2f nice:%.2f idle:%.2f io:%.2f ctxt:%d' % ( strftime("%H:%M:%S", gmtime()), self.__perc_cpu_user, self.__perc_cpu_sys, self.__perc_cpu_nice, self.__perc_cpu_idle, self.__perc_cpu_iowait, self.__ctxt_per_delta )

	def check_uptime(self):
		f = open( '/proc/uptime' )
		contents = f.read().split()
		f.close()
		total_seconds = float(contents[0])
		minute = 60
		hour = minute * 60
		day = hour * 24
		days = int( total_seconds / day )
		hours = int( ( total_seconds % day ) / hour )
		minutes = int( ( total_seconds % hour ) / minute )
		seconds = int( total_seconds % minute )
		self.__uptime = '%dd:%dh:%dm:%ds' % (days, hours, minutes, seconds)
		return self.__uptime;
		
	def check_load(self):
		fin = open('/proc/loadavg', 'r')
		for line in fin:
			line = line.strip()
			field = line.split()
			self.__avg_1m=float(field[0])
			self.__avg_5m=float(field[1])
			self.__avg_15m=float(field[2])
			if len(field)>3:
				tmp=field[3].split('/')
				self.__nr_running=int(tmp[0])
				self.__nr_threads=int(tmp[1])
				if len(field)>4:
					self.__last_pid=int(field[4])

	def check_mem(self):
		fin = open('/proc/meminfo', 'r')
		for line in fin:
			line = line.strip()
			field = line.split()
			if field[0]=='MemTotal:':
				self.__mem_total=int(field[1])
				continue
			if field[0]=='MemFree:':
				self.__mem_free=int(field[1])
				continue
			if field[0]=='Buffers:':
				self.__mem_buffers=int(field[1])
				continue
			if field[0]=='Cached:':
				self.__mem_cached=int(field[1])
				continue
			if field[0]=='SwapTotal:':
				self.__swp_total=int(field[1])
				continue
			if field[0]=='SwapFree:':
				self.__swp_free=int(field[1])
				continue
			if field[0]=='SwapCached:':
				self.__swp_cached=int(field[1])
				continue
		fin.close()	

	def check_vmstart(self):
		global sys_delta_time
		self.__num_cpu = 0
		fin = open('/proc/vmstat', 'r')
		for line in fin:
			line = line.strip()
			field = line.split()
			key = field[0]
			value = int(field[1])
			if key == 'pgpgin':
				self.__delta_page_in = value - self.__prev_page_in
				self.__prev_page_in = value
			elif key == 'pgpgout':
				self.__delta_page_out = value - self.__prev_page_out
				self.__prev_page_out = value
			elif key == 'pswpin':
				self.__delta_swap_in = value - self.__prev_swap_in
				self.__prev_swap_in = value
			elif key == 'pswpout':
				self.__delta_swap_out = value - self.__prev_swap_out
				self.__prev_swap_out = value
		fin.close()

	def check_stat(self):
		global sys_delta_time
		self.__num_cpu = 0
		fin = open('/proc/stat', 'r')
		for line in fin:
			line = line.strip()
			field = line.split()
			if field[0][:3] == 'cpu':
				if field[0] == 'cpu':
					cpu_user=float(field[1])
					cpu_nice=float(field[2])
					cpu_sys=float(field[3])
					cpu_idle=float(field[4])
					cpu_iowait=float(field[5])
					cpu_hardirq=float(field[6])
					cpu_softirq=float(field[7])
					cpu_steal=float(field[8])
					uptime=cpu_user + cpu_nice + cpu_sys + cpu_idle + cpu_iowait + cpu_hardirq + cpu_softirq
					if self.__prev_uptime!=0:
						self.__delta = uptime - self.__prev_uptime
						sys_delta_time = self.__delta
						self.__perc_cpu_user = (cpu_user-self.__prev_cpu_user)/self.__delta*100
						self.__perc_cpu_sys = (cpu_sys-self.__prev_cpu_sys)/self.__delta*100
						self.__perc_cpu_nice = (cpu_nice-self.__prev_cpu_nice)/self.__delta*100
						self.__perc_cpu_idle = (cpu_idle-self.__prev_cpu_idle)/self.__delta*100
						self.__perc_cpu_iowait = (cpu_iowait-self.__prev_cpu_iowait)/self.__delta*100
						self.__perc_cpu_steal = (cpu_steal-self.__prev_cpu_steal)/self.__delta*100
					self.__prev_uptime=uptime
					self.__prev_cpu_user=cpu_user
					self.__prev_cpu_nice=cpu_nice
					self.__prev_cpu_sys=cpu_sys
					self.__prev_cpu_idle=cpu_idle
					self.__prev_cpu_iowait=cpu_iowait
					self.__prev_cpu_hardirq=cpu_hardirq
					self.__prev_cpu_softirq=cpu_softirq
					self.__prev_cpu_steal=cpu_steal
					continue
				else:
					self.__num_cpu+=1
					continue
			if field[0] == 'ctxt':
				ctxt = float(field[1])
				if self.__prev_ctxt!=0:
					self.__ctxt_per_delta=(ctxt - self.__prev_ctxt)
				self.__prev_ctxt=ctxt;
				continue
			if field[0] == 'btime':
				btime=time.localtime(float(field[1]))
				self.__boot_time=time.strftime('%d/%m/%Y %H:%M:%S', btime)
				continue
			if field[0] == 'processes':
				self.__processes=int(field[1])
				continue
			if field[0] == 'procs_running':
				self.__procs_running=int(field[1])
				continue
			if field[0] == 'procs_blocked':
				self.__procs_blocked=int(field[1])
				continue

		fin.close()

	def get_cpu(self):
		return self.__perc_cpu_user, self.__perc_cpu_sys, self.__perc_cpu_nice, self.__perc_cpu_idle, self.__perc_cpu_iowait, self.__perc_cpu_steal

	def get_delta_context_switch(self):
		return self.__ctxt_per_delta

	def get_context_switch(self):
		return self.__prev_ctxt

	def get_mem_perc(self):
		k=float(100/float(self.__mem_total))
		return 100, (self.__mem_cached * k), (self.__mem_buffers * k), (self.__mem_free * k)
	
	def get_mem_info(self):
		return self.__mem_total, self.__mem_cached, self.__mem_buffers, self.__mem_free

	def get_swap_perc(self):
		k=float(100/float(self.__swp_total))
		return 100, (self.__swp_cached * k), (self.__swp_free * k)
		
	def get_swap_info(self):	
		return self.__swp_total, self.__swp_cached, self.__swp_free

	def get_load(self):
		return self.__avg_1m, self.__avg_5m, self.__avg_15m, self.__nr_running, self.__nr_threads, self.__last_pid 

	def get_proc_status(self):
		return self.__processes, self.__procs_running, self.__procs_blocked

	def get_boot_time(self):
		return self.__boot_time

	def get_hostname(self):
		return self.__hostname	

	def get_release(self):
		return self.__kernel_release	

	def get_uptime(self):
		return self.__uptime
	
	def get_num_cpu(self):
		return self.__num_cpu	

	def get_page_couter(self):
		return self.__delta_page_in, self.__delta_page_out

	def get_swap_couter(self):
		return self.__delta_swap_in, self.__delta_swap_out

	def check(self):
		self.check_stat()
		self.check_vmstart()
		self.check_mem()
		self.check_load()
		self.check_uptime()


