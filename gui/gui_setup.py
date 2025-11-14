import tkinter as tk
from tkinter import ttk


def createRoot() -> tk.Tk:
    """Skapar och konfigurerar huvudfönstret för applikationen."""
    root = tk.Tk()
    root.title("Tävlingsbil")
    root.geometry("1000x650")  # Justera storleken vid behov
    return root


def addFrames(root: tk.Tk) -> list[tk.Frame]:
    """Lägger till olika ramkomponenter i huvudfönstret."""
    frames = {}
    # Specifikationer för ramarnas position, storlek och namn
    frame_specs = [
        (0, 0, 500, 500, "Karta"),  # X, Y, Width, Height
        (725, 275, 275, 100, "Autonomi"),
        (500, 0, 500, 275, "Hastighet & Gyro"),
        (0, 500, 1000, 150, "Konsol"),
        (500, 275, 225, 225, "Status"),
        (725, 375, 275, 125, "Kontroller"),
    ]

    for i, (x, y, width, height, name) in enumerate(frame_specs):
        # Skapa en ram med specifika dimensioner och etikett
        frame = ttk.Frame(
            root, width=width, height=height, relief=tk.SOLID, borderwidth=2
        )
        frame.place(x=x, y=y, width=width, height=height)
        label = tk.Label(
            frame,
            text=name,
            anchor="nw",
            justify="left",
            font=("Helvetica", 10, "bold"),
        )
        label.pack(anchor="nw", side="top", padx=5, pady=5)
        frames[name] = frame  # Lägg till ramen i listan
    return frames
