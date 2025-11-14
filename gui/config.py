"""This file contains parameters and settings for usage of GUI"""

VARIABLES = {
    "ELAPSED_TIME": 0,  # Körtid startvärde
    "UPDATE_FREQUENCY": 10,  # milliseconds
    "MAP_UPDATE_FREQ": 0.2,  # seconds
    "MAP_DIVISION_FACTOR": 15,
    "GAS_STRENGTH": 180,
    "MIDDLE_STEER": 115,
    "URI": "ws://10.42.0.1:12306",
    "AUTOSPEED": 160,
    "TURN_COEFF": 150,
}


def getVariables() -> list[any]:
    return VARIABLES
