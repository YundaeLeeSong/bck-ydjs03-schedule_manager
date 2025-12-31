# app.py

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QIcon

from .view_welcome import ViewWelcome
from .view_student_manager import ViewStudentManager
from .view_schedule_manager import ViewScheduleManager

class StageMain(QMainWindow):
    """
    Main application window managing navigation.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutoring Scheduler App")
        self.setMinimumSize(1200, 980)

        # "scene" holds and manage transitions btw views.
        self.scene = QStackedWidget()
        self.setCentralWidget(self.scene)

        self.welcome_page = ViewWelcome(
            on_start=self.go_to_schedule, 
            on_quit=self.close
        )
        self.schedule_page = ViewScheduleManager(
            on_back=self.go_to_welcome,
            on_go_students=self.go_to_students
        )
        self.student_page = ViewStudentManager(
            on_back=self.go_to_schedule
        )

        self.scene.addWidget(self.welcome_page)
        self.scene.addWidget(self.schedule_page)
        self.scene.addWidget(self.student_page)
        self.scene.setCurrentWidget(self.welcome_page)

    def go_to_schedule(self):
        """Navigate to the schedule page."""
        self.schedule_page.refresh_data()
        self.scene.setCurrentWidget(self.schedule_page)

    def go_to_welcome(self):
        """Navigate to the welcome page."""
        self.scene.setCurrentWidget(self.welcome_page)

    def go_to_students(self):
        """Navigate to the student management page."""
        self.student_page.refresh_data()
        self.scene.setCurrentWidget(self.student_page)

def main():
    """
    Application entry point.
    """
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QPushButton { padding: 8px; font-size: 20px; }
        QLabel { font-size: 20px; }
        QTableWidget { font-size: 20px; }
        QLineEdit { font-size: 20px; }
        QTextEdit { font-size: 20px; }
        QListWidget { font-size: 20px; }
        QCheckBox { font-size: 20px; }
        QSpinBox { font-size: 20px; }
        QDateTimeEdit { font-size: 20px; }
    """)
    window = StageMain()
    window.show()
    sys.exit(app.exec())