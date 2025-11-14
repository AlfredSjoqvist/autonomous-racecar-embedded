import asyncio
from asyncio import Queue
from car_settings import (
    AVR_BAUDRATE,
    MEAS_SIZE,
)
import json
import drive
import lidar
from lidar import Dot
import logging
from ports import Ports
import sensor
from sensor import SensorData
import serial
import signal
import time
import math
import util
import websockets
from pathfinder import pair_cones_moment
from websockets.asyncio.server import ServerConnection
from mapping import Cone, CarPos, ConesMap

logger = logging.getLogger(__name__)


class Car:
    """Class for keeping track of all the internal state of the car."""

    def __init__(self):
        self.angle: int = 127
        self.auto: bool = False
        self.reverse: bool = False
        self.brake: bool = False
        self.event_q: Queue = Queue()
        self.ports: Ports = Ports.new()
        self.running: bool = True
        self.throttle: int = 1
        self.sensor_data: SensorData = SensorData(0, 0, 0, 0)
        self.cones: list[Cone] = []
        self.dots: list[Dot] = []
        self.sensor_angle: float = 0
        self.car_pos: CarPos = CarPos((0, 0), 0)
        self.cones_map: ConesMap = ConesMap([])
        self.next_gate_center = (0, 0)
        self.set_throttle(False, 0)
        self.turn_coeff: int = 150
        self.auto_speed: int = 160

    def steer_function(func):
        """Update steering after the decorated function."""

        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            drive.set_gas_and_servo(
                self.throttle, self.angle, self.reverse, self.brake, self.ports.steer
            )

        return wrapper

    async def autopilot(self):
        await asyncio.sleep(2)
        logger.info("Entering autopilot")
        while self.running:  # and len(self.cones) >= 2:
            await asyncio.sleep(0.2)
            cone_map = ConesMap(self.cones)
            # logger.info(str(cone_map.cones))
            if len(cone_map.cones) >= 2 and self.auto:
                self.set_throttle(False, self.auto_speed)
                # logger.info(f"cones map length: {len(cone_map.cones)}")
                local_gate_map = pair_cones_moment(cone_map)
                local_gates = local_gate_map.gates
                if len(local_gates) >= 1:
                    sorted_gates = sorted(
                        local_gates,
                        key=lambda gate: abs(
                            math.atan2(gate.center[0], gate.center[1])
                        ),
                    )
                    # logger.info(f"{sorted_gates}")
                    next_gate = sorted_gates[0]
                    for gate in sorted_gates:
                        if 2000 > gate.center[1] > 200:
                            next_gate = gate
                            # logger.info(f"Atangrej: {abs(math.atan2(next_gate.center[0],next_gate.center[1]))}")
                            break

                    next_gate_x, next_gate_y = next_gate.center
                    # logger.info(f"x: {next_gate_x} y: {next_gate_y}")

                    AIMPOINT_OFFSET = 200
                    aiming_point_x = next_gate_x - next_gate.directionVector[0] * AIMPOINT_OFFSET
                    aiming_point_y = next_gate_y - next_gate.directionVector[1] * AIMPOINT_OFFSET

                    CLOSE = 600
                    if CLOSE > math.sqrt(aiming_point_x**2 + aiming_point_y**2):
                        aiming_point_x = next_gate_x + next_gate.directionVector[0] * AIMPOINT_OFFSET
                        aiming_point_y = next_gate_y + next_gate.directionVector[1] * AIMPOINT_OFFSET

                    self.next_gate_center = (aiming_point_x, aiming_point_y)
                    angle = 127 + self.turn_coeff * math.atan2(aiming_point_x, aiming_point_y)
                    angle = util.clamp(angle, 1, 255)
                    self.set_angle(int(angle))

            elif self.auto:
                self.set_throttle(False, 0)
        logger.info("Exiting autopilot")
        self.set_throttle(False, 0)

    async def event_handler(self, websocket: ServerConnection):
        """Handle events in event_q."""
        logger.info("Starting event handler.")
        while self.running:
            match await self.event_q.get():
                case ["steer", {"angle": angle}]:
                    self.set_angle(angle)
                case ["throttle", {"reverse": reverse, "velocity": velocity}]:
                    self.set_throttle(reverse, velocity)
                case ["brake", {"brake": brake}]:
                    self.set_brake(brake)
                case ["auto", {"auto": auto, "speed": speed, "turn": turn}]:
                    self.auto = auto
                    self.auto_speed = speed
                    self.turn_coeff = turn
                    if not auto:
                        self.set_throttle(False, 0)
                    logger.info(f"current auto status:{self.auto} , recieved: {auto}")
                case ["get_cones", _]:
                    logger.debug("Sending cone data.")
                    await self.try_send(
                        websocket,
                        json.dumps(
                            [
                                "get_cones",
                                {
                                    "cones": [
                                        (c.pos[0], c.pos[1], c.size) for c in self.cones
                                    ],
                                    "next_center": self.next_gate_center,
                                },
                            ]
                        ),
                    )
                case ["get_data", _]:
                    logger.debug("Sending data.")
                    await self.try_send(
                        websocket,
                        json.dumps(
                            [
                                "get_data",
                                {
                                    "distance": math.sqrt(
                                        self.next_gate_center[0] ** 2
                                        + self.next_gate_center[1] ** 2
                                    ),
                                    "angle_to_gate": math.degrees(
                                        math.atan2(
                                            self.next_gate_center[0],
                                            self.next_gate_center[1],
                                        )
                                    ),
                                    "throttle": self.throttle,
                                    "turn": self.angle,
                                },
                            ]
                        ),
                    )
                case ["get_dots", _]:
                    logger.debug("Sending dot data.")
                    await self.try_send(
                        websocket,
                        json.dumps(
                            [
                                "get_dots",
                                {
                                    "dots": [
                                        {"a": d.angle, "d": d.distance}
                                        for d in self.dots
                                    ]
                                },
                            ]
                        ),
                    )
                case ["get_sensors", _]:
                    logger.debug("Sending sensor data.")
                    await self.try_send(
                        websocket,
                        json.dumps(
                            [
                                "get_sensors",
                                {
                                    "velocity": self.sensor_data.velocity,
                                    "angular_rate": self.sensor_data.angular_rate,
                                    "delta_time": self.sensor_data.delta_time,
                                    "angle": self.sensor_angle,
                                },
                            ],
                            sort_keys=True,
                        ),
                    )
                case ["exit", _]:
                    logger.info("Exiting")
                    self.running = False
                case x:
                    logger.warning(f"Unexpected message: {x}")
        logger.info("Exiting event handler.")

    async def lidar_reader(self):
        """Read data from the lidar and update the lidar_data variable atomically."""
        logger.info("Starting lidar reader.")
        lidar_cpp = await lidar.start_lidar(self.ports.lidar)

        while self.running:
            dot_lst = []
            for i in range(0, MEAS_SIZE):
                try:
                    line = (await lidar_cpp.stdout.readline()).decode("utf-8").split()
                    angle = float(line[0])
                    distance = float(line[1])
                    dot_lst.append(Dot(angle, distance))

                except IndexError:
                    logger.error("Lidar not detected!")
                    self.running = False
                    break
            self.cones = lidar.identify_cones(dot_lst)
            self.dots = dot_lst

        lidar_cpp.send_signal(signal.SIGTERM)

        logger.info("Exiting lidar reader.")

    async def read_messages(self, websocket: ServerConnection):
        """Read messages from the remote client."""
        logger.info("Starting message reader.")
        async for message in websocket:
            if not self.running:
                return
            try:
                msg = json.loads(message)
                await self.event_q.put(msg)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decoding failed due to error: {e}")
        await self.event_q.put(["exit", {}])
        logger.info("Exiting message reader.")

    async def sensor_reader(self):
        """Read data from sensors and update the sensor_data variable atomically."""
        logger.info("Starting sensor reader.")
        with serial.Serial(self.ports.sensor, AVR_BAUDRATE, stopbits=2) as s:
            previous_time = time.time()
            while self.running:
                await asyncio.sleep(0.05)
                if s.in_waiting and int.from_bytes(s.read(1)) == 255:
                    # Read sensor data
                    left, right, gyro_data = tuple(s.read(3))

                    # Calculate velocity
                    current_time = time.time()
                    delta_time = current_time - previous_time
                    avg_hall_inter = (left + right) / 2
                    distance_covered = sensor.calculate_distance(avg_hall_inter)
                    velocity = distance_covered / delta_time
                    angular_rate = sensor.calculate_angular_rate(gyro_data)
                    self.sensor_angle = sensor.calculate_angle(
                        angular_rate, delta_time, self.sensor_angle
                    )
                    # Atomically swap data.
                    self.sensor_data = SensorData(
                        velocity, angular_rate, delta_time, self.sensor_angle
                    )

                    # For next time it enter while-loop
                    previous_time = time.time()
        logger.info("Exiting sensor reader.")

    @steer_function
    def set_angle(self, angle: int):
        """Set the steering angle of the car."""
        self.angle = util.clamp(angle, 1, 255)
        logger.debug(f"Steer [angle: {angle}]")

    @steer_function
    def set_brake(self, brake: bool):
        """Enable or disable braking."""
        self.brake = brake
        logger.debug(f"Brake [brake: {brake}]")

    @steer_function
    def set_throttle(self, reverse: bool, velocity: int):
        """Set the throttle of the car."""
        self.throttle = util.clamp(velocity, 1, 255)
        self.reverse = reverse
        logger.debug(f"Throttle [reverse: {reverse}, velocity: {velocity}]")

    async def try_send(self, websocket: ServerConnection, msg: str):
        try:
            await websocket.send(msg)
        except websockets.exceptions.ConnectionClosed:
            logger.critical("Connection closed unexpectedly while sending.")
            self.running = False
            self.set_throttle(False, 1)
