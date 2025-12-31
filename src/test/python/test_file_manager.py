#!/usr/bin/env python3
"""
test_file_manager.py — Unit tests for file_manager.core

Run with:
    python runner.py test
"""

import unittest
import shutil
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from file_manager import FileManager

class TestFileManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for resources
        self.test_dir = tempfile.mkdtemp()
        self.patcher = patch("pathlib.Path.cwd", return_value=Path(self.test_dir))
        self.mock_cwd = self.patcher.start()
        
        # Reset Singleton
        FileManager._instance = None
        self.fm = FileManager()

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir)
        FileManager._instance = None

    def test_singleton(self):
        fm2 = FileManager()
        self.assertIs(self.fm, fm2)

    def test_initialization_creates_directories(self):
        resources = Path(self.test_dir) / "resources"
        self.assertTrue((resources / "schedules").exists())
        self.assertTrue((resources / "students").exists())
        self.assertTrue((resources / "templates").exists())

    def test_load_save_schedules(self):
        data = [{"name": "Test", "time": "2025-01-01 10:00"}]
        self.fm.save_schedules(data)
        
        loaded = self.fm.load_schedules()
        self.assertEqual(loaded, data)

    def test_load_schedules_empty(self):
        # Remove file if exists (though it shouldn't yet)
        if self.fm.schedules_path.exists():
            self.fm.schedules_path.unlink()
        
        self.assertEqual(self.fm.load_schedules(), [])

    def test_load_save_students(self):
        data = [{"name": "Student A", "email": "a@example.com"}]
        self.fm.save_students(data)
        
        loaded = self.fm.load_students()
        self.assertEqual(loaded, data)

    def test_load_template(self):
        template_content = "<html>{{DATA}}</html>"
        template_path = self.fm.templates_dir / "test.html"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)
            
        loaded = self.fm.load_template("test.html")
        self.assertEqual(loaded, template_content)

    def test_load_template_missing(self):
        loaded = self.fm.load_template("missing.html")
        self.assertEqual(loaded, "")

    def test_get_export_path(self):
        path = self.fm.get_export_path("export.txt")
        self.assertEqual(path.name, "export.txt")
        self.assertTrue(path.parent.exists())
        self.assertEqual(path.parent.name, "downloads")

if __name__ == "__main__":
    unittest.main()
