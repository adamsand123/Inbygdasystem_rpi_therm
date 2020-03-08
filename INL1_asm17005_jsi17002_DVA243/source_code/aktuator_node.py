import socket                   # Library to handle udp connections
from threading import *         # Library to enable threading
import threading                # Threading to enable the lock function
import time                     # Import time library
import RPi.GPIO as GPIO         # Library to be able to control the electronics / GPIO pins of the RPi
import datetime

isOn=False                      # Global variable to track if the first LED is on or off
keepAlive=1                     # global variable tat keeps track of the connection to the sensor node with hello messages

def udp_server(host='10.34.0.1', port=1234):                            # udp server function that listens to the socket 10.34.0.1:1234
        print("started udp serv")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)            # create a socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # check if socket is already in use and if so cancel it to be able to use it
        s.bind((host, port))                                            # start listening on host ipv4 address 10.34.0.1 and port 1234 (by default if other arguments isn't passed to udp_server())

        global lastRecv
        global keepAlive
        global isOn

        while True:                                                     # while loop that keeps the udp server running
                (data, addr) = s.recvfrom(128*1024)                     # store the return values from the incoming connection in the variables, 'data' and 'addr'
                udpSendHello(data)                                      # Calls a function that sends back to recieved data (as a form of a 2-way handshake to verify to sender that we recieved data)

                if int(data) == 1:      # checks if the value of recieved data is equal to 1 - turn first LED on
                        if isOn == False:       # checks if the first LED is turned on or not
                                isOn = True
                                ledThread=Thread(target=led1Start)      # if isOn is false start a new thread for the function led1Start() to turn on the first LED (otherwise if it is already on we don't have to turn it on again)
                                ledThread.start()                       # start the thread

                elif int(data) == 0:    # checks if recieved data is equal to 0 (indicating that the LED should be turned off)
                        ledStop()       # turn of all LEDs

                elif int(data) == -1:   # -1 turn of the whole program
                        return 0

                elif int(data) == 2:
                        keepAlive = 1   # set the global variable keepAlive to 1 every time we recieve an error message
                else:   # unkown data value recieved (accepts: -1,0,1)
                        print("ERROR: Unkown input")

        return 0

def udpSendHello(data): # function that sends the argument to the other RPi @ 10.35.0.2:5555
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # create a socket
        address = ("10.35.0.2", 5555) # define a tuple to hold the socket information of the other RPi
        s.sendto(data, address) # send that data to the socket

        return 0

def led2Start():        # function that turns on the second LED (will be called from led1Start on a different thread)
        global isOn     # defines that the variable isOn should be the global variable and not a new local variable
        GPIO.output(14, GPIO.HIGH)      # send ON signal (HIGH) to GPIO pin 14 to turn on the second LED

        print("Turning on LED2 at time: " + str(datetime.datetime.now()))

        return 0

def ledStop():          # function to turn of both LEDs
        global isOn     # defines that the variable isOn should be the global variable and not a new local variable
        isOn = False    # set global variable isOn to false indicating the LEDs are turned off
        GPIO.output(14, GPIO.LOW)       # turn of the LED on GPIO pin 14
        GPIO.output(4, GPIO.LOW)        # turn of the LED on GPIO pin 14

        return 0

def led1Start():        # function that turns the first LED on
        global isOn     # defines that the variable isOn should be the global variable and not a new local variable
        GPIO.output(4, GPIO.HIGH)       # send ON signal (high) to GPIO pin 4, turning the led ON
        tid1=time.time()        # variable that stores the time when LED1 is turned on
        print("Turning on LED1 at time: " + str(datetime.datetime.now()))
        time.sleep(5)   # sleep this thread (this function will only be run in a separate thread from the main thread)


        if isOn:        # after the thread has sleept for 5 seconds - check if the variable isOn is true (if LED1 is on)
                try:
                        led2Start() # turn LED2 on if LED1 is on
                except:
                        return 0

def keepAliveFunc():    # Function that keeps track of the connection to the sensor node
        global keepAlive        # global variable that keeps track of the keep-alive value, true means that we have recieved a keep alive withn the last 6 seconds
        firstWarning=True       # variable that keeps track if this is the first warning or not (so that we dont spam the error / status message
        while True:
                if keepAlive == 1:      # if keep alive is set to 1 (or true)
                        if firstWarning == False:       # if first warning is false meaning that this is the first warning since the connection changed status
                                print("STATUS: Connection established to host") # print status message indicating we have recieved connection to the sensor node
                                firstWarning=True       # set firstwarning to ture indicating we have recieved the first warning
                        keepAlive = 0   # set the global variable keepAlive to 0 - keepAlive will be set to 1 everytime we recieve a hello message in main-thread
                        time.sleep(6)   # sleep for 6 seconds

                elif keepAlive == 0 and firstWarning: # if keepAlive is 0 and firstWarning is true print error message (that we lost connection)
                        print("ERROR: Lost Connection to host")
                        firstWarning=False      # set firstWarning to false indicating we have printed the first wanring

def main():
        # Turns the GPIO pins 4, and 14 on for communication OUT (to them)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(14, GPIO.OUT)
        GPIO.setup(4, GPIO.OUT)

        t1 = Thread(target=keepAliveFunc)
        t1.start()
        ledStop() # turns the LEDs off (if they should have been on by default) before starting the programing

        udp_server() # start UDP server from where another thread will be run to controll the LEDs

        GPIO.cleanup() # turns the GPIO pins of before closing the program

        return 0

if __name__ == '__main__':
        main()
