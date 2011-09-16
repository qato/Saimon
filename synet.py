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

class SyNetStat:
	def __init__(self):
		self.__rxbyte=0
		self.__txbyte=0
		self.__rxpacket=0
		self.__txpacket=0
		self.__delta_rxbyte=0
		self.__delta_txbyte=0
		self.__delta_rxpacket=0
		self.__delta_txpacket=0
		self.__max_rxbyte=0
		self.__max_txbyte=0
		self.__max_rxpacket=0
		self.__max_txpacket=0
		self.__numdev = 0
		self.__flag = 0
	def check(self):
		fname='/proc/net/dev'
		self.__flag += 1
		rxb=0; rxp=0; txb=0; txp=0
		self.__numdev = 0
		fin = open(fname, 'r')
		for line in fin:
			line = line.strip()
			data = line.split(':')
			if len(data)==2:
				field = data[1].split()
				device=data[0]
				self.__numdev += 1
				rxb+=int(field[0])
				rxp+=int(field[1])
				txb+=int(field[8])
				txp+=int(field[9])
		fin.close()	
		if self.__flag>1:
			self.__delta_rxbyte=rxb-self.__rxbyte
			self.__delta_txbyte=txb-self.__txbyte
			self.__delta_rxpacket=rxp-self.__rxpacket
			self.__delta_txpacket=txp-self.__txpacket
			if (self.__delta_rxbyte > self.__max_rxbyte): self.__max_rxbyte=self.__delta_rxbyte
			if (self.__delta_txbyte > self.__max_txbyte): self.__max_txbyte=self.__delta_txbyte
			if (self.__delta_rxpacket > self.__max_rxpacket): self.__max_rxpacket=self.__delta_rxpacket
			if (self.__delta_txpacket > self.__max_txpacket): self.__max_txpacket=self.__delta_txpacket
		self.__rxbyte=rxb	
		self.__txbyte=txb	
		self.__rxpacket=rxp	
		self.__txpacket=txp	
		
	def get_data_delta(self):
		return self.__delta_rxbyte, self.__delta_txbyte, self.__delta_rxpacket, self.__delta_txpacket

	def get_data(self):
		return self.__rxbyte, self.__txbyte, self.__rxpacket, self.__txpacket

	def get_data_perc(self):
		if self.__flag == 0:
			return 0, 0, 0, 0
		k_byte = (100/float(self.__max_rxbyte + self.__max_txbyte + 1024))
		k_packet = (100/float(self.__max_rxpacket + self.__max_txpacket + 1024))
		return (k_byte * self.__delta_rxbyte), (k_byte * self.__delta_txbyte), (k_packet * self.__delta_rxpacket), (k_packet * self.__delta_txpacket)

