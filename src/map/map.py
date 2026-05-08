# tkinter is used here so EventMap can be a Frame (a panel inside the main window)
import tkinter as tk
# TkinterMapView is a third-party widget that shows an interactive map
from tkintermapview import TkinterMapView
# We need EventService to load events from the CSV so we can place pins on the map
from src.services.event_service import EventService


# EventMap is a custom widget that displays the map and plots event markers on it.
# It inherits from tk.Frame so it can be embedded inside the main window like any other widget.
class EventMap(tk.Frame):

    # parent is the window or frame that this map will sit inside
    def __init__(self, parent, on_location_selected=None):
        # Initialise the Frame so it's ready to hold other widgets
        super().__init__(parent)

        # Create an EventService so we can load events from the CSV
        self.event_service = EventService()
        # Keep track of all the markers currently on the map so we can remove them later
        self.markers = []
        # Stores the temporary marker created when the user clicks on the map
        self.selected_location_marker = None
        # Optional callback to send clicked coordinates back to the parent UI
        self.on_location_selected = on_location_selected

        # Create the actual interactive map widget and place it inside this frame
        self.map_widget = TkinterMapView(self, width=700, height=500)
        self.map_widget.pack(fill="both", expand=True)

        # Use CartoDB Positron — clean, minimal Apple Maps-style appearance
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png")
        # Centre the map on the UK when it first loads (lat 54.5, lon -2.5)
        self.map_widget.set_position(54.5, -2.5)
        # Zoom level 6 shows the whole of the UK
        self.map_widget.set_zoom(6)

        # Enable clicking anywhere on the map to choose coordinates for a new event
        self.map_widget.add_left_click_map_command(self.handle_map_click)

        # Load and display any events already saved in the CSV
        self.load_events_from_csv()

    # Called when the user clicks on any point on the map.
    # Coordinates are sent to the parent callback and shown with a temporary marker.
    def handle_map_click(self, coordinates):
        lat, lon = coordinates

        # Replace the previous temporary "selected location" marker if it exists
        if self.selected_location_marker is not None:
            self.selected_location_marker.delete()

        self.selected_location_marker = self.map_widget.set_marker(
            lat,
            lon,
            text="Selected location for new event"
        )

        # Send coordinates back to the main window if a callback was provided
        if self.on_location_selected:
            self.on_location_selected(lat, lon)

    # Removes all existing pins/markers from the map.
    # Called before reloading events so we don't end up with duplicate markers.
    def clear_markers(self):
        for marker in self.markers:
            marker.delete()  # Tell the map widget to remove this marker visually
        self.markers = []    # Reset our list to empty

    # Reads all events from the CSV and plots a pin on the map for each one.
    def load_events_from_csv(self):
        # Remove any pins already on the map before adding fresh ones
        self.clear_markers()

        # Get the full list of events from the CSV file
        events = self.event_service.get_all_events()

        for event in events:
            try:
                # Convert the lat/lon strings from the CSV into decimal numbers
                lat = float(event["lat"])
                lon = float(event["lon"])

                # Build the text that will appear when a user clicks the marker.
                # f-strings (f"...") let us insert variable values directly into a string.
                marker_text = (
                    f"{event['title']}\n"
                    f"Date: {event['date']}\n"
                    f"Time: {event['time']}\n"
                    f"Location: {event['location']}\n"
                    f"Address: {event['address']}\n"
                    f"Notes: {event['notes']}"
                )

                # Place a marker pin at the given coordinates with a click handler.
                # Clicking the marker opens a popup with full details and a mini map.
                marker = self.map_widget.set_marker(
                    lat,
                    lon,
                    text=marker_text,
                    command=lambda _marker=None, event=event, lat=lat, lon=lon: self.open_event_popup(event, lat, lon)
                )
                # Save a reference to the marker so clear_markers() can remove it later
                self.markers.append(marker)

            except (ValueError, KeyError):
                # If a row in the CSV has a missing or non-numeric lat/lon, skip it
                # and print a warning to the terminal instead of crashing
                print(f"Skipping bad event row: {event}")

    # Opens a new window showing full event details and a mini map focused on the event.
    def open_event_popup(self, event, lat, lon):
        popup = tk.Toplevel(self)
        popup.title(event.get("title", "Event Details"))
        popup.geometry("500x560")
        popup.transient(self.winfo_toplevel())

        content = tk.Frame(popup)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(
            content,
            text=event.get("title", "Untitled Event"),
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 8))

        details = [
            ("Event ID", event.get("event_id", "")),
            ("Date", event.get("date", "")),
            ("Time", event.get("time", "")),
            ("Location", event.get("location", "")),
            ("Address", event.get("address", "")),
            ("Latitude", str(lat)),
            ("Longitude", str(lon)),
            ("Notes", event.get("notes", "")),
        ]

        for label, value in details:
            tk.Label(
                content,
                text=f"{label}: {value}",
                anchor="w",
                justify="left",
                wraplength=460
            ).pack(fill="x", pady=2)

        tk.Label(content, text="Mini Map", font=("Arial", 11, "bold"), anchor="w").pack(fill="x", pady=(12, 6))

        mini_map = TkinterMapView(content, width=460, height=260)
        mini_map.pack(fill="x")
        mini_map.set_tile_server("https://a.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png")
        mini_map.set_position(lat, lon)
        mini_map.set_zoom(14)
        mini_map.set_marker(lat, lon, text=event.get("title", "Event"))

        tk.Button(content, text="Close", command=popup.destroy).pack(anchor="e", pady=(10, 0))