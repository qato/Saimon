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

from reader.proc_file_reader import ProcFileReader
import reader.normalization 


class UpdateMode:
	DICTIONARY = 1
	TABLE = 2

class FileWatcher:

	__freader = None
	__fname = None
	__current_content = None
	__previous_content = None
	__current = None
	__previous = None
	__label = None
	__sep = None
	__upd_mode = UpdateMode.TABLE
	__values_invalid = False
	__line_norm_fn = None
	__filter = None
	
	def __init__(self, fname):
		self.__fname = fname
		self.__freader = ProcFileReader(fname)

	def update(self):
		if (self.__freader.open()):
			self.__previous = self.__current
			self.__previous_content = self.__current_content
			
			self.__current_content = self.__freader.readAll()
			
			if (not self.isChanged()):
				self.__current = self.__previous
				self.__values_invalid = False
			else:
				self.__values_invalid = True
			self.__freader.close()
			
		
	def __getValues(self):
		if (self.__upd_mode == UpdateMode.TABLE):
			self.__getTable()
		else:
			self.__getDictionary()
		self.__values_invalid = False
		
	def __getTable(self):
		self.__current = reader.normalization.getTable(self.__current_content, self.__sep, self.__label, self.__line_norm_fn, self.__filter)

	def __getDictionary(self):
		self.__current = reader.normalization.getDictionary(self.__current_content, self.__sep, self.__line_norm_fn)
	
	def getCurrent(self):
		if (self.__values_invalid): self.__getValues()
		return self.__current
	
	def getPrevious(self):
		if (self.__values_invalid): self.__getValues()
		if (self.__previous): 
			return self.__previous
		return self.__current

	def isChanged(self):
		return not(self.__previous_content == self.__current_content and self.__previous)
	
	def setLabel(self, lbl):
		self.__label = lbl
		
	def setSeparator(self, sep):
		self.__sep = sep
		
	def setLineNormalizationFunc(self, fn):
		self.__line_norm_fn = fn
	
	def setUpdateMode(self, mode):
		self.__upd_mode = mode
	
	def setFilter(self, filter):
		self.__filter = filter