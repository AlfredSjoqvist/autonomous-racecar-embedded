import tkinter as tk
from config import getVariables

VARIABLES = getVariables()


def open_parameters_window(VARIABLES: list[tk.Variable]):
    """Open a separate window to display and edit configuration parameters."""

    def save_changes():
        """Save the changes made in the parameters window back to VARIABLES."""
        for key, entry in entries.items():
            try:
                # Convert value to the correct type based on the current value in VARIABLES
                current_value = VARIABLES[key]
                if isinstance(current_value, int):
                    VARIABLES[key] = int(entry.get())
                else:
                    VARIABLES[key] = entry.get()
            except ValueError:
                # If there's a conversion error, keep the old value
                entry.delete(0, "end")
                entry.insert(0, str(VARIABLES[key]))

    # Create a new window
    window = tk.Toplevel()
    window.title("Edit Parameters")
    window.geometry("400x600")

    # Create a frame for the entries
    frame = tk.Frame(window)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create a dictionary to store entry widgets
    entries = {}

    # Iterate through VARIABLES to create a label and entry for each item
    for i, (key, value) in enumerate(VARIABLES.items()):
        if (
            (key == "GAS_STRENGTH")
            or (key == "MIDDLE_STEER")
            or (key == "AUTOSPEED")
            or (key == "TURN_COEFF")
        ):
            label = tk.Label(frame, text=key)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            entry = tk.Entry(frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="we")
            entry.insert(0, str(value))  # Pre-fill the entry with the current value

            # Save each entry widget to the dictionary
            entries[key] = entry

    # Create a save button to apply changes
    save_button = tk.Button(window, text="Save", command=save_changes)
    save_button.pack(pady=10)

    abort_button = tk.Button(window, text="Close", command=window.destroy)
    abort_button.pack(pady=10)

    # Allow resizing
    frame.grid_columnconfigure(1, weight=1)
