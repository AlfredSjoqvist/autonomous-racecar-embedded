from mapping import Cone, CarPos, ConesMap
from enum import Enum
import math as m
from path_inspector import map_islegal

# from numpy import array as np_vector

from pathf_linear_algebra import (
    vector_from_to,
    magnitude,
    angle_between_vectors,
    normal,
    normalize,
    basis_transform_2d,
    orthogonal_projection,
)

from pathfinder_config import (
    MIN_GATE_SIZE,
    MAX_GATE_SIZE,
    CONE_RADII,
    MAX_NEXT_GATE_DISTANCE,
    START_GATE_PATH_VECTOR_CLOCKWISE,
    ConeSize,
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
        car_pos_obj: CarPos = CarPos((0, 0), 0),
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
        self.directionVector = self.calculate_direction_vector(car_pos_obj)

    def __repr__(self):
        return f"{self.center}, A={self.coneA.pos}, B={self.coneB.pos}, type={self.gateType.name})"
        return f"Gate(center={self.center}, coneA={self.coneA}, coneB={self.coneB}, gateType={self.gateType})"

    def attach_gate_link(self, next_gate):
        """Setter for linked list append operation."""

        self.nextGate = next_gate

    def calculate_direction_vector(self, car_pos_obj: CarPos):
        """Calculate direction the gate is facing from the car's perspective."""

        # Create a vector from the car's current position to this gate.
        car_moment_vector = vector_from_to(car_pos_obj.pos, self.center)

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


class GateMap:
    def __init__(self, x_lower: int, x_upper: int, y_lower: int, y_upper: int):
        self.x_lower = x_lower
        self.x_upper = x_upper
        self.y_lower = y_lower
        self.y_upper = y_upper
        self.gates = []
        self.conemap = ConesMap([])

        # The start/stop gate is assigned here when a path is searched. The rest of the gates will be attached in a circular linked list.
        self.rootGate = None

    def __repr__(self):
        return f"All gates: {self.gates})"

    def add_gate(self, gate: Gate):
        """Setter for adding a gate to the map."""

        self.gates.append(gate)

    def add_cone(self, cone: Cone):
        """Setter for adding a cone to the map."""

        self.conemap.cones.append(cone)

    def find_root_gate(self):
        """Iterate through the gates in the map to find the starting point."""

        # Will assume that there is only one start/stop gate.
        for gate in self.gates:
            if gate.gateType == GateType.STARTSTOP:
                self.rootGate = gate

    def find_path(self):
        """Find the correct path through all of the gates, given that all gates exact position are known."""

        self.find_root_gate()
        attach_next_gate(
            self.rootGate, self, find_complete_path=True, root_gate=self.rootGate
        )

    def expose_undiscovered_gates(self):
        """Create a set of all gates in the map that was not found by the pathfinder."""

        found_gates_in_path = set()
        total_gates_on_map = set()

        gate_iter = self.rootGate

        # Iterate through the linked list path and add all the gates to a set.
        while gate_iter not in found_gates_in_path:
            found_gates_in_path.add(gate_iter.center)
            gate_iter = gate_iter.nextGate

        # Iterate through the unordered internal list of gates and add them to another set.
        for gate in self.gates:
            total_gates_on_map.add(gate.center)

        # Return the difference between the sets.
        gates_not_in_path = total_gates_on_map - found_gates_in_path

        return gates_not_in_path

    def verify_path(self):
        """Check if the path includes all gates."""

        undiscovered_gates = self.expose_undiscovered_gates()

        if undiscovered_gates:
            return False
        else:
            return True

    def display_path(self):
        """Display all of the gates of the path in the correct order."""

        path_list = []
        path_list.append(self.rootGate)

        this_gate = self.rootGate.nextGate

        while this_gate.center != self.rootGate.center:
            path_list.append(this_gate)
            this_gate = this_gate.nextGate

        path_list.append(self.rootGate)

        for row in path_list:
            print(row)

    def render(self):
        """Renders a text based representation of the map."""

        LARGE_CONE = "☐"
        SMALL_CONE = "o"
        UNKNOWN_CONE = "x"
        EMPTY_CHAR = "."

        MAP_SIZE = 41
        MAP_PADDING = 19

        map_matrix = []
        matrix_string = ""

        # Create and empty matrix.
        for row in range(0, MAP_SIZE):
            map_matrix.append([])
            for column in range(0, MAP_SIZE):
                map_matrix[row].append(EMPTY_CHAR)

        pos_max = 0

        # Set the map bounds based on the gate that is furthest away from the origin.
        for gate in self.gates:
            if abs(gate.coneA.pos[0]) > pos_max:
                pos_max = abs(gate.coneA.pos[0])
            if abs(gate.coneB.pos[0]) > pos_max:
                pos_max = abs(gate.coneB.pos[0])
            if abs(gate.coneA.pos[1]) > pos_max:
                pos_max = abs(gate.coneA.pos[1])
            if abs(gate.coneB.pos[1]) > pos_max:
                pos_max = abs(gate.coneB.pos[1])

        # Put all of the gates in the map into the matrix.
        for gate in self.gates:
            for cone in gate.coneA, gate.coneB:
                matrix_pos_x = (
                    int((cone.pos[0] / pos_max) * MAP_PADDING) + MAP_PADDING + 1
                )
                matrix_pos_y = (
                    int((cone.pos[1] / pos_max) * MAP_PADDING) + MAP_PADDING + 1
                )

                # Put different characters depending on the cone type.
                if cone.get_size() == ConeSize.SMALL:
                    map_matrix[matrix_pos_y][matrix_pos_x] = SMALL_CONE
                elif cone.get_size() == ConeSize.LARGE:
                    map_matrix[matrix_pos_y][matrix_pos_x] = LARGE_CONE
                elif cone.get_size() == ConeSize.UNDEFINED:
                    map_matrix[matrix_pos_y][matrix_pos_x] = UNKNOWN_CONE

        # Join the matrix into a string representation
        for row in list(reversed(map_matrix)):
            matrix_string += " ".join(row)
            matrix_string += "\n"

        print(matrix_string)


def calculate_cone_gap(cone_a: Cone, cone_b: Cone):
    """Calculate the gap between two cones from the distance between the center points and added padding on the sides based on cone size."""

    cone_gap = 0

    cone_a_x = cone_a.pos[0]
    cone_a_y = cone_a.pos[1]

    cone_b_x = cone_b.pos[0]
    cone_b_y = cone_b.pos[1]

    cone_x_diff = cone_a_x - cone_b_x
    cone_y_diff = cone_a_y - cone_b_y

    # Difference between center points.
    cone_center_diff = m.sqrt(cone_x_diff**2 + cone_y_diff**2)

    cone_gap += cone_center_diff

    cone_gap -= CONE_RADII[cone_a.get_size()]
    cone_gap -= CONE_RADII[cone_b.get_size()]

    return cone_gap


def find_cone_center(coneA: Cone, coneB: Cone) -> tuple[int, int]:
    """Calcuate the center of a gate by taking the average of the cone positions."""

    center_x = (coneA.pos[0] + coneB.pos[0]) / 2
    center_y = (coneA.pos[1] + coneB.pos[1]) / 2

    return (center_x, center_y)


def pair_cones_moment(
    cone_map: ConesMap, car_pos_obj: CarPos = CarPos((0, 0), 0)
) -> GateMap:
    """
    Pair all of the cones in the map into gates and cathegorize them.

    The cathegorization of left and right turn gates will be different depending on the location of the car,
    therefore the function takes in the current position and redoes the cathegorization from the perspective of
    each gate to be able to get the correct cathegorization for the entire path.
    """

    gates = GateMap(-2000, 2000, -2000, 2000)
    banned_cones = []

    # Compare each cone pair on the map.
    for cone_a in cone_map.cones:
        cone_a_x = cone_a.pos[0]
        cone_a_y = cone_a.pos[1]

        # Add the cone to the list of cones in the map.
        gates.add_cone(cone_a)

        # If a cone has already been added to a gate, we won't search it again
        if (cone_a.pos[0], cone_a.pos[1]) in banned_cones:
            continue

        for cone_b in cone_map.cones:
            if (cone_b.pos[0], cone_b.pos[1]) in banned_cones:
                continue

            cone_b_x = cone_b.pos[0]
            cone_b_y = cone_b.pos[1]

            cone_gap = calculate_cone_gap(cone_a, cone_b)

            # Check if the gap between the cones is within the allowed range (Rule 2)
            if MIN_GATE_SIZE <= cone_gap <= MAX_GATE_SIZE:
                clockwise = None

                # The gate type can be determined purely from the character of the two cones in these 3 cases:
                if (
                    cone_a.get_size() == ConeSize.SMALL
                    and cone_b.get_size() == ConeSize.SMALL
                ):
                    gate_type = GateType.STRAIGHT
                elif (
                    cone_a.get_size() == ConeSize.LARGE
                    and cone_b.get_size() == ConeSize.LARGE
                ):
                    gate_type = GateType.STARTSTOP
                    clockwise = START_GATE_PATH_VECTOR_CLOCKWISE
                elif (
                    cone_a.get_size() == ConeSize.UNDEFINED
                    or cone_b.get_size() == ConeSize.UNDEFINED
                ):
                    gate_type = GateType.UNKNOWN

                # It becomes a little bit more complicated when we have to detemine if it's a right or left turn when there is both a large and a small cone in the gate.
                # This block checks the direction of the turn from the position of the previous gate in the path:
                elif cone_a.get_size() != cone_b.get_size():
                    vector_to_cone_a = vector_from_to(car_pos_obj.pos, cone_a.pos)
                    vector_to_cone_b = vector_from_to(car_pos_obj.pos, cone_b.pos)
                    vector_to_gate_center = vector_from_to(
                        car_pos_obj.pos, find_cone_center(cone_a, cone_b)
                    )
                    normal_of_gate_center_vector = normal(
                        vector_to_gate_center, clockwise=True
                    )

                    # Transform vectors to a new basis where the cone A- and cone B vectors are on opposite sides of the x-axis.
                    # With the new basis we can just check the sign of the y-coordinate to detemine which cone is to the right and which is to the left.
                    transformed_vector_to_cone_a = basis_transform_2d(
                        vector_to_cone_a,
                        vector_to_gate_center,
                        normal_of_gate_center_vector,
                    )
                    transformed_vector_to_cone_b = basis_transform_2d(
                        vector_to_cone_b,
                        vector_to_gate_center,
                        normal_of_gate_center_vector,
                    )

                    # Cone A is to the right and Cone B is to the left.
                    if (
                        transformed_vector_to_cone_a[1] >= 0
                        and transformed_vector_to_cone_b[1] <= 0
                    ):
                        if (
                            cone_a.get_size() == ConeSize.LARGE
                            and cone_b.get_size() == ConeSize.SMALL
                        ):
                            gate_type = GateType.RIGHT
                        else:
                            gate_type = GateType.LEFT

                    # Cone B is to the right and Cone A is to the left.
                    if (
                        transformed_vector_to_cone_b[1] >= 0
                        and transformed_vector_to_cone_a[1] <= 0
                    ):
                        if (
                            cone_a.get_size() == ConeSize.LARGE
                            and cone_b.get_size() == ConeSize.SMALL
                        ):
                            gate_type = GateType.LEFT
                        else:
                            gate_type = GateType.RIGHT

                new_gate = Gate(cone_a, cone_b, gate_type, car_pos_obj, clockwise)

                gates.add_gate(new_gate)

                banned_cones.append((cone_a_x, cone_a_y))
                banned_cones.append((cone_b_x, cone_b_y))

                break
    return gates


def attach_next_gate(
    this_gate: Gate,
    global_gate_map: GateMap,
    find_complete_path: bool = False,
    start_gate_passed: bool = False,
    root_gate: Gate = None,
):
    """Attaches the next gate in the path according to the ruleset."""

    # Makes a new gate map with the current gate as center point

    moment_gate_map = pair_cones_moment(
        global_gate_map.conemap, CarPos((this_gate.center), 0)
    )

    if this_gate.gateType == GateType.STARTSTOP:
        # The start gate uses a special path vector to find the next gate according to Rule 8.
        this_gate.pathVector = normal(
            this_gate.tangentVector, this_gate.clockwise
        )  # May cause issues later with the start direction vector (clockwise??)
        this_gate.directionVector = this_gate.pathVector

        # Recursion stop condition (end of circular linked list).
        if start_gate_passed:
            this_gate = root_gate
            return
        start_gate_passed = True

    # We want to find the next gate which has the minimal angle between the two vectors (Rule 7):
    # Current path vector: The vector between the center of the previous gate and the center of this gate
    # Next path vector: The vector between the center of this gate and the center of the next gate
    best_angle = m.inf
    best_path_vector = None

    # Search all of the other possible gates in the map.
    for other_gate in moment_gate_map.gates:
        # Doesn't have to search itself.
        if this_gate.center == other_gate.center:
            continue

        next_path_vector = vector_from_to(this_gate.center, other_gate.center)

        # The next center of the next gate can't be further away from the current gate center than a certain distance (Rule 5).
        distance_to_gate = magnitude(next_path_vector)

        if distance_to_gate < MAX_NEXT_GATE_DISTANCE:
            # Check the angle between the current path vector and the next path vector.
            other_angle = angle_between_vectors(this_gate.pathVector, next_path_vector)

            # Save it if it is the smallest angle yet found.
            if other_angle < best_angle:
                best_angle = other_angle
                this_gate.attach_gate_link(other_gate)
                best_path_vector = next_path_vector

    # If the next gate is not found (should not be possible), add a dummy gate.
    if not this_gate.nextGate:
        this_gate.nextGate = Gate(None, None, GateType.ERROR)

    this_gate.nextGate.pathVector = best_path_vector

    # The function can be turned on to search recursively for the complete path.
    if find_complete_path:
        attach_next_gate(
            this_gate.nextGate, global_gate_map, True, start_gate_passed, root_gate
        )


test1 = False
if test1:
    cone1 = Cone((-150, 0), ConeSize.SMALL)
    cone2 = Cone((-150, 50), ConeSize.LARGE)
    cone3 = Cone((-150, 100), ConeSize.SMALL)
    cone4 = Cone((0, 0), ConeSize.UNDEFINED)
    cone5 = Cone((50, 0), ConeSize.UNDEFINED)

    cone6 = Cone((150, 0), ConeSize.SMALL)
    cone7 = Cone((150, 50), ConeSize.LARGE)

    cone_array = [cone1, cone2, cone4, cone5, cone6, cone7]

    cone_array.append(Cone((-25, 150), ConeSize.SMALL))
    cone_array.append(Cone((25, 150), ConeSize.LARGE))
    cone_array.append(Cone((-25, -100), ConeSize.SMALL))
    cone_array.append(Cone((25, -100), ConeSize.LARGE))

    global_gate_map = pair_cones_moment(cone_array)

    global_gate_map.render()
    print(global_gate_map)

    map_islegal(global_gate_map)

cone_array = []

test2 = False
if test2:
    cone_array.append(Cone((100, 150), ConeSize.LARGE))
    cone_array.append(Cone((100, 100), ConeSize.LARGE))

    cone_array.append(Cone((0, 150), ConeSize.SMALL))
    cone_array.append(Cone((0, 100), ConeSize.LARGE))

    cone_array.append(Cone((-180, 50), ConeSize.SMALL))
    cone_array.append(Cone((-150, 0), ConeSize.LARGE))

    cone_array.append(Cone((-150, -100), ConeSize.LARGE))
    cone_array.append(Cone((-180, -150), ConeSize.SMALL))

    cone_array.append(Cone((0, -200), ConeSize.SMALL))
    cone_array.append(Cone((0, -250), ConeSize.SMALL))

    cone_array.append(Cone((100, -200), ConeSize.LARGE))
    cone_array.append(Cone((100, -250), ConeSize.SMALL))

    cone_array.append(Cone((200, -100), ConeSize.SMALL))
    cone_array.append(Cone((250, -100), ConeSize.SMALL))

    cone_array.append(Cone((200, 0), ConeSize.LARGE))
    cone_array.append(Cone((250, 0), ConeSize.SMALL))


test3 = True
if test3:
    cone_array.append(Cone((100, 145), ConeSize.LARGE))
    cone_array.append(Cone((100, 75), ConeSize.LARGE))

    cone_array.append(Cone((-40, 145), ConeSize.SMALL))
    cone_array.append(Cone((-40, 75), ConeSize.LARGE))

    cone_array.append(Cone((-215, 75), ConeSize.SMALL))
    cone_array.append(Cone((-150, 75), ConeSize.SMALL))

    cone_array.append(Cone((-245, -40), ConeSize.SMALL))
    cone_array.append(Cone((-170, -50), ConeSize.LARGE))

    cone_array.append(Cone((-140, -145), ConeSize.SMALL))
    cone_array.append(Cone((-160, -200), ConeSize.SMALL))

    cone_array.append(Cone((-50, -130), ConeSize.LARGE))
    cone_array.append(Cone((-50, -195), ConeSize.SMALL))

    cone_array.append(Cone((40, -100), ConeSize.LARGE))
    cone_array.append(Cone((90, -140), ConeSize.SMALL))

    cone_array.append(Cone((120, -60), ConeSize.SMALL))
    cone_array.append(Cone((180, -60), ConeSize.SMALL))

    cone_array.append(Cone((180, 50), ConeSize.LARGE))
    cone_array.append(Cone((250, 50), ConeSize.SMALL))

    START_GATE_PATH_VECTOR_CLOCKWISE = True

"""
cone_map = ConesMap()
cone_map.cones = cone_array

global_gate_map = pair_cones_moment(cone_map)

global_gate_map.render()

print(global_gate_map.gates)

global_gate_map.find_path()
# print(f"Path includes all gates: {global_gate_map.verify_path()}")
global_gate_map.display_path()
print(map_islegal(global_gate_map))
"""
