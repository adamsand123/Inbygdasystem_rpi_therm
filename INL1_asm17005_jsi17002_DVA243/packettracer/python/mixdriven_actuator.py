from udp import *
from time import *
from gpio import *

packetRecieved = False

def onUDPReceive(ip, port, data):
	global packetRecieved
	packetRecieved = True
	
	pinMode(1, OUT)

	if data == "HELLO!":
		print uptime()
		print(data)
	elif int(data) >= 26:
		customWrite(1, 2);
	else:
		customWrite(1, 0);
	
def main():
	socket = UDPSocket()
	socket.onReceive(onUDPReceive)
	socket.begin(1235)
	
	global packetRecieved

	while True:
		if packetRecieved == True:
			socket.send("10.0.0.1", 1235, "OK")
			packetRecieved=False

if __name__ == "__main__":
	main()