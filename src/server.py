import time
import socket
import random

expected = 0
packetLost = 0

# Returns true if the communication should continue
def handleMessage() -> bool:
    global expected, packetLost
    message, addr = sock.recvfrom(1024)

    # If transmission finished send packet lost.
    if "EOF" in message.decode():
        sock.sendto(str(packetLost).encode(), addr)
        return False

    print(f"Received {message.decode()}, expected {expected}")

    # 10% of the times error.
    if random.random() < .1:
        # 50% of the times long time response.
        if random.random() < .5:
            print("Simulating long time response . . .")
            time.sleep(2)
            sendHack(message, addr)
        # 50% of the times transmission error.
        else:
            print("Simulating packet lost . . .")
            packetLost += 1
    else:
        sendHack(message, addr)
    return True

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
    and is willing to send acks for the received ones. In the end it's expected
    to receive an EOF packet and it will send back how many packets were lost.
    """
)

while handleMessage():
    time.sleep(.1)
    continue
