#!/bin/env python
"""
TSEA29 2024 group 9

This file handles contains the main loop for the Communication module.

In the startup: It spawns threads for for handeling the LiDAR, Sensor module and
Steering module.

In the main loop: It controls the car with data from LiDAR and Sensor module.
It also communicates with the GUI external computer.
"""

import input_output
import lidar
import sensor
import drive
import mapping
import time
import ports
from queue import Queue
from threading import Thread

from car_settings import (
    STEER_USB_PORT,
    SENSOR_USB_PORT,
    LIDAR_USB_PORT,
    ENABLE_LIDAR,
    ENABLE_SENSOR,
    ENABLE_LISTEN,
    ENABLE_SEND,
    ENABLE_MAP,
    ENABLE_DRIVE,
    ENABLE_LIDAR_DRAW_LOCALLY,
    KILL_SWITCH_MS,
    MAIN_LOOP_UPS,
)

DEFAULT_COMMAND = None


def start_threads(
    tx_q: Queue, sensor_q: Queue, lidar_q: Queue, sensor_port: str, lidar_port: str
):
    if ENABLE_SENSOR:
        # Initiate sensor module thread
        sensor_thread = Thread(
            target=sensor.sensor_main, args=[sensor_q, tx_q, sensor_port]
        )
        sensor_thread.start()

    if ENABLE_LIDAR:
        # Initiate LiDAR thread
        LiDAR_thread = Thread(
            target=lidar.lidar_main,
            args=[ENABLE_LIDAR_DRAW_LOCALLY, lidar_q, lidar_port],
        )
        LiDAR_thread.start()

    if ENABLE_MAP:
        map_thread = Thread(target=mapping.map_main, args=[lidar_q, sensor_q, tx_q])
        map_thread.start()

    if ENABLE_SEND:
        send_thread = Thread(target=input_output.send_main, args=[tx_q])
        send_thread.start()


def main():
    """Commmunication module's main thread."""
    rx_q = Queue()
    tx_q = Queue()
    sensor_q = Queue()
    lidar_q = Queue()

    curr_angle = 128
    curr_velocity = 1
    velocity_temp = 1
    backward = False
    curr_brake = False
    ms_since_ping = 0

    # Set USB ports to default values.
    steer_port = STEER_USB_PORT
    sensor_port = SENSOR_USB_PORT
    lidar_port = LIDAR_USB_PORT
    try:
        p = ports.Ports.new()
        if ENABLE_DRIVE:
            steer_port = p.steer
        if ENABLE_SENSOR:
            sensor_port = p.sensor
        if ENABLE_LIDAR:
            lidar_port = p.lidar
    except:  # noqa: E722
        print("One or more usb port was not set up (probably missing)")

    if ENABLE_LISTEN:
        # Initiate listener to await commands.
        listener_thread = Thread(target=input_output.listen, args=[rx_q])
        listener_thread.start()
    else:
        # If running locally without connection, run this as startup.
        start_threads(tx_q, sensor_q, lidar_q, sensor_port, lidar_port)

    # If stop_all is true, stop the car from driving.
    stop_all = False

    # Main loop to run as long as the Communication module is on.
    while not stop_all:
        time.sleep(1 / MAIN_LOOP_UPS)  # Dont update too often to not overload cpu.

        if ENABLE_LISTEN and not rx_q.empty():
            command = rx_q.get()
        else:
            command = DEFAULT_COMMAND
            # Assumes valid input:

        # Handle commands
        match command:
            case ["throttle", {"velocity": velocity, "reverse": rev}]:
                curr_velocity = velocity
                backward = rev
                if ENABLE_DRIVE:
                    drive.set_gas_and_servo(
                        curr_velocity, curr_angle, backward, curr_brake, steer_port
                    )

            case ["steer", {"angle": angle}]:
                curr_angle = angle
                if ENABLE_DRIVE:
                    curr_angle = angle
                    drive.set_gas_and_servo(
                        curr_velocity, curr_angle, backward, curr_brake, steer_port
                    )
            case ["brake", {"brake": brake}]:
                if brake:
                    curr_brake = True
                    velocity_temp = curr_velocity
                    curr_velocity = 1
                    if ENABLE_DRIVE:
                        drive.set_gas_and_servo(
                            curr_velocity, curr_angle, backward, curr_brake, steer_port
                        )
                else:
                    curr_brake = False
                    curr_velocity = velocity_temp
                    if ENABLE_DRIVE:
                        drive.set_gas_and_servo(
                            curr_velocity, curr_angle, backward, curr_brake, steer_port
                        )
            case [
                "set_ports",
                {
                    "sensor_port": sensor_port,
                    "steer_port": steer_port1,
                    "lidar_port": lidar_port,
                },
            ]:
                # Once "set ports"-command is recieved, the startup of other threads begin.
                if ENABLE_LISTEN:
                    start_threads(tx_q, sensor_q, lidar_q, sensor_port, lidar_port)
                    steer_port = steer_port1

            case ["info", {"pc_ip_addr": gui_ip, "port_A": port_A}]:
                if ENABLE_SEND:
                    input_output.establish_connection(gui_ip, port_A, tx_q)
                    # input("Sending connection established, continue? (enter)")
            case ["exit", _]:
                pass
            case ["ping", _]:
                ms_since_ping = 0

            case None:
                ms_since_ping += 1000 / MAIN_LOOP_UPS

                if ms_since_ping > KILL_SWITCH_MS:
                    curr_angle = 128
                    curr_velocity = 1
                    backward = False
                    curr_brake = True
                    drive.set_gas_and_servo(
                        curr_velocity, curr_angle, backward, curr_brake, steer_port
                    )

                elif ENABLE_DRIVE:
                    curr_brake = False
                    drive.set_gas_and_servo(
                        curr_velocity, curr_angle, backward, curr_brake, steer_port
                    )

            case x:
                print(f"Unexpected: {x}")
                print(f"Type of message is: {type(x)}")


if __name__ == "__main__":
    main()
