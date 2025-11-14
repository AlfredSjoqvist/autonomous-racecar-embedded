from mapping import Cone
import math as m
from enum import Enum

from pathf_linear_algebra import (
    vector_from_to,
    normal,
    normalize,
    orthogonal_projection,
)


class GateType(Enum):
    STARTSTOP = "StartStop"
    STRAIGHT = "Straight"
    LEFT = "Left"
    RIGHT = "Right"
    UNKNOWN = "Unknown"
    ERROR = "Error"

    def opposite(self):
        opposites = {GateType.LEFT: GateType.RIGHT, GateType.RIGHT: GateType.LEFT}
        return opposites[self]


class Gate:
    def __init__(
        self,
        coneA: Cone,
        coneB: Cone,
        gate_type: GateType,
        car_pos: tuple[int, int] = (0, 0),
        clockwise: bool = None,
    ):
        self.coneA = coneA
        self.coneB = coneB
        self.center = self.find_gate_center(coneA, coneB)
        self.gateType = gate_type

        # This attribute is only set for the start gate to set the correct direction vector
        self.clockwise = clockwise

        # Used to calculate the next gate in the path according to Rule 7.
        # The start/stop gate also has to have a pre-defined start direction according to Rule 2.
        self.pathVector = None

        # Linked list attachment.
        self.nextGate = None

        # Gate tangent: Vector pointing from cone A to cone B (perpendicular to the driving direction).
        self.tangentVector = vector_from_to(coneA.pos, coneB.pos)

        # Set direction vector for later usage in pathfinding.
        self.directionVector = self.calculate_direction_vector(car_pos)

    def __repr__(self):
        return f"{self.center}, A={self.coneA.pos}, B={self.coneB.pos}, type={self.gateType.name})"
        return f"Gate(center={self.center}, coneA={self.coneA}, coneB={self.coneB}, gateType={self.gateType})"

    def attach_gate_link(self, next_gate):
        """Setter for linked list append operation."""

        self.nextGate = next_gate

    def calculate_direction_vector(self, car_pos):
        """Calculate direction the gate is facing from the car's perspective."""

        # Create a vector from the car's current position to this gate.
        car_moment_vector = vector_from_to(car_pos, self.center)

        # Project the created vector upon the normal vector of the gate.
        projected_direction = orthogonal_projection(
            car_moment_vector, normal(self.tangentVector)
        )

        # Set the projected vector to length 1.
        direction_vector = normalize(projected_direction)

        return direction_vector

    def find_gate_center(self, coneA: Cone, coneB: Cone) -> tuple[int, int]:
        """Calcuate the center of a gate by taking the average of the cone positions."""

        center_x = (coneA.pos[0] + coneB.pos[0]) / 2
        center_y = (coneA.pos[1] + coneB.pos[1]) / 2

        return (center_x, center_y)

    def distance_to(self, another_gate) -> float:
        x_diff = abs(self.center[0] - another_gate.center[0])
        y_diff = abs(self.center[1] - another_gate.center[1])

        return m.sqrt(x_diff**2 + y_diff**2)
