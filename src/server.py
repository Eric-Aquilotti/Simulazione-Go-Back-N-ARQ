import time
import socket
import random

expected = 0

def handleMessage():
    global expected
    message, addr = sock.recvfrom(1024)
    print(f"Received {message.decode()}, expected {expected}")
    # 5% of the times long response.
    if random.random() < .05:
        print("Simulating long time response . . .")
        time.sleep(2)
        sendHack(message, addr)
    # 5% of the times transmission error.
    elif (random.random() < .05):
        print("Simulating transmission error . . .")
    else:
        sendHack(message, addr)

def sendHack(message, addr):
    global expected
    packNumber = int(message.decode().split(':')[0])
    if (packNumber == expected):
        print(f"Sending ack for {packNumber}\n\n")
        sock.sendto(str(packNumber).encode(), addr)
        expected += 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('localhost', 8080)
sock.bind((address))

print(
    f"""
    The server started an UDP socket on {address}
    The server is waiting to receive messages that are ordered starting from 0
    and is willing to send acks for the received ones.
    """
)

while True:
    handleMessage()
    time.sleep(.5)
