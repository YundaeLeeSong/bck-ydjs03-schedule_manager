import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QFrame, QMainWindow
from PyQt5.QtCore import Qt

class AppDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('File Dialog Example')
        self.setGeometry(100, 100, 700, 700)

        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.frame)

        self.layout = QVBoxLayout()
        self.frame.setLayout(self.layout)

        self.apps = []

        self.openFileBtn = QPushButton('Open File', self)
        self.openFileBtn.setStyleSheet("background-color: #263D42; color: white; padding: 10px 25px;")
        self.openFileBtn.clicked.connect(self.addApp)
        self.layout.addWidget(self.openFileBtn)

    def addApp(self):
        for i in reversed(range(self.layout.count())): 
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.deleteLater()

        filename, _ = QFileDialog.getOpenFileName(self, "Select file", "/", "Executables (*.exe);;All Files (*)")
        if filename:
            self.apps.append(filename)
            print(self.apps)
            for app in self.apps:
                label = QLabel(app, self)
                label.setStyleSheet("background-color: gray;")
                self.layout.addWidget(label)


def print_hi(name):
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())
    print(f'Hi, {name}')

if __name__ == '__main__':
    print_hi('PyCharm')
