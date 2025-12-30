# Automate Zoom Schedule and Google Calendar Import

This guide explains how to automate Zoom meeting scheduling using a CSV file and how to generate ICS and CSV files for manual import into Google Calendar.

---

## 1️⃣ Generate an ICS File for Google Calendar

Google Calendar supports **iCalendar (.ics) files**, which can be imported to add events.

### **📌 Python Script to Create an ICS File**
```python
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import csv

def create_ics_file(csv_file, ics_filename):
    cal = Calendar()

    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            event = Event()
            start_datetime = datetime.strptime(f"{row['date']} {row['start_time']}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=int(row['duration']))
            
            event.add("summary", row["topic"])
            event.add("dtstart", start_datetime)
            event.add("dtend", end_datetime)
            event.add("dtstamp", datetime.now())
            event.add("description", f"Zoom Meeting Link: {row.get('zoom_link', 'No Link')}")

            cal.add_component(event)

    with open(ics_filename, "wb") as f:
        f.write(cal.to_ical())

    print(f"ICS file '{ics_filename}' created successfully!")

# Example usage
create_ics_file("zoom_schedule.csv", "zoom_meetings.ics")
```

### **🛠 Steps to Import the ICS File into Google Calendar:**
1. Generate `zoom_meetings.ics` using the script.
2. Open **Google Calendar**.
3. Click on the **gear icon** → **Settings**.
4. Under "Import & Export," select **Import**.
5. Choose `zoom_meetings.ics` and import it.

---

## 2️⃣ Generate a CSV File for Google Calendar

Google Calendar allows importing **CSV files** with a specific format.

### **📌 Python Script to Create a CSV File for Google Calendar**
```python
import csv
from datetime import datetime, timedelta

def create_google_calendar_csv(csv_file, output_csv):
    fieldnames = ["Subject", "Start Date", "Start Time", "End Date", "End Time", "All Day Event", "Description", "Location"]

    with open(csv_file, newline='') as csvfile, open(output_csv, "w", newline='') as outcsv:
        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(outcsv, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            start_datetime = datetime.strptime(f"{row['date']} {row['start_time']}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=int(row['duration']))
            
            writer.writerow({
                "Subject": row["topic"],
                "Start Date": start_datetime.strftime("%m/%d/%Y"),
                "Start Time": start_datetime.strftime("%I:%M %p"),
                "End Date": end_datetime.strftime("%m/%d/%Y"),
                "End Time": end_datetime.strftime("%I:%M %p"),
                "All Day Event": "False",
                "Description": f"Zoom Meeting Link: {row.get('zoom_link', 'No Link')}",
                "Location": "Online"
            })

    print(f"CSV file '{output_csv}' created successfully!")

# Example usage
create_google_calendar_csv("zoom_schedule.csv", "zoom_meetings_google.csv")
```

### **🛠 Steps to Import the CSV File into Google Calendar:**
1. Generate `zoom_meetings_google.csv` using the script.
2. Open **Google Calendar**.
3. Click on the **gear icon** → **Settings**.
4. Under "Import & Export," select **Import**.
5. Choose `zoom_meetings_google.csv` and import it.

---

## **📌 Which One Should You Use?**
| Method | Pros | Cons |
|---------|------|------|
| **ICS File** | Supports event descriptions, recurring events, and proper timezones. | More complex structure. |
| **CSV File** | Easier to edit manually in Excel, directly importable. | Limited in features like recurring events. |

If you need recurring meetings or detailed descriptions, **ICS format** is recommended. Otherwise, CSV is a simple and effective alternative.

Let me know if you need modifications! 🚀

