#!/usr/bin/env python
# encoding: UTF-8

import argparse
import random
from scapy.all import *
import signal
import socket
import sys
import time

# unverified? 
DRONE_IP = ('192.168.1.1',5556)

# for the subverter instance
subverter = None

# code used to send land commands?

# seqno = 1
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.bind(("", 5554))
# def setBits( lst ):
#     """
#     set the bits in lst to 1.
#     also set bits 18, 20, 22, 24, and 28 to one (since they should always be set)
#     all other bits will be 0
#     """
#     res = 0
#     for b in lst + [18,20,22,24,28]:
#         res |= (1 << b)
#     return res
# def sendCommand( cmd ):
#     global address
#     global seqno
#     global s
#     print "DEBUG: Sending:  '%s'" % cmd.strip()
#     s.sendto(cmd ,address)
#     seqno += 1    
# def land():
#     global seqno
#     land_cmd = setBits([])
#     for i in xrange(1,25):
#         sendCommand("AT*REF=%d,%d\r" % (seqno,land_cmd))

class Subverter(object):
    """ Lands adversary drones. """

    def __init__(self):
        """ Sets up scanner. """
        pass

    def shutdown(self):
        """ Ends the subverting. """
        sys.exit(0)

    def onPacket(self):
        """ Returns a callback function w/ access to class vars. """
        def packetCallback(packet):
            """ A callback that keeps track of packets seen 
            and calls a method to search for consecutive probes.
            """
            src = packet[IP].src
            port = packet[TCP].dport
            currentTime = time.time()

            # TODO: if it is going to the drone, forge a copy to land

        return packetCallback

    def subvert(self):
        """ Begins sniffing with onPacket callback """
        sniff(iface="eth1", prn=self.onPacket())

def handler(signum,frame):
    """ Handles a SIGINT (ctrl c) """
    print('Interrupted')
    if subverter:
        print('Shutting down')
        subverter.shutdown()
    sys.exit(0)

def main():
    """ Sets up and runs the Subverter. """
    subverter = Subverter()
    try:
        subverter.subvert()
    except Exception as e:
        print(e)
        subverter.shutdown()

if __name__ == "__main__":
    signal.signal(signal.SIGINT,handler)
    main()



