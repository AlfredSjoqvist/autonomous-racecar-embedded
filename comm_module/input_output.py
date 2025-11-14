"""
TSEA29 2024 group 9

This file handles sending and recieving from GUI external computer.
A thread constantly listens to what is sent from GUI.
"""

import time
import asyncio
import json
from queue import Queue
import socket
from websockets.asyncio.server import serve
from car_settings import MY_IP, LISTENER_PORT

SENDING_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)


# asyncio.run(main())
async def main(rx_q: Queue):
    async with serve(handler, "", 12306):
        await asyncio.get_running_loop().create_future()


def listen(rx_q: Queue):
    """
    Await message via LISTENER_PORT and MY_IP.
    """
    my_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_listener_socket.bind((MY_IP, LISTENER_PORT))
    my_listener_socket.listen(1)

    print(f"Listening on {MY_IP}:{LISTENER_PORT}...")

    external_sender_socket, address = my_listener_socket.accept()
    print(f"Connection from {address}")

    try:
        while True:
            data = external_sender_socket.recv(1024).decode()
            if data == 0:
                rx_q.put(["exit", {}])
                continue
            try:
                msg = json.loads(data)
                print(f"Valid message: {msg}")
                rx_q.put(msg)
            except json.JSONDecodeError:
                time.sleep(1)  # Slow down excessive printing.
                print(f"Invalid json recieved: {data}")
    finally:
        my_listener_socket.close()
        external_sender_socket.close()


def send_main(tx_q: Queue):
    """
    Send a message to EXTERN_IP via SENDER_SOCKET.
    """
    global SENDING_SOCKET
    while True:
        message = tx_q.get()
        try:
            SENDING_SOCKET.send(message.encode())
        except:  # förlåt @Kacper //Samuel  # noqa: E722
            print(f"Error sending: {message}")


def establish_connection(ip_addr: str, port_A: str, tx_q):
    """
    Establish connection to gui ip (ip_addr) via socket_A using SENDING_SOCKET
    """
    global SENDING_SOCKET
    print(f"Connecting to {ip_addr}:{port_A}...")
    SENDING_SOCKET.connect((ip_addr, int(port_A)))


def close_connection():
    """
    Close the socket
    """
    SENDING_SOCKET.close()
    print("Sender connection closed.")
