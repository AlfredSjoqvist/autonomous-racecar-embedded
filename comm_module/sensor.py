"""
TSEA29 2024 group 9

This file handles input from the sensor module.
A thread constantly recieves data from the sensor module AVR and makes it
availible for the main loop.
"""

from car_settings import (
    ADC_RESOLUTION,
    AVR_BAUDRATE,
    GYRO_SENSITIVITY,
    GYRO_ZERO,
    WHEEL_CIRCUMFERENCE,
)
from dataclasses import dataclass
import logging
import message
from queue import Queue
import serial
import time

logger = logging.getLogger(__name__)


@dataclass
class SensorData:
    velocity: float
    angular_rate: float
    delta_time: float
    sensor_angle: float


def calculate_angular_rate(adc_value: int) -> float:
    """
    Converts the ADC value from the gyro to an angular rate in degrees/second.
    Assumes 127 represents 0°/s, above is positive, below is negative.
    Returns neg value if rotation counter clockwise and pos otherwise
    """
    Vout = 5 * adc_value / ADC_RESOLUTION
    if adc_value == 127:
        return 0
    else:
        return (Vout - GYRO_ZERO) / (GYRO_SENSITIVITY)


def calculate_angle(angular_rate: float, delta_time, old_angle: float):
    return angular_rate * delta_time + old_angle


def calculate_distance(avg_hall_interupts: int) -> float:
    MAGNETS_PER_WHEEL = 10
    # Revolutions/s (we get avg_hall_interupts 10X/second)
    revolutions_per_second = avg_hall_interupts / MAGNETS_PER_WHEEL
    speed = revolutions_per_second * WHEEL_CIRCUMFERENCE
    return speed


# This is the main loop for the sensor module thread.
def sensor_main(sensor_q: Queue, tx_q: Queue, sensor_port: str) -> None:
    sensor_serial = serial.Serial(sensor_port, AVR_BAUDRATE, timeout=1, stopbits=2)
    # sensor = serial.Serial(SENSOR_FILENAME, baudrate=115200)

    # Then fill data and set updated to true
    previous_time = time()

    while True:
        if int.from_bytes(sensor_serial.read(1)) == 255:
            # Read sensor data
            left, right, gyro_data = tuple(sensor_serial.read(3))

            # Calculate velocity
            current_time = time()
            delta_time = current_time - previous_time
            avg_hall_inter = (left + right) / 2
            distance_covered = calculate_distance(avg_hall_inter)
            velocity = distance_covered / delta_time

            # Calculate angular_rate
            angular_rate = calculate_angular_rate(gyro_data)

            tx_q.put(message.sensor(velocity, angular_rate))
            sensor_q.put((velocity, angular_rate, delta_time))

            # For next time it enter while-loop
            previous_time = time()
