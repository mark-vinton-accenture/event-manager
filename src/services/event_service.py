# csv is a built-in Python module for reading and writing CSV (comma-separated values) files
import csv
# os lets us work with the file system, e.g. checking if a file exists
import os


# EventService handles all the data logic — reading, saving, updating and deleting events.
# Keeping this separate from the GUI means the window code stays clean and simple.
class EventService:

    # csv_path is the location of the CSV file. If none is provided we use the default path.
    def __init__(self, csv_path=None):
        if csv_path is None:
            # os.path.join builds the path correctly for any operating system
            self.csv_path = os.path.join("src", "data", "events.csv")
        else:
            self.csv_path = csv_path
        
        # CACHING: Store the event list in memory so we don't re-read the CSV every time.
        # Initialize it as None so we know we haven't loaded it yet.
        self._cached_events = None

    # Reads every event from the CSV file and returns them as a list of dictionaries.
    # Each dictionary has keys like "title", "date", "lat" etc. matching the CSV columns.
    # CACHING: Returns the cached list if available, otherwise reads from disk.
    def get_all_events(self):
        # If we've already loaded the events into memory, return them right away (super fast!)
        if self._cached_events is not None:
            return self._cached_events
        
        events = []

        # If the file doesn't exist yet there are no events to return
        if not os.path.exists(self.csv_path):
            self._cached_events = events  # Cache the empty list
            return events

        # Open the file in read mode
        with open(self.csv_path, mode="r", newline="", encoding="utf-8") as file:
            # DictReader reads each row as a dictionary using the header row as keys
            reader = csv.DictReader(file)
            for row in reader:
                events.append(row)

        # CACHING: Store the result in memory for next time
        self._cached_events = events
        return events

    # Adds a new event to the CSV file.
    # event_data is a dictionary with all the event fields.
    def create_event(self, event_data):
        # Check if the file already exists before we open it
        file_exists = os.path.exists(self.csv_path)

        # Open the file in append mode ("a") so we add to the end rather than overwrite it
        with open(self.csv_path, mode="a", newline="", encoding="utf-8") as file:
            # fieldnames defines the order of columns in the CSV
            fieldnames = [
                "event_id",
                "title",
                "date",
                "time",
                "location",
                "address",
                "lat",
                "lon",
                "notes",
                "owner_id",
            ]

            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Only write the header row (event_id, title, date ...) if the file is brand new or empty
            if not file_exists or os.path.getsize(self.csv_path) == 0:
                writer.writeheader()

            # Write the new event as a row in the CSV
            writer.writerow(event_data)
        
        # CACHING: Invalidate the cache since we just modified the CSV
        self._invalidate_cache()

    # Removes the event with the given event_id from the CSV file.
    def delete_event(self, event_id, current_user):
        # Load all events into memory
        events = self.get_all_events()

        # Find the event and check if the current user is allowed to delete it.
        target_event = next((event for event in events if event["event_id"] == str(event_id)), None)
        if target_event is None:
            return False, "Event not found."

        is_admin = current_user.get("role") == "admin"
        is_owner = target_event.get("owner_id", "") == str(current_user.get("user_id", ""))

        if not is_admin and not is_owner:
            return False, "You can only delete your own events."

        # Keep every event EXCEPT the one we want to delete.
        # This is a list comprehension — a compact way to filter a list.
        updated_events = [event for event in events if event["event_id"] != str(event_id)]

        # Write the filtered list back to the file (replacing the old contents)
        self._rewrite_csv(updated_events)
        
        # CACHING: Invalidate the cache since we just deleted an event
        self._invalidate_cache()
        return True, "Event deleted successfully."

    # Updates an existing event's details.
    # updated_event_data is a dictionary containing only the fields you want to change.
    def update_event(self, event_id, updated_event_data):
        events = self.get_all_events()

        # Find the event with the matching ID and overwrite its fields
        for event in events:
            if event["event_id"] == str(event_id):
                event.update(updated_event_data)  # dict.update() merges the new values in

        self._rewrite_csv(events)
        
        # CACHING: Invalidate the cache since we just updated an event
        self._invalidate_cache()

    # Private helper to clear the cache.
    # Call this whenever the CSV file is modified so the next get_all_events() re-reads from disk.
    def _invalidate_cache(self):
        self._cached_events = None

    # Private helper method (the _ prefix is a convention meaning "don't call this from outside").
    # Completely overwrites the CSV file with the provided list of events.
    # Used by delete_event and update_event after they modify the in-memory list.
    def _rewrite_csv(self, events):
        # Open in write mode ("w") which clears the file first
        with open(self.csv_path, mode="w", newline="", encoding="utf-8") as file:
            fieldnames = [
                "event_id",
                "title",
                "date",
                "time",
                "location",
                "address",
                "lat",
                "lon",
                "notes",
                "owner_id",
            ]

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()        # Write the column header row
            writer.writerows(events)    # Write all the event rows
        
        # CACHING: Update the in-memory cache with the new data
        self._cached_events = events