import csv


CSV_HEADERS = [
	"event_id",
	"title",
	"date",
	"time",
	"location_name",
	"address",
	"lat",
	"lon",
	"notes",
]


def _read_events(csv_path):
	with open(csv_path, "r", newline="", encoding="utf-8") as f:
		return list(csv.DictReader(f))


def _write_events(csv_path, events):
	with open(csv_path, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
		writer.writeheader()
		writer.writerows(events)


def add_event(csv_path, event):
	events = _read_events(csv_path)
	events.append({key: str(event.get(key, "")) for key in CSV_HEADERS})
	_write_events(csv_path, events)


def remove_event(csv_path, event_id):
	events = _read_events(csv_path)
	updated = [e for e in events if e["event_id"] != str(event_id)]
	_write_events(csv_path, updated)


def edit_event(csv_path, event_id, updates):
	events = _read_events(csv_path)
	for event in events:
		if event["event_id"] == str(event_id):
			for key, value in updates.items():
				if key in CSV_HEADERS:
					event[key] = str(value)
			break
	_write_events(csv_path, events)
