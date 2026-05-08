# tkinter is Python's built-in library for making desktop GUIs (windows, buttons, text boxes etc.)
import tkinter as tk
# messagebox lets us show pop-up alert dialogs like errors or success messages
from tkinter import messagebox

# Import our custom map widget (defined in src/map/map.py)
from src.map.map import EventMap
# Import our EventService which handles reading/writing the CSV file
from src.services.event_service import EventService


# MainWindow inherits from tk.Tk, which means this class IS the main application window.
# Inheriting from tk.Tk gives us all the window behaviour for free.
class MainWindow(tk.Tk):

    # __init__ runs automatically when we create a MainWindow object.
    # It builds everything the window needs before it appears on screen.
    def __init__(self, current_user):
        # Call the parent class (tk.Tk) setup first so the window is properly initialised
        super().__init__()

        self.current_user = current_user

        # Set the text shown in the window's title bar
        self.title("AtTheFunc Event Manager")
        # Set the starting size of the window in pixels (width x height)
        self.geometry("1100x700")

        # Create an EventService so this window can save/load/delete events
        self.event_service = EventService()

        # --- Heading label at the top of the window ---
        title_label = tk.Label(
            self,
            text="AtTheFunc Event Manager",
            font=("Arial", 18, "bold")   # Large bold font makes this look like a heading
        )
        # pack() places the widget in the window; pady adds vertical spacing around it
        title_label.pack(pady=10)

        login_label = tk.Label(
            self,
            text=f"Logged in as: {self.current_user.get('username')} ({self.current_user.get('role')})",
            font=("Arial", 10)
        )
        login_label.pack()

        # --- Form area ---
        # A Frame is an invisible container used to group widgets together
        form_frame = tk.Frame(self)
        # fill="x" stretches the frame to fill the full window width
        form_frame.pack(fill="x", padx=10, pady=10)

        # Create a label + text entry for each field using _make_field (defined below).
        # row and col control where each field sits in the grid layout.
        self.event_id_entry = self._make_field(form_frame, "Event ID",  row=0, col=0)
        self.title_entry    = self._make_field(form_frame, "Title",     row=0, col=1)
        self.date_entry     = self._make_field(form_frame, "Date",      row=1, col=0)
        self.time_entry     = self._make_field(form_frame, "Time",      row=1, col=1)
        self.location_entry = self._make_field(form_frame, "Location",  row=2, col=0)
        self.address_entry  = self._make_field(form_frame, "Address",   row=2, col=1)
        self.lat_entry      = self._make_field(form_frame, "Latitude",  row=3, col=0)
        self.lon_entry      = self._make_field(form_frame, "Longitude", row=3, col=1)

        # Notes spans multiple columns so it is wider than the other fields
        tk.Label(form_frame, text="Notes").grid(row=4, column=0, sticky="w", padx=5)
        self.notes_entry = tk.Entry(form_frame, width=50)
        # columnspan=3 makes this entry box stretch across 3 grid columns
        self.notes_entry.grid(row=4, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # --- Buttons ---
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)

        # Each button's command= points to the method that runs when the button is clicked
        tk.Button(button_frame, text="Add Event",    command=self.add_event).pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete Event", command=self.delete_event).pack(side="left", padx=5)
        tk.Button(button_frame, text="Reload Map",   command=self.reload_map).pack(side="left", padx=5)

        # --- Map widget ---
        # Add the interactive map at the bottom of the window.
        # When the user clicks the map, coordinates are sent to on_map_location_selected.
        self.map_frame = EventMap(self, on_location_selected=self.on_map_location_selected)
        # expand=True lets the map grow to fill any remaining space in the window
        self.map_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Helper: creates a label and text entry side by side and positions them in the grid.
    # We use this to avoid repeating the same 3 lines of code for every field.
    def _make_field(self, parent, label, row, col=0, width=25):
        # Place the label text (e.g. "Event ID") to the left of the input box.
        # col * 2 spreads columns out so labels and entries alternate: 0, 1, 2, 3 ...
        tk.Label(parent, text=label).grid(row=row, column=col * 2, sticky="w", padx=5, pady=3)
        # Create the text input box
        entry = tk.Entry(parent, width=width)
        entry.grid(row=row, column=col * 2 + 1, padx=5, pady=3)
        # Return the entry so the caller can store it and read what the user typed
        return entry

    # Called when the "Add Event" button is clicked
    def add_event(self):
        # try/except catches errors so the app doesn't crash if something unexpected happens
        try:
            # Read the text from each input box. strip() removes accidental leading/trailing spaces.
            event_data = {
                "event_id": self.event_id_entry.get().strip(),
                "title":    self.title_entry.get().strip(),
                "date":     self.date_entry.get().strip(),
                "time":     self.time_entry.get().strip(),
                "location": self.location_entry.get().strip(),
                "address":  self.address_entry.get().strip(),
                "lat":      self.lat_entry.get().strip(),
                "lon":      self.lon_entry.get().strip(),
                "notes":    self.notes_entry.get().strip(),
                "owner_id": str(self.current_user.get("user_id", "")),
            }

            # List the fields that must not be left empty
            required_fields = [
                event_data["event_id"],
                event_data["title"],
                event_data["date"],
                event_data["time"],
                event_data["location"],
                event_data["address"],
                event_data["lat"],
                event_data["lon"],
            ]

            # all() returns False if any value in the list is an empty string
            if not all(required_fields):
                messagebox.showerror("Input Error", "Please fill in all required fields.")
                return  # Stop here — don't try to save an incomplete event

            # Try converting lat/lon to decimal numbers.
            # If they aren't valid numbers this raises a ValueError (caught below).
            float(event_data["lat"])
            float(event_data["lon"])

            # Save the event to the CSV file
            self.event_service.create_event(event_data)
            # Refresh the map so the new marker appears straight away
            self.reload_map()
            # Clear the form so it's ready for the next entry
            self.clear_form()

            messagebox.showinfo("Success", "Event added successfully.")

        except ValueError:
            # Runs if float() above failed — the user typed non-numeric lat/lon
            messagebox.showerror("Input Error", "Latitude and longitude must be valid numbers.")

    # Called when the "Delete Event" button is clicked
    def delete_event(self):
        # Read the Event ID the user typed in
        event_id = self.event_id_entry.get().strip()

        # Don't proceed if no ID was entered — we wouldn't know what to delete
        if not event_id:
            messagebox.showerror("Input Error", "Enter an Event ID to delete.")
            return

        # Ask the service to remove this event from the CSV file
        success, message = self.event_service.delete_event(event_id, self.current_user)
        if not success:
            messagebox.showerror("Delete Failed", message)
            return

        # Refresh the map so the removed marker disappears
        self.reload_map()
        self.clear_form()

        messagebox.showinfo("Success", message)

    # Called when "Reload Map" is clicked, or automatically after adding/deleting an event
    def reload_map(self):
        # Tell the map widget to re-read the CSV and redraw all the markers
        self.map_frame.load_events_from_csv()

    # Receives coordinates from map clicks and writes them into the form.
    def on_map_location_selected(self, lat, lon):
        # Replace existing values with the clicked location rounded for readability
        self.lat_entry.delete(0, tk.END)
        self.lat_entry.insert(0, f"{lat:.6f}")

        self.lon_entry.delete(0, tk.END)
        self.lon_entry.insert(0, f"{lon:.6f}")

        # Auto-fill a simple location label so it's clear the coordinates came from a map click
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, "Map Selected Point")

    # Clears all the text input boxes back to empty
    def clear_form(self):
        # delete(0, tk.END) removes all characters from position 0 to the very end of the box
        self.event_id_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.lat_entry.delete(0, tk.END)
        self.lon_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)