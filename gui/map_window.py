import tkinter as tk
import random

X = 500
Y = 300


def retrieve_car() -> tuple[int, int]:
    global X
    global Y

    def get_random():
        return random.choice([-1, 0, 1])

    X += get_random()
    Y += get_random()
    return X, Y


def open_map_window() -> None:
    """Öppnar ett nytt fönster som visar en fullständig karta med 50x50 rutor."""
    # Skapa ett nytt fönster
    map_window = tk.Toplevel()
    map_window.title("Fullständig Karta")

    # Sätt storlek på det nya fönstret
    map_window.geometry("1000x600")

    # Skapa en Canvas-widget för kartan med fast storlek
    canvas = tk.Canvas(map_window, width=1000, height=600, bg="light grey")
    canvas.pack()

    # Kartans dimensioner
    width = 1000
    height = 600

    # Gridens cellstorlek
    cell_size = 100

    # Rita streckade linjer för att dela in kartan i 50x50 rutor
    for x in range(0, width, cell_size):
        canvas.create_line(
            x, 0, x, height, fill="dark grey", dash=(5, 5)
        )  # Vertikala linjer
    for y in range(0, height, cell_size):
        canvas.create_line(
            0, y, width, y, fill="dark grey", dash=(5, 5)
        )  # Horisontella linjer

    def update_map():
        canvas.delete("robot")

        x, y = retrieve_car()
        # Draw a blue dot in the center to represent the robot
        canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5, fill="blue", outline="black", tags="robot"
        )

        # Schedule the next update in 5 milliseconds
        canvas.after(5, update_map)

    update_map()
