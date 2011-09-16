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
from syprocess import * 
from sydisk import * 

def main(argv):
	iters = 10
	delay = 2
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

	processes = []
 	for dirname, dirnames, filenames in os.walk('/proc', topdown=False):
		for filename in filenames:
			tmp=dirname.split('/')
			if len(tmp)==3 :
				if filename == 'io':
					pid=int(os.path.basename(dirname))
					processes.append(Process(pid))

	Sy = SyStat()
	if disk!='':
		D = Disk(disk)
	for i in range(iters+1):
		Sy.check()   
		for P in processes:
			P.check()
		if disk!='':
	 		D.check()	 
		Sy.show()   
		for P in processes:
			P.show(threshold)
		if disk!='':
	 		D.show()	 
		print ''
		if (i<iters) and (i!=0):
			time.sleep(delay)


if __name__ == "__main__":
	main(sys.argv[1:])		

