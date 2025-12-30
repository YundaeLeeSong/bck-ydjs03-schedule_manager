import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout, QPushButton, QListWidget, QFileDialog, QWidget, QStackedWidget
from PyPDF2 import PdfMerger

class MainMenu(QWidget):
    """
    The main menu widget providing options to merge, split, and exit the application.

    Methods
    -------
    show_merge_window()
        Switches the view to the PDF merger window.
    """
    def __init__(self, parent=None):
        """
        Constructs all the necessary attributes for the MainMenu object.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget (default is None).
        """
        super(MainMenu, self).__init__(parent)
        
        # Main widget and layout
        self.layout = QGridLayout(self)
        
        # Buttons for different functionalities
        self.merge_button = QPushButton('Merge PDF')
        self.merge_button.clicked.connect(self.show_merge_window)
        self.layout.addWidget(self.merge_button, 0, 0, Qt.AlignVCenter | Qt.AlignHCenter)
        
        self.split_button = QPushButton('Split PDF')
        self.layout.addWidget(self.split_button, 1, 0, Qt.AlignVCenter | Qt.AlignHCenter)
        
        self.exit_button = QPushButton('Exit')
        self.exit_button.setObjectName('exitButton')  # Set object name
        self.exit_button.clicked.connect(QApplication.instance().quit)  # Ensure the application exits
        self.layout.addWidget(self.exit_button, 2, 1, Qt.AlignVCenter | Qt.AlignRight) 
        # Qt.AlignTop / Qt.AlignBottom / Qt.AlignVCenter
        # Qt.AlignLeft / Qt.AlignRight / Qt.AlignHCenter
        
        self.setStyleSheet(open('style.css').read())

    def show_merge_window(self):
        """
        Switches the view to the PDF merger window and updates the window title.
        """
        self.parentWidget().setCurrentIndex(1)
        self.parentWidget().parentWidget().setWindowTitle('PDF_merge')  # Update title

class PDFMergerApp(QWidget):
    """
    The PDF merger application widget for selecting and merging PDF files.

    Methods
    -------
    select_pdfs()
        Opens a file dialog to select PDF files.
    merge_pdfs()
        Merges the selected PDF files into a single PDF.
    reset_pdfs()
        Clears the list of selected PDF files.
    show_main_menu()
        Switches the view back to the main menu.
    """
    def __init__(self, parent=None):
        """
        Constructs all the necessary attributes for the PDFMergerApp object.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget (default is None).
        """
        super(PDFMergerApp, self).__init__(parent)
        
        # Main widget and layout
        self.layout = QGridLayout(self)
        
        # Button to go back to the main menu
        self.back_button = QPushButton('Back')
        self.back_button.setObjectName('backButton')  # Set object name
        self.back_button.clicked.connect(self.show_main_menu)
        self.layout.addWidget(self.back_button, 0, 0)
        
        # List widget to show selected PDF files
        self.pdf_list = QListWidget()
        self.pdf_list.setSelectionMode(QListWidget.MultiSelection)
        self.pdf_list.setDragDropMode(QListWidget.InternalMove)
        self.layout.addWidget(self.pdf_list, 1, 0, 1, 2)
        
        # Button to select PDF files
        self.select_button = QPushButton('Select PDF Files')
        self.select_button.clicked.connect(self.select_pdfs)
        self.layout.addWidget(self.select_button, 2, 0)
        
        # Button to merge PDF files
        self.merge_button = QPushButton('Merge PDF Files')
        self.merge_button.clicked.connect(self.merge_pdfs)
        self.layout.addWidget(self.merge_button, 2, 1)
        
        # Button to reset selected files
        self.reset_button = QPushButton('Reset Selected Files')
        self.reset_button.clicked.connect(self.reset_pdfs)
        self.layout.addWidget(self.reset_button, 3, 0, 1, 2)
        
        self.setStyleSheet(open('style.css').read())

    def select_pdfs(self):
        """
        Opens a file dialog to select PDF files and adds them to the list widget.
        """
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)", options=options)
        if files:
            for file in files:
                self.pdf_list.addItem(file)

    def merge_pdfs(self):
        """
        Merges the selected PDF files into a single PDF file named 'merged_pdf.pdf'.
        """
        merger = PdfMerger()
        for index in range(self.pdf_list.count()):
            merger.append(self.pdf_list.item(index).text())
        merger.write("merged_pdf.pdf")
        merger.close()

    def reset_pdfs(self):
        """
        Clears the list of selected PDF files.
        """
        self.pdf_list.clear()
    
    def show_main_menu(self):
        """
        Switches the view back to the main menu and updates the window title.
        """
        self.parentWidget().setCurrentIndex(0)
        self.parentWidget().parentWidget().setWindowTitle('PDF_manager')  # Update title
        self.pdf_list.clear()

class MainApp(QMainWindow):
    """
    The main application window that manages the stacked widget containing the main menu and the PDF merger application.

    Methods
    -------
    update_window(title, width, height)
        Updates the window title and size.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the MainApp object.
        """
        super().__init__()
        self.setWindowTitle('PDF_manager')

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.main_menu = MainMenu(self.stacked_widget)
        self.pdf_merger_app = PDFMergerApp(self.stacked_widget)
        
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.pdf_merger_app)

    def update_window(self, title, width, height):
        """
        Updates the window title and size.

        Parameters
        ----------
        title : str
            The new window title.
        width : int
            The new window width.
        height : int
            The new window height.
        """
        self.setWindowTitle(title)
        self.setFixedSize(width, height)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
