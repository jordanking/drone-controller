# encoding: UTF-8
import socket
import sys, tty, termios

def getChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def setBits( lst ):
    """
    set the bits in lst to 1.
    also set bits 18, 20, 22, 24, and 28 to one (since they should always be set)
    all other bits will be 0
    """
    res = 0
    for b in lst + [18,20,22,24,28]:
        res |= (1 << b)
    return res

def sendCommand( cmd ):
    global address
    global seqno
    global s
    print "DEBUG: Sending:  '%s'" % cmd.strip()
    s.sendto(cmd ,address)
    seqno += 1

def reset():
    global seqno
    seqno = 1
    sendCommand("AT*FTRIM=%d\r" % seqno )
     
def takeoff():
    global seqno
    sendCommand("AT*FTRIM=%d\r" % seqno )
    takeoff_cmd = setBits([9])
    for i in xrange(1,25):
        sendCommand("AT*REF=%d,%d\r" % (seqno,takeoff_cmd))
     
def land():
    global seqno
    land_cmd = setBits([])
    for i in xrange(1,25):
        sendCommand("AT*REF=%d,%d\r" % (seqno,land_cmd))

def toggleEmergencyMode():
    global seqno
    shutdown_cmd = setBits([8])
    sendCommand("AT*REF=%d,%d\r" % (seqno,shutdown_cmd))

def roll(direction): #fly left/right

    global seqno
    if direction == 'j': #fly left at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1, -1098907648,0,0,0))
    elif direction == 'k': #fly right at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1, 1048576000,0,0,0))

def pitch(direction): #fly front/back

    global seqno
    if direction == 'i': #fly frontwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1, 0,-1098907648,0,0))
    elif direction == 'm':#fly backwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1, 0,1048576000,0,0))

def gaz(direction): #fly up/down

    global seqno
    if direction == 'r': #fly upwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1,0,0,1048576000,0))
    elif direction == 'c': #fly downwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1, 0,0,-1098907648,0))

def yaw(direction): #spin left/right

    global seqno

    if direction == 'd': #spin counterclockwise at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1, 0,0,0,-1098907648))
    elif direction == 'c': #fly clockwise at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,1, 0,0,0,1048576000))

def printUsage():
    print "\n\n"
    print "Keyboard commands:"
    print "\tq       - quit"
    print "\tt       - takeoff"
    print "\tl       - land"
    print "\t(space) - emergency shutoff"
    print "\tj       - roll L"
    print "\tk       - roll R"
    print "\ti       - pitch front"
    print "\tm       - pitch back"
    print "\tr       - fly up"
    print "\tc       - fly down"
    print "\td       - spin clockwise"
    print "\tf       - spin counterclockwise"

print """
NOTE:  This program assumes you are already connected to the
       drone's WiFi network.
"""

address = ('192.168.1.1',5556)
seqno = 1
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 5554))

while True:
    printUsage()
    ch = getChar()
    if ch == 'q':
        exit(0)
    elif ch == 't':
        takeoff()
    elif ch == 'l':
        land()
    elif ch == ' ':
        reset()
        toggleEmergencyMode()
    elif ch == 'j' or ch == 'k':
        roll(ch)
    elif ch == 'i' or ch == 'm':
        pitch(ch)
    elif ch == 'r' or ch == 'c':
        gaz(ch)
    elif ch == 'd' or ch == 'f':
        yaw(ch)
    else:
        print "Invalid command!"