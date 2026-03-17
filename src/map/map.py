import tkinter as tk
from tkintermapview import TkinterMapView

root = tk.Tk()
root.title("Event Manager Map")
root.geometry("800x600")

map_widget = TkinterMapView(root, width=800, height=600)
map_widget.pack(fill="both", expand=True)

# Set the map location first
map_widget.set_position(51.5074, -0.1278)  # London
map_widget.set_zoom(12)

# Add a marker
marker = map_widget.set_marker(51.5074, -0.1278, text="London Event")

# Force map to center on the marker
map_widget.set_position(marker.position[0], marker.position[1])

root.mainloop()