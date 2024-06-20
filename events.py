# events.py
import json

class EventTracker:
    def __init__(self, filepath='events_log.json'):
        self.filepath = filepath
        self.events = []
        self.load_events()

    def log_event(self, event):
        self.events.append(event)
        self.save_events()

    def save_events(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.events, file)

    def load_events(self):
        try:
            with open(self.filepath, 'r') as file:
                self.events = json.load(file)
        except FileNotFoundError:
            self.events = []

    def get_previous_state(self):
        if self.events:
            return self.events[-1]
        return None

    def reset_events(self):
        self.events = []
        self.save_events()
