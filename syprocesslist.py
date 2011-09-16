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
from operator import itemgetter

from systat import * 

class SyProcessListStat:

	def __init__(self):
		self.__plist = {}
		self.__pid_list = set()
		self.__page_size = os.sysconf("SC_PAGESIZE")
		self.__sort_key = 'cpu'
		self.__sort_desc = True

	def reset_list_stat(self):
		self.__running=0
		self.__sleeping=0
		self.__uninterruptible=0
		self.__zombie=0
		self.__stopped=0

	def update_list_stat(self, state):
		if state=='R':
			self.__running+=1
		elif state=='S':
			self.__sleeping+=1
		elif state=='D':
			self.__uninterruptible+=1
		elif state=='Z':
			self.__zombie+=1
		elif state=='T':
			self.__stopped+=1
		
	def get_pstat_io(self, pid, detail):
		fname='/proc/%d/io' % pid
		if os.path.exists(fname):
			fin = open(fname, 'r')
			for line in fin:
				line = line.strip()
				field = line.split(' ')
				if field[0]=='syscr:':
					detail["syscr"]=int(field[1])
				if field[0]=='syscw:':
					detail["syscw"]=int(field[1])
			fin.close()
		detail["delta_syscr"]=0
		detail["delta_syscw"]=0

	def get_pstat(self, pid):
		self.reset_list_stat()

		detail = {}
		detail['pid']=pid
		detail['cmd']='blablabla'

		fname='/proc/%d/stat' % pid
		fin = open(fname, 'r')
		line=fin.readline()
		fin.close()	
		line = line.strip()
		field = line.split()

		cmd=field[1]
		cmd=cmd.replace('(','')
		cmd=cmd.replace(')','')
		detail['cmd']=cmd
		detail['state']=field[2]
		detail['ppid']=field[3]
		detail['pgrp']=field[4]
		detail['sid']=field[5]
		detail['tty_nr']=field[6]
		detail['tty_pgrp']=field[7]
		detail['flags']=field[8]
		detail['min_flt']=field[9]
		detail['cmin_flt']=field[10]
		detail['maj_flt']=field[11]
		detail['cmaj_flt']=field[12]
		detail['utime']=field[13]
		detail['stime']=field[14]
		detail['cutime']=field[15]
		detail['cstime']=field[16]
		detail['priority']=field[17]
		detail['nice']=field[18]
		detail['num_threads']=field[19]
		detail['it_real_value']=field[20]
		detail['start_time']=field[21]
		detail['vsize']=field[22]
		detail['rss']=int(field[23]) * self.__page_size
		detail['rsslim']=field[24]
		detail['start_code']=field[25]
		detail['end_code']=field[26]
		detail['start_stack']=field[27]
		detail['esp']=field[28]
		detail['eip']=field[29]
		detail['pending']=field[30]
		detail['blocked']=field[31]
		detail['sigign']=field[32]
		detail['sigcatch']=field[33]
		detail['wchan']=field[34]
		detail['exit_signal']=field[37]
		detail['task_cpu']=field[38]
		detail['rt_priority']=field[39]
		if len(field)>40:
			detail['policy']=field[40]
			detail['blkio_ticks']=field[41]
			detail['gtime']=field[42]
			detail['cgtime']=field[43]

		detail['perc_cpu_usr']=0
		detail['perc_cpu_sys']=0
		detail['cpu']=0
		detail['sysio']=0

		self.get_pstat_io(pid, detail)

		self.update_list_stat(detail['state'])

		return detail

	def update_pstat_io(self, detail):
		pid=detail['pid']

		fname='/proc/%d/io' % pid
		if os.path.exists(fname):
			fin = open(fname, 'r')
			for line in fin:
				line = line.strip()
				field = line.split(' ')
				if field[0]=='syscr:':
					new_val = int(field[1])
					detail["delta_syscr"]= int (new_val - detail["syscr"])
					detail["syscr"]=new_val
				if field[0]=='syscw:':
					new_val = int(field[1])
					detail["delta_syscw"]=new_val - detail["syscw"]
					detail["syscw"]=int(field[1])
			fin.close()
		detail['sysio']= detail["delta_syscr"] + detail["delta_syscw"]

	def update_pstat(self, detail):

		pid=detail['pid']
		fname='/proc/%d/stat' % pid
		fin = open(fname, 'r')
		line=fin.readline()
		fin.close()	
		line = line.strip()
		field = line.split()

		prev_utime = float(detail['utime'])
		prev_stime = float(detail['stime'])

		detail['state']=field[2]
		detail['utime']=field[13]
		detail['stime']=field[14]
		detail['cutime']=field[15]
		detail['cstime']=field[16]
		detail['priority']=field[17]
		detail['nice']=field[18]
		detail['num_threads']=field[19]
		detail['vsize']=field[22]
		detail['rss']=int(field[23]) * self.__page_size
		detail['task_cpu']=field[38]
		detail['rt_priority']=field[39]
		if len(field)>40:
			detail['policy']=field[40]
			detail['blkio_ticks']=float(field[41])
			detail['gtime']=field[42]
			detail['cgtime']=field[43]

		delta = float(getSysDeltaTime())
		if delta>0:
			detail['perc_cpu_usr']=float(float(detail['utime']) - prev_utime)/delta*100
			detail['perc_cpu_sys']=float(float(detail['stime']) - prev_stime)/delta*100
			detail['cpu']=detail['perc_cpu_usr']+detail['perc_cpu_sys']

		self.update_list_stat(detail['state'])

	def check(self):
		pids=set()
		for dirname in os.listdir('/proc'):
			if dirname[0]>='0' and dirname[0]<='9':
				pid=int(dirname)
				pids.add(pid)

		# Process started
		for pid in (pids - self.__pid_list):
			self.__pid_list.add(pid)
			self.__plist[pid] = self.get_pstat(pid)

		# Process terminated
		for pid in (self.__pid_list - pids):
			self.__pid_list.remove(pid)
			del self.__plist[pid]

		self.reset_list_stat()
		for p in self.__plist:
			self.update_pstat(self.__plist[p])	
			self.update_pstat_io(self.__plist[p])	

		self.__sorted_plist = sorted(self.__plist.iteritems(), cmp=lambda x, y: cmp(x[1]["sysio"], y[1]["sysio"]), reverse=self.__sort_desc)
		self.__sorted_plist = sorted(self.__plist.iteritems(), cmp=lambda x, y: cmp(x[1][self.__sort_key], y[1][self.__sort_key]), reverse=self.__sort_desc)

#self.__sorted_plist = sorted(self.__plist.iteritems(), cmp=lambda x, y: cmp(x[1]['cpu'], y[1]['cpu']), reverse=True)
#self.__sorted_plist = sorted(self.__plist.iteritems(), key=itemgetter(1,'cpu'), reverse=True)

	def get_sort_detail(self):
		return self.__sort_key, self.__sort_desc

	def set_sort_detail(self, key, desc = True):
		self.__sort_key = key
		self.__sort_desc = desc

	def get_process_list(self):
		return self.__sorted_plist

	def get_processes_status(self):
		return len(self.__pid_list), self.__running, self.__sleeping, self.__uninterruptible, self.__zombie, self.__stopped
#x=self.__plist[p]
#if (x['cpu']>0): print 'pid<%d> cpu<%.2f>' % (x['pid'], x['cpu'])


