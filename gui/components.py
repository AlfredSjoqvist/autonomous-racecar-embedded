import asyncio

import tkinter as tk
import math as m
from config import getVariables
from map_window import open_map_window
from param_window import open_parameters_window
import message
from utils import simulate_elapsed_time

VARIABLES = getVariables()


async def createAutonomy(
    root: tk.Tk, frame: tk.Frame, console_output: tk.Text, websocket, car_data: dict
) -> None:
    """Skapar knappar för att styra autonomin och loggar toggling av läge till konsolen."""

    # Startknapp för autonomt läge
    async def toggle(toggle):
        if toggle:
            await websocket.send(
                message.auto(toggle, VARIABLES["AUTOSPEED"], VARIABLES["TURN_COEFF"])
            )
            simulate_elapsed_time(root, car_data["elapsed_time"])
            log_to_console("Autonomt läge STARTAT!")
        else:
            await websocket.send(message.auto(toggle, 0, 0))
            log_to_console("Autonomt läge STOPPAT!")
            root.after_cancel(simulate_elapsed_time)
            car_data["elapsed_time"].set(0)

    start_button = tk.Button(
        frame,
        text="Start",
        command=lambda: asyncio.create_task(toggle(True)),
    )
    start_button.pack(side="left", padx=5, pady=5)

    # Stoppknapp för autonomt läge
    stop_button = tk.Button(
        frame,
        text="Stop",
        command=lambda: asyncio.create_task(toggle(False)),
    )
    stop_button.pack(side="left", padx=5, pady=5)

    def log_to_console(message: str) -> None:
        """Loggar ett meddelande till konsolens utmatning."""
        console_output.insert("end", f"{message}\n")  # Lägg till meddelandet
        console_output.see("end")  # Rulla ner till slutet av texten


def createStatus(
    frame: tk.Frame,
    car_data: dict[str:any],
) -> None:
    """Skapar statusinformationen för gasnivå, styrvinkel och annan information."""

    global VARIABLES

    labels = {}
    properties = [
        "Körtid",
        "Hastighet",
        "Gyro",
        "Gaspådrag",
        "Styrutslag",
        "Avstånd",
        "Vinkel",
    ]

    for prop in properties:
        # Skapa en label för varje egenskap
        label = tk.Label(frame, text=f"{prop}: -", anchor="w")
        label.pack(anchor="w", padx=5, pady=2)
        labels[prop] = label  # Spara labeln för senare användning

    def update_status() -> None:
        """Uppdaterar statusinformationen varje sekund."""
        elapsed_time = car_data["elapsed_time"].get()  # Hämta förfluten tid
        labels["Körtid"].config(text=f"Körtid: {elapsed_time}s")  # Simulera körtid
        labels["Hastighet"].config(
            text=f"Hastighet: {round(car_data['velocity'].get(), 2)} m/s"
        )  # Simulera hastighet
        labels["Gyro"].config(
            text=f"Gyro: {round(car_data['gyro_angle'].get() % 360, 2)}°"
        )  # Uppdatera styrvinkel
        labels["Gaspådrag"].config(
            text=f"Gaspådrag: {round(car_data['throttle'].get(), 2)}  /  256"
        )
        labels["Styrutslag"].config(
            text=f"Styrutslag: {round(car_data['turn'].get(), 2)}          (~120 är mitten)"
        )
        labels["Avstånd"].config(
            text=f"Avstånd till port: {round(car_data['distance'].get() / 1000, 2)}m"
        )
        labels["Vinkel"].config(
            text=f"Vinkel till port: {round(car_data['angle_to_gate'].get(), 2)}°"
        )

        frame.after(
            VARIABLES["UPDATE_FREQUENCY"], update_status
        )  # Schemalägg nästa uppdatering

    update_status()  # Starta den första uppdateringen


def createConsole(frame: tk.Frame) -> tk.Text:
    """Skapar konsolramen för användarens kommandon och utdata."""
    output_text = tk.Text(
        frame, wrap="word", height=5
    )  # Textområde för att visa utdata
    output_text.pack(expand=True, fill="both", padx=5, pady=(0, 5))

    input_entry = tk.Entry(frame)  # Inmatningsfält för kommandon
    input_entry.pack(fill="x", padx=5, pady=5)

    def handle_input(event=None) -> None:
        """Hantera kommandon som användaren skriver in."""
        command = input_entry.get()
        if command.strip():  # Kontrollera att kommandot inte är tomt
            output_text.insert("end", f"> {command}\n")  # Skriv kommandot till konsolen
            output_text.see("end")  # Rulla ner till slutet av texten
            input_entry.delete(0, "end")  # Rensa inmatningsfältet
            output_text.insert("end", "Kommandot har körts.\n")  # Bekräftelsemeddelande

    input_entry.bind(
        "<Return>", handle_input
    )  # Bind Return-tangenten till kommandohanteringen
    return output_text


async def createControls(
    root: tk.Tk,
    frame: tk.Frame,
    console_output: tk.Text,
    websocket,
    RUNNING,
) -> None:
    """Skapar knappar & pilar för config resp. manuell körning."""
    # Skapa pilar och deras tillstånd
    arrows = {
        "Left": {
            "label": tk.Label(frame, text="←", font=("Arial", 24), fg="black"),
            "pressed": False,
            "nemesis": "Right",
            "nemesis_command": lambda: message.steer(VARIABLES["MIDDLE_STEER"]),
            "message_on": lambda: message.steer(1),
            "message_off": lambda: message.steer(VARIABLES["MIDDLE_STEER"]),
        },
        "Up": {
            "label": tk.Label(frame, text="↑", font=("Arial", 24), fg="black"),
            "pressed": False,
            "nemesis": "Down",
            "nemesis_command": lambda: message.throttle(1, False),
            "message_on": lambda: message.throttle(VARIABLES["GAS_STRENGTH"], False),
            "message_off": lambda: message.throttle(1, False),
        },
        "Down": {
            "label": tk.Label(frame, text="↓", font=("Arial", 24), fg="black"),
            "pressed": False,
            "nemesis": "Up",
            "nemesis_command": lambda: message.throttle(1, True),
            "message_on": lambda: message.throttle(160, True),
            "message_off": lambda: message.throttle(1, False),
        },
        "Right": {
            "label": tk.Label(frame, text="→", font=("Arial", 24), fg="black"),
            "pressed": False,
            "nemesis": "Left",
            "nemesis_command": lambda: message.steer(VARIABLES["MIDDLE_STEER"]),
            "message_on": lambda: message.steer(255),
            "message_off": lambda: message.steer(VARIABLES["MIDDLE_STEER"]),
        },
    }
    brake_pressed = False

    # Packa pilarna
    for arrow in arrows.values():
        arrow["label"].pack(side="left", padx=5)

    # Knappar för 'Parametrar' och 'Fullständig karta'
    parameters_button = tk.Button(
        frame,
        text="Parametrar",
        command=lambda: open_parameters_window(VARIABLES),
    )
    parameters_button.pack(anchor="w", padx=5, pady=5)

    full_map_button = tk.Button(
        frame, text="Fullständig karta", command=open_map_window
    )
    full_map_button.pack(anchor="w", padx=5, pady=5)

    # Funktion för att logga till konsolen
    def log_to_console(message: str) -> None:
        console_output.insert("end", f"{message}\n")
        console_output.see("end")

    # Funktion för att hantera tangenttryckningar
    async def on_key_event(event: tk.Event, pressed: bool) -> None:
        nonlocal brake_pressed
        nonlocal RUNNING
        if event.keysym in arrows:
            arrow = arrows[event.keysym]
            if (
                pressed
                and not arrow["pressed"]
                and not (arrows[arrow["nemesis"]]["pressed"])
            ):
                arrow["label"].config(fg="red")
                log_to_console(event.keysym.lower())
                await websocket.send(arrow["message_on"]())
                arrow["pressed"] = True
            elif not pressed and arrow["pressed"]:
                arrow["label"].config(fg="black")
                log_to_console(f"{event.keysym.lower()}'")
                await websocket.send(arrow["message_off"]())
                arrow["pressed"] = False
        elif event.keysym == "space":
            if pressed and not brake_pressed:
                log_to_console("brake")
                await websocket.send(message.brake(True))
                brake_pressed = True
            elif not pressed and brake_pressed:
                log_to_console("STOP brake")
                await websocket.send(message.brake(False))
                brake_pressed = False
        elif event.keysym == "Escape":
            if pressed:
                log_to_console("exit")
                await websocket.send(message.exit())
                RUNNING = False
                print("Connection closed by ESC key.")
                root.destroy()

    # Binda tangenttryck och släpp
    frame.bind_all("<KeyPress>", lambda e: asyncio.create_task(on_key_event(e, True)))
    frame.bind_all(
        "<KeyRelease>", lambda e: asyncio.create_task(on_key_event(e, False))
    )


def createVelocityGyro(frame: tk.Frame, car_data: dict[str:any]) -> None:
    """Skapar gas- och styrkomponenterna för att visa gasnivå och styrvinkel."""

    global VARIABLES

    # Skapa en Canvas-widget för att rita hastighet
    vel_canvas = tk.Canvas(frame, width=50, height=200, bg="white")
    vel_canvas.pack(side="left", padx=10, pady=10)  # Placera gasnivån till vänster
    vel_canvas.create_text(28, 20, text="Hastigh.", font=("Arial", 10), fill="black")

    # Skapa en Canvas-widget för att rita gaspådrag
    thrott_canvas = tk.Canvas(frame, width=50, height=200, bg="white")
    thrott_canvas.pack(side="left", padx=10, pady=10)  # Placera gasnivån till vänster
    thrott_canvas.create_text(25, 20, text="Gas", font=("Arial", 10), fill="black")

    # Skapa en Canvas-widget för cirekl och linje till GYRO
    gyro_canvas = tk.Canvas(frame, width=150, height=150, bg="white")
    gyro_canvas.pack(side="left", padx=5, pady=10)  # Placera styrvinkeln till höger
    gyro_canvas.create_text(75, 20, text="Gyro", font=("Arial", 10), fill="black")

    # Skapa en Canvas-widget för cirekl och linje till styrutslag
    steering_canvas = tk.Canvas(frame, width=150, height=150, bg="white")
    steering_canvas.pack(side="left", padx=5, pady=10)  # Placera styrvinkeln till höger
    steering_canvas.create_text(75, 20, text="Styr", font=("Arial", 10), fill="black")

    # Radie av cirkeln
    radius = 45
    center_x = 75  # Cirkels mittpunkt (x)
    center_y = 75  # Cirkels mittpunkt (y)

    # Rita cirkeln GYRO
    gyro_canvas.create_oval(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
        outline="black",
    )

    # Rita cirkeln Steer
    steering_canvas.create_oval(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
        outline="black",
    )

    # Funktion för att uppdatera hastighet
    def update_velocity() -> None:
        level = round(car_data["velocity"].get(), 2)  # Hämta aktuellt gaspådrag
        vel_canvas.delete("liquid")  # Ta bort eventuell tidigare ritad gasnivå
        canvas_height = 200
        fill_height = (
            level / 10
        ) * canvas_height  # Beräkna hur hög gasnivån ska vara TODO: varför 10? lul
        vel_canvas.create_rectangle(
            10,
            canvas_height - fill_height,
            45,
            canvas_height,
            fill="light green",
            tags="liquid",
        )  # Rita gasnivån
        vel_canvas.create_text(
            30,
            canvas_height - fill_height - 10,
            text=f"{level}m/s",
            tags="liquid",
        )  # Visa procent

        frame.after(
            VARIABLES["UPDATE_FREQUENCY"], update_velocity
        )  # Uppdatera gasnivån varje sekund

    # Funktion för att uppdatera gasnivån
    def update_throttle() -> None:
        level = round(car_data["throttle"].get() - 140, 2)  # Hämta aktuellt gaspådrag
        thrott_canvas.delete("liquid")  # Ta bort eventuell tidigare ritad gasnivå
        canvas_height = 200
        thrott_canvas.create_rectangle(
            10,
            canvas_height - level,
            45,
            canvas_height,
            fill="blue",
            tags="liquid",
        )  # Rita gasnivån
        thrott_canvas.create_text(
            30,
            canvas_height - level - 10,
            text=f"{level}m/s",
            tags="liquid",
        )  # Visa procent

        frame.after(
            VARIABLES["UPDATE_FREQUENCY"], update_throttle
        )  # Uppdatera gasnivån varje sekund

    # Funktion för att rita linjen som indikerar styrvinkeln
    def update_gyro() -> None:
        angle = round(car_data["gyro_angle"].get(), 2) % 360
        gyro_canvas.delete("indicator")  # Ta bort tidigare linje
        # Beräkna linjens slutpunkt baserat på styrvinkeln
        angle_rad = (90 - angle) * (
            m.pi / 180
        )  # Konvertera till radianer (90° är norrläge)
        end_x = center_x + radius * m.cos(angle_rad)  # Beräkna slutpunktens x-koordinat
        end_y = center_y - radius * m.sin(
            angle_rad
        )  # Beräkna slutpunktens y-koordinat (subtrahera)

        # Rita linjen
        gyro_canvas.create_line(
            center_x,
            center_y,
            end_x,
            end_y,
            fill="red",
            width=2,
            tags="indicator",
        )

        frame.after(
            VARIABLES["UPDATE_FREQUENCY"], update_gyro
        )  # Uppdatera varje sekund

    # Funktion för att rita linjen som indikerar styrvinkeln
    def update_steer() -> None:
        angle = round(car_data["turn"].get() - 120, 2) % 360
        steering_canvas.delete("indicator")  # Ta bort tidigare linje
        # Beräkna linjens slutpunkt baserat på styrvinkeln
        angle_rad = (90 - angle) * (
            m.pi / 180
        )  # Konvertera till radianer (90° är norrläge)
        end_x = center_x + radius * m.cos(angle_rad)  # Beräkna slutpunktens x-koordinat
        end_y = center_y - radius * m.sin(
            angle_rad
        )  # Beräkna slutpunktens y-koordinat (subtrahera)

        # Rita linjen
        steering_canvas.create_line(
            center_x,
            center_y,
            end_x,
            end_y,
            fill="orange",
            width=2,
            tags="indicator",
        )

        frame.after(
            VARIABLES["UPDATE_FREQUENCY"], update_steer
        )  # Uppdatera varje sekund

    update_velocity()  # Starta uppdatering av gasnivån
    update_throttle()
    update_gyro()  # Starta uppdatering av styrvinkeln
    update_steer()
