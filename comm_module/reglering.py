import Kommunikationsmodul.pathfinder as p
import mapping
import math as m
import time


TOLERANCE = 10  # Car position / Gate center

# Reglering-parametrar
KP = 1  # Proportionell term
KD = 0.5  # Deriverande term

previous_angle_error = 0
previous_time = None


def adjustSteering(car_pos: mapping.CarPos, target_gate: p.Gate) -> None:
    global previous_angle_error, previous_time

    current_x, current_y = car_pos.pos
    current_orientation = car_pos.deg_rotation  # ( i grader)

    target_x, target_y = target_gate.center
    direction_to_target = (target_x - current_x, target_y - current_y)

    # Beräkna önskad vinkel
    desired_angle = m.degrees(
        m.atan2(direction_to_target[1], direction_to_target[0])
    )  # atan beräknar vinkel, degrees omvandlar rad->grader
    if desired_angle < 0:
        desired_angle += 360  # Undvik negativ vinkel

    # Vinkelfel
    angle_error = desired_angle - current_orientation
    if angle_error > 180:
        angle_error -= 360
    elif (
        angle_error < -180
    ):  # Normalisera fel (t.ex blir -270 grader fel -> +90 grader fel)
        angle_error += 360

    current_time = time.time()
    if previous_time is None:  # Händer bara första gången
        previous_time = current_time

    delta_time = (
        current_time - previous_time if current_time != previous_time else 1e-6
    )  # Kan annars dela med 0 i D_term beräkning

    P_term = (
        KP * angle_error
    )  # Proportionerlig term. Större vinkelfel -> större styr-justering
    D_term = (KD / delta_time) * (
        angle_error - previous_angle_error
    )  # Deriverande term. Justering baseras på förändring av fel

    steering_adjustment = P_term + D_term

    # Uppdatera globala variabler
    previous_angle_error = angle_error
    previous_time = current_time

    # TODO: Implementera manipulering av bilens styrvinkel här!
    print(f"Steering adjustment needed: {steering_adjustment} degrees")


def reachedGate(car_pos: mapping.CarPos, target_gate: p.Gate) -> bool:
    return car_pos.pos == target_gate.center


def main(cones_map: mapping.ConesMap) -> None:
    gates = cones_map.gates
    initial_gate = gates[
        0
    ]  # TODO: Detta var bara för att ha något tillfälligt, men kanske?

    visited_gates = set()  # Håll reda på passerade gates
    current_gate = initial_gate

    car_pos = mapping.getCarPos()

    while current_gate is not None:
        visited_gates.add(current_gate)

        # Hitta nästa gate kontinuerligt, iterera när target-gate nåtts
        current_gate = p.findNextGate(gates, current_gate, visited_gates)

        while not reachedGate(car_pos, current_gate):
            car_pos = mapping.getCarPos()
            adjustSteering(car_pos, current_gate)
            # TODO: Justera styr-vinkel (antingen i adjustSteering() eller här utanför)
