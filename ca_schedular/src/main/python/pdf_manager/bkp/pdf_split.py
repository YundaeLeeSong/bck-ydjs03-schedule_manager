import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout, QPushButton, QListWidget, QFileDialog, QWidget, QLineEdit, QLabel, QHBoxLayout, QStackedWidget
from PyPDF2 import PdfReader, PdfWriter


class PDFSplitApp(QWidget):
    """
    The PDF split application widget for selecting and splitting PDF files.
    """
    def __init__(self, parent=None):
        super(PDFSplitApp, self).__init__(parent)
        self.pdf_file = None

        self.layout = QVBoxLayout(self)
        self.split_ranges = []

        # Back button
        self.back_button = QPushButton('Back')
        self.back_button.setObjectName('backButton')
        self.back_button.clicked.connect(self.show_main_menu)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        # Display for selected PDF file
        self.selected_file_label = QLabel('No file selected')
        self.layout.addWidget(self.selected_file_label, alignment=Qt.AlignCenter)

        # Button to select PDF file
        self.select_button = QPushButton('Select PDF File')
        self.select_button.clicked.connect(self.select_pdf)
        self.layout.addWidget(self.select_button, alignment=Qt.AlignCenter)

        # Layout for split page ranges
        self.split_layout = QVBoxLayout()
        self.layout.addLayout(self.split_layout)

        # Button to add split range
        self.add_split_button = QPushButton('+')
        self.add_split_button.clicked.connect(self.add_split_range)
        self.layout.addWidget(self.add_split_button, alignment=Qt.AlignCenter)

        # Button to generate split PDF files
        self.split_button = QPushButton('Split PDF File')
        self.split_button.clicked.connect(self.split_pdf)
        self.layout.addWidget(self.split_button, alignment=Qt.AlignCenter)

        self.setStyleSheet(open('style.css').read())

    def show_main_menu(self):
        self.parentWidget().setCurrentIndex(0)
        self.parentWidget().parentWidget().setWindowTitle('PDF_manager')

    def select_pdf(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)", options=options)
        if file:
            self.pdf_file = file
            self.selected_file_label.setText(f'Selected file: {file}')

    def add_split_range(self):
        layout = QHBoxLayout()
        start_page = QLineEdit()
        start_page.setPlaceholderText('Start page')
        end_page = QLineEdit()
        end_page.setPlaceholderText('End page')
        layout.addWidget(start_page)
        layout.addWidget(end_page)
        self.split_ranges.append((start_page, end_page))
        self.split_layout.addLayout(layout)

    def split_pdf(self):
        if not self.pdf_file:
            return

        reader = PdfReader(self.pdf_file)
        pdf_count = 1

        for start_page, end_page in self.split_ranges:
            try:
                start = int(start_page.text())
                end = int(end_page.text())
            except ValueError:
                continue

            if start < 1 or end > len(reader.pages) or start >= end:
                continue

            writer = PdfWriter()
            for page in range(start - 1, end - 1):
                writer.add_page(reader.pages[page])

            with open(f'splitted_pdf-{pdf_count:02}.pdf', 'wb') as out_file:
                writer.write(out_file)

            pdf_count += 1

        # Write remaining pages
        if self.split_ranges:
            last_end = int(self.split_ranges[-1][1].text())
            writer = PdfWriter()
            for page in range(last_end - 1, len(reader.pages)):
                writer.add_page(reader.pages[page])

            with open(f'splitted_pdf-{pdf_count:02}.pdf', 'wb') as out_file:
                writer.write(out_file)

    def reset_splits(self):
        for layout in self.split_ranges:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                widget.setParent(None)
        self.split_ranges.clear()


class MainMenu(QWidget):
    """
    The main menu widget providing options to merge, split, and exit the application.
    """
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)

        self.layout = QVBoxLayout(self)

        self.split_button = QPushButton('Split PDF')
        self.split_button.clicked.connect(self.show_split_window)
        self.layout.addWidget(self.split_button, alignment=Qt.AlignCenter)

        self.exit_button = QPushButton('Exit')
        self.exit_button.setObjectName('exitButton')
        self.exit_button.clicked.connect(QApplication.instance().quit)
        self.layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)

        self.setStyleSheet(open('style.css').read())

    def show_split_window(self):
        self.parentWidget().setCurrentIndex(1)
        self.parentWidget().parentWidget().setWindowTitle('PDF_split')


class MainApp(QMainWindow):
    """
    The main application window that manages the stacked widget containing the main menu and the PDF splitter application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PDF_manager')

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_menu = MainMenu(self.stacked_widget)
        self.pdf_split_app = PDFSplitApp(self.stacked_widget)

        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.pdf_split_app)

        self.setFixedSize(1600, 1000)

    def update_window(self, title, width, height):
        self.setWindowTitle(title)
        self.setFixedSize(width, height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())