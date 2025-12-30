from datetime import datetime, timedelta
from icalendar import Calendar, Event
import csv

def create_ics_file(csv_file, ics_filename):
    # # Example usage
    # create_ics_file("zoom_schedule.csv", "zoom_meetings.ics")
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
