'''
Created on Jan 20, 2020

@author: blew
'''
from socket import *
import datetime
import sys


def UDPserver(host,port,log):
    log.info("Listening on udp {}:{}".format(host, port))
    
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.bind((host, int(port)))
    while 1:
        (data, addr) = s.recvfrom(128*1024)
        yield data


# if __name__ == '__main__':
#     pass
