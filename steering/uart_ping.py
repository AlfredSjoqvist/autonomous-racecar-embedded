"""
TSEA29 2024 group 9

This file is a test of the UART interface for the steering module.
"""

import serial

print(serial.__file__)  # This will print the path to the imported 'serial' module

UPDATED = False

# Serial UART file.
SENSOR_FILENAME = "COM4"
BAUDRATE = 9600

ser = serial.Serial(SENSOR_FILENAME, baudrate=BAUDRATE, timeout=1)


bit_sequence = "01111110"
integer_value = int(bit_sequence, 2)
byte_message = integer_value.to_bytes(1, byteorder="big")
byte_message = "Hello".encode("utf-8")


def string_to_bit_sequence(text: str) -> str:
    return "".join(format(ord(char), "08b") for char in text)


def create_time_based_bit_sequence(microseconds: int) -> str:
    microseconds_in_a_second = 10**6
    serve_sequence_length = 320

    bit_count = int(microseconds * 8 * BAUDRATE / microseconds_in_a_second)

    # Adjust bit_count to be divisible by 8
    if bit_count % 8 != 0:
        ex_bit_count = 8 - (bit_count % 8)
    else:
        ex_bit_count = 0

    angle_sequence = "1" * bit_count + "0" * ex_bit_count
    fill_sequence = "0" * (serve_sequence_length * 8 - len(angle_sequence))

    return angle_sequence + fill_sequence


def set_servo(steering_angle: int):
    """Set the steering angle
    steering_angle = an angle in degrees between -90 and 90
    """

    servo_begin = string_to_bit_sequence("S")
    servo_end = string_to_bit_sequence("E")
    straight_ahead_high_time = 1500
    left_right_scope = 500
    max_side_angle = 90

    angular_high_time = straight_ahead_high_time + int(
        left_right_scope * steering_angle / max_side_angle
    )

    servo_command = (
        servo_begin + create_time_based_bit_sequence(angular_high_time) + servo_end
    )

    send_bits_to_uart(servo_command)


def set_gas(duty_cycle: int):
    dc_msg_begin = string_to_bit_sequence("G")

    dc_bit_sequnce = f"{duty_cycle:08b}"
    print(dc_bit_sequnce)

    dc_command = dc_msg_begin + dc_bit_sequnce

    send_bits_to_uart(dc_command)


def send_bits_to_uart(bit_sequence):
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
        ser.write(byte_message)  # Send each byte over UART


if __name__ == "__main__":
    # byte_message = "Q".encode("utf-8")
    # binary_string = ''.join(format(byte, '08b') for byte in byte_message)
    # print(binary_string)
    set_gas(128)
