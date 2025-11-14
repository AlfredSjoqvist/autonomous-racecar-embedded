import math
import queue
from mapping import Cone, CarPos


def update_position(
    old_car_pos: CarPos, new_car_angle: float, old_cone: Cone, new_cones: list
):
    """
    Using a globla reference cone and car's angle and list for relative
    cones which the lidar sees right now, update the cars position

    new_cones is a list for mapping.Cone:s that are relative to the car. (from lidar)

    old_cone is a global mapping.Cone that should be taken from the Cones map.
    Preferebly, the old cone is close to the car.
    """

    new_local_cone = None
    old_local_cone = global_to_relative(old_car_pos, old_car_pos.deg_rotation, old_cone)

    MAX_DISTANCE_DIFF = 200  # mm

    for cone in new_cones:
        if cone.distance_to(old_local_cone) < MAX_DISTANCE_DIFF:
            new_local_cone = cone
            break

    if new_local_cone is not None:
        delta_x = new_local_cone.pos[0] - old_local_cone.pos[0]
        delta_y = new_local_cone.pos[1] - old_local_cone.pos[1]

        radian_angle = math.radians(new_car_angle)

        new_global_x = old_car_pos.pos[0] + (
            delta_x * math.cos(radian_angle) - delta_y * math.sin(radian_angle)
        )
        new_global_y = old_car_pos.pos[1] + (
            delta_x * math.sin(radian_angle) + delta_y * math.cos(radian_angle)
        )

        return CarPos((new_global_x, new_global_y), new_car_angle)

    return old_car_pos  # If it failed, dont update position.


def relative_to_global(car_pos: CarPos, car_angle, relative_cone: Cone):
    """Convert a relative cone to global. Inverse of global_to_relative()"""
    x_car = car_pos.pos[0]
    y_car = car_pos.pos[1]
    x_cone = relative_cone.pos[0]
    y_cone = relative_cone.pos[1]
    radian_angle = math.radians(car_angle)

    x_cone_global = x_car + (
        x_cone * math.cos(radian_angle) - y_cone * math.sin(radian_angle)
    )
    y_cone_global = y_car + (
        x_cone * math.sin(radian_angle) + y_cone * math.cos(radian_angle)
    )
    return Cone((x_cone_global, y_cone_global), relative_cone.size)


def global_to_relative(car_pos: CarPos, car_angle, global_cone: Cone):
    """Convert a global cone to relative to car. Inverse of relative_to_global()"""
    x_car = car_pos.pos[0]
    y_car = car_pos.pos[1]
    x_cone_global = global_cone.pos[0]
    y_cone_global = global_cone.pos[1]

    radian_angle = math.radians(car_angle)

    x_cone = (x_cone_global - x_car) * math.cos(radian_angle) + (
        y_cone_global - y_car
    ) * math.sin(radian_angle)
    y_cone = -(x_cone_global - x_car) * math.sin(radian_angle) + (
        y_cone_global - y_car
    ) * math.cos(radian_angle)

    return Cone((x_cone, y_cone), global_cone.size)


# Assume that queue has value
def update_position_and_orientation(
    sensor_q: queue, car_position
) -> tuple[tuple[int, int], float]:
    # 3 most recent readings from sensor_q
    velocity, angular_rate, delta_time = sensor_q.get(-1)
    # Last orientation
    theta = car_position.deg_rotation
    theta_new = theta + angular_rate * delta_time
    # print("print orientation: ",theta,"print new orientation: ",theta_new, "angular_rate: ", angular_rate)
    # Last postion
    x, y = car_position.pos

    # Update position
    x_new = x + velocity * math.cos(theta_new) * delta_time
    y_new = y + velocity * math.sin(theta_new) * delta_time
    car_position.pos = (x_new, y_new)
    car_position.orientation = theta_new
    print(velocity, angular_rate)

    return car_position.pos, car_position.orientation
