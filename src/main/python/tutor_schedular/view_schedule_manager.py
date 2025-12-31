# view_schedule_manager.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, QMessageBox, 
    QDateTimeEdit, QSpinBox, QTextEdit, QCheckBox, QProgressDialog
)
from PySide6.QtCore import Qt
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any

from file_manager import FileManager
from zoomproxy import ZoomProxy

# Import ics library for export
try:
    from ics import Calendar, Event
except ImportError:
    Calendar = None
    Event = None

# --- Singleton Access ---
fm = FileManager()

class ViewScheduleManager(QWidget):
    """
    View to manage the schedule list.
    """
    def __init__(self, on_back, on_go_students):
        super().__init__()
        self.on_back = on_back
        self.on_go_students = on_go_students
        self.schedules: List[Dict[str, Any]] = []
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
        """Reload schedules from file manager and update table."""
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
        """Update Paid status."""
        self.schedules[row]["isPaid"] = checked
        self.schedules.sort(key=lambda x: (x['name'], x['time']))
        fm.save_schedules(self.schedules)

    def toggle_done(self, row, checked):
        """Update Done status."""
        self.schedules[row]["isDone"] = checked
        self.schedules.sort(key=lambda x: (x['name'], x['time']))
        fm.save_schedules(self.schedules)

    def on_cell_double_clicked(self, row, col):
        """Handle cell double clicks for editing."""
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
            
            if dialog.exec() == QDialog.Accepted:
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
            
            if dialog.exec() == QDialog.Accepted:
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
            
            if dialog.exec() == QDialog.Accepted:
                new_note = note_edit.toPlainText()
                self.schedules[row]['note'] = new_note
                fm.save_schedules(self.schedules)
                self.refresh_data()

    def duplicate_schedule(self, row):
        """Duplicate an existing schedule entry."""
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
        """Delete a schedule entry."""
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
        """Process schedules: create Zoom meetings and export ICS."""
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
