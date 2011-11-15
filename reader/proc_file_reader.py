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
import os, sys, string

import normalization

class ProcFileReader:

	__fname="/dev/zero"
	__fin = None
	__line_norm = None

	def __init__(self, fname):
		self.__fname = fname

	def setLineNormalizationFunc(self,fn):
		self.__line_norm = fn


	def open(self):
		if os.path.exists(self.__fname) and os.access(self.__fname, os.R_OK):
			self.__fin = open(self.__fname, 'r')
			return True
		return False

	def close(self):
		if (self.__fin):
			self.__fin.close()

	def readLine(self, strip = True):
		line = None
		if (self.__fin):
			line = self.__fin.readline()
			if line[-1]=='\n': line=line[:-1]
			if (strip):
				line = self.__normalizeLine(line.strip())
		return line

	def readAll(self):
		content = None
		if (self.__fin):
			content = self.__fin.read()
		return content

	def readColumns(self):
		line = self.readLine()
		if (line):
			return line.split(' ')
		return None

