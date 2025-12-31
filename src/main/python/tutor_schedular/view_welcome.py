# view_welcome.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ViewWelcome(QWidget):
    """
    View for the Welcome Screen.
    """
    def __init__(self, on_start, on_quit):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Tutoring Manager")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(50)

        btn_start = QPushButton("Start")
        btn_start.setFixedSize(200, 60)
        btn_start.setFont(QFont("Arial", 14))
        btn_start.clicked.connect(on_start)
        layout.addWidget(btn_start, alignment=Qt.AlignCenter)

        layout.addSpacing(20)

        btn_quit = QPushButton("Quit")
        btn_quit.setFixedSize(200, 60)
        btn_quit.setFont(QFont("Arial", 14))
        btn_quit.clicked.connect(on_quit)
        layout.addWidget(btn_quit, alignment=Qt.AlignCenter)
