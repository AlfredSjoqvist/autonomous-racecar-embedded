"""
Cones are added to the cone map based on the distance and angle from
the lidar to the cone and the absolute position of the car compared to
its starting position
"""

import math
import logging
from pathfinder_config import ConeSize

from car_settings import (
    CONE_DISTANCE_TOLERANCE,
    MAX_VIABLE_MEASUREMENT,
)
from pathfinder_config import CONE_RADII

logger = logging.getLogger(__name__)


class CarPos:
    def __init__(self, pos: tuple[int, int], deg_rotation: float):
        self.pos = pos
        self.deg_rotation = deg_rotation % 360  # Begränsad till 0-359 grader

    def __repr__(self):
        return f"CarPos(pos={self.pos}, deg_rotation={self.deg_rotation})"


class Cone:
    def __init__(self, pos: tuple[int, int], size):
        match size:
            case ConeSize.LARGE:
                self.size = 1
            case ConeSize.SMALL:
                self.size = -1
            case ConeSize.UNDEFINED:
                self.size = 0
            case x if isinstance(x, int):
                self.size = size
            case x:
                self.error(f"Wrong value for size: {size}")
                self.size = 0
        self.pos = pos
        self.radius = CONE_RADII[self.get_size()]

    def get_size(self):
        if self.size > 0:
            return ConeSize.LARGE
        elif self.size < 0:
            return ConeSize.SMALL
        else:
            return ConeSize.UNDEFINED

    def get_pos(self):
        return self.pos

    def __repr__(self):
        return f"Cone(pos={self.pos}, size={self.get_size()})"

    def distance_to(self, another_cone):
        x_diff = abs(self.pos[0] - another_cone.pos[0])
        y_diff = abs(self.pos[1] - another_cone.pos[1])

        return math.sqrt(x_diff**2 + y_diff**2)

    def distance_to_car(self, car_pos):
        x_diff = abs(self.pos[0] - car_pos.pos[0])
        y_diff = abs(self.pos[1] - car_pos.pos[1])
        return math.sqrt(x_diff**2 + y_diff**2)


class ConesMap:
    def __init__(self, cones: list[Cone]):
        self.cones = cones

    def add_cones_relative_to_car(self, car_pos: CarPos, cones: list[Cone]):
        """Lägg till en kon baserat på bilens position, avstånd och vinkel."""

        for cone in [
            cone
            for cone in cones
            if cone.distance_to_car(car_pos) < MAX_VIABLE_MEASUREMENT
        ]:
            # Beräkna den absoluta vinkeln
            absolute_angle = math.radians(
                car_pos.deg_rotation
                + math.degrees(math.atan2(cone.pos[1], cone.pos[0]))
            )  # Omvandla till radianer

            distance = cone.distance_to_car(car_pos)

            # Beräkna konens absoluta position
            x_cone = car_pos.pos[0] + (distance * math.cos(absolute_angle))
            y_cone = car_pos.pos[1] + (distance * math.sin(absolute_angle))

            # Skapa en Cone med den beräknade positionen
            cone_pos = (x_cone, y_cone)

            # Iterate through all existing cones and check if they already are in the cone map.
            # Check if the x and y values are within the tolerance range
            match [
                c
                for c in self.cones
                if abs(c.pos[0] - x_cone) <= CONE_DISTANCE_TOLERANCE
                and abs(c.pos[1] - y_cone) <= CONE_DISTANCE_TOLERANCE
            ]:
                case [existing_cone, *_]:
                    # We want to update the position of the cone to the average measurement
                    new_x = (existing_cone.pos[0] + cone_pos[0]) / 2
                    new_y = (existing_cone.pos[1] + cone_pos[1]) / 2
                    existing_cone.pos = new_x, new_y
                    logger.debug(f"existing_cone.pos: {existing_cone.pos}")
                    # Update cone_size cone_size > 0 => Large cone
                    # cone_size = 0 => Undefined cone size
                    # cone_size < 0 => small cone
                    if cone.size > 0:
                        existing_cone.size += 1
                    elif cone.size < 0:
                        existing_cone.size -= 1
                case _:
                    self.cones.append(Cone(cone_pos, cone.size))

            logger.debug(
                f"absolute angle: {absolute_angle}, cone_pos: {cone_pos}, size: {cone.size}"
            )

    def __repr__(self):
        return f"ConesMap(cones={self.cones})"
