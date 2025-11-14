from path_gate import Gate as Gate
from path_gate import GateType as GateType
from mapping import Cone as Cone
from mapping import ConeSize as ConeSize
import math as m


from pathfinder_config import (
    RULE_5_ILLEGAL_GATE_MAX,
    RULE_5_ILLEGAL_GATE_MIN,
    MAX_PATH_GATE_DISTANCE,
    MIN_GATE_CONE_GAP,
    CANDIDATE_ANGLE_MARGIN_RAD,
    MAX_NEXT_GATE_DISTANCE,
)


from pathf_linear_algebra import (
    vector_from_to,
    magnitude,
    normal,
    angle_between_vectors,
    orthogonal_projection,
    correct_direction,
)


class DuplicateConeException(Exception):
    def __init__(self, faulty_cone):
        message = f"\n{faulty_cone} exists in multiple gates."
        super().__init__(message)


class GateCountException(Exception):
    def __init__(self, gate_count):
        message = f"\nThe map has {gate_count} gates, the number of gates should be between 4 and 10."
        super().__init__(message)


class GateDistanceException(Exception):
    def __init__(self, gate_a, gate_b):
        message = f"\nThe distance between the following gates are between 200 and 220 cm which is illegal:\n{gate_a}\n{gate_b}"
        super().__init__(message)


class PathDistanceException(Exception):
    def __init__(self, gate_a, gate_b):
        message = f"\nThe distance between the following path gates is over 200 cm which is illegal since they are sequiental in a path:\n{gate_a}\n{gate_b}"
        super().__init__(message)


class ConeDistanceException(Exception):
    def __init__(self, cone_a, cone_b):
        message = f"\nThe following cones that belong to different gates are less than two car widths apart:\n{cone_a}\n{cone_b}"
        super().__init__(message)


class LightObstructionException(Exception):
    def __init__(self, this_gate, next_gate):
        message = f"\nLooking from the gate:\n{this_gate}\n...the following gate's gap between the cones is not visible:{next_gate}"
        super().__init__(message)


class CandidateAngleException(Exception):
    def __init__(self, this_gate, next_gate_cand1, next_gate_cand2):
        message = f"\nThe difference between the path vector angles of \n{next_gate_cand1}\n ...and {next_gate_cand2} is too small, seen from:\n{this_gate}"
        super().__init__(message)


class TurningCategoryException(Exception):
    def __init__(self, faulty_gate):
        message = f"\nThe direction of gate:\n{faulty_gate}\n...is set to {faulty_gate.gateType} but it should be set to {faulty_gate.gateType.opposite()}"
        super().__init__(message)


def has_duplicate_cones(gate_map):
    """See if any of the cones in the map occur in more than one gate."""

    all_cones = []

    for gate in gate_map.gates:
        all_cones.append(gate.coneA)
        all_cones.append(gate.coneB)

    seen = set()
    for cone in all_cones:
        if cone in seen:
            raise DuplicateConeException(cone)
        seen.add(cone)


def has_correct_gate_count(gate_map):
    """Check if the number of gates in the map is within the allowed range 4 to 10."""

    gate_count = len(gate_map.gates)

    if not 10 >= gate_count >= 4:
        raise GateCountException(gate_count)


def check_gate_distances(gate_map):
    for gate_a in gate_map.gates:
        for gate_b in gate_map.gates:
            distance_between_gates = gate_a.distance_to(gate_b)

            if (
                RULE_5_ILLEGAL_GATE_MIN
                <= distance_between_gates
                <= RULE_5_ILLEGAL_GATE_MAX
            ):
                raise GateDistanceException(gate_a, gate_b)


def check_path_distances(gate_map):
    this_gate = gate_map.rootGate

    while True:
        next_gate = this_gate.nextGate
        if not next_gate:  # Lazy hotfix
            return
        if this_gate.distance_to(next_gate) > MAX_PATH_GATE_DISTANCE:
            raise PathDistanceException(this_gate, next_gate)
        this_gate = next_gate


def check_cone_distances(gate_map):
    for gate in gate_map.gates:
        for cone in gate_map.conemap.cones:
            if cone.pos != gate.coneA.pos and cone.pos != gate.coneB.pos:
                if cone.distance_to(gate.coneA) <= MIN_GATE_CONE_GAP:
                    raise ConeDistanceException(cone, gate.coneA)
                if cone.distance_to(gate.coneB) <= MIN_GATE_CONE_GAP:
                    raise ConeDistanceException(cone, gate.coneB)


def light_passing_looking_from_at(current_gate: Gate, next_gate: Gate):
    for next_cone in next_gate.coneA, next_gate.coneB:
        vector_to_cone_center = vector_from_to(current_gate.center, next_cone.pos)

        distance_to_cone_center = magnitude(vector_to_cone_center)

        scalar_S = (next_cone.radius**2) / (distance_to_cone_center**2)

        scalar_T = (
            next_cone.radius * m.sqrt(distance_to_cone_center**2 - next_cone.radius**2)
        ) / (distance_to_cone_center**2)

        # Calculate the two lines that is tangentical to the cone and passes through th current position.
        tangent_vector_1 = scalar_S * vector_to_cone_center + scalar_T * normal(
            vector_to_cone_center
        )
        tangent_vector_2 = scalar_S * vector_to_cone_center - scalar_T * normal(
            vector_to_cone_center
        )

        for searching_cone in next_gate.coneA, next_gate.coneB:
            for tangent_vector in tangent_vector_1, tangent_vector_2:
                # This expression cretes a circle equation for the cone and a line equation for the tangent.
                scalar_A = tangent_vector[1] ** 2 + tangent_vector[0] ** 2
                scalar_B = -2 * (
                    tangent_vector[1] * searching_cone.pos[0]
                    + tangent_vector[0] * searching_cone.pos[1]
                )
                scalar_C = (
                    searching_cone.pos[0] ** 2
                    + searching_cone.pos[1] ** 2
                    - searching_cone.radius**2
                )

                discriminant = scalar_B**2 - 4 * scalar_A * scalar_C

                # If the discriminant is positive, it means we have a double root which means that the tangent
                # has passed through a cone so therefore the light is obstructed in that case.
                if discriminant > 0:
                    return False

            # TODO: This part may be unneccessary but I'm not 100% sure
            """
            tangent1_angle = m.atan2(tangent_vector_1[0], tangent_vector_1[1])
            tangent2_angle = m.atan2(tangent_vector_2[0], tangent_vector_2[1])

            tangent1_angle = normalize_angle(tangent1_angle)
            tangent2_angle = normalize_angle(tangent2_angle)

            if tangent1_angle > tangent2_angle:
                tangent1_angle, tangent2_angle = tangent2_angle, tangent1_angle
            
            if tangent2_angle - tangent1_angle > m.pi:
                tangent1_angle, tangent2_angle = tangent2_angle, tangent1_angle + 2 * m.pi
            
            angle_to_cone_center = m.atan2(searching_cone.pos[0], searching_cone.pos[1])
            angle_to_cone_center = normalize_angle(angle_to_cone_center)

            vector_to_scone_center = vector_from_to(current_gate.center, searching_cone.pos)

            distance_to_scone_center = magnitude(vector_to_scone_center)

            angular_radius_of_cone = m.asin(searching_cone.radius / distance_to_scone_center)

            angular_range_min = normalize_angle(angle_to_cone_center - angular_radius_of_cone)
            angular_range_max = normalize_angle(angle_to_cone_center + angular_radius_of_cone)

            if angular_range_min > angular_range_max:
                angular_range_min -= 2*m.pi
            
            cone_within_tangents = tangent1_angle <= angular_range_min and angular_range_max <= tangent2_angle
    
            if cone_within_tangents:
                return False
            """

    return True


"""
cone1 = Cone((25, 0), ConeSize.LARGE)
cone2 = Cone((-25, 0), ConeSize.LARGE)
cone3 = Cone((0, 100), ConeSize.SMALL)
cone4 = Cone((0, 150), ConeSize.SMALL)

cur_gate = Gate(cone1, cone2, GateType.STARTSTOP)
light_gate = Gate(cone3, cone4, GateType.STRAIGHT)

print(light_passing_looking_from_at(cur_gate, light_gate))
"""


def check_candidate_angles(gate_map):
    this_gate = gate_map.rootGate

    while True:
        next_gate = this_gate.nextGate

        check_gate_angles(this_gate, next_gate, gate_map.gates)

        if this_gate == gate_map.rootGate:
            break


def check_gate_angles(this_gate, next_gate, gate_list):
    best_angle = angle_between_vectors(this_gate.pathVector, next_gate.pathVector)

    for other_gate in gate_list:
        if (
            other_gate.center == this_gate.center
            or other_gate.center == next_gate.center
        ):
            continue

        next_path_vector = vector_from_to(this_gate.center, other_gate.center)
        projected_path_vector = orthogonal_projection(
            next_path_vector, this_gate.directionVector
        )
        distance_to_gate = magnitude(next_path_vector)
        path_vector_angle = angle_between_vectors(
            this_gate.pathVector, next_path_vector
        )

        if distance_to_gate < MAX_NEXT_GATE_DISTANCE and correct_direction(
            projected_path_vector, this_gate.directionVector
        ):
            if path_vector_angle < best_angle + CANDIDATE_ANGLE_MARGIN_RAD:
                raise CandidateAngleException(this_gate, next_gate, other_gate)


# TODO: idk
def verify_turning_gates(gate_map):
    return

    this_gate = gate_map.rootGate

    while True:
        next_gate = this_gate.nextGate

        if next_gate.gateType == GateType.RIGHT:
            pass

        if this_gate == gate_map.rootGate:
            break


def check_light(gate_map):
    this_gate = gate_map.rootGate

    while True:
        next_gate = this_gate.nextGate

        if not light_passing_looking_from_at(this_gate, next_gate):
            raise LightObstructionException(this_gate, next_gate)

        this_gate = next_gate
        if this_gate == gate_map.rootGate:
            break


def map_islegal(gate_map) -> bool:
    """Run tests to see if the detected map obeys the rules."""

    total_tests = 6
    tests_completed = 0

    print("\n\n ==== Running map verification tests: ====")

    test = "The map should have four(4) to ten(10) gates (Rule 1)"
    try:
        has_correct_gate_count(gate_map)
        print(f"[✓] {test}:\nSuccess!")
        tests_completed += 1
    except GateCountException as e:
        print(f"[X] {test}: {e}")

    test = "No pairs of cones may be places within a distance of between 200 cm and 220 cm from each other (Rule 4)"
    try:
        check_gate_distances(gate_map)
        print(f"[✓] {test}:\nSuccess!")
        tests_completed += 1
    except GateDistanceException as e:
        print(f"[X] {test}: {e}")

    test = "The distance between two sequiental gates may be at most 2 meters (Rule 5)"
    try:
        check_path_distances(gate_map)
        print(f"[✓] {test}:\nSuccess!")
        tests_completed += 1
    except PathDistanceException as e:
        print(f"[X] {test}: {e}")

    test = "The distance between two cones that belong to different gates may not be less than two car widths (Rule 6)"
    try:
        check_cone_distances(gate_map)
        print(f"[✓] {test}:\nSuccess!")
        tests_completed += 1
    except PathDistanceException as e:
        print(f"[X] {test}: {e}")

    """
    #TODO: This one does not work properly:
    test = "One should always be able to see through the the gap in the next gate of the path (Rule 9)"
    try:
        check_light(gate_map)
        print(f"[✓] {test}:\nSuccess!")
        tests_completed += 1
    except LightObstructionException as e:
        print(f"[X] {test}: {e}")
    """

    test = "Two gates which may be chosen as the candidate for next gate may not have a path vector angle difference of less than 10 degrees (Rule 11)"
    try:
        check_candidate_angles(gate_map)
        print(f"[✓] {test}:\nSuccess!")
        tests_completed += 1
    except CandidateAngleException as e:
        print(f"[X] {test}: {e}")

    # WIP:
    """
    test = "All gates which signify a sharp turn to the left should have a large cone on the left side and the ones that signify a turn to the right should have a large cone on the right side (Rule 14)"
    try:
        verify_turning_gates(gate_map)
        print(f"[✓] {test}:\nSuccess!")'
        tests_completed += 1
    except TurningCategoryException as e:
        print(f"[X] {test}: {e}")
    """

    test = "No cones may be part of more than one gate (Rule X)"
    try:
        has_duplicate_cones(gate_map)
        print(f"[✓] {test}:\nSuccess!")
        tests_completed += 1
    except DuplicateConeException as e:
        print(f"[X] {test}: {e}")

    print(f"\nThe map passed {tests_completed} out of {total_tests} tests!\n")

    return tests_completed == total_tests
