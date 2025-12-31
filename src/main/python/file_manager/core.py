# file_manager/core.py
import json
import os
import sys
from pathlib import Path

class FileManager:
    _instance = None
    _resources_dir = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FileManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize paths to resources."""
        # Resources directory is expected to be at the execution location (current working directory)
        self._resources_dir = Path.cwd() / "resources"
        
        # Ensure directories exist
        (self._resources_dir / "schedules").mkdir(parents=True, exist_ok=True)
        (self._resources_dir / "students").mkdir(parents=True, exist_ok=True)
        (self._resources_dir / "templates").mkdir(parents=True, exist_ok=True)

        self.schedules_path = self._resources_dir / "schedules" / "data.json"
        self.students_path = self._resources_dir / "students" / "data.json"
        self.templates_dir = self._resources_dir / "templates"

    def load_template(self, filename="gmail.html"):
        """Load an HTML template."""
        path = self.templates_dir / filename
        if not path.exists():
            return ""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except IOError:
            return ""

    def load_schedules(self):
        """Load schedules from JSON."""
        if not self.schedules_path.exists():
            return []
        try:
            with open(self.schedules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_schedules(self, data):
        """Save schedules to JSON."""
        with open(self.schedules_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_students(self):
        """Load students from JSON."""
        if not self.students_path.exists():
            return []
        try:
            with open(self.students_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_students(self, data):
        """Save students to JSON."""
        with open(self.students_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_export_path(self, filename="schedule.ics"):
        """Get a path for exporting files (usually in a downloads folder or similar)."""
        # For simplicity, let's use the current working directory or a 'downloads' folder
        export_dir = Path.cwd() / "downloads"
        export_dir.mkdir(exist_ok=True)
        return export_dir / filename
