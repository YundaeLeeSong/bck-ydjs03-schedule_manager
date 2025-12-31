# view_student_manager.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, 
    QListWidgetItem, QFormLayout, QLineEdit, QMessageBox, QDialog, QTextEdit, 
    QFileDialog
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from datetime import datetime
import os
from typing import List, Dict, Any, Optional

from file_manager import FileManager
from gmailproxy import GmailProxy
from .utils import get_status_emoji

# --- Singleton Access ---
fm = FileManager()

class EmailDialog(QDialog):
    """
    Dialog for composing and sending email reports.
    """
    def __init__(self, parent: Optional[QWidget], student_name: str, recipient_emails: List[str], template_context: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.setWindowTitle(f"Email Report for {student_name}")
        self.resize(700, 600)
        self.recipient_emails = recipient_emails
        self.template_context = template_context or {}
        self.attachments: List[str] = []
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        # Default subject: [today's date] {name} - Report
        today_str = datetime.now().strftime("%Y-%m-%d")
        default_subject = f"[{today_str}] {student_name} - Report"
        self.input_subject = QLineEdit(default_subject)
        self.input_desc = QTextEdit()
        self.input_desc.setPlainText("Scribes are attached...")
        self.input_desc.setPlaceholderText("Enter report comment/description here...")
        
        form.addRow("To:", QLabel(", ".join(recipient_emails)))
        form.addRow("Subject:", self.input_subject)
        form.addRow("Comment:", self.input_desc)
        layout.addLayout(form)
        
        # Preview of Status List (ReadOnly)
        if "STATUS_LIST" in self.template_context:
            layout.addWidget(QLabel("Schedule Status Preview:"))
            preview = QTextEdit()
            preview.setReadOnly(True)
            preview.setPlainText(self.template_context["STATUS_LIST"])
            preview.setMaximumHeight(150)
            layout.addWidget(preview)

        # Attachments
        layout.addWidget(QLabel("Attachments:"))
        self.list_attachments = QListWidget()
        self.list_attachments.setMaximumHeight(100)
        layout.addWidget(self.list_attachments)
        
        h_att = QHBoxLayout()
        btn_add_att = QPushButton("Add Attachment")
        btn_add_att.clicked.connect(self.add_attachment)
        btn_clear_att = QPushButton("Clear Attachments")
        btn_clear_att.clicked.connect(self.clear_attachments)
        h_att.addWidget(btn_add_att)
        h_att.addWidget(btn_clear_att)
        layout.addLayout(h_att)
        
        # Actions
        h_btn = QHBoxLayout()
        btn_send = QPushButton("Send Email")
        btn_send.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_send.clicked.connect(self.on_send)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        h_btn.addWidget(btn_send)
        h_btn.addWidget(btn_cancel)
        layout.addLayout(h_btn)

    def add_attachment(self):
        """Open file dialog to add an attachment."""
        path, _ = QFileDialog.getOpenFileName(self, "Select Attachment")
        if path:
            self.attachments.append(path)
            self.list_attachments.addItem(os.path.basename(path))

    def clear_attachments(self):
        """Clear all attachments."""
        self.attachments.clear()
        self.list_attachments.clear()

    def on_send(self):
        """Confirm and accept dialog to trigger send."""
        # Double check
        msg = f"Send to: {', '.join(self.recipient_emails)}\n\nSubject: {self.input_subject.text()}\nAttachments: {len(self.attachments)}"
        reply = QMessageBox.question(self, "Confirm Send", msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.accept()

    def get_data(self) -> Dict[str, Any]:
        """
        Get the data for the email.

        Returns:
            Dict[str, Any]: Contains subject, body, and attachments.
        """
        # Construct Body using Template
        template = fm.load_template("gmail.html")
        
        # Fallback if no template
        if not template:
            template = """
            <html><body>
            <p><strong>Report Date:</strong> {{DATE}}</p>
            <p><strong>Runtime:</strong> {{RUNTIME}} min</p>
            <div style="background-color:#eee;padding:10px;">{{COMMENT}}</div>
            <pre>{{STATUS_LIST}}</pre>
            </body></html>
            """
            
        comment = self.input_desc.toPlainText().replace("\n", "<br>")
        status_list = self.template_context.get("STATUS_LIST", "").replace("\n", "<br>")
        
        body = template.replace("{{DATE}}", self.template_context.get("DATE", ""))
        body = body.replace("{{RUNTIME}}", str(self.template_context.get("RUNTIME", "")))
        body = body.replace("{{STUDENT_NAME}}", self.template_context.get("STUDENT_NAME", ""))
        body = body.replace("{{COMMENT}}", comment)
        body = body.replace("{{STATUS_LIST}}", status_list)
        
        return {
            "subject": self.input_subject.text(),
            "body": body,
            "attachments": self.attachments
        }

class ViewStudentManager(QWidget):
    """
    View to manage the list of students.
    """
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.students: List[Dict[str, Any]] = []
        self.gmail = GmailProxy()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        title = QLabel("Manage Students")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.on_back)
        header.addWidget(btn_back)
        layout.addLayout(header)

        # Content
        content_layout = QHBoxLayout()
        
        # Left: Form
        form_layout = QFormLayout()
        self.input_name = QLineEdit()
        self.input_username = QLineEdit()
        self.input_emails = QLineEdit()
        self.input_emails.setPlaceholderText("comma, separated, emails")
        
        form_layout.addRow("Name:", self.input_name)
        form_layout.addRow("Username:", self.input_username)
        form_layout.addRow("Emails:", self.input_emails)
        
        btn_add = QPushButton("Add Student")
        btn_add.clicked.connect(self.add_student)
        form_layout.addWidget(btn_add)
        
        form_container = QWidget()
        form_container.setLayout(form_layout)
        content_layout.addWidget(form_container, 1)

        # Right: List
        self.student_list = QListWidget()
        content_layout.addWidget(self.student_list, 2)
        
        btn_remove = QPushButton("Remove Selected Student")
        btn_remove.clicked.connect(self.remove_student)
        
        right_panel = QVBoxLayout()
        right_panel.addLayout(content_layout)
        right_panel.addWidget(btn_remove)
        
        layout.addLayout(right_panel)

    def refresh_data(self):
        """Reload students from file manager and update list."""
        self.students = fm.load_students()
        # Sort students by name
        self.students.sort(key=lambda x: x.get('name', '').lower())
        self.student_list.clear()
        for i, s in enumerate(self.students):
            # Container
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 2, 5, 2)
            
            # Label
            lbl = QLabel(f"{s['name']} ({s.get('username','')})")
            item_layout.addWidget(lbl)
            
            item_layout.addStretch()
            
            # Email Button
            btn_email = QPushButton("Email Report (Gmail)")
            btn_email.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            btn_email.setFixedWidth(250)
            btn_email.clicked.connect(lambda _, idx=i: self.open_email_dialog(idx))
            item_layout.addWidget(btn_email)
            
            # Add to list
            item = QListWidgetItem(self.student_list)
            item.setSizeHint(item_widget.sizeHint())
            self.student_list.addItem(item)
            self.student_list.setItemWidget(item, item_widget)

    def open_email_dialog(self, idx: int):
        """Open the email dialog for a student."""
        student = self.students[idx]
        emails = student.get("emailRecipients", [])
        if not emails:
            QMessageBox.warning(self, "No Email", "This student has no registered emails.")
            return
        
        # Prepare Template Data
        schedules = fm.load_schedules()
        # Filter for this student
        student_scheds = [s for s in schedules if s['name'] == student['name']]
        # Sort by Time
        student_scheds.sort(key=lambda x: x['time'])
        
        # Generate Status List
        status_lines = []
        latest_date = "N/A"
        latest_runtime = "0"
        
        for i, s in enumerate(student_scheds):
            # Parse Time: 2025-12-14 15:30
            try:
                dt = datetime.strptime(s['time'], "%Y-%m-%d %H:%M")
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")
            except ValueError:
                date_str = s['time']
                time_str = ""
            
            # Enumerable Name: anderson14
            enum_name = f"{student['name']}{i+1:02d}"
            username = student.get('username', '')
            full_ref = f"{enum_name}({username})" if username else enum_name
            
            # Status Icon - handle migration from old format
            if "isPaid" in s:
                is_paid = s.get("isPaid", False)
                is_done = s.get("isDone", False)
            else:
                # Old format: use status field
                is_paid = s.get("status") == "done" if "status" in s else False
                is_done = s.get("status") == "done" if "status" in s else False
            icon = get_status_emoji(is_paid, is_done)
            
            line = f"{date_str},{time_str},{full_ref},{s['duration']} {icon}"
            status_lines.append(line)
            
            # Update latest runtime (since sorted, last is latest)
            latest_runtime = str(s['duration'])

        # Report date is today's date
        report_date = datetime.now().strftime("%m/%d/%y")
        
        context = {
            "DATE": report_date,
            "RUNTIME": latest_runtime,
            "STUDENT_NAME": student['name'],
            "STATUS_LIST": "\n".join(status_lines)
        }
            
        dlg = EmailDialog(self, student["name"], emails, template_context=context)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            success, err = self.gmail.send_email(
                recipients=emails,
                subject=data["subject"],
                body_html=data["body"],
                attachments=data["attachments"]
            )
            if success:
                QMessageBox.information(self, "Success", "Email sent successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to send email:\n{err}")

    def add_student(self):
        """Add a new student to the list."""
        name = self.input_name.text().strip()
        username = self.input_username.text().strip()
        emails_str = self.input_emails.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Input Error", "Name is required.")
            return

        emails = [e.strip() for e in emails_str.split(",") if e.strip()]
        
        new_student = {
            "name": name,
            "username": username,
            "emailRecipients": emails
        }
        
        self.students.append(new_student)
        fm.save_students(self.students)
        
        self.input_name.clear()
        self.input_username.clear()
        self.input_emails.clear()
        
        self.refresh_data()

    def remove_student(self):
        """Remove the selected student."""
        row = self.student_list.currentRow()
        if row < 0:
            return
        
        confirm = QMessageBox.question(
            self, "Confirm", 
            f"Delete student '{self.students[row]['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            del self.students[row]
            fm.save_students(self.students)
            self.refresh_data()
