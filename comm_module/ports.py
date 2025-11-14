from dataclasses import dataclass
import subprocess


@dataclass
class Ports:
    """Class to store all port paths."""

    lidar: str
    sensor: str
    steer: str

    @staticmethod
    def new():
        """Read port paths from bash script."""

        # Note the bash script "ports.sh" is a modified version of a script
        # written by the user "Phemmer" on https://unix.stackexchange.com/questions/144029/command-to-determine-ports-of-a-device-like-dev-ttyusb0
        script_output = subprocess.check_output("./ports.sh").decode().split()

        ports = dict(zip(script_output[1::2], script_output[::2]))
        return Ports(
            lidar=ports["Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001"],
            sensor=ports["FTDI_TTL232R_FT94S3SE"],
            steer=ports["FTDI_TTL232R_FT94NZK6"],
        )
