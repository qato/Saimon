#! /usr/bin/env python
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
import curses
import random
import time
import string

from systat import * 
from syprocess import * 
from syprocesslist import * 
from sydisk import * 
from synet import * 

delay = 2
process_cpu_alert_threhold = 45
sys_ctxt_alert_threshold = 2000

alert_color = 1
white = 2
black = 3
usr_color = 4
sys_color = 5
nice_color = 6
io_color = 7
m_used_color = 8
m_cached_color = 9
m_buff_color = 10
rx_color = 4
tx_color = 5
plist_color_header = 11
plist_color_text = 12

gen_y=1
cpu_y=3
mem_y=4
swp_y=5
dsk_y=6
net_y=7

plist_y=9

pos_sys_bar = 45

Sy = SyStat()
Disk = DiskStat()
Net = SyNetStat()
PList = SyProcessListStat()

def show_general_stat(myscreen, mywin):
	global black, alert_color, sys_ctxt_alert_threshold

	release = Sy.get_release()
	processes, procs_running, procs_blocked = Sy.get_proc_status()
	pin, pout = Sy.get_page_couter()
	sin, sout = Sy.get_swap_couter()
	p_total, p_running, p_sleeping, p_uninterruptible, p_zombie, p_stopped = PList.get_processes_status()
	avg_1m, avg_5m, avg_15m, nr_running, nr_threads, last_pid = Sy.get_load()
	ctxt = Sy.get_delta_context_switch()

	y,x=myscreen.getmaxyx()
	s_title =' %s  - kernel version %s - boot (%s) ' % (Sy.get_hostname(), release, Sy.get_boot_time())
	s_general1 ='Uptime (%s) - Context switch:%d - Paging in:%d out:%d - Swap in:%d out:%d%s' % (Sy.get_uptime(), ctxt, pin, pout, sin, sout, ' '*x)
	s_general2='CPU:%d R:%d/S:%d/B:%d/Z:%d/Total:%d Threads:%d/%d Load (1m:%.2f 5m:%.2f 15m:%.2f) %s' % (Sy.get_num_cpu(), p_running, p_sleeping, p_uninterruptible, p_zombie, p_total, nr_running, nr_threads, avg_1m, avg_5m, avg_15m, ' '*x)

	general_color1 = black
	general_color2 = black

	if ctxt > sys_ctxt_alert_threshold:
		general_color1 = alert_color

	myscreen.addstr(0, 2, s_title[:x-2])

	mywin.addstr(gen_y, 1, s_general1[:x-2], curses.color_pair(general_color1))
	mywin.addstr(gen_y+1, 1, s_general2[:x-2], curses.color_pair(general_color2))


def show_net_stat(myscreen, mywin):
	rxbyte,txbyte,rxpacket,txpacket = Net.get_data_delta()
	rxb_base='K'; rxbyte=float(rxbyte/1024)
	txb_base='K'; txbyte=float(rxbyte/1024)
	if rxbyte>512: 
		rxb_base='M'
		rxbyte=rxbyte / 1024
	if txbyte>512: 
		txb_base='M'
		txbyte=txbyte / 1024
	if rxbyte>512: 
		rxb_base='G'
		rxbyte=rxbyte / 1024
	if txbyte>512: 
		txb_base='G'
		txbyte=txbyte / 1024
	s_net = 'NET (rx:%.2f%c tx:%.2f%c)%s' % (rxbyte, rxb_base, txbyte, txb_base, ' '*pos_sys_bar)
	rxb, txb, rxp, txp = Net.get_data_perc()
	y,x=myscreen.getmaxyx()
	xspace=x-pos_sys_bar
	if xspace > 0:
		kspace=float(float(xspace)/100)
		s_rx		= 'R'*int(kspace*rxb)
		s_tx		= 'T'*int(kspace*txb)
		s_null		= '-'*(xspace-len(s_rx + s_tx))
		mywin.addstr(net_y, 1, s_net[:x-2])
		mywin.move(net_y, pos_sys_bar-1)
		mywin.addstr(s_rx, curses.color_pair(rx_color))
		mywin.addstr(s_tx, curses.color_pair(tx_color))
		mywin.addstr(s_null, curses.color_pair(black))

def show_disk_stat(myscreen, mywin):
	perc = Disk.get_perc()
	num = Disk.get_num_mon()
	s_disk = 'DISK (%2.2f/%d)%s' % (perc, num, ' '*pos_sys_bar)
	y,x=myscreen.getmaxyx()
	xspace=x-pos_sys_bar
	if xspace > 0:
		kspace=float(float(xspace)/100)
		s_used		= 'D'*int(kspace*perc*num)
		s_null		= '-'*(xspace-len(s_used))
		mywin.addstr(dsk_y, 1, s_disk[:x-2])
		mywin.move(dsk_y, pos_sys_bar-1)
		mywin.addstr(s_used, curses.color_pair(io_color))
		mywin.addstr(s_null, curses.color_pair(black))
#mywin.move(6,5)
#mywin.addstr(str(disk.get_disks()))

def show_swp_stat(myscreen, mywin):
	swp_total, swp_cached, swp_free = Sy.get_swap_info()
	p_swp_total, p_swp_cached, p_swp_free = Sy.get_swap_perc()
	m_used=swp_total - swp_free
	p_m_used=p_swp_total - p_swp_free
	s_swp = 'SWP (u:%2.2f c:%2.2f)%s' % (p_m_used - p_swp_cached, p_swp_cached, ' '*pos_sys_bar)
	y,x=myscreen.getmaxyx()
	xspace=x-pos_sys_bar
	if xspace > 0:
		kspace=float(float(xspace)/100)
		s_used		= 'U'*int(kspace*(p_m_used - p_swp_cached ))
		s_cached	= 'C'*int(kspace*p_swp_cached)
		s_null		= '-'*(xspace-len(s_used+s_cached))
		mywin.addstr(swp_y, 1, s_swp[:x-2])
		mywin.move(swp_y, pos_sys_bar-1)
		mywin.addstr(s_used, curses.color_pair(m_used_color))
		mywin.addstr(s_cached, curses.color_pair(m_cached_color))
		mywin.addstr(s_null, curses.color_pair(black))

def show_mem_stat(myscreen, mywin):
	mem_total, mem_cached, mem_buffers, mem_free = Sy.get_mem_info()
	p_mem_total, p_mem_cached, p_mem_buffers, p_mem_free = Sy.get_mem_perc()
	m_used=mem_total - mem_free
	p_m_used=p_mem_total - p_mem_free
	s_mem = 'MEM (u:%2.2f c:%2.2f b:%2.2f)%s' % (p_m_used - p_mem_cached - p_mem_buffers, p_mem_cached, p_mem_buffers, ' '*pos_sys_bar)
	y,x=myscreen.getmaxyx()
	xspace=x-pos_sys_bar
	if xspace > 0:
		kspace=float(float(xspace)/100)
		s_used		= 'U'*int(kspace*(p_m_used - p_mem_cached - p_mem_buffers))
		s_cached	= 'C'*int(kspace*p_mem_cached)
		s_buffers	= 'B'*int(kspace*p_mem_buffers)
		s_null		= '-'*(xspace-len(s_used+s_cached+s_buffers))
		mywin.addstr(mem_y, 1, s_mem[:x-2])
		mywin.move(mem_y, pos_sys_bar-1)
		mywin.addstr(s_used, curses.color_pair(m_used_color))
		mywin.addstr(s_cached, curses.color_pair(m_cached_color))
		mywin.addstr(s_buffers, curses.color_pair(m_buff_color))
		mywin.addstr(s_null, curses.color_pair(black))
	
def show_cpu_stat(myscreen, mywin):
	dusr,dsys,dnice,didle,diowait,dsteal = Sy.get_cpu()
	s_cpu = 'CPU (u%2.2f s%2.2f n%2.2f io%2.2f st%2.2f)%s' % (dusr, dsys, dnice, diowait, dsteal, ' '*pos_sys_bar)
	y,x=myscreen.getmaxyx()
	xspace=x-pos_sys_bar
	if xspace > 0:
		kspace=float(float(xspace)/100)
		s_usr	='U'*int(kspace*dusr)
		s_sys	='S'*int(kspace*dsys)
		s_nice	='N'*int(kspace*dnice)
		s_iowait='D'*int(kspace*diowait)
		s_steal	='s'*int(kspace*dsteal)
		s_null	='-'*(xspace-len(s_usr+s_sys+s_nice+s_iowait+s_steal))
		mywin.addstr(cpu_y, 1, s_cpu[:x-2])
		mywin.move(cpu_y, pos_sys_bar-1)
		mywin.addstr(s_usr, curses.color_pair(usr_color))
		mywin.addstr(s_sys, curses.color_pair(sys_color))
		mywin.addstr(s_nice, curses.color_pair(nice_color))
		mywin.addstr(s_iowait, curses.color_pair(io_color))
		mywin.addstr(s_steal, curses.color_pair(nice_color))
		mywin.addstr(s_null, curses.color_pair(black))


def show_sys_box(myscreen):
	y,x=myscreen.getmaxyx()
	win = myscreen.subwin(9, x, 0, 0)
	win.box()
	show_cpu_stat(myscreen, win)
	show_mem_stat(myscreen, win)
	show_swp_stat(myscreen, win)
	show_disk_stat(myscreen, win)
	show_net_stat(myscreen, win)
	show_general_stat(myscreen, win)

def update_process():
	PList.check()

def str_align(s, len):
	z = ' '*len
	x = '%s%s' % (s, z)
	return x[:len]

def calc_bytes(value):
	base='b'
	if (value>1024):
		value/=1024
		base='k'
	if (value>1024):
		value/=1024
		base='m'
	if (value>1024):
		value/=1024
		base='g'
	return str('%4d%s' % (value, base))

def calc_int(value):
	base=' '
	if (value>1000):
		value/=1000
		base='K'
	if (value>1000):
		value/=1000
		base='M'
	if (value>1000):
		value/=1000
		base='G'
	return str('%4d%s' % (value, base))
	 
def show_process(myscreen, x, process_detail):
	row	=	str('%6d ' % process_detail['pid'])
	row	+=	process_detail['state'] + ' '
	row	+=	str('%-15s ' % process_detail['cmd'])
	row	+=	str('%4d ' % int(process_detail['priority']))
	row	+=	str('%4d ' % int(process_detail['nice']))
	row	+=	str('%4s ' % calc_bytes(int(process_detail['vsize'])))
	row	+=	str('%4s ' % calc_bytes(process_detail['rss']))
	row	+=	str('%4s ' % process_detail['num_threads'])
	row	+=	str('%-4.2f ' % process_detail['cpu'])
	row	+=	str('r:%4s w:%4s ' % ( calc_int ( process_detail['delta_syscr'] ) , calc_int( process_detail["delta_syscw"] ) ) )

	row += ' '*x

	if process_detail['cpu'] > process_cpu_alert_threhold:
		myscreen.addstr(row[:x], curses.color_pair(alert_color))
	else:
		myscreen.addstr(row[:x], curses.color_pair(plist_color_text))
		
def show_process_box(myscreen):
	y,x=myscreen.getmaxyx()
#win = myscreen.subwin(y-10, x, plist_y, 0)
#win.bkgdset(' ', curses.color_pair(black))
#win.clear()
	y,x=myscreen.getmaxyx()
	plist = PList.get_process_list()
	yy=plist_y + 1

	header	=	'   PID '
	header	+=	'S '
	header	+=	'COMMAND           '
	header	+=	'PR    '
	header	+=	'N   '
	header	+=	'VSS  '
	header	+=	' RSS '
	header	+=	' NT  '
	header	+=	'CPU  '
	header	+=	'I/O            '

	myscreen.addstr(plist_y, 0, header, curses.color_pair(plist_color_header))
	
	for p in plist:
		detail=p[1]
		if yy<y-1:
			myscreen.move(yy, 0)
			show_process(myscreen, len(header), detail)
		yy+=1

def init(myscreen):	
	myscreen.bkgdset(' ', curses.color_pair(black))
	myscreen.clear()
	myscreen.nodelay(1000)
	myscreen.refresh()

def main_loop(myscreen):

	init(myscreen)

	Sy.check()   
	Disk.check()   
	Net.check()
	update_process()
	sleep(0.25)
	
	while 1:	
		Sy.check()   
		Disk.check()   
		Net.check()
		update_process()
		show_sys_box(myscreen)
		show_process_box(myscreen)
		c=myscreen.getch()
		if c==ord('q'): break
		time.sleep(delay)				


def real_main(stdscr):
	try: 
		curses.start_color()
		curses.init_pair(alert_color, curses.COLOR_RED, curses.COLOR_WHITE)
		curses.init_pair(white, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(black, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(usr_color, curses.COLOR_WHITE, curses.COLOR_GREEN)
		curses.init_pair(sys_color, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(nice_color, curses.COLOR_WHITE, curses.COLOR_YELLOW)
		curses.init_pair(io_color, curses.COLOR_WHITE, curses.COLOR_RED)
		curses.init_pair(m_used_color, curses.COLOR_WHITE, curses.COLOR_GREEN)
		curses.init_pair(m_cached_color, curses.COLOR_WHITE, curses.COLOR_YELLOW)
		curses.init_pair(m_buff_color, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(plist_color_header, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(plist_color_text, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.noecho() 
		curses.cbreak() 
		stdscr.keypad(1) 
		main_loop(stdscr)

	finally: 
		stdscr.keypad(0) 
		curses.nocbreak() 
		curses.echo()  
		curses.endwin()

def main(argv):
	global delay

	iters = 10
	threshold=1024
	disk=''

	try:                                
		opts, args = getopt.getopt(argv, "i:d:t:D:")
	except getopt.GetoptError:          
		print 'invalid parameters'
		sys.exit(2)                     

	for opt, arg in opts:
		if opt == '-d':
			delay = int(arg)
		elif opt == '-i':
			iters = int(arg)
		elif opt == '-t':
			threshold = int(arg)
		elif opt == '-D':
			disk = arg

	curses.wrapper(real_main)

if __name__ == "__main__":
	main(sys.argv[1:])		
	
