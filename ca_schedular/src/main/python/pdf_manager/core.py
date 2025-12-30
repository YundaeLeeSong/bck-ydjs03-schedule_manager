# pdf_manager/core.py
import sys
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QStackedWidget, QGridLayout, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QComboBox
)
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from pdf_manager.endorser import endorse_pdf

# Style constants
STYLE = {
    'BUTTON': """
        QPushButton {
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            min-width: 200px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """,
    'TITLE': """
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #333;
    """,
    'SUBTITLE': """
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0;
        color: #333;
    """,
    'FILE_LABEL': """
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 5px;
        color: #333;
    """,
    'INPUT': """
        padding: 5px;
        border: 1px solid #ddd;
        border-radius: 3px;
        font-size: 14px;
    """,
    'LIST': """
        QListWidget {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 5px;
            background-color: white;
        }
        QListWidget::item {
            padding: 5px;
            border-bottom: 1px solid #eee;
        }
        QListWidget::item:selected {
            background-color: #e0e0e0;
        }
    """,
    'PARTITION_FRAME': """
        QFrame {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
            background-color: #f9f9f9;
        }
    """
}

@dataclass
class Partition:
    """Represents a PDF partition with its page number and suffix."""
    page_number: int
    suffix: str
    is_special: bool = False
    special_name: str = ""

    def __post_init__(self):
        """Ensure suffix starts with underscore."""
        if self.suffix and not self.suffix.startswith('_'):
            self.suffix = '_' + self.suffix

class PartitionFrame(QFrame):
    """Frame for a single partition with fixed size."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 50)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 4px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                padding: 8px 12px;
                border-radius: 6px;
                background-color: #dc3545;
                color: white;
                font-size: 14px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QLabel {
                color: #495057;
                font-size: 14px;
            }
        """)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Page number section
        page_layout = QHBoxLayout()
        page_label = QLabel("Page:")
        page_label.setFixedWidth(50)
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("Enter page number")
        self.page_input.setFixedWidth(100)
        self.page_input.setValidator(QIntValidator(1, 9999))
        page_layout.addWidget(page_label)
        page_layout.addWidget(self.page_input)
        layout.addLayout(page_layout)
        
        # Suffix section
        suffix_layout = QHBoxLayout()
        suffix_label = QLabel("Suffix:")
        suffix_label.setFixedWidth(50)
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("Enter suffix (e.g., part2)")
        self.suffix_input.setFixedWidth(200)
        suffix_layout.addWidget(suffix_label)
        suffix_layout.addWidget(self.suffix_input)
        layout.addLayout(suffix_layout)
        
        # Remove button
        self.remove_button = QPushButton("Remove")
        layout.addWidget(self.remove_button)
        
        layout.addStretch()

class MainMenu(QWidget):
    """Main menu widget providing options to merge or split PDF files."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel("PDF Manager")
        title.setStyleSheet(STYLE['TITLE'])
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Buttons
        self.split_button = QPushButton("Split PDF File")
        self.split_button.setStyleSheet(STYLE['BUTTON'])
        self.split_button.clicked.connect(self._on_split_clicked)
        layout.addWidget(self.split_button, alignment=Qt.AlignCenter)
        
        self.endorse_button = QPushButton("Endorse PDF File")
        self.endorse_button.setStyleSheet(STYLE['BUTTON'])
        self.endorse_button.clicked.connect(self._on_endorse_clicked)
        layout.addWidget(self.endorse_button, alignment=Qt.AlignCenter)
        
        self.merge_button = QPushButton("Merge PDF Files")
        self.merge_button.setStyleSheet(STYLE['BUTTON'])
        self.merge_button.clicked.connect(self._on_merge_clicked)
        layout.addWidget(self.merge_button, alignment=Qt.AlignCenter)
        
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet(STYLE['BUTTON'])
        self.exit_button.clicked.connect(QApplication.instance().quit)
        layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)
    
    def _on_merge_clicked(self):
        """Handle merge button click."""
        self.parentWidget().setCurrentIndex(1)
        self.parentWidget().parentWidget().setWindowTitle("PDF Manager - Merge")
    
    def _on_split_clicked(self):
        """Handle split button click."""
        self.parentWidget().setCurrentIndex(2)
        self.parentWidget().parentWidget().setWindowTitle("PDF Manager - Split")
        
    def _on_endorse_clicked(self):
        """Handle endorse button click."""
        self.parentWidget().setCurrentIndex(3)
        self.parentWidget().parentWidget().setWindowTitle("PDF Manager - Endorse")

class PDFMergerApp(QWidget):
    """Widget for merging multiple PDF files."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Back button
        back_button = QPushButton("← Back to Main Menu")
        back_button.setStyleSheet(STYLE['BUTTON'])
        back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_button)
        
        # Title
        title = QLabel("Merge PDF Files")
        title.setStyleSheet(STYLE['SUBTITLE'])
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # File list with drag and drop support
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(STYLE['LIST'])
        self.file_list.setDragDropMode(QListWidget.InternalMove)
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.file_list)
        
        # Instructions
        instructions = QLabel("Drag and drop files to reorder them")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions, alignment=Qt.AlignCenter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton("Select PDF Files")
        self.select_button.setStyleSheet(STYLE['BUTTON'])
        self.select_button.clicked.connect(self._select_files)
        button_layout.addWidget(self.select_button)
        
        self.merge_button = QPushButton("Merge Files")
        self.merge_button.setStyleSheet(STYLE['BUTTON'])
        self.merge_button.clicked.connect(self._merge_files)
        self.merge_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.merge_button)
        
        layout.addLayout(button_layout)
    
    def _on_back_clicked(self):
        """Handle back button click."""
        self.parentWidget().setCurrentIndex(0)
        self.parentWidget().parentWidget().setWindowTitle("PDF Manager")
        self.file_list.clear()
        self.merge_button.setEnabled(False)
    
    def _select_files(self):
        """Open file dialog to select PDF files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        if files:
            # Clear existing files only if new files are selected
            self.file_list.clear()
            self.merge_button.setEnabled(False)
            
            for file in files:
                item = QListWidgetItem(Path(file).name)
                item.setToolTip(file)  # Store full path in tooltip
                self.file_list.addItem(item)
            self.merge_button.setEnabled(True)
    
    def _merge_files(self):
        """Merge selected PDF files."""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please select PDF files first.")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            "",
            "PDF Files (*.pdf)"
        )
        
        if output_file:
            try:
                merger = PdfMerger()
                for i in range(self.file_list.count()):
                    item = self.file_list.item(i)
                    file_path = item.toolTip()  # Get full path from tooltip
                    merger.append(file_path)
                merger.write(output_file)
                merger.close()
                QMessageBox.information(
                    self,
                    "Success",
                    f"PDF files merged successfully!\nSaved as: {output_file}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to merge PDF files: {str(e)}")

class PDFSplitApp(QWidget):
    """Widget for splitting a PDF file."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.partitions: List[Partition] = []
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Back button
        back_button = QPushButton("← Back")
        back_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #6c757d;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_button)
        
        # Title
        title = QLabel("Split PDF")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        file_layout.addWidget(self.file_label, stretch=1)
        
        self.select_button = QPushButton("Select PDF")
        self.select_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #007bff;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.select_button.clicked.connect(self._select_file)
        file_layout.addWidget(self.select_button)
        layout.addLayout(file_layout)
        
        # Split points section
        split_points_label = QLabel("Split Points:")
        split_points_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(split_points_label)
        
        # Split points list
        self.points_list = QListWidget()
        self.points_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(self.points_list)
        
        # Add point section
        add_point_layout = QHBoxLayout()
        
        # Page number input
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("Page number")
        self.page_input.setValidator(QIntValidator(1, 9999))
        self.page_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        add_point_layout.addWidget(self.page_input)
        
        # Suffix input
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("Suffix (optional)")
        self.suffix_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        add_point_layout.addWidget(self.suffix_input)
        
        # Add button
        self.add_button = QPushButton("Add Point")
        self.add_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #28a745;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.add_button.clicked.connect(self._add_point)
        self.add_button.setEnabled(False)
        add_point_layout.addWidget(self.add_button)
        
        layout.addLayout(add_point_layout)
        
        # Split button
        self.split_button = QPushButton("Split PDF")
        self.split_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #007bff;
                color: white;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.split_button.clicked.connect(self._split_pdf)
        self.split_button.setEnabled(False)
        layout.addWidget(self.split_button)
    
    def _add_point(self):
        """Add a new split point."""
        try:
            page = int(self.page_input.text())
            suffix = self.suffix_input.text() or "_split"
            
            # Create partition
            partition = Partition(page_number=page, suffix=suffix)
            self.partitions.append(partition)
            
            # Add to list
            item_text = f"Page {page}"
            if suffix != "_split":
                item_text += f" (suffix: {suffix})"
            self.points_list.addItem(item_text)
            
            # Clear inputs
            self.page_input.clear()
            self.suffix_input.clear()
            self.page_input.setFocus()
            
            # Sort partitions
            self.partitions.sort(key=lambda p: p.page_number)
            
            # Update split button
            self.split_button.setEnabled(True)
            
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid page number.")
    
    def _select_file(self):
        """Open file dialog to select a PDF file."""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.file_label.setText(file)
            self.add_button.setEnabled(True)
    
    def _on_back_clicked(self):
        """Handle back button click."""
        self.parentWidget().setCurrentIndex(0)
        self.parentWidget().parentWidget().setWindowTitle("PDF Manager")
        self.file_label.setText("No file selected")
        self.points_list.clear()
        self.partitions.clear()
        self.add_button.setEnabled(False)
        self.split_button.setEnabled(False)
    
    def _split_pdf(self):
        """Split the selected PDF file."""
        if self.file_label.text() == "No file selected":
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return
        
        if not self.partitions:
            QMessageBox.warning(self, "Warning", "Please add at least one split point.")
            return
        
        input_file = self.file_label.text()
        output_dir = str(Path(input_file).parent)
        base_name = Path(input_file).stem
        
        try:
            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            
            # Sort partitions by page number
            self.partitions.sort(key=lambda p: p.page_number)
            
            # Create first part with pages before first partition
            if self.partitions[0].page_number > 1:
                writer = PdfWriter()
                for page in range(self.partitions[0].page_number - 1):
                    writer.add_page(reader.pages[page])
                
                output_file = str(Path(output_dir) / f"{base_name}_first.pdf")
                with open(output_file, "wb") as f:
                    writer.write(f)
            
            # Create parts for each partition
            for i, partition in enumerate(self.partitions):
                start_page = partition.page_number - 1  # Convert to 0-based index
                end_page = (self.partitions[i + 1].page_number - 1 
                          if i + 1 < len(self.partitions) 
                          else total_pages)
                
                writer = PdfWriter()
                for page in range(start_page, end_page):
                    writer.add_page(reader.pages[page])
                
                suffix = partition.suffix
                if not suffix.startswith('_'):
                    suffix = '_' + suffix
                
                output_file = str(Path(output_dir) / f"{base_name}{suffix}.pdf")
                with open(output_file, "wb") as f:
                    writer.write(f)
            
            QMessageBox.information(
                self,
                "Success",
                "PDF split successfully!\nCheck the output directory for the split files."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to split PDF: {str(e)}")

class PDFEndorserApp(QWidget):
    """Widget for endorsing PDF files."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Back button
        back_button = QPushButton("← Back")
        back_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #6c757d;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_button)
        
        # Title
        title = QLabel("Endorse PDF Files")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # File list with drag and drop support
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(STYLE['LIST'])
        self.file_list.setDragDropMode(QListWidget.InternalMove)
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.file_list)
        
        # Instructions
        instructions = QLabel("Drag and drop files to reorder them")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions, alignment=Qt.AlignCenter)
        
        # Stamp text input
        stamp_layout = QHBoxLayout()
        stamp_label = QLabel("Stamp Text:")
        stamp_label.setStyleSheet("font-weight: bold;")
        stamp_layout.addWidget(stamp_label)
        
        self.stamp_input = QLineEdit()
        self.stamp_input.setPlaceholderText("Enter text to stamp on PDF")
        self.stamp_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        stamp_layout.addWidget(self.stamp_input)
        layout.addLayout(stamp_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton("Select PDF Files")
        self.select_button.setStyleSheet(STYLE['BUTTON'])
        self.select_button.clicked.connect(self._select_files)
        button_layout.addWidget(self.select_button)
        
        self.endorse_button = QPushButton("Endorse Files")
        self.endorse_button.setStyleSheet(STYLE['BUTTON'])
        self.endorse_button.clicked.connect(self._endorse_pdfs)
        self.endorse_button.setEnabled(False)
        button_layout.addWidget(self.endorse_button)
        
        layout.addLayout(button_layout)
        
    def _select_files(self):
        """Open file dialog to select PDF files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        if files:
            # Clear existing files only if new files are selected
            self.file_list.clear()
            self.stamp_input.clear()
            self.endorse_button.setEnabled(False)
            
            for file in files:
                item = QListWidgetItem(Path(file).name)
                item.setToolTip(file)  # Store full path in tooltip
                self.file_list.addItem(item)
            self.endorse_button.setEnabled(True)
    
    def _on_back_clicked(self):
        """Handle back button click."""
        self.parentWidget().setCurrentIndex(0)
        self.parentWidget().parentWidget().setWindowTitle("PDF Manager")
        self.file_list.clear()
        self.stamp_input.clear()
        self.endorse_button.setEnabled(False)
    
    def _endorse_pdfs(self):
        """Endorse all selected PDF files."""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please select PDF files first.")
            return
        
        stamp_text = self.stamp_input.text().strip()
        if not stamp_text:
            QMessageBox.warning(self, "Warning", "Please enter stamp text.")
            return
        
        success_count = 0
        error_files = []
        
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            input_file = item.toolTip()  # Get full path from tooltip
            output_file = str(Path(input_file).parent / f"{Path(input_file).stem}_endorsed.pdf")
            
            try:
                endorse_pdf(
                    input_pdf=input_file,
                    stamp_text=stamp_text,
                    margin_inch=0.02,
                    stamp_scale=0.8
                )
                success_count += 1
            except Exception as e:
                error_files.append(f"{Path(input_file).name}: {str(e)}")
        
        # Show results
        if success_count > 0:
            message = f"Successfully endorsed {success_count} file(s)."
            if error_files:
                message += "\n\nFailed files:\n" + "\n".join(error_files)
            QMessageBox.information(self, "Results", message)
        else:
            QMessageBox.critical(self, "Error", "Failed to endorse any files:\n" + "\n".join(error_files))

class MainApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Manager")
        self.setMinimumSize(600, 400)
        
        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Add widgets
        self.main_menu = MainMenu(self.stacked_widget)
        self.merger_app = PDFMergerApp(self.stacked_widget)
        self.split_app = PDFSplitApp(self.stacked_widget)
        self.endorser_app = PDFEndorserApp(self.stacked_widget)
        
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.merger_app)
        self.stacked_widget.addWidget(self.split_app)
        self.stacked_widget.addWidget(self.endorser_app)

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()