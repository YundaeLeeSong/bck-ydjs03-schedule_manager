import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

def on_button_click():
    user_text = text_entry.text()
    QMessageBox.information(window, "Information", f"You entered: {user_text}")

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Simple PyQt5 App")

layout = QVBoxLayout()

label = QLabel("Enter something:")
layout.addWidget(label)

text_entry = QLineEdit()
layout.addWidget(text_entry)

button = QPushButton("Submit")
button.clicked.connect(on_button_click)
layout.addWidget(button)

window.setLayout(layout)
window.show()

sys.exit(app.exec_())
