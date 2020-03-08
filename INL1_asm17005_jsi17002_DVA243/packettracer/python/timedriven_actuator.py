from udp import *
from time import *
from gpio import *

def onUDPReceive(ip, port, data):
	pinMode(1, OUT)

	if int(data) > 26:
		customWrite(1, 2);
	else:
		customWrite(1, 0);

def main():
	socket = UDPSocket()
	socket.onReceive(onUDPReceive)
	socket.begin(1235)
	
	while True:
		sleep(5)

if __name__ == "__main__":
	main()