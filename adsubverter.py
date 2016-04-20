# encoding: UTF-8

import argparse
import random
import signal
import socket
import sys
import time

from scapy.all import *
detector = None
WINDOW = 5
SEQ_LEN = 15

scanner = None
PORT_MIN = 0
PORT_MAX = 65535

# from prev assignment
drone_address = ('192.168.1.1',5556)
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



class Detector(object):
    """Port Scanner."""

    def __init__(self):
        """Sets up scanner."""
        self.packetList = {}

    def shutdown(self):
        """ close """
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

            # add the packet to the list for the src
            if src not in self.packetList:
                self.packetList[src] = [[port, currentTime]]
            else:
                self.packetList[src].insert(0, [port, currentTime])

            # drop the old packets
            for ip in self.packetList:
                oldest = len(self.packetList[ip]) - 1
                if (oldest >= 0):
                    while(currentTime - self.packetList[ip][oldest][1] > WINDOW):
                        self.packetList[ip].pop()
                        oldest = oldest-1

            # check the packet list for a sequence
            if (len(self.packetList[src]) > SEQ_LEN - 1):
                self.checkPacketList(src)

        return packetCallback

    def checkPacketList(self, src): # TODO fix the checking after dict revisionss
        """ Searches the packet list of src for consecutive ports """
        lastPort = None
        counter = 0
        for port, time in self.packetList[src]:
            if lastPort != port+1:
                counter = 1
                lastPort = port
            else:
                counter += 1
                lastPort = port
                if counter > SEQ_LEN - 1:
                    print('Scanner detected. The scanner originated from host %s' % (src))
                    self.shutdown()

    def detect(self):
        """ Begins sniffing with onPacket callback """
        sniff(iface="eth1", prn=self.onPacket())

def handler(signum,frame):
    """ handle a SIGINT """
    print('int')
    if detector:
        print('Shutting down')
        detector.shutdown()
    sys.exit(0)

def main():
    """ Sets up and runs the detector. """
    detector = Detector()
    try:
        detector.detect()
    except Exception as e:
        print(e)
        detector.shutdown()

if __name__ == "__main__":
    signal.signal(signal.SIGINT,handler)
    main()



