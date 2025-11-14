import random
from config import getVariables
import tkinter as tk


# Simulerar förändring av gaspådrag
def simulate_throttle_changes(root: tk.Tk, throttle_level_var: tk.IntVar) -> None:
    """Simulerar förändring av gaspådrag"""
    variables = getVariables()
    coin_flip = random.randint(0, 10)  # Simulera ny gasnivå
    if (coin_flip >= 5) & (throttle_level_var.get() < 80):
        throttle_level_var.set(throttle_level_var.get() + 1)  # höj gasnivån
    elif throttle_level_var.get() > 0:
        throttle_level_var.set(throttle_level_var.get() - 1)  # sänk gasnivån
    root.after(
        variables["UPDATE_FREQUENCY"],
        lambda: simulate_throttle_changes(root, throttle_level_var),
    )  # Schemalägg nästa förändring


# Simulerar förändring av styrvinkel
def simulate_steering_changes(root: tk.Tk, steering_angle_var: tk.IntVar) -> None:
    """Simulerar förändring av styrvinkel"""
    variables = getVariables()
    coin_flip = random.randint(0, 1)  # Simulera ny styrvinkel
    if coin_flip & (steering_angle_var.get() < 30):
        steering_angle_var.set(steering_angle_var.get() + 1)  # höj styrvinkel
    elif (not coin_flip) & (steering_angle_var.get() > -30):
        steering_angle_var.set(steering_angle_var.get() - 1)  # sänk styrvinkel
    else:
        pass
    root.after(
        variables["UPDATE_FREQUENCY"],
        lambda: simulate_steering_changes(root, steering_angle_var),
    )  # Schemalägg nästa förändring


# Simulerar förändring av styrvinkel
def simulate_elapsed_time(root: tk.Tk, elapsed_time_var: tk.DoubleVar) -> None:
    """Simulerar passerad tid"""
    elapsed_time_var.set(elapsed_time_var.get() + 1)
    root.after(
        1000, lambda: simulate_elapsed_time(root, elapsed_time_var)
    )  # Schemalägg nästa förändring


def simulatePoints(root: tk.Tk, current_points: list) -> None:
    """Simulerar förändring av styrvinkel"""
    for i in range(50):
        rand_x = random.randint(0, 3000)  # Simulate new steering angle
        rand_y = random.randint(0, 3000)
        rand_size = random.randint(-1, 1)
        tup = (rand_x, rand_y, rand_size)
        current_points.append(tup)

    root.after(
        100,
        lambda: simulatePoints(root, current_points),
    )  # Schemalägg nästa förändring
