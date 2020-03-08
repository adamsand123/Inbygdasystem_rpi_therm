from udp import *
from gpio import *
from time import *
import math

def js_map(x, inMin, inMax, outMin, outMax):
    return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin

def blink():
	pinMode(1, OUT)
	socket = UDPSocket()
	socket.begin(1235)
	
	while True:
		data = math.floor(js_map(analogRead(A0), 0, 1023, -100, 100) + 0.5)
		
		socket.send("10.0.0.2", 1235, data)
		
		if int(data) > 26:
			digitalWrite(1, HIGH);
			
		else:
			digitalWrite(1, LOW);
			
		sleep(1)
			
blink()