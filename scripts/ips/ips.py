# -*- coding: utf-8 –*-

"""
使用 高春晖的2016.6月的IP库  https://www.ipip.net/index.html
github地址： https://github.com/17mon/python
遇数据不准确时请及时更新
"""

import struct
from socket import inet_aton
import os
import sys


_unpack_V = lambda b: struct.unpack("<L", b)
_unpack_N = lambda b: struct.unpack(">L", b)
_unpack_C = lambda b: struct.unpack("B", b)


class IP(object):
    offset = 0
    index = 0
    binary = ""
    file = ''

    @staticmethod
    def load(file):
        if IP.file == file:
            return
        try:
            path = os.path.abspath(file)
            with open(path, "rb") as f:
                IP.binary = f.read()
                IP.offset, = _unpack_N(IP.binary[:4])
                IP.index = IP.binary[4:IP.offset]
                IP.file = file
        except Exception as ex:
            print "cannot open file %s" % file
            print ex.message
            exit(0)

    @staticmethod
    def find(ip):
        index = IP.index
        offset = IP.offset
        binary = IP.binary
        nip = inet_aton(ip)
        ipdot = ip.split('.')
        if int(ipdot[0]) < 0 or int(ipdot[0]) > 255 or len(ipdot) != 4:
            return "N/A"

        tmp_offset = int(ipdot[0]) * 4
        start, = _unpack_V(index[tmp_offset:tmp_offset + 4])

        index_offset = index_length = 0
        max_comp_len = offset - 1028
        start = start * 8 + 1024
        while start < max_comp_len:
            if index[start:start + 4] >= nip:
                index_offset, = _unpack_V(index[start + 4:start + 7] + chr(0).encode('utf-8'))
                index_length, = _unpack_C(index[start + 7])
                break
            start += 8

        if index_offset == 0:
            return "N/A"

        res_offset = offset + index_offset - 1024
        return binary[res_offset:res_offset + index_length].decode('utf-8')


class IPX:
    binary = ""
    index = 0
    offset = 0

    @staticmethod
    def load(file):
        try:
            path = os.path.abspath(file)
            with open(path, "rb") as f:
                IPX.binary = f.read()
                IPX.offset, = _unpack_N(IPX.binary[:4])
                IPX.index = IPX.binary[4:IPX.offset]
        except Exception as ex:
            print "cannot open file %s" % file
            print ex.message
            exit(0)

    @staticmethod
    def find(ip):
        index = IPX.index
        offset = IPX.offset
        binary = IPX.binary
        nip = inet_aton(ip)
        ipdot = ip.split('.')
        if int(ipdot[0]) < 0 or int(ipdot[0]) > 255 or len(ipdot) != 4:
            return "N/A"

        tmp_offset = (int(ipdot[0]) * 256 + int(ipdot[1])) * 4
        start, = _unpack_V(index[tmp_offset:tmp_offset + 4])

        index_offset = index_length = -1
        max_comp_len = offset - 262144 - 4
        start = start * 9 + 262144

        while start < max_comp_len:
            if index[start:start + 4] >= nip:
                index_offset, = _unpack_V(index[start + 4:start + 7] + chr(0).encode('utf-8'))
                index_length, = _unpack_C(index[start + 8:start + 9])
                break
            start += 9

        if index_offset == 0:
            return "N/A"

        res_offset = offset + index_offset - 262144
        return binary[res_offset:res_offset + index_length].decode('utf-8')


cache = {}


def get_ip_addr(ip):
    """
    得到IP 所在区域
    """
    if not ip:
        return ''

    if ip in cache:
        addr = cache[ip]
    else:
        cur_dir = "%s/17monipdb.dat" % os.path.dirname(os.path.abspath(__file__))
        IP.load(cur_dir)
        addr = IP.find(ip)
        cache[ip] = addr
    return addr


if __name__ == '__main__':

    count = 0
    ip_list_file = "%s/ip_list.txt" % os.path.dirname(os.path.abspath(__file__))
    with open(ip_list_file, 'r') as f:
        for ip in f:
            ip_addr = get_ip_addr(ip)
            print '====ip', ip, ip_addr
            count += 1

    # print 'all_ip_count', count
    # IPX.load(os.path.abspath("mydata4vipday2.datx"))
    # print IPX.find("118.28.8.8")