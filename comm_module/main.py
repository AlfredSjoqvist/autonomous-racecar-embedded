#!/usr/bin/env python
import asyncio
from car import Car
import logging
from websockets.asyncio.server import serve, ServerConnection

logger = logging.getLogger(__name__)


async def handler(websocket: ServerConnection, car: Car):
    """Handle a connection."""
    car.running = True
    auto = car.autopilot()
    sense = car.sensor_reader()
    lidar = car.lidar_reader()
    message = car.read_messages(websocket)
    dispatch = car.event_handler(websocket)
    await asyncio.gather(auto, sense, lidar, message, dispatch)


async def main():
    """Start the server and setup logger."""
    logging.basicConfig(level=logging.INFO)
    car = Car()
    async with serve(lambda w: handler(w, car), "", 12306) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
