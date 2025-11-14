import json
import logging

logger = logging.getLogger(__name__)

get_sensors = json.dumps(["get_sensors", {}])
get_cones = json.dumps(["get_cones", {}])
get_dots = json.dumps(["get_dots", {}])
get_data = json.dumps(["get_data", {}])


def throttle(velocity: int, rev: bool) -> str:
    return json.dumps(
        ["throttle", {"velocity": velocity, "reverse": rev}], sort_keys=True
    )


def steer(angle: int) -> str:
    return json.dumps(["steer", {"angle": angle}], sort_keys=True)


def brake(brake) -> str:
    return json.dumps(["brake", {"brake": brake}])


def auto(auto: bool, speed: int, turn: int) -> str:
    return json.dumps(["auto", {"auto": auto, "speed": speed, "turn": turn}])


def ping() -> str:
    return json.dumps(["ping", {}])


def exit() -> str:
    return json.dumps(["exit", {}])


async def request_get_sensors(websocket):
    await websocket.send(get_sensors)
    match json.loads(await websocket.recv()):
        case ["get_sensors", x]:
            return x
        case x:
            return None


async def request_get_cones(websocket):
    await websocket.send(get_cones)
    msg = json.loads(await websocket.recv())
    match msg:
        case ["get_cones", {"cones": cone_lst, "next_center": center}]:
            return cone_lst, center
        case _:
            logger.error(f"Incorrect response for cones request {msg}")
            return []


async def request_get_dots(websocket):
    await websocket.send(get_dots)
    match json.loads(await websocket.recv()):
        case ["get_dots", {"dots": dot_lst}]:
            return [(int(p["a"]), int(p["d"])) for p in dot_lst]
        case x:
            print("Error: ", x)
            return None


async def request_get_data(websocket):
    await websocket.send(get_data)
    match json.loads(await websocket.recv()):
        case [
            "get_data",
            {
                "distance": dist,
                "angle_to_gate": gate_angle,
                "throttle": thrott,
                "turn": turn,
            },
        ]:
            return dist, gate_angle, thrott, turn
        case x:
            logger.error(f"Incorrect response for data request {x}")
            return None
