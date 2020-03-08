from udp import *
from gpio import *
from time import *
import math

packetRecieved = False

def js_map(x, inMin, inMax, outMin, outMax):
    return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
    
def onUDPReceive(ip, port, data):
	global packetRecieved
	packetRecieved = True
	
def blink():
	pinMode(1, OUT)
	socket = UDPSocket()
	socket.onReceive(onUDPReceive)
	socket.begin(1235)
	global packetRecieved

	isOn = False

	while True:
		data = math.floor(js_map(analogRead(A0), 0, 1023, -100, 100) + 0.5)

		tid = int(uptime())

		if (tid % 5) == 0:
			socket.send("10.0.0.2", 1235, "HELLO!")
			print tid

		if int(data) >= 26 and isOn == False:
			digitalWrite(1, HIGH);
			isOn=True
			
			while packetRecieved == False:
				socket.send("10.0.0.2", 1235, data)
				sleep(1)
				
				
		elif int(data) < 26 and isOn == True:
			digitalWrite(1, LOW);
			isOn=False
			
			while packetRecieved == False:
				socket.send("10.0.0.2", 1235, data)
				sleep(1)
			
		packetRecieved = False
			
blink()