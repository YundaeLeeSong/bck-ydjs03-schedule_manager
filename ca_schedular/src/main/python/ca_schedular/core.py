# ca_schedular/core.py


#### PyQt5/PySide6

import sys
import os
import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QRadioButton,
    QStackedWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLineEdit,
    QLabel, QMessageBox, QListWidget, QListWidgetItem, QCheckBox,
    QTableWidget, QTableWidgetItem, QTimeEdit, QSpinBox, QComboBox
)
from PyQt5.QtCore import QRegExp, QTime, QSize, Qt
from PyQt5.QtGui import QRegExpValidator
from ics import Calendar, Event



# Load environment variables for dynamic configuration
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed; ensure GRADES env var is set manually.")


# CSS themes as raw strings
LIGHT_CSS = """
QWidget {
    font-size: 28px;
    font-family: Arial, sans-serif;
}
QPushButton {
    min-width: 60px;
}
QListWidget::item {
    min-height: 60px;
    padding: 4px;
}
QTableWidget::item {
    min-height: 60px;
    padding: 4px;
}
"""

DARK_CSS = """
QWidget {
    font-size: 28px;
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: #E0E0E0;
}

/* Buttons with violet accent */
QPushButton {
    min-width: 60px;
    background-color: #3D2A54;
    color: #E0E0E0;
    border: 1px solid #9B59B6;
    border-radius: 6px;
    padding: 10px;
}
QPushButton:hover {
    background-color: #5E3B78;
}

/* List widget items */
QListWidget::item {
    min-height: 60px;
    padding: 4px;
    background-color: #1E1E1E;
    color: #E0E0E0;
}
QListWidget::item:selected {
    background-color: #9B59B6;
    color: #000;
}

/* Table cells with borders */
QTableWidget::item {
    min-height: 60px;
    padding: 4px;
    background-color: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #777;
}
QTableWidget::item:selected {
    background-color: #9B59B6;
    color: #000;
}

/* Table headers */
QHeaderView::section {
    background-color: #2A2A2A;
    color: #CCCCCC;
    border: 1px solid #777;
    padding: 6px;
}
"""






# Data files
DATA_DIR = "ca_data"
STUDENTS_CSV = os.path.join(DATA_DIR, "students.csv")
TEACHERS_CSV = os.path.join(DATA_DIR, "teachers.csv")
SCHEDULES_CSV = os.path.join(DATA_DIR, "schedules.csv")

# Regex for Validation
TXTFIELD_REGEX = QRegExp("^[A-Za-z0-9 /-]+$")
EMAIL_REGEX = QRegExp(r"^[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,7}$")


# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)



# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)








# Load grade options from .env, fallback defaults
GRADE_OPTIONS = []
env_grades = os.getenv("GRADES")
if env_grades:
    GRADE_OPTIONS = [g.strip() for g in env_grades.split(",") if g.strip()]
else:
    # Default fallback
    GRADE_OPTIONS = [f"{i}th" for i in range(1, 13)]
    GRADE_OPTIONS += ["college-freshman", "college-sophomore"]







SYSTEM_TZ = datetime.now().astimezone().tzinfo







class FocusablePage(QWidget):
    """Reusable base class to configure focus behavior for UI components."""

    def configure_focus_behavior(self):
        # Ensure table does not grab keyboard focus
        for widget in self.findChildren(QTableWidget):
            widget.setFocusPolicy(Qt.NoFocus)
        # Apply strong focus and autoDefault to buttons
        for widget in self.findChildren(QPushButton):
            widget.setFocusPolicy(Qt.StrongFocus)
            widget.setAutoDefault(False)  # Only one button should have True
        # Set auto-default True only on Add Assignment button
        for widget in self.findChildren(QPushButton):
            if widget.text() == "Add Assignment": widget.setAutoDefault(True)
            if widget.text() == "Add Student": widget.setAutoDefault(True)
            if widget.text() == "Add Teacher": widget.setAutoDefault(True)
            if widget.text() == "Schedule": widget.setAutoDefault(True)
            if widget.text() == "Export .ics": widget.setAutoDefault(True)

        # Apply strong focus to all day checkboxes
        for widget in self.findChildren(QCheckBox):
            widget.setFocusPolicy(Qt.StrongFocus)


























class StudentPage(FocusablePage):
    """Page to register, list, and delete student info."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.teacher_id = None
        self.assignments = []
        self._setup_ui()
        self.load_students()

    def showEvent(self, event):
        """Refresh assignments whenever the page is shown."""
        super().showEvent(event)
        if self.teacher_id is not None:
            self._load_assignments()
            self._refresh_table()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # First and Last name
        self.first_edit = QLineEdit()
        self.last_edit = QLineEdit()
        alpha_val = QRegExpValidator(TXTFIELD_REGEX, self)
        self.first_edit.setValidator(alpha_val)
        self.last_edit.setValidator(alpha_val)
        # Email field (was grade)
        self.email_edit = QLineEdit()
        self.email_validator = QRegExpValidator(EMAIL_REGEX, self)
        self.email_edit.setValidator(self.email_validator)
        # Grade dropdown
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(GRADE_OPTIONS)
        # Subject
        self.subject_edit = QLineEdit()
        self.subject_edit.setValidator(QRegExpValidator(TXTFIELD_REGEX, self))

        form.addRow("First Name:", self.first_edit)
        form.addRow("Last Name:", self.last_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Grade:", self.grade_combo)
        form.addRow("Subject:", self.subject_edit)
        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student)
        form.addRow(add_btn)
        layout.addLayout(form)
        # List
        layout.addWidget(QLabel("Registered Students:"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        # button-behavior
        self.configure_focus_behavior()

    def load_students(self):
        """Load student list with delete buttons."""
        self.list_widget.clear()
        try:
            with open(STUDENTS_CSV, newline='') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    sid, fn, ln = row[0], row[1], row[2]
                    item = QListWidgetItem()
                    widget = QWidget()
                    hl = QHBoxLayout(widget)
                    hl.setContentsMargins(0,0,0,0)
                    subject = row[5] if len(row) > 5 else ""
                    email = row[4] if len(row) > 4 else ""
                    hl.addWidget(QLabel(f"{sid}: {ln}, {fn} ({subject}) [{email}]"))
                    btn = QPushButton("x")
                    btn.setFixedWidth(20)
                    btn.clicked.connect(lambda _, s=sid: self.delete_student(s))
                    hl.addWidget(btn)
                    self.list_widget.addItem(item)
                    self.list_widget.setItemWidget(item, widget)
        except FileNotFoundError:
            pass

    def add_student(self):
        fn = self.first_edit.text().strip()
        ln = self.last_edit.text().strip()
        email = self.email_edit.text().strip()
        grade = self.grade_combo.currentText()
        subject = self.subject_edit.text().strip()
        if not all([fn, ln, email, subject]):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        # Email format check
        if self.email_validator.validate(email, 0)[0] != QRegExpValidator.Acceptable:
            QMessageBox.warning(
                self, "Invalid Email",
                "Please enter a valid email address, e.g., user@example.com"
            )
            return
        new_id = 1
        try:
            with open(STUDENTS_CSV, newline='') as f:
                rows = list(csv.reader(f))
                if len(rows)>1: new_id = int(rows[-1][0])+1
        except FileNotFoundError:
            pass
        write_header = not os.path.exists(STUDENTS_CSV)
        with open(STUDENTS_CSV,'a',newline='') as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["ID","FirstName","LastName","Email","Grade","Subject"])
            w.writerow([new_id, fn, ln, email, grade, subject])
        self.first_edit.clear(); self.last_edit.clear()
        self.email_edit.clear(); self.subject_edit.clear()
        self.load_students()
        self.main_window.check_enable_teachers()

    def delete_student(self, sid):
        """Delete student by ID."""
        rows=[]
        try:
            with open(STUDENTS_CSV,newline='') as f:
                for row in csv.reader(f):
                    if not row or row[0]==sid: continue
                    rows.append(row)
        except FileNotFoundError:
            return
        with open(STUDENTS_CSV,'w',newline='') as f:
            csv.writer(f).writerows(rows)
        self.load_students()
        self.main_window.check_enable_teachers()






















class TeacherPage(FocusablePage):
    """Page to register, list, delete teachers and validate inputs."""
    """Page to register, list, delete teachers, and schedule."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()
        self.load_teachers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        # Name fields
        self.first_edit = QLineEdit()
        self.last_edit = QLineEdit()
        name_validator = QRegExpValidator(TXTFIELD_REGEX, self)
        self.first_edit.setValidator(name_validator)
        self.last_edit.setValidator(name_validator)




        # Email field
        self.email_edit = QLineEdit()
        self.email_validator = QRegExpValidator(EMAIL_REGEX, self)
        self.email_edit.setValidator(self.email_validator)
        # Form layout
        form.addRow("First Name:", self.first_edit)
        form.addRow("Last Name:", self.last_edit)
        form.addRow("Email:", self.email_edit)
        add_btn = QPushButton("Add Teacher")
        add_btn.clicked.connect(self.add_teacher)
        form.addRow(add_btn)
        layout.addLayout(form)
        # List
        layout.addWidget(QLabel("Registered Teachers:"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        # button-behavior
        self.configure_focus_behavior()

    def load_teachers(self):
        """Load teacher list with delete buttons and scheduling on double-click."""
        """Load teachers with Delete and Schedule buttons."""
        self.list_widget.clear()
        try:
            with open(TEACHERS_CSV, newline='') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    tid, fn, ln, email = row[0], row[1], row[2], row[3]
                    item = QListWidgetItem()
                    widget = QWidget()
                    hl = QHBoxLayout(widget)
                    hl.setContentsMargins(0, 0, 0, 0)
                    # Label
                    hl.addWidget(QLabel(f"{tid}: {ln}, {fn} ({email})"))
                    # Schedule button
                    sched_btn = QPushButton("Schedule")
                    sched_btn.setFocusPolicy(Qt.StrongFocus)
                    sched_btn.setAutoDefault(True)  # Only one button should have True
                    sched_btn.clicked.connect(lambda _, t=tid: self.open_schedule(t))
                    hl.addWidget(sched_btn)
                    # Delete button
                    del_btn = QPushButton("x")
                    del_btn.setFixedWidth(20)
                    del_btn.clicked.connect(lambda _, t=tid: self.delete_teacher(t))
                    hl.addWidget(del_btn)
                    self.list_widget.addItem(item)
                    self.list_widget.setItemWidget(item, widget)
        except FileNotFoundError:
            pass

    def add_teacher(self):
        fn = self.first_edit.text().strip()
        ln = self.last_edit.text().strip()
        email = self.email_edit.text().strip()
        if not all([fn, ln, email]):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        # Email format check
        if self.email_validator.validate(email, 0)[0] != QRegExpValidator.Acceptable:
            QMessageBox.warning(
                self, "Invalid Email",
                "Please enter a valid email address, e.g., user@example.com"
            )
            return
        new_id = 1
        try:
            with open(TEACHERS_CSV, newline='') as f:
                rows = list(csv.reader(f))
                if len(rows) > 1:
                    new_id = int(rows[-1][0]) + 1
        except FileNotFoundError:
            pass
        write_header = not os.path.exists(TEACHERS_CSV)
        with open(TEACHERS_CSV, 'a', newline='') as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["ID","FirstName","LastName","Email"])
            w.writerow([new_id, fn, ln, email])
        self.first_edit.clear()
        self.last_edit.clear()
        self.email_edit.clear()
        self.load_teachers()

    def delete_teacher(self, tid):
        """Delete teacher by ID."""
        rows = []
        try:
            with open(TEACHERS_CSV, newline='') as f:
                for row in csv.reader(f):
                    if not row or row[0] == tid:
                        continue
                    rows.append(row)
        except FileNotFoundError:
            return
        with open(TEACHERS_CSV, 'w', newline='') as f:
            csv.writer(f).writerows(rows)
        self.load_teachers()

    def open_schedule(self, teacher_id):
        """Navigate to SchedulePage for chosen teacher."""
        # pass teacher_id as an integer so it matches how we parse CSV
        self.main_window.schedule_page.set_teacher(int(teacher_id))
        self.main_window.stacked.setCurrentWidget(self.main_window.schedule_page)


















class SchedulePage(FocusablePage):
    """Page to assign students to a teacher, sync schedules.csv, and export .ics."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.teacher_id = None
        self.assignments = []
        self._setup_ui()

    def showEvent(self, event):
        """Every time this page becomes visible, reload the CSV and refresh."""
        super().showEvent(event)
        if self.teacher_id is not None:
            self._load_assignments()
            self._refresh_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Student selector
        layout.addWidget(QLabel("Select Students:"))
        self.student_list = QListWidget()
        layout.addWidget(self.student_list)

        # Days checkboxes
        day_layout = QHBoxLayout()
        self.day_checks = []
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            chk = QCheckBox(d)
            self.day_checks.append(chk)
            day_layout.addWidget(chk)
        layout.addLayout(day_layout)

        # Time and duration
        time_layout = QHBoxLayout()
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.time_edit.setDisplayFormat("hh:mm AP")  # 12-hour picker
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 480)
        self.duration_spin.setSuffix(" min")
        time_layout.addWidget(QLabel("Start:"))
        time_layout.addWidget(self.time_edit)
        time_layout.addWidget(QLabel("Duration:"))
        time_layout.addWidget(self.duration_spin)
        layout.addLayout(time_layout)

        # Session type
        self.session_combo = QComboBox()
        self.session_combo.addItems(["In-Person", "Online"])
        layout.addWidget(QLabel("Session Type:"))
        layout.addWidget(self.session_combo)
        # Add assignment
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Assignment")
        add_btn.clicked.connect(self.add_assignment)
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table (7th column for delete)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Day", "Time", "Duration", "Student", "Subject", "Type", ""]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Export ICS
        exp_layout = QHBoxLayout()
        exp_layout.addStretch()
        export_btn = QPushButton("Export .ics")
        export_btn.clicked.connect(self.export_ics)
        exp_layout.addWidget(export_btn)
        layout.addLayout(exp_layout)

        # Focus/filter behavior
        self.installEventFilter(self)
        self.student_list.viewport().installEventFilter(self)
        self.student_list.setCursor(Qt.PointingHandCursor)
        # button-behavior
        self.configure_focus_behavior()

    def eventFilter(self, source, event):
        from PyQt5.QtCore import QEvent
        if event.type() == QEvent.Show:
            self._load_assignments()
            self._refresh_table()

        # Fix: use viewport for accurate position
        if source == self.student_list.viewport() and event.type() == QEvent.MouseButtonRelease:
            item = self.student_list.itemAt(event.pos())
            if item:
                current_state = item.checkState()
                item.setCheckState(Qt.Unchecked if current_state == Qt.Checked else Qt.Checked)
                return True  # Prevent default behavior
        return super().eventFilter(source, event)

    def set_teacher(self, teacher_id):
        # ensure teacher_id is an int to match CSV parsing
        self.teacher_id = int(teacher_id)
        self._load_students()
        self._load_assignments()
        self._refresh_table()

    def _load_students(self):
        self.student_list.clear()
        try:
            with open(STUDENTS_CSV, newline='') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    sid, fn, ln, *_ , subject = row ## ID,FirstName,LastName,Email,Subject
                    text = f"{fn} {ln} ({subject})"
                    item = QListWidgetItem(text)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    item.setData(Qt.UserRole, {
                        'id': sid, 'name': f"{fn} {ln}", 'subject': subject
                    })
                    self.student_list.addItem(item)
        except FileNotFoundError:
            pass

    def _load_assignments(self):
        """Read schedules.csv and populate self.assignments."""
        self.assignments.clear()
        try:
            with open(SCHEDULES_CSV, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['TeacherID']) != self.teacher_id:
                        continue
                    tm = datetime.strptime(row['Time'], "%H:%M").time()
                    self.assignments.append({
                        'day': row['Day'],
                        'time': tm,
                        'duration': int(row['Duration']),
                        'student_id': row['StudentID'],
                        'student_name': row['Student'],
                        'subject': row['Subject'],
                        'type': row['Type']
                    })
        except FileNotFoundError:
            pass

    def add_assignment(self):
        selected = [
            (item.data(Qt.UserRole)['id'],
             item.data(Qt.UserRole)['name'],
             item.data(Qt.UserRole)['subject'])
            for i in range(self.student_list.count())
            if (item := self.student_list.item(i)).checkState() == Qt.Checked
        ]
        days = [chk.text() for chk in self.day_checks if chk.isChecked()]
        if not selected or not days:
            QMessageBox.warning(self, "Error", "Select a student and a day.")
            return
        start = self.time_edit.time().toPyTime()
        dur   = self.duration_spin.value()
        stype = self.session_combo.currentText()
        for day in days:
            for sid, name, subj in selected:
                self.assignments.append({
                    'day': day, 'time': start, 'duration': dur,
                    'student_id': sid, 'student_name': name,
                    'subject': subj, 'type': stype
                })
        self._save_csv()
        self._refresh_table()
        # reset checks
        for i in range(self.student_list.count()):
            self.student_list.item(i).setCheckState(Qt.Unchecked)




    def _save_csv(self):
        """Write schedules.csv: keep everyone else's assignments, update this teacher’s."""
        fieldnames = ["TeacherID", "StudentID", "Day", "Time",
                      "Duration", "Student", "Subject", "Type"]

        # 1) Read existing file, keep rows for _other_ teachers
        existing = []
        try:
            with open(SCHEDULES_CSV, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row["TeacherID"]) != self.teacher_id:
                        existing.append(row)
        except FileNotFoundError:
            # no file yet: nothing to preserve
            pass

        # 2) Add our current teacher’s in‐memory assignments
        for a in self.assignments:
            existing.append({
                "TeacherID": str(self.teacher_id),
                "StudentID": a["student_id"],
                "Day": a["day"],
                "Time": a["time"].strftime("%H:%M"),
                "Duration": str(a["duration"]),
                "Student": a["student_name"],
                "Subject": a["subject"],
                "Type": a["type"]
            })

        # 3) Rewrite the CSV with everyone
        with open(SCHEDULES_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing)






    def remove_assignment(self, row):
        """Remove one assignment."""
        self.assignments.pop(row)
        self._save_csv()
        self._refresh_table()

    def _refresh_table(self):
        """Sort and display all loaded assignments."""
        order = {d: i for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])}
        self.assignments.sort(key=lambda x: (order[x['day']], x['time']))
        self.table.setRowCount(len(self.assignments))
        for r, a in enumerate(self.assignments):
            self.table.setItem(r, 0, QTableWidgetItem(a['day']))
            # display AM/PM time
            ampm = a['time'].strftime("%I:%M %p").lstrip("0")
            self.table.setItem(r, 1, QTableWidgetItem(ampm))
            self.table.setItem(r, 2, QTableWidgetItem(f"{a['duration']} min"))
            self.table.setItem(r, 3, QTableWidgetItem(a['student_name']))
            self.table.setItem(r, 4, QTableWidgetItem(a['subject']))
            self.table.setItem(r, 5, QTableWidgetItem(a['type']))
            # Resize columns and rows based on content
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

            # delete button
            btn = QPushButton("×")
            btn.setFixedWidth(20)
            btn.clicked.connect(lambda _, row=r: self.remove_assignment(row))
            self.table.setCellWidget(r, 6, btn)
        



    def export_ics(self):
        """Export only the current teacher’s assignments to an .ics file."""
        cal = Calendar()

        # Find this week’s Sunday
        today = datetime.now()
        days_since_sunday = (today.weekday() + 1) % 7
        sunday = (today - timedelta(days=days_since_sunday)).date()
        weekday_map = {"Mon":1,"Tue":2,"Wed":3,"Thu":4,"Fri":5,"Sat":6}

        # First, build a mapping from student_id to email
        student_email_map = {}

        try:
            with open(STUDENTS_CSV, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    student_email_map[row['ID']] = row.get('Email', '')
        except FileNotFoundError:
            pass

        print(student_email_map)

        # Build events from in-memory assignments
        for a in self.assignments:
            session_date = sunday + timedelta(days=weekday_map[a['day']])
            # combine date+time into a naive datetime...
            naive_start = datetime.combine(session_date, a['time'])
            # …then attach your system tz
            start_dt = naive_start.replace(tzinfo=SYSTEM_TZ)
            end_dt   = start_dt + timedelta(minutes=a['duration'])
            # start_dt = datetime.combine(session_date, a['time'])
            # end_dt   = start_dt + timedelta(minutes=a['duration'])
            student_email = student_email_map.get(a['student_id'], '')

            e = Event()
            e.name  = f"[{"IN" if a['type'] == "In-Person" else "Online"}] {a['subject']} ({a['student_name']})"
            e.begin = start_dt
            e.end   = end_dt
            e.description   = f"Student email: {student_email}" if student_email else "No student email found."
            cal.events.add(e)

        # Lookup teacher email via DictReader (skips header row)
        teacher_email = None
        try:
            with open(TEACHERS_CSV, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['ID']) == self.teacher_id:
                        teacher_email = row['Email']
                        break
        except FileNotFoundError:
            pass

        if not teacher_email:
            teacher_email = f"teacher_{self.teacher_id}"

        # Write out the .ics
        fname = f"{sunday.isoformat()}/{teacher_email}.ics"
        ics_path = os.path.join(DATA_DIR, fname)
        os.makedirs(os.path.dirname(ics_path), exist_ok=True)
        with open(ics_path, "w") as f:
            f.writelines(cal)  # ICS library implements __iter__ to produce lines

        QMessageBox.information(self, "Exported",
                                f"Schedule for teacher #{self.teacher_id} exported to {fname}")















class MainWindow(QMainWindow):
    """Main application window with navigation and theming."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scheduler Tool")

        # Window (Stage) Sizing
        # self.resize(1200, 900) # Sets width to 800 and height to 600
        self.setMinimumSize(QSize(1600, 1000)) # Minimum width 400, minimum height 300
        # self.setMaximumSize(QSize(1200, 900)) # Maximum width 1200, maximum height 900


        # Navigation and theming controls
        central = QWidget()
        vlayout = QVBoxLayout(central)
        hlayout = QHBoxLayout()
        self.btn_students = QPushButton("Students")
        self.btn_teachers = QPushButton("Teachers")
        self.btn_teachers.setEnabled(False)
        self.radio_light = QRadioButton("Light")
        self.radio_dark = QRadioButton("Dark")
        self.radio_light.setChecked(True)
        self.radio_light.toggled.connect(self.apply_theme)
        hlayout.addWidget(self.btn_students)
        hlayout.addWidget(self.btn_teachers)
        hlayout.addWidget(self.radio_light)
        hlayout.addWidget(self.radio_dark)
        vlayout.addLayout(hlayout)
        # Stacked widget with pages
        self.stacked = QStackedWidget()
        self.student_page = StudentPage(self)
        self.teacher_page = TeacherPage(self)
        self.schedule_page = SchedulePage(self)
        self.stacked.addWidget(self.student_page)
        self.stacked.addWidget(self.teacher_page)
        self.stacked.addWidget(self.schedule_page)
        vlayout.addWidget(self.stacked)
        self.setCentralWidget(central)
        # Connections
        self.btn_students.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.student_page)
        )
        self.btn_teachers.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.teacher_page)
        )
        # Enable teachers if students exist
        self.check_enable_teachers()
        # force the initial theme to take effect
        # self.apply_theme()

    def apply_theme(self) -> None:
        """Apply selected theme stylesheet."""
        style = LIGHT_CSS if self.radio_light.isChecked() else DARK_CSS
        self.setStyleSheet(style)

    def check_enable_teachers(self) -> None:
        """Enable Teachers button if at least one student exists."""
        enabled = False
        try:
            with open(STUDENTS_CSV, newline='') as f:
                if len(list(csv.reader(f))) > 1:
                    enabled = True
        except FileNotFoundError:
            enabled = False
        self.btn_teachers.setEnabled(enabled)


def main() -> None:
    """Launch the scheduler application."""
    app = QApplication(sys.argv)
    app.setStyleSheet(LIGHT_CSS)   # <- first theme
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
