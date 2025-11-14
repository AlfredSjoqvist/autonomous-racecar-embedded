"""
TSEA29 2024 group 9

This file is a test of the UART interface for the steering module.
"""

import socket
import serial

SERVER_IP = "172.20.10.7"
PORT = 12302
UPDATED = False

# Serial UART file.
SENDER_USB_PORT = "COM4"  # OBS ändra port så den passar med pajen
# RECEIVER_USB_PORT = "COM3"
BAUDRATE = 9600  # Baud rate, must match the ATMega1248P setting
INCOMING_SIGNAL = "00000000"
HOLES_TO_SPEED_FACTOR = 1


def start_server(server_ip=SERVER_IP, port=PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, port))
    server_socket.listen()
    server_socket.settimeout(10)  # Set timeout for 10 seconds
    key_vector = []

    print(f"Server listening on {server_ip}:{port}")

    try:
        while True:
            try:
                conn, client_address = server_socket.accept()
                print(f"Connection from {client_address}")

                while True:
                    data = conn.recv(1024)
                    if data:
                        print(
                            f"Received gas command with gas level: '{data.decode()}' from client"
                        )
                        conn.sendall(b"Gas command received.")
                        if data.decode() == "w":
                            key_vector.append("W")
                        if data.decode() == "w'":
                            key_vector.remove("W")
                        if data.decode() == "a":
                            key_vector.append("A")
                        if data.decode() == "a'":
                            key_vector.remove("A")
                        if data.decode() == "d":
                            key_vector.append("D")
                        if data.decode() == "d'":
                            key_vector.remove("D")
                        if data.decode() == "s":
                            key_vector.append("S")
                        if data.decode() == "s''":
                            key_vector.remove("S")
                        steer_car(key_vector)
                        # print(data.decode())
                        # key_vector = data.decode()
                        # steer_car(key_vector)
                    else:
                        break
            except socket.timeout:
                print("Waiting for a connection...")
    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        server_socket.close()
        print("Server socket closed")


"""
def decode_speed():
    # Receive the holes per second via UART (WIP)
    global current_speed
    if ser_receiver.in_waiting:
        received_data = ser_receiver.read(ser_receiver.in_waiting)
        holes_per_second = received_data.decode('ascii', errors='ignore')
        current_speed = holes_per_second * HOLES_TO_SPEED_FACTOR
"""


def steer_car(key_vector):
    # ACCELERATION = 20
    TURNING_FACTOR = 1
    turn_angle = None

    if "W" in key_vector and "S" in key_vector:
        pass
    elif "W" in key_vector:
        local_speed = 200
    elif "S" in key_vector:
        local_speed = 1

    if "A" in key_vector and "D" in key_vector:
        pass
    elif "A" in key_vector:
        turn_angle = int(127 * (1 - TURNING_FACTOR))
    elif "D" in key_vector:
        turn_angle = int(128 + 127 * TURNING_FACTOR)

    set_gas_and_servo(local_speed, turn_angle)


def string_to_bit_sequence(text: str) -> str:
    return "".join(format(ord(char), "08b") for char in text)


def set_gas_and_servo(duty_cycle: int, servo_cycle: int):
    servo_bit_sequence = f"{servo_cycle:08b}"
    gas_bit_sequence = f"{duty_cycle:08b}"

    avr_command = INCOMING_SIGNAL + gas_bit_sequence + servo_bit_sequence

    print(f"avr command set to {avr_command}")

    send_bits_to_avr(avr_command)


def send_bits_to_avr(bit_sequence):
    """Split up a string of 0:s and 1:s to a bit sequence that is sent via UART to the AVR"""

    # Ensure the bit sequence length is a multiple of 8 by padding with zeros if necessary
    if len(bit_sequence) % 8 != 0:
        bit_sequence = bit_sequence.zfill(
            len(bit_sequence) + (8 - len(bit_sequence) % 8)
        )

    # Convert each 8-bit chunk to an integer and send it as a byte
    for i in range(0, len(bit_sequence), 8):
        byte_chunk = bit_sequence[i : i + 8]
        integer_value = int(byte_chunk, 2)
        byte_message = integer_value.to_bytes(1, byteorder="big")
        ser_sender.write(byte_message)  # Send each byte over UART


if __name__ == "__main__":
    set_gas_and_servo(1, 128)

    ser_sender = serial.Serial(port=SENDER_USB_PORT, baudrate=BAUDRATE, timeout=1)

    start_server()
    """
    ser_receiver = serial.Serial(
    port=RECEIVER_USB_PORT,          
    baudrate=BAUDRATE,              
    bytesize=serial.EIGHTBITS,      # Byte size (usually 8)
    parity=serial.PARITY_NONE,      # Parity bit (None for no parity)
    stopbits=serial.STOPBITS_ONE,   # Stop bit (usually 1)
    timeout=1                       # Optional: read timeout in seconds
    )
    """
