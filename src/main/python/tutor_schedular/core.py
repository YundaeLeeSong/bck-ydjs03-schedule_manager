# ca_schedular/core.py

import sys
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QDateTimeEdit, QSpinBox, QListWidget, QListWidgetItem,
    QProgressDialog, QCheckBox, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QDateTime, QSize
from PyQt5.QtGui import QFont, QIcon

# Import singleton FileManager
from file_manager.core import FileManager
# Import Proxies
from zoomproxy.core import ZoomProxy
from gmailproxy.core import GmailProxy

# Import ics library for export
try:
    from ics import Calendar, Event
except ImportError:
    Calendar = None
    Event = None

# --- Singleton Access ---
fm = FileManager()

def get_status_emoji(is_paid, is_done):
    """Get emoji based on isPaid and isDone flags."""
    if is_paid and is_done:
        return "✅"
    elif is_paid and not is_done:
        return "⏳"
    elif not is_paid and is_done:
        return "🔄✅"
    else:  # not paid and not done
        return "🔄"

class WelcomeWidget(QWidget):
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

class EmailDialog(QDialog):
    def __init__(self, parent, student_name, recipient_emails, template_context=None):
        super().__init__(parent)
        self.setWindowTitle(f"Email Report for {student_name}")
        self.resize(700, 600)
        self.recipient_emails = recipient_emails
        self.template_context = template_context or {}
        self.attachments = []
        
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
        path, _ = QFileDialog.getOpenFileName(self, "Select Attachment")
        if path:
            self.attachments.append(path)
            self.list_attachments.addItem(os.path.basename(path))

    def clear_attachments(self):
        self.attachments.clear()
        self.list_attachments.clear()

    def on_send(self):
        # Double check
        msg = f"Send to: {', '.join(self.recipient_emails)}\n\nSubject: {self.input_subject.text()}\nAttachments: {len(self.attachments)}"
        reply = QMessageBox.question(self, "Confirm Send", msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.accept()

    def get_data(self):
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

class StudentManagerWidget(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.students = []
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

    def open_email_dialog(self, idx):
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
            
            # Update latest (since sorted, last is latest)
            latest_date = dt.strftime("%m/%d/%y")
            latest_runtime = str(s['duration'])

        context = {
            "DATE": latest_date,
            "RUNTIME": latest_runtime,
            "STUDENT_NAME": student['name'],
            "STATUS_LIST": "\n".join(status_lines)
        }
            
        dlg = EmailDialog(self, student["name"], emails, template_context=context)
        if dlg.exec_() == QDialog.Accepted:
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

class ScheduleManagerWidget(QWidget):
    def __init__(self, on_back, on_go_students):
        super().__init__()
        self.on_back = on_back
        self.on_go_students = on_go_students
        self.schedules = []
        self.zoom_proxy = ZoomProxy()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Top Bar
        top_bar = QHBoxLayout()
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.on_back)
        top_bar.addWidget(btn_back)
        
        top_bar.addStretch()
        
        btn_students = QPushButton("Manage Students")
        btn_students.clicked.connect(self.on_go_students)
        top_bar.addWidget(btn_students)
        
        self.btn_schedule = QPushButton("Schedule Now (Zoom/ICS Export)")
        self.btn_schedule.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_schedule.clicked.connect(self.schedule_now)
        top_bar.addWidget(self.btn_schedule)
        
        layout.addLayout(top_bar)

        # Title
        layout.addWidget(QLabel("Schedule List (Double-click time to edit)"))

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6) # Name, Time, Duration, Note, Status, Actions
        self.table.setHorizontalHeaderLabels(["Name", "Time", "Duration (min)", "Note", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        layout.addWidget(self.table)

    def refresh_data(self):
        # 1. Load Data
        self.schedules = fm.load_schedules()
        students = fm.load_students()
        
        # 2. Migrate old format and check for students without schedules
        existing_student_names = {s['name'] for s in self.schedules}
        changes_made = False
        
        # Migrate old status format to new isPaid/isDone format
        for entry in self.schedules:
            if "status" in entry and "isPaid" not in entry:
                # Migrate: "done" -> isPaid=True, isDone=True; "pending" -> isPaid=False, isDone=False
                old_status = entry.get("status")
                entry["isPaid"] = (old_status == "done")
                entry["isDone"] = (old_status == "done")
                del entry["status"]
                changes_made = True
            # Ensure both flags exist
            if "isPaid" not in entry:
                entry["isPaid"] = False
                changes_made = True
            if "isDone" not in entry:
                entry["isDone"] = False
                changes_made = True
            # Ensure note field exists
            if "note" not in entry:
                entry["note"] = ""
                changes_made = True
        
        for std in students:
            if std['name'] not in existing_student_names:
                default_entry = {
                    "name": std['name'],
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "duration": 60,
                    "isPaid": False,
                    "isDone": False,
                    "note": ""
                }
                self.schedules.append(default_entry)
                changes_made = True
        
        if changes_made:
            fm.save_schedules(self.schedules)

        # 3. Sort
        self.schedules.sort(key=lambda x: (x['name'], x['time']))

        # 4. Populate Table
        self.table.setRowCount(0)
        for i, entry in enumerate(self.schedules):
            self.table.insertRow(i)
            
            # Name
            self.table.setItem(i, 0, QTableWidgetItem(entry['name']))
            
            # Time
            time_item = QTableWidgetItem(entry['time'])
            time_item.setFlags(time_item.flags() | Qt.ItemIsEditable) 
            self.table.setItem(i, 1, time_item)
            
            # Duration
            self.table.setItem(i, 2, QTableWidgetItem(str(entry['duration'])))
            
            # Note
            note_item = QTableWidgetItem(entry.get("note", ""))
            note_item.setFlags(note_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(i, 3, note_item)
            
            # Status (Two Checkboxes: Paid and Done)
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(0,0,0,0)
            status_layout.setAlignment(Qt.AlignCenter)
            
            is_paid = entry.get("isPaid", False)
            is_done = entry.get("isDone", False)
            
            chk_paid = QCheckBox("Paid")
            chk_paid.setChecked(is_paid)
            chk_paid.toggled.connect(lambda checked, row=i: self.toggle_paid(row, checked))
            
            chk_done = QCheckBox("Done")
            chk_done.setChecked(is_done)
            chk_done.toggled.connect(lambda checked, row=i: self.toggle_done(row, checked))
            
            status_layout.addWidget(chk_paid)
            status_layout.addWidget(chk_done)
            self.table.setCellWidget(i, 4, status_widget)
            
            # Actions: + / - Buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(4)
            
            btn_add = QPushButton("+")
            btn_add.setFixedSize(30, 30)
            btn_add.setToolTip("Duplicate")
            btn_add.clicked.connect(lambda _, row=i: self.duplicate_schedule(row))
            
            btn_minus = QPushButton("-")
            btn_minus.setFixedSize(30, 30)
            btn_minus.setToolTip("Delete")
            btn_minus.clicked.connect(lambda _, row=i: self.delete_schedule(row))
            
            action_layout.addWidget(btn_add)
            action_layout.addWidget(btn_minus)
            
            self.table.setCellWidget(i, 5, action_widget)

    def toggle_paid(self, row, checked):
        self.schedules[row]["isPaid"] = checked
        self.schedules.sort(key=lambda x: (x['name'], x['time']))
        fm.save_schedules(self.schedules)

    def toggle_done(self, row, checked):
        self.schedules[row]["isDone"] = checked
        self.schedules.sort(key=lambda x: (x['name'], x['time']))
        fm.save_schedules(self.schedules)

    def on_cell_double_clicked(self, row, col):
        if col == 1: # Time
            current_time_str = self.schedules[row]['time']
            try:
                dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M")
            except ValueError:
                dt = datetime.now()

            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Time")
            d_layout = QVBoxLayout(dialog)
            
            dt_edit = QDateTimeEdit(dt)
            dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
            dt_edit.setCalendarPopup(True)
            d_layout.addWidget(dt_edit)
            
            btn_save = QPushButton("Save")
            btn_save.clicked.connect(lambda: dialog.accept())
            d_layout.addWidget(btn_save)
            
            if dialog.exec_() == QDialog.Accepted:
                new_time_str = dt_edit.dateTime().toString("yyyy-MM-dd HH:mm")
                self.schedules[row]['time'] = new_time_str
                self.schedules.sort(key=lambda x: (x['name'], x['time']))
                fm.save_schedules(self.schedules)
                self.refresh_data()
        
        elif col == 2: # Duration
            current_dur = self.schedules[row]['duration']
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Duration")
            d_layout = QVBoxLayout(dialog)
            
            spin = QSpinBox()
            spin.setRange(1, 480)
            spin.setValue(int(current_dur))
            d_layout.addWidget(spin)
            
            btn_save = QPushButton("Save")
            btn_save.clicked.connect(lambda: dialog.accept())
            d_layout.addWidget(btn_save)
            
            if dialog.exec_() == QDialog.Accepted:
                self.schedules[row]['duration'] = spin.value()
                self.schedules.sort(key=lambda x: (x['name'], x['time']))
                fm.save_schedules(self.schedules)
                self.refresh_data()
        
        elif col == 3: # Note
            current_note = self.schedules[row].get("note", "")
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Note")
            dialog.resize(400, 200)
            d_layout = QVBoxLayout(dialog)
            
            note_edit = QTextEdit()
            note_edit.setPlainText(current_note)
            d_layout.addWidget(note_edit)
            
            btn_save = QPushButton("Save")
            btn_save.clicked.connect(lambda: dialog.accept())
            d_layout.addWidget(btn_save)
            
            if dialog.exec_() == QDialog.Accepted:
                new_note = note_edit.toPlainText()
                self.schedules[row]['note'] = new_note
                fm.save_schedules(self.schedules)
                self.refresh_data()

    def duplicate_schedule(self, row):
        entry = self.schedules[row].copy()
        entry["isPaid"] = False
        entry["isDone"] = False
        entry["note"] = entry.get("note", "")  # Keep note but can be edited
        if "status" in entry:
            del entry["status"]
        try:
            dt = datetime.strptime(entry['time'], "%Y-%m-%d %H:%M")
            dt += timedelta(days=7)
            entry['time'] = dt.strftime("%Y-%m-%d %H:%M")
        except:
            pass
        self.schedules.append(entry)
        self.schedules.sort(key=lambda x: (x['name'], x['time']))
        fm.save_schedules(self.schedules)
        self.refresh_data()

    def delete_schedule(self, row):
        confirm = QMessageBox.question(
            self, "Confirm", 
            "Delete this schedule?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            del self.schedules[row]
            self.schedules.sort(key=lambda x: (x['name'], x['time']))
            fm.save_schedules(self.schedules)
            self.refresh_data()

    def schedule_now(self):
        if not self.schedules:
            QMessageBox.information(self, "Empty", "No schedules to process.")
            return

        reply = QMessageBox.question(
            self, "Schedule Now",
            f"This will attempt to schedule {len(self.schedules)} meetings on Zoom and export an ICS file.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        progress = QProgressDialog("Processing Schedules...", "Cancel", 0, len(self.schedules), self)
        progress.setWindowModality(Qt.WindowModal)
        
        name_counts = defaultdict(int)
        results = []
        ics_events = []

        sorted_schedules = sorted(self.schedules, key=lambda x: (x['name'], x['time']))

        for i, entry in enumerate(sorted_schedules):
            if progress.wasCanceled():
                break
            
            name_counts[entry['name']] += 1
            count = name_counts[entry['name']]
            topic = f"{entry['name']}{count:02d}"
            
            res = self.zoom_proxy.create_meeting(topic, entry['time'], int(entry['duration']))
            status = "OK" if "join_url" in res else f"Err: {res.get('error')}"
            results.append(f"{topic}: {status}")
            
            if Calendar:
                try:
                    start_naive = datetime.strptime(entry['time'], "%Y-%m-%d %H:%M")
                    start_aware = start_naive.astimezone() 
                    e = Event()
                    e.name = topic
                    e.begin = start_aware
                    e.duration = timedelta(minutes=int(entry['duration']))
                    if "join_url" in res:
                        e.description = f"Zoom Link: {res['join_url']}"
                    ics_events.append(e)
                except ValueError:
                    continue
            
            progress.setValue(i + 1)

        if Calendar and ics_events:
            cal = Calendar()
            for e in ics_events:
                cal.events.add(e)
            path = fm.get_export_path("tutor_schedule.ics")
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(cal.serialize())
                results.append(f"\nICS File exported to: {path}")
            except Exception as e:
                results.append(f"\nICS Export Failed: {e}")
        elif not Calendar:
            results.append("\nICS library missing. Skipped export.")

        QMessageBox.information(self, "Report", "\n".join(results))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutoring Scheduler App")
        self.setMinimumSize(1200, 980)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.welcome_page = WelcomeWidget(
            on_start=self.go_to_schedule, 
            on_quit=self.close
        )
        self.schedule_page = ScheduleManagerWidget(
            on_back=self.go_to_welcome,
            on_go_students=self.go_to_students
        )
        self.student_page = StudentManagerWidget(
            on_back=self.go_to_schedule
        )

        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.schedule_page)
        self.stacked_widget.addWidget(self.student_page)
        self.stacked_widget.setCurrentWidget(self.welcome_page)

    def go_to_schedule(self):
        self.schedule_page.refresh_data()
        self.stacked_widget.setCurrentWidget(self.schedule_page)

    def go_to_welcome(self):
        self.stacked_widget.setCurrentWidget(self.welcome_page)

    def go_to_students(self):
        self.student_page.refresh_data()
        self.stacked_widget.setCurrentWidget(self.student_page)

def main():
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
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()