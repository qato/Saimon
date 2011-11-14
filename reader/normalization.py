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
import string

def procStatNormFn(line):
	pre=string.find(line, "(")
	post=string.find(line, ")")
	if (post>pre):
		return line[0:pre] + string.replace(line[pre+1:post], " ", "$") + line[post+1:]
	return line

def arrayToDict(cols, label):
	c = 0
	result = dict()
	for col in cols:
		if (len(label)>c):
			result[label[c]] = col
		else:
			result["unk_%d" % c] = col
		c = c + 1
	return result
	
def normalizeLine(line_norm_fn, line):
	if (line_norm_fn):
		return line_norm_fn(line)
	return line

def split(str, sep):
	if (str): 
		i = str.find(sep)
		if (i>=0):
			return str[0:i], str[i+1:]
		return str, None
	return None, None

def getTable(content, sep = None, label = None, line_norm_fn = None, filter = None): 
	result = dict()
	if (content):
		cnt = 0
		for line in content.split('\n'):
			line = normalizeLine(line_norm_fn, line)
			cols = line.split(sep)
			if (len(cols)>1):
				if (filter):
					v = cols[filter['col']]
					if (not v in filter['values']): continue
				if (label):
					result[cnt] = arrayToDict(cols, label)
				else:
					result[cnt] = cols
				cnt = cnt + 1
	return result

def getDictionary2(content, sep = ':', line_norm_fn = None):
	result = dict()
	if (content):
		for line in content.split('\n'):
			line = normalizeLine(line_norm_fn, line)
			cols = line.split(sep)
			if (len(cols)>1):
				result[cols[0].strip()] = ' '.join(cols[1:]).strip()
	return result

def getDictionary(content, sep = ':', line_norm_fn = None):
	result = dict()
	if (content):
		for line in content.split('\n'):
			line = normalizeLine(line_norm_fn, line)
			k,v = split(line, sep)
			result[k] = v
	return result

