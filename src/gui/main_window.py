import os
import tkinter as tk
from tkinter import ttk, messagebox

from src.map.map import EventMap
from src.services.event_service import EventService
from src.gui import theme


class MainWindow(tk.Tk):

    def __init__(self, current_user):
        super().__init__()
        theme.apply(self)

        self.current_user = current_user
        self.configure(bg=theme.BG)
        self.title("AtTheFunc Event Manager")
        self.geometry("1100x700")

        self.event_service = EventService()

        # Internal lat/lon — populated by map clicks, not shown in the form
        self._lat = ""
        self._lon = ""

        # Header bar
        top_frame = tk.Frame(self, bg=theme.PANEL, height=60)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)

        tk.Label(
            top_frame,
            text="AtTheFunc Event Manager",
            font=(theme.FONT, 18, 'bold'),
            bg=theme.PANEL,
            fg=theme.ACCENT,
        ).pack(side='left', padx=15, pady=12)

        # Info block on the right, with logo to the right of it
        right_frame = tk.Frame(top_frame, bg=theme.PANEL)
        right_frame.pack(side='right', padx=15, pady=8)

        tk.Label(
            right_frame,
            text=f"Logged in as: {self.current_user.get('username')}",
            font=(theme.FONT, 9, 'bold'),
            bg=theme.PANEL,
            fg=theme.TEXT,
        ).pack(anchor='e')
        tk.Label(
            right_frame,
            text=f"Role: {self.current_user.get('role')}",
            font=(theme.FONT, 8),
            bg=theme.PANEL,
            fg=theme.LABEL,
        ).pack(anchor='e')

        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Logo.png'))
        if os.path.exists(logo_path):
            self.logo_image = tk.PhotoImage(file=logo_path)
            if self.logo_image.width() > 44:
                scale = max(1, self.logo_image.width() // 44)
                self.logo_image = self.logo_image.subsample(scale, scale)
            tk.Label(top_frame, image=self.logo_image, bg=theme.PANEL).pack(side='right', padx=(0, 8))

        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill='x')

        # Form
        form_frame = tk.Frame(self, bg=theme.BG)
        form_frame.pack(fill="x", padx=15, pady=8)

        self.event_id_entry = self._make_field(form_frame, "Event ID",  row=0, col=0)
        self.title_entry    = self._make_field(form_frame, "Title",     row=0, col=1)
        self.date_entry     = self._make_field(form_frame, "Date",      row=1, col=0)
        self.time_entry     = self._make_field(form_frame, "Time",      row=1, col=1)
        self.location_entry = self._make_field(form_frame, "Location",  row=2, col=0)
        self.address_entry  = self._make_field(form_frame, "Address",   row=2, col=1)

        ttk.Label(form_frame, text="Notes").grid(row=3, column=0, sticky="w", padx=5)
        self.notes_entry = ttk.Entry(form_frame, width=50)
        self.notes_entry.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # Coordinate status — updated when the user clicks the map
        self._coord_label = ttk.Label(self, text="Click the map to set event coordinates")
        self._coord_label.pack(anchor='w', padx=15, pady=(0, 4))

        # Buttons
        button_frame = tk.Frame(self, bg=theme.BG)
        button_frame.pack(fill="x", padx=15, pady=(0, 8))

        ttk.Button(button_frame, text="Add Event",    command=self.add_event).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Delete Event", command=self.delete_event).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Reload Map",   command=self.reload_map,
                   style='Accent.TButton').pack(side="left", padx=4)

        # Map with 1px border
        map_container = tk.Frame(self, bg=theme.BORDER)
        map_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.map_frame = EventMap(map_container, on_location_selected=self.on_map_location_selected, bg=theme.BG)
        self.map_frame.pack(fill="both", expand=True, padx=1, pady=1)

    def _make_field(self, parent, label, row, col=0, width=25):
        ttk.Label(parent, text=label).grid(row=row, column=col * 2, sticky="w", padx=5, pady=3)
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=col * 2 + 1, padx=5, pady=3)
        return entry

    def add_event(self):
        try:
            event_data = {
                "event_id": self.event_id_entry.get().strip(),
                "title":    self.title_entry.get().strip(),
                "date":     self.date_entry.get().strip(),
                "time":     self.time_entry.get().strip(),
                "location": self.location_entry.get().strip(),
                "address":  self.address_entry.get().strip(),
                "lat":      self._lat,
                "lon":      self._lon,
                "notes":    self.notes_entry.get().strip(),
                "owner_id": str(self.current_user.get("user_id", "")),
            }

            required_fields = [
                event_data["event_id"], event_data["title"],
                event_data["date"],     event_data["time"],
                event_data["location"], event_data["address"],
                event_data["lat"],      event_data["lon"],
            ]

            if not all(required_fields):
                messagebox.showerror(
                    "Input Error",
                    "Please fill in all fields and click the map to set a location."
                )
                return

            existing_ids = {e["event_id"] for e in self.event_service.get_all_events()}
            if event_data["event_id"] in existing_ids:
                messagebox.showerror("Input Error", f"Event ID '{event_data['event_id']}' already exists.")
                return

            float(event_data["lat"])
            float(event_data["lon"])

            self.event_service.create_event(event_data)
            self.reload_map()
            self.clear_form()
            messagebox.showinfo("Success", "Event added successfully.")

        except ValueError:
            messagebox.showerror("Input Error", "Invalid coordinates — please click a point on the map.")

    def delete_event(self):
        event_id = self.event_id_entry.get().strip()
        if not event_id:
            messagebox.showerror("Input Error", "Enter an Event ID to delete.")
            return

        success, message = self.event_service.delete_event(event_id, self.current_user)
        if not success:
            messagebox.showerror("Delete Failed", message)
            return

        self.reload_map()
        self.clear_form()
        messagebox.showinfo("Success", message)

    def reload_map(self):
        self.map_frame.load_events_from_csv()

    def on_map_location_selected(self, lat, lon):
        self._lat = f"{lat:.6f}"
        self._lon = f"{lon:.6f}"
        self._coord_label.config(text=f"Coordinates set: {self._lat}, {self._lon}")
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, "Map Selected Point")

    def clear_form(self):
        for entry in (
            self.event_id_entry, self.title_entry, self.date_entry,
            self.time_entry, self.location_entry, self.address_entry,
            self.notes_entry,
        ):
            entry.delete(0, tk.END)
        self._lat = ""
        self._lon = ""
        self._coord_label.config(text="Click the map to set event coordinates")
