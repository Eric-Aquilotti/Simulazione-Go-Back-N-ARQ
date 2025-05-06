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
data = ["pkt" + str(i) for i in range(nPackets)]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 8080)

sock.setblocking(False)

def send_message(i):
    message = f"{i}:{data[i]}"
    sock.sendto(message.encode(), server_address)
    print(f"Sent {message}")

base: int = 0
current: int = 0
lost_packets: int = 0
retrasmissions: int = 0

while base < len(data):
    while current < min(len(data), base + window_size):
        send_message(current)
        if current == base:
            timer_start = time.time()
        current += 1
    
    remaining_time = timeout - (time.time() - timer_start) if timer_start else timeout
    if remaining_time <= 0:
        print("Timeout --> retransmitting window")
        retrasmissions += 1

        # Retransmit all un-acked packets
        for seq in range(base, current):
            lost_packets += 1
            send_message(seq)
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

print(f"{nPackets} packets were sent succesfully\nLost packages: {lost_packets}\nRetrasmissions: {retrasmissions}")