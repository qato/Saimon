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

import time

def perc(value, total):
	if (total<=0): return 0.0
	result = float(float(100.0/total)*value)
	if result>100: result=100
	return result

def get_msec():
	return int(round(time.time() * 1000))

def calc_delta(curr, prev):
	delta = {}
	if prev:
		for (k,v) in curr.iteritems():
			v_prev = prev[k]
			if (type(v_prev)==type('')):
				v_prev=int(v_prev)
			if (type(v)==type('')):
				v=int(v)
			if (type(v)==type(0) and type(v_prev)==type(0)):
				delta[k]=v-v_prev
	return delta
