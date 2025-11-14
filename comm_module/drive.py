"""
TSEA29 2024 group 9

This file handles sending steering instructions.
A thread constantly sends whatever instruction the main loop gives to the
steering module AVR.
"""

import subprocess
# from car_settings import AVR_BAUDRATE

# Steering module:
# steering = serial.Serial(STEERING_FILENAME, baudrate=115200)
INCOMING_SIGNAL = "00000000"


def activate_kill_switch(steer_port):
    set_gas_and_servo(1, 128, False, True, steer_port)


def set_gas_and_servo(
    velocity: int, angle: int, backward: bool, brake: bool, steer_port: str
):
    """Primitive function for setting engine effect."""

    direction = 1

    if brake:
        direction += 2
    if backward:
        direction += 1

    subprocess.Popen(
        [
            "steer",
            "-p",
            f"{steer_port}",
            "-v",
            f"{velocity}",
            "-a",
            f"{angle}",
            "-d",
            f"{direction}",
        ]
    ).wait()
