"""
Preset Manager for ChronoFlow Timer.
Handles built-in presets and persistent custom presets saved in JSON.
"""

import json
import os

DEFAULT_PRESETS = [
    {"name": "Deep Focus", "hours": 0, "minutes": 25, "seconds": 0, "builtin": True},
    {"name": "Quick Break", "hours": 0, "minutes": 5, "seconds": 0, "builtin": True},
    {"name": "Power Nap", "hours": 0, "minutes": 20, "seconds": 0, "builtin": True},
    {"name": "Power Hour", "hours": 1, "minutes": 0, "seconds": 0, "builtin": True},
    {"name": "Quick Standup", "hours": 0, "minutes": 15, "seconds": 0, "builtin": True},
    {"name": "Meditation", "hours": 0, "minutes": 10, "seconds": 0, "builtin": True},
    {"name": "Tea Brewing", "hours": 0, "minutes": 3, "seconds": 0, "builtin": True},
    {"name": "Boiled Eggs", "hours": 0, "minutes": 8, "seconds": 0, "builtin": True},
    {"name": "HIIT Interval", "hours": 0, "minutes": 0, "seconds": 45, "builtin": True},
]

class PresetManager:
    def __init__(self, filename="presets.json"):
        self.filepath = os.path.join(os.path.dirname(__file__), filename)
        self.presets = []
        self.load_presets()

    def load_presets(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.presets = json.load(f)
            except Exception as e:
                print(f"Error loading presets: {e}")
                self.presets = list(DEFAULT_PRESETS)
        else:
            self.presets = list(DEFAULT_PRESETS)
            self.save_presets()

    def save_presets(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            print(f"Error saving presets: {e}")

    def add_preset(self, name, hours, minutes, seconds):
        if not name.strip():
            name = f"{hours:02d}:{minutes:02d}:{seconds:02d} Timer"
        new_item = {
            "name": name.strip(),
            "hours": int(hours),
            "minutes": int(minutes),
            "seconds": int(seconds),
            "builtin": False
        }
        self.presets.append(new_item)
        self.save_presets()
        return new_item

    def delete_preset(self, index):
        if 0 <= index < len(self.presets):
            del self.presets[index]
            self.save_presets()

    def get_presets(self):
        return self.presets
