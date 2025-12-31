# file_manager/core.py
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

class FileManager:
    """
    Singleton class to manage file operations for schedules, students, and templates.
    
    This class handles loading and saving JSON data, ensuring resource directories exist,
    and providing paths for exports.
    """
    _instance = None
    _resources_dir = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FileManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initialize paths to resources.
        
        Creates necessary directories for schedules, students, and templates relative
        to the current working directory.
        """
        # Resources directory is expected to be at the execution location (current working directory)
        self._resources_dir = Path.cwd() / "resources"
        
        # Ensure directories exist
        (self._resources_dir / "schedules").mkdir(parents=True, exist_ok=True)
        (self._resources_dir / "students").mkdir(parents=True, exist_ok=True)
        (self._resources_dir / "templates").mkdir(parents=True, exist_ok=True)

        self.schedules_path = self._resources_dir / "schedules" / "data.json"
        self.students_path = self._resources_dir / "students" / "data.json"
        self.templates_dir = self._resources_dir / "templates"

    def load_template(self, filename: str = "gmail.html") -> str:
        """
        Load an HTML template from the templates directory.

        Args:
            filename (str): The name of the template file. Defaults to "gmail.html".

        Returns:
            str: The content of the template file, or an empty string if not found or on error.
        """
        path = self.templates_dir / filename
        if not path.exists():
            return ""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except IOError:
            return ""

    def load_schedules(self) -> List[Dict[str, Any]]:
        """
        Load schedules from the JSON data file.

        Returns:
            List[Dict[str, Any]]: A list of schedule dictionaries. Returns empty list on error or if file missing.
        """
        if not self.schedules_path.exists():
            return []
        try:
            with open(self.schedules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_schedules(self, data: List[Dict[str, Any]]) -> None:
        """
        Save schedules to the JSON data file.

        Args:
            data (List[Dict[str, Any]]): The list of schedule dictionaries to save.
        """
        with open(self.schedules_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_students(self) -> List[Dict[str, Any]]:
        """
        Load students from the JSON data file.

        Returns:
            List[Dict[str, Any]]: A list of student dictionaries. Returns empty list on error or if file missing.
        """
        if not self.students_path.exists():
            return []
        try:
            with open(self.students_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_students(self, data: List[Dict[str, Any]]) -> None:
        """
        Save students to the JSON data file.

        Args:
            data (List[Dict[str, Any]]): The list of student dictionaries to save.
        """
        with open(self.students_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_export_path(self, filename: str = "schedule.ics") -> Path:
        """
        Get a path for exporting files.
        
        Creates a 'downloads' directory in the current working directory if it doesn't exist.

        Args:
            filename (str): The name of the export file. Defaults to "schedule.ics".

        Returns:
            Path: The full path to the export file.
        """
        # For simplicity, let's use the current working directory or a 'downloads' folder
        export_dir = Path.cwd() / "downloads"
        export_dir.mkdir(exist_ok=True)
        return export_dir / filename