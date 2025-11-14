#!/usr/bin/env python3
"""Kör denna fil för att starta GUI:t.
Se README-fil för en kort förklaring av de olika filerna & metoderna som används för att skapa GUI:t"""

import asyncio
from websockets.asyncio.client import connect

from gui_setup import createRoot, addFrames
from config import getVariables
from components import (
    createAutonomy,
    createConsole,
    createControls,
    createVelocityGyro,
    createStatus,
)
from map_display import createMap
from listener import listen_and_update_gui
from tkinter import DoubleVar
import logging

RUNNING = True
logger = logging.getLogger(__name__)


async def main():
    """Skapar nätverksramen med knappar för att skicka IP och portar."""

    logging.basicConfig(level=logging.INFO)

    variables = getVariables()
    uri = variables["URI"]

    async with connect(uri) as websocket:
        await build_gui(websocket)


async def build_gui(websocket) -> None:
    """Huvudfunktionen som sätter ihop GUI:t och startar programmet."""

    global RUNNING

    # skapa root och frames
    root = createRoot()
    frames = addFrames(root)  # Lägger till ramarna
    console_output = createConsole(frames["Konsol"])  # Skapa konsolram

    elapsed_time = DoubleVar(value=0.0)  # Initial körtid
    throttle = DoubleVar(value=0.0)
    map_points = []
    velocity = DoubleVar(value=0.0)  # Initial hastighet
    gyro_angle = DoubleVar(value=0.0)  # Initial vinkel bilens nos pekar
    distance = DoubleVar(value=0.0)
    turn = DoubleVar(value=0.0)
    gate_ang = DoubleVar(value=0.0)
    next_center = [0, 0]

    car_data = {
        "elapsed_time": elapsed_time,
        "map_points": map_points,
        "velocity": velocity,
        "gyro_angle": gyro_angle,
        "throttle": throttle,
        "distance": distance,
        "angle_to_gate": gate_ang,
        "turn": turn,
        "next_center": next_center,
    }

    # skapa resterande gui-komponenter
    await createAutonomy(
        root, frames["Autonomi"], console_output, websocket, car_data
    )  # Skapa autonomikontroller
    createStatus(
        frames["Status"],
        car_data,
    )  # Skapa statusinformation
    await createControls(
        root,
        frames["Kontroller"],
        console_output,
        websocket,
        RUNNING,
    )  # Skapa kontroller
    createVelocityGyro(
        frames["Hastighet & Gyro"], car_data
    )  # Skapa gas- och styrkomponenter

    async def start_mainloop():
        while RUNNING:
            root.update_idletasks()
            root.update()
            await asyncio.sleep(0.01)

    await asyncio.gather(
        start_mainloop(),
        listen_and_update_gui(websocket, console_output, car_data, RUNNING),
        createMap(frames["Karta"], map_points, car_data, RUNNING),
    )  # Starta lyssnare)


if __name__ == "__main__":
    asyncio.run(main())  # Kör programmet
