import time
import socket
import select
from typing import Callable

def read_int(message: str, condition: Callable[[int], bool], conditionErrorMessage: str) -> int:
    while True:
        try:
            value = int(input(message))
            if not condition(value):
                print(conditionErrorMessage)
                continue
            return value
        except ValueError:
            print("Please insert an integer")

window_size: int = read_int(
    message="Window size: ",
    condition= lambda i: i > 0,
    conditionErrorMessage="Please insert an integer > 0"
)

nPackets: int = read_int(
    message="N packets to send: ",
    condition= lambda i: i > 0,
    conditionErrorMessage="Please insert an integer > 0"
)

timeout: float = 2

data: list = ["pkt" + str(i) for i in range(nPackets)]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address: tuple = ('localhost', 8080)

sock.setblocking(False)

def send_message(i):
    message = f"{i}:{data[i]}"
    sock.sendto(message.encode(), server_address)
    print(f"Sent {message}")

def send_window(base, current):
    for seq in range(base, current):
        send_message(seq)

base: int = 0
current: int = 0
lost_packets: int = 0
retrasmissions: int = 0

while base < len(data):
    while current < min(len(data), base + window_size):
        send_message(current)
        if current == base:
            timer_start: float = time.time()
        current += 1
    
    remaining_time: float = timeout - (time.time() - timer_start) if timer_start else timeout
    if remaining_time <= 0:
        print("Timeout --> retransmitting window")
        retrasmissions += 1

        # Retransmit all un-acked packets
        send_window(base=base, current=current)

        # Restart timer
        timer_start = time.time()
        continue
    
    ready, _, _ = select.select([sock], [], [], remaining_time)
    if ready:
        message, _ = sock.recvfrom(1024)
        ack = int(message.decode())
        print(f"Received ack {ack}")
        if ack == base:
            base += 1
            if base < current:
                timer_start = time.time()
            else: timer_start = None
        else:
            print(f"Ignoring out-of-order ack {ack}, expected {base}")

# Tell the server the communication is over and get number of lost packets
sock.sendto(b"EOF", server_address)
ready, _, _ = select.select([sock], [], [])
lost_packets = int(sock.recvfrom(1024)[0].decode())
print(f"{nPackets} packets were sent succesfully\nLost packets: {lost_packets}\nRetrasmissions: {retrasmissions}")