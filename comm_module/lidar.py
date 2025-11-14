"""
TSEA29 2024 group 9

This file handles input from the LiDAR.
It runs a c++ program (simple_grabber.c) to get data from the LiDAR and
converts the data to "cones".
"""

import asyncio
import cmath
from dataclasses import dataclass
import subprocess
import math
import signal
import os
import enum
from queue import Queue
from car_settings import (
    CONE_DIAM_LOWER,
    CONDE_DIAM_UPPER,
    CONE_DIAM_MIDDLE,
    COUNT_ONLY_AMOUNT_OF_DOTS_DISTANCE,
    MAX_VIEW_DISTANCE,
    MEAS_SIZE,
    OBJ_MAX_DISTANCE,
)
from typing import Self
from mapping import Cone
# AMOUNT_OF_DOTS_THRESHOLD  # Samuel forgot to implement this hehe. Let it be for the moment.


@dataclass
class Dot:
    """Class that are the data points coming from the lidar."""

    angle: float
    distance: float

    def centre_point(self, other: Self) -> Self:
        """Find centrum between this dot and another."""
        angle_diff = (self.angle - other.angle + 180) % 360 - 180
        ang = self.angle + angle_diff / 2
        dist = (self.distance + other.distance) / 2
        return Dot(ang, dist)

    def distance_to(self, other: Self) -> float:
        """Find distance between two dots"""
        x1 = self.distance * math.cos(math.radians(self.angle))
        y1 = self.distance * math.sin(math.radians(self.angle))
        x2 = other.distance * math.cos(math.radians(other.angle))
        y2 = other.distance * math.sin(math.radians(other.angle))
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_between_dots(dot1: Dot, dot2: Dot):
    """Find distance between two dots"""
    x1 = dot1.distance * math.cos(math.radians(dot1.angle))
    y1 = dot1.distance * math.sin(math.radians(dot1.angle))
    x2 = dot2.distance * math.cos(math.radians(dot2.angle))
    y2 = dot2.distance * math.sin(math.radians(dot2.angle))
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def kill_lidar(lidar_cpp):
    """Stop the lidar, doesn't work though."""
    os.kill(lidar_cpp.pid, signal.SIGINT)


def lidar_main(do_paint_local: bool, lidar_q: Queue, lidar_port: str):
    """Main funcion for the LiDAR"""

    # Note:
    # We used a modified version of "simple_grabber" which is a program created
    # by Slamtec availible in the rplidar's SDK at: https://github.com/Slamtec/rplidar_sdk
    # We modified it to fit our purposes.
    args = [
        "../rplidar_sdk/output/Linux/Release/simple_grabber",
        "--channel",
        "--serial",
        lidar_port,
        "115200",
    ]
    print("Lidar on usb port: " + lidar_port)
    lidar_cpp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        data_str = ""
        data_lst = []

        for i in range(0, MEAS_SIZE):
            try:
                line = lidar_cpp.stdout.readline().decode("utf-8").split()
                angle = 90 - float(line[0])
                distance = float(line[1])

                dot = Dot(angle, distance)
                data_lst.append(dot)

                # TODO: Change following string to whatever protocol is used for messages from rpi to gui.
                data_str = data_str + str(int(angle)) + " " + str(int(distance)) + "\n"

            except IndexError:
                # print("Lidar not detected!")
                exit

        cones = identify_cones(data_lst)  # TODO: Remove global variables.

        lidar_q.put(cones)


def find_centre_point(dot1: Dot, dot2: Dot) -> Dot:
    """Find centrum between two dots"""
    angle_diff = (dot2.angle - dot1.angle + 180) % 360 - 180
    ang = dot1.angle + angle_diff / 2
    dist = (dot1.distance + dot2.distance) / 2
    return Dot(ang, dist)


@dataclass
class Obj:
    """This class represents the two dots that are furthest away from
    eachother and amount of dots are inbetween"""

    dot1: Dot
    dot2: Dot
    amount: int


class ConeSize(enum.Enum):
    """Enum for cone sizes"""

    LARGE = "Large"
    SMALL = "Small"
    UNDEFINED = "Undefined"


@dataclass
class LidarCone:
    """Class for cones, they have a center point, diameter and size"""

    centrum: Dot
    diam: float
    size: ConeSize

    def to_tuple(self):
        coords = cmath.rect(self.centrum.angle, self.centrum.distance)
        return (coords.real, coords.imag, 0)


def identify_cones(data: list[Dot]) -> list[LidarCone]:
    """With the data from the lidar, determine what clusters of dots should
    be considered as cones."""
    objects = []
    dummy = Obj(Dot(0, 0), Dot(0, 1000000), 0)  # "dummy"-object with very big distance.
    objects.append(dummy)
    cones = []

    # Find all pairs of dots with a distance of less than OBJ_MIN_DISTANCE
    in_range = [
        (a, b)
        for (a, b) in zip(data, data[1:])
        if a.distance < MAX_VIEW_DISTANCE
        and b.distance < MAX_VIEW_DISTANCE
        and distance_between_dots(a, b) <= OBJ_MAX_DISTANCE
    ]

    # Group dots into clusters (Obj).
    amount_in_current = 2
    for p, q in in_range:
        if objects[-1].dot2.angle == p.angle:
            objects[-1].dot2 = q
            amount_in_current += 1
        else:
            objects.append(Obj(p, q, amount_in_current))
            amount_in_current = 2

    # Make cones of objects that are of correct size.
    for obj in objects:
        dist = distance_between_dots(obj.dot1, obj.dot2)
        cent = find_centre_point(obj.dot1, obj.dot2)
        cone_size = 0
        if CONE_DIAM_LOWER < dist < CONDE_DIAM_UPPER:
            if (
                CONE_DIAM_MIDDLE < dist
                and cent.distance < COUNT_ONLY_AMOUNT_OF_DOTS_DISTANCE
            ):
                cone_size = 1
            elif (
                dist <= CONE_DIAM_MIDDLE
                and cent.distance < COUNT_ONLY_AMOUNT_OF_DOTS_DISTANCE
            ):
                cone_size = -1
            else:  # COUNT_ONLY_AMOUNT_OF_DOTS_DISTANCE <= cent.distance
                cone_size = 0

            # Make a cone of the data.
            x_cone = int(cent.distance * math.cos(math.radians(-90 + cent.angle)))
            y_cone = -int(cent.distance * math.sin(math.radians(-90 + cent.angle)))
            new_cone = Cone((x_cone, y_cone), cone_size)

            cones.append(new_cone)
    return cones


async def start_lidar(port: str) -> asyncio.subprocess.Process:
    """
    Note:
    We used a modified version of "simple_grabber" which is a program created
    by Slamtec availible in the rplidar's SDK at: https://github.com/Slamtec/rplidar_sdk
    We modified it to fit our purposes.
    """
    return await asyncio.create_subprocess_exec(
        "../rplidar_sdk/output/Linux/Release/simple_grabber",
        "--channel",
        "--serial",
        port,
        "115200",
        stdout=asyncio.subprocess.PIPE,
    )
