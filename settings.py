# settings.py
import json

class Settings:
    def __init__(self, filepath='settings.json'):
        self.filepath = filepath
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_settings(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.settings, file)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_setting(self, key):
        return self.settings.get(key, None)
