#!/usr/bin/env python

import asyncio
import json
import message
import tkinter as tk
from websockets.asyncio.client import connect
import math


POINT_DIAMETER = 5
POINT_COLOR = "blue"
CONE_COLOR = "red"


async def get_sensors(websocket):
    await websocket.send(message.get_sensors)
    match json.loads(await websocket.recv()):
        case ["get_sensors", x]:
            return x
        case x:
            return None


async def get_cones(websocket):
    await websocket.send(message.get_cones)
    match json.loads(await websocket.recv()):
        case ["get_cones", {"cones": cone_lst}]:
            return [(int(p["a"]), int(p["d"])) for p in cone_lst]
        case _:
            return None


async def get_dots(websocket):
    await websocket.send(message.get_dots)
    match json.loads(await websocket.recv()):
        case ["get_dots", {"dots": dot_lst}]:
            return [(int(p["a"]), int(p["d"])) for p in dot_lst]
        case x:
            print("Error: ", x)
            return None


async def drive(angle, speed, distance, websocket):
    await websocket.send(message.steer(angle))
    await websocket.send(message.throttle(abs(speed), speed < 0))
    await asyncio.sleep(distance / (0.0329 * abs(speed) - 4.8))
    await websocket.send(message.throttle(1, False))
    await websocket.send(message.steer(angle))
    await websocket.send(message.brake(True))
    await asyncio.sleep(0.1)
    await websocket.send(message.brake(False))


async def sender(websocket):
    await websocket.send(message.steer(115))
    await websocket.send(message.throttle(160, False))
    for i in range(5):
        await asyncio.sleep(1)
        print("\n")
        for i in await get_cones(websocket):
            print(i)
    await websocket.send(message.throttle(1, False))
    # await drive(115, 160, 2, websocket)
    await websocket.send(message.exit())
    print("Sent all.")


async def main():
    uri = "ws://10.42.0.1:12307"
    async with connect(uri) as websocket:
        await sender(websocket)


async def update_points(canvas, point_ids):
    # Delete the previous points if they exist
    canvas.delete("all")
    point_ids = []

    # Draw new points on the canvas
    for argument, magnitude in global_dots:
        x = math.cos(argument * 2 * math.pi / 360) * magnitude
        y = math.sin(argument * 2 * math.pi / 360) * magnitude

        x += 4000
        y += 4000

        point_id = canvas.create_oval(
            x / 10,
            y / 10,
            x / 10 + POINT_DIAMETER,
            y / 10 + POINT_DIAMETER,
            fill=POINT_COLOR,
            outline=POINT_COLOR,
        )
        point_ids.append(point_id)
    for argument, magnitude in global_cones:
        x = math.cos(argument * 2 * math.pi / 360) * magnitude
        y = math.sin(argument * 2 * math.pi / 360) * magnitude

        x += 4000
        y += 4000

        point_id = canvas.create_oval(
            x / 10,
            y / 10,
            x / 10 + 2 * POINT_DIAMETER,
            y / 10 + 2 * POINT_DIAMETER,
            fill=CONE_COLOR,
            outline=CONE_COLOR,
        )
        point_ids.append(point_id)


async def tk_main():
    uri = "ws://10.42.0.1:12307"
    async with connect(uri) as websocket:
        root = tk.Tk()
        root.title("Random Points Animation")

        # Set the dimensions of the canvas
        canvas_width = canvas_height = 800

        # Number of points to display

        # Create the canvas widget
        canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
        canvas.pack()

        # Initialize the list of point identifiers
        point_ids = []
        while True:
            global global_dots
            global global_cones
            global_dots = await get_dots(websocket)
            global_cones = await get_cones(websocket)
            await update_points(canvas, point_ids)
            root.update()
        await websocket.send(message.exit())


global_cones = [(1, 1)]
global_dots = [(1, 1)]

if __name__ == "__main__":
    asyncio.run(tk_main())
