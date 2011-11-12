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

class Property:

	__properties = None
	
	def __init__(self):
		self.__properties = {}

	def add(self, name, fn):
		self.__properties[name] = {
			'name': name,
			'value': None,
			'callback': fn,
			'valid': False
		}
	
	def __update(self, callback, property):
		if (callback):
			callback(property)

	def get(self, property):
		if (property not in self.__properties):
			return None
		p = self.__properties[property]
		if (not p['valid'] or not p['value'] ):
			self.__update(p['callback'], property)
		return p['value']

	def set(self, property, value):
		if (property not in self.__properties):
			return
		p = self.__properties[property]
		p['value'] = value
		p['valid'] = True

	def invalidate(self, property):
		if (property not in self.__properties):
			return
		p = self.__properties[property]
		p['valid'] = False
	
	def invalidateAll(self):
		for prop in self.__properties:
			self.invalidate(prop)
	
		