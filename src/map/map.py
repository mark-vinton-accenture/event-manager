import os
import tkinter as tk
from tkintermapview import TkinterMapView
from src.services.event_service import EventService
from src.gui import theme

DARK_TILES = "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
TILE_CACHE = os.path.join(os.path.dirname(__file__), '..', '..', 'map_tiles.db')


class EventMap(tk.Frame):

    def __init__(self, parent, on_location_selected=None, bg=None):
        super().__init__(parent, bg=bg or theme.BG)

        self.event_service = EventService()
        self.markers = []
        self.selected_location_marker = None
        self.on_location_selected = on_location_selected

        self.map_widget = TkinterMapView(self, width=700, height=500, database_path=TILE_CACHE)
        self.map_widget.pack(fill="both", expand=True)

        self.map_widget.set_tile_server(DARK_TILES)
        self.map_widget.set_position(54.5, -2.5)
        self.map_widget.set_zoom(6)

        self.map_widget.add_left_click_map_command(self.handle_map_click)

        self.load_events_from_csv()

    def handle_map_click(self, coordinates):
        lat, lon = coordinates

        if self.selected_location_marker is not None:
            self.selected_location_marker.delete()

        self.selected_location_marker = self.map_widget.set_marker(
            lat, lon, text="Selected location for new event",
            text_color=theme.SUCCESS, marker_color_circle=theme.SUCCESS,
        )

        if self.on_location_selected:
            self.on_location_selected(lat, lon)

    def clear_markers(self):
        for marker in self.markers:
            marker.delete()
        self.markers = []

    def load_events_from_csv(self):
        self.clear_markers()
        events = self.event_service.get_all_events()

        for event in events:
            try:
                lat = float(event["lat"])
                lon = float(event["lon"])

                marker_text = (
                    f"{event['title']}\n"
                    f"Date: {event['date']}\n"
                    f"Time: {event['time']}\n"
                    f"Location: {event['location']}\n"
                    f"Address: {event['address']}\n"
                    f"Notes: {event['notes']}"
                )

                marker = self.map_widget.set_marker(
                    lat, lon,
                    text=marker_text,
                    text_color=theme.ACCENT,
                    marker_color_circle=theme.PRIMARY,
                    command=lambda _marker=None, event=event, lat=lat, lon=lon:
                        self.open_event_popup(event, lat, lon)
                )
                self.markers.append(marker)

            except (ValueError, KeyError):
                print(f"Skipping bad event row: {event}")

    def open_event_popup(self, event, lat, lon):
        popup = tk.Toplevel(self)
        popup.title(event.get("title", "Event Details"))
        popup.geometry("500x560")
        popup.configure(bg=theme.BG)
        popup.transient(self.winfo_toplevel())

        # Popup header
        header = tk.Frame(popup, bg=theme.PANEL)
        header.pack(fill='x')
        tk.Label(
            header,
            text=event.get("title", "Untitled Event"),
            font=(theme.FONT, 14, 'bold'),
            bg=theme.PANEL,
            fg=theme.ACCENT,
            anchor='w',
        ).pack(fill='x', padx=12, pady=10)
        tk.Frame(popup, bg=theme.BORDER, height=1).pack(fill='x')

        content = tk.Frame(popup, bg=theme.BG)
        content.pack(fill="both", expand=True, padx=12, pady=10)

        details = [
            ("Event ID", event.get("event_id", "")),
            ("Date",     event.get("date", "")),
            ("Time",     event.get("time", "")),
            ("Location", event.get("location", "")),
            ("Address",  event.get("address", "")),
            ("Latitude", str(lat)),
            ("Longitude", str(lon)),
            ("Notes",    event.get("notes", "")),
        ]

        for label, value in details:
            row = tk.Frame(content, bg=theme.BG)
            row.pack(fill='x', pady=1)
            tk.Label(row, text=f"{label}:", width=10, anchor='w',
                     bg=theme.BG, fg=theme.LABEL,
                     font=(theme.FONT, 9, 'bold')).pack(side='left')
            tk.Label(row, text=value, anchor='w', justify='left',
                     wraplength=360, bg=theme.BG, fg=theme.TEXT,
                     font=(theme.FONT, 9)).pack(side='left')

        tk.Label(content, text="Location Preview",
                 font=(theme.FONT, 10, 'bold'),
                 bg=theme.BG, fg=theme.LABEL, anchor='w').pack(fill='x', pady=(10, 4))

        mini_map = TkinterMapView(content, width=460, height=220, database_path=TILE_CACHE)
        mini_map.pack(fill='x')
        mini_map.set_tile_server(DARK_TILES)
        mini_map.set_position(lat, lon)
        mini_map.set_zoom(14)
        mini_map.set_marker(lat, lon, text=event.get("title", "Event"))

        tk.Button(
            content, text="Close", command=popup.destroy,
            bg=theme.PRIMARY, fg='white', relief='flat',
            font=(theme.FONT, 9), padx=12, pady=4,
            activebackground='#1976D2', activeforeground='white', cursor='hand2',
        ).pack(anchor='e', pady=(8, 0))
