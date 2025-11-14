from locate_car import update_position_and_orientation
from mapping import CarPos
from queue import Queue
import time

last_time = time.time()


# def update_position_and_orientation(sensor_q: queue, car_position, last_time):


def test():
    sensor_q = Queue()
    sensor_q.put((127, 127, 127))
    coord = (0, 0)
    angle = 0
    newCar = CarPos(coord, angle)
    time.sleep(3)
    # should give out same 0 values for carPos
    # updated  = update_position_and_orientation(sensor_q, newCar, last_time)
    print(
        "print car coordinates",
        newCar.pos,
        "print car orientation",
        newCar.deg_rotation,
    )
    time.sleep(3)
    sensor_q.put((127, 127, 127))
    update_position_and_orientation()


test()
