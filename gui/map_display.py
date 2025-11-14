import tkinter as tk
from config import getVariables
import logging
import asyncio

logger = logging.getLogger(__name__)

VARIABLES = getVariables()


def setup_map(map_canvas) -> None:
    # Draw crosshair lines
    map_canvas.create_line(
        0, 200, 400, 200, fill="wheat2", dash=(2, 4)
    )  # Horizontal line
    map_canvas.create_line(
        200, 0, 200, 400, fill="wheat2", dash=(2, 4)
    )  # Vertical line

    # Draw a rectangle in the center to represent the robot
    map_canvas.create_rectangle(
        195, 190, 205, 210, fill="DodgerBlue3", outline="DodgerBlue3", tags="robot"
    )
    # Draw race-car stripes
    map_canvas.create_rectangle(
        198, 190, 199, 210, fill="white", outline="white", tags="stripe"
    )
    map_canvas.create_rectangle(
        201, 190, 202, 210, fill="white", outline="white", tags="stripe"
    )
    # Draw a rectangle on car to act as window
    map_canvas.create_rectangle(
        196,
        193,
        204,
        197,
        fill="light sky blue",
        outline="light sky blue",
        tags="window",
    )

    # Draw wheels
    def draw_wheel(x1, y1, x2, y2):
        map_canvas.create_rectangle(
            x1, y1, x2, y2, fill="black", outline="black", tags="wheel"
        )

    draw_wheel(194, 192, 195, 195)  # top left
    draw_wheel(206, 192, 207, 195)  # top right

    draw_wheel(194, 205, 195, 208)  # bottom left
    draw_wheel(206, 205, 207, 208)  # bottom right

    # Draw spoiler
    map_canvas.create_rectangle(
        194, 212, 206, 213, fill="DodgerBlue3", outline="DodgerBlue3", tags="spoiler"
    )


async def createMap(frame: tk.Frame, current_points: list, car_data, RUNNING) -> None:
    """Creates the map visualization in the 'Karta' frame in the GUI."""
    map_canvas = tk.Canvas(frame, width=400, height=400, bg="antique white")
    map_canvas.pack(expand=False)

    setup_map(map_canvas)

    async def draw_map() -> None:
        """Draws the map points on the canvas."""
        # Clear only the previous points but keep the crosshair lines
        middle = 200
        map_canvas.delete("points")
        map_canvas.delete("path")

        # ----------------------------------------------------------------------------
        # draw next center
        tup = car_data["next_center"]
        xpos, ypos = tup[0], tup[1]
        x, y = (
            int(xpos) / VARIABLES["MAP_DIVISION_FACTOR"] + middle,
            -int(ypos) / VARIABLES["MAP_DIVISION_FACTOR"] + middle,
        )
        map_canvas.create_oval(
            x - 3,
            y - 3,
            x + 3,
            y + 3,
            fill="red3",
            outline="red3",
            tags="points",
        )

        map_canvas.create_line(
            middle,
            middle,
            x,
            y,
            fill="red3",
            width=1,
            tags="path",
        )
        # ----------------------------------------------------------------------------

        half = len(current_points) // 2
        points = current_points[-half:]

        for point in points:
            try:
                x_undiv, y_undiv, size = tuple(point)
                x, y = (
                    int(x_undiv) / VARIABLES["MAP_DIVISION_FACTOR"] + middle,
                    -int(y_undiv) / VARIABLES["MAP_DIVISION_FACTOR"] + middle,
                )

                point_width = 0
                color = "black"
                outline = "black"

                if size < 0:
                    point_width = 3
                    color = "olive drab"
                    outline = "olive drab"
                elif size > 0:
                    point_width = 5
                    color = "dark olive green"
                    outline = "dark olive green"
                elif size == 0:
                    point_width = 2
                    color = "wheat3"
                    outline = "wheat3"
                else:
                    logger.error(f"Incorrect point size: {size}")

                # Draw the point on the canvas
                map_canvas.create_oval(
                    x - point_width,
                    y - point_width,
                    x + point_width,
                    y + point_width,
                    fill=color,
                    outline=outline,
                    tags="points",
                )
            except ValueError as e:
                logger.error(f"Value error when splitting: {e}")
                # print("There are no points to draw!")

    while RUNNING:
        """Updates the map visualization in real-time."""
        await draw_map()  # Redraw map with the latest points
        current_points.clear()  # Clear points after drawing to prevent duplicates
        await asyncio.sleep(VARIABLES["MAP_UPDATE_FREQ"])
