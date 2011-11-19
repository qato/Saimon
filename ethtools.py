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
import array, fcntl, os, socket, struct

SIOCETHTOOL = 0x8946

ETHTOOL_GSET = 0x00000001

def ethtool(sock, name, buf):
    ifreq = struct.pack('16sP', name, buf.buffer_info()[0])
    fcntl.ioctl(sock.fileno(), SIOCETHTOOL, ifreq)

def ethtool_info(sock, name):
    cmd = struct.pack('=I', ETHTOOL_GSET)
    buf = array.array('c', cmd)
    format = '=IIHBBBBBBIIHBBIII'
    buf.extend('\0' * struct.calcsize(format))
    ethtool(sock, name, buf)
    return dict(zip(['supported', 'advertising', 'speed', 'duplex', 'port', 'phy_address', 'transceiver', 'autoneg', 
    				'mdio_support', 'maxtxpkt', 'maxrxpkt','speed_hi','eth_tp_mdix','reserved2', 'lp_advertising', 'r1','r2'],
                    struct.unpack(format, buf[len(cmd):])))

def ethtool_get_speed(device):
    sock = socket.socket()
    info = ethtool_info(sock, device)
    sock.close()
    return info['speed']
