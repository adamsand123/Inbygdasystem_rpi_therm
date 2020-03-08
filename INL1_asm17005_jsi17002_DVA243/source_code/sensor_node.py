import socket
from threading import *
from time import *
import datetime
import os


isOn = False #global variable, that check if we have sent a message that the temp has changed
answer = -1 #global variable, that check if weve got an ack
temp = 0
checkTimeOnce = False

#load drivers from operating system
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#where our sensor output file is located
temp_sensor = '/sys/bus/w1/devices/28-000009367a30/w1_slave'

#function that will handle sending messages to the other RPI
def udpSend():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        adress = ("10.34.0.1", 1234)
        global isOn
        global answer
        global temp
        while True:
                #if the temprature are 26 or greater and the isON variable is false, which means the lights shouldnt be on on the other rpi device we will send a message to tell it to turn it on.
                if temp >= 26 and not isOn:
                        try:
                                while not answer == 1: #keep sending until we get a 1 back from the other rpi device, to assure that he recieved the msg
                                        s.sendto("1", adress)
                                        isOn = True
                                        print "turn on"

                        except:
                                print "Error sending a 1"
                                sleep(1)
                #if temprature are below 26 degrees C and isOn is true, which means that we should turn of the lights and the lights are still on on the other device, send a 0 to tell the other device to turn lights off
                elif temp < 26 and isOn:
                        try:
                                while not answer == 0: #keep sending until we get a 0 back from the other rpi device, to assure that it revieced the msg
                                        s.sendto("0", adress)
                                        isOn = False
                                        print "turn off"

                        except:
                                print "Error sending a zero"

#function that will handle keepAlive messages, it will send a keepAlive every 2 sec.
def keepAlive():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        adress = ("10.34.0.1", 1234)
        while True:
                try:
                        s.sendto("2", adress)
                        sleep(2)
                        print "keep alive sent"

                except:
                        print("error sending keep alive")


#function that will handle messages that this RPI revieves.
def udpRecieve():
        global answer
        while True:
                try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        server = "10.35.0.2"
                        port = 5555
                        s.bind((server, port))
                        while True:
                                (data, addr) =  s.recvfrom(128*1024)
                                #if the data recieved is a 1, change answer to 1 to show that we got a acknowlegdement on the 1 we sent to the other rpi device, or if its a 0 change answer to 0
                                if int(data) == 1:
                                        answer = 1
                                elif int(data) == 0:
                                        answer = 0
                                elif int(data) == 2:
                                        keepAliveHolder = 2
                                else:
                                        print("error on recieve")

                except:
                        print "try again"

#function that read the output file from our thermometer
def thermFile():
        f = open(temp_sensor, 'r') #open thermometer output file
        lines = f.readlines() #read the lines
        f.close() #close the file
        return lines #return what was read from the file

#function that will figure out what temprature it is
def tempCheck():
        global temp
        global checkTimeOnce
        while True:
                lines = thermFile() #call the thermFile() function to get the lines

                #check for errors, take away everything from the line except for the last 3 chars, if there is a "YES" it means the temprature was read correctly, if there was something else keep reading the file
                while lines[0].strip()[-3:] != 'YES':
                        time.sleep(0.2)
                        lines = tempFile()
                tempErrorCheck = lines[1].find('t=') #the temprature numbers will be found after 't=', check whats there so we can check for errors
                if tempErrorCheck != -1: #if there was no error
                        tempValue = lines[1].strip()[tempErrorCheck+2:] #strip out "t= part" and keep only the temprature numbers
                        temp = float(tempValue) / 1000.0 #add some maths and get the temprature in celcius
                if temp >= 26 and not checkTimeOnce:
                        print "Temprature measured to be at 26 C or higher at: " + str(datetime.datetime.now())
                        checkTimeOnce = True


def main():
        global temp
        #create threads
        t1 = Thread(target=udpSend)
        t2 = Thread(target=udpRecieve)
        t3 = Thread(target=keepAlive)
        t4 = Thread(target=tempCheck)
        #start threads
        t1.start()
        t2.start()
        t3.start()
        t4.start()

        while True:
                sleep(1)
                print temp

if __name__=='__main__':
        main()
