"""
Settings file for the car
"""

# ---------------------------------------------------------------------------------
# Settings for mainloop
ENABLE_LIDAR = True
ENABLE_SENSOR = True
ENABLE_LISTEN = True
ENABLE_SEND = True
ENABLE_MAP = True
ENABLE_DRIVE = True
ENABLE_LIDAR_DRAW_LOCALLY = False

# ---------------------------------------------------------------------------------
# USB ports for sensor, steer and lidar.
STEER_USB_PORT = "/dev/ttyUSB0"
SENSOR_USB_PORT = "/dev/ttyUSB1"
LIDAR_USB_PORT = "/dev/ttyUSB2"

# ---------------------------------------------------------------------------------
# The RPi:s IP and listening port.
MY_IP = "10.42.0.1"
LISTENER_PORT = 12306

# ---------------------------------------------------------------------------------
# Sensor and steer module settings.
AVR_BAUDRATE = 9600

# ---------------------------------------------------------------------------------
# Mapping settings
CONE_DISTANCE_TOLERANCE = (
    200  # Max distance between two identified cones to be considered as the same cone.
)

# The timer until the kill switch fires when the car hasn't received a command in milliseconds'
KILL_SWITCH_MS = 1000

# Updates per second of the main loop (approx.)
MAIN_LOOP_UPS = 10

# ---------------------------------------------------------------------------------
# LiDAR settings
MEAS_SIZE = 800  # Amount of points of data to read before doing all calculations.

OBJ_MAX_DISTANCE = 100  # Maximum distance in milimeters between two data point for them to be considered to be in the same object.

CONE_DIAM_LOWER = 20  # Minimum diameter of a cone in milimeters.
CONE_DIAM_MIDDLE = (
    120  # Threshold for a cone to be considered as a small/large in milimeters.
)
CONDE_DIAM_UPPER = 250  # maximum diameter of a cone in milimeters.

SCALER = 1 / 5  # Picture scaledown factor for turtle graphics.

COUNT_ONLY_AMOUNT_OF_DOTS_DISTANCE = 2000  # Outside of this distance(milimetes), only amount of dots in an object are considered for defining cones.
AMOUNT_OF_DOTS_THRESHOLD = 2  # Amount of dots for an object to be considered a cone.
MAX_VIEW_DISTANCE = (
    3000  # Outside of this distance(milimets), the progam doesnt consider the data.
)
MAX_VIABLE_MEASUREMENT = 2000

# ---------------------------------------------------------------------------------
# Locate car settings
# ADC referensspänning i Volt
ADC_REF_VOLTAGE = 5.0
# 8-bit ADC (vänsterjusterat)
ADC_RESOLUTION = 255.0
# Gyro känslighet i V/°/s
GYRO_SENSITIVITY = 0.00667
# Gyro nollpunkt i volt
GYRO_ZERO = 2.5
# WHEEL CIRCUMFRANCE IN M
WHEEL_CIRCUMFERENCE = 0.250
