##
## A very low level AR.Drone2.0 Python controller
## by Micah Sherr
## (use at your own risk)
##

# Each group will be writing a controller to control the drones. The drone acts as a wireless access
# point (WAP). Your controller will operate on a group member’s laptop (or, if you are really
# masochistic, a tablet or smartphone1
# ). You should join the drone’s WAP using the computer’s
# built-in functionality. That is, your controller should assume that the computer is already connected
# to the drone’s WAP.

# Your controller should have the following functionality:
# • The controller should enable the drone to take off and hover.
# • The controller should enable the drone to land.
# • The controller must have an emergency power-off mode.
# • The controller should enable the drone to adjust its roll (left/right tilt), pitch (front/back
# tilt), gaz (vertical speed), and yaw (angular speed).
# • Your controller should be interactive – the user should be able to issue the above commands
# using single keystrokes (without having to press ENTER).


# Although you don’t have to base your code off of the above, we strongly encourage you to do so.
# You do not need to cite our code. You may not use the Parrot SDK — your controller must craft its
# own control messages (see the teaching staff’s controllers for examples).

# And there’s even more good news! There’s a very good writeup of the drone’s interface at:
# http://goo.gl/zZKDCn. You should read chapters A-D, carefully!

# A tricky bit of the assignment is to take as input single keystrokes without requiring the user to
# press ENTER. Guess what? This is also done for you! See the above code for details.

# Your controller does not need to have a GUI or show the streaming video from the drone. In effect,
# you’ll be adding just the steering features to the provided code.

# So, how can you build a controller without easy access to the drone? Fortunately, the fact that the
# drone uses UDP and that Wireshark “speaks” the AR.Parrot protocol makes this fairly easy. You
# can operate your controller without the drone and capture all messages using tcpdump. (Make
# sure to set the snaplength to be 0 to capture all of the payloads.) Then, using Wireshark, you
# can see whether Wireshark’s interpretation of the message matches what you intended. Note that
# you’ll need to use a recent version of Wireshark since older versions do not know how to parse
# AR.Parrot messages.

#Developer Guide - http://www.robotappstore.com/Files/KB/ARDrone/ARDrone_SDK_1_7_Developer_Guide.pdf
# Syntax : AT*PCMD=%d,%d,%d,%d,%d,%d<LF>
# Argument 1 : the sequence number
# Argument 2 : flag enabling the use of progressive commands and/or the Combined Yaw mode (bitfield)
# Argument 3 : drone left-right tilt - floating-point value in range [−1..1]
# Argument 4 : drone front-back tilt - floating-point value in range [−1..1]
# Argument 5 : drone vertical speed - floating-point value in range [−1..1]
# Argument 6 : drone angular speed - floating-point value in range [−1..1]


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
    s.sendto(cmd,address)
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
    #roll_cmd = setBits([0,1]) 
    if direction == 'j': #fly left at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, -1098907648,0,0,0))
    elif direction == 'k': #fly right at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, 1048576000,0,0,0))

def pitch(direction): #fly front/back

    global seqno
    #pitch_cmd = setBits([0,1])
    if direction == 'i': #fly frontwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, 0,-1098907648,0,0))
    elif direction == 'm':#fly backwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, 0,1048576000,0,0))

def gaz(direction): #fly up/down

    global seqno
    #gaz_cmd = setBits([0,1])
    if direction == 'r': #fly upwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, 0,0,1048576000,0))
    elif direction == 'c': #fly downwards at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, 0,0,-1098907648,0))

def yaw(direction): #spin left/right

    global seqno
    #yaw_cmd = setBits([0])
    if direction == 'd': #spin counterclockwise at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, 0,0,0,-1098907648))
    elif direction == 'c': #fly clockwise at 1/4 speed
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d" % (seqno,1, 0,0,0,1048576000))


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
        
    
