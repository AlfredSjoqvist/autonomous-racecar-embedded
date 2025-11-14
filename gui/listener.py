import tkinter as tk
from config import getVariables
from typing import List
import message
import logging
import asyncio

logger = logging.getLogger(__name__)

VARIABLES = getVariables()


async def listen_and_update_gui(
    websocket, console_output: tk.Text, vars_to_modify: List[tk.Variable], RUNNING
):
    """Lyssna efter data från socket och uppdatera GUI med mottagen data."""
    while RUNNING:
        match await message.request_get_sensors(websocket):
            case {
                "velocity": vel,
                "angular_rate": _ar,
                "delta_time": _dlt,
                "angle": angle,
            }:
                vel_var = vars_to_modify["velocity"]
                vel_var.set(vel)
                angle_var = vars_to_modify["gyro_angle"]
                angle_var.set(angle)
            case x:
                logger.error(f"Incorrect response for sensor request: {x}")

        dist, gate_angle, thrott, turn = await message.request_get_data(websocket)
        dist_var = vars_to_modify["distance"]
        dist_var.set(dist)
        gate_angle_var = vars_to_modify["angle_to_gate"]
        gate_angle_var.set(gate_angle)
        thrott_var = vars_to_modify["throttle"]
        thrott_var.set(thrott)
        turn_var = vars_to_modify["turn"]
        turn_var.set(turn)

        cones, center = await message.request_get_cones(websocket)
        vars_to_modify["map_points"] += cones
        vars_to_modify["next_center"][0], vars_to_modify["next_center"][1] = (
            center[0],
            center[1],
        )

        console_output.after(
            0, update_console_with_data, console_output, cones
        )  # Anropa en funktion på huvudtråden för att uppdatera GUI

        await asyncio.sleep(0.1)


def update_console_with_data(console_output: tk.Text, message: str) -> None:
    """Uppdatera konsolen i GUI:t med mottagen data."""
    # console_output.insert("end", f"Received: {message}\n")
    console_output.see("end")
