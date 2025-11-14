# This file contains the json-ification functions for sending to GUI.

import json


def cones(cones) -> str:
    return json.dumps(["cones", {"cones": cones}], sort_keys=False)


def sensor(velocity: int, angle: int) -> str:
    return json.dumps(["sensor_data", {"velocity": velocity, "angle": angle}])


def car(x: int, y: int, orientation: int) -> str:
    return json.dumps(["car", {"x": x, "y": y, "orientation": orientation}])
