import csv
from datetime import datetime, timedelta

input_file = 'zoom_schedule.csv'
output_file = 'zoom_schedule_full_week.csv'

# Read the original schedule
with open(input_file, newline='') as csvfile:
    reader = list(csv.DictReader(csvfile))
    base_date = datetime.strptime(reader[0]['date'], '%Y-%m-%d')

# Generate schedule for 7 days
rows = []
for i in range(7):
    day = base_date + timedelta(days=i)
    for row in reader:
        new_row = row.copy()
        new_row['date'] = day.strftime('%Y-%m-%d')
        rows.append(new_row)

# Write to new CSV
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=reader[0].keys())
    writer.writeheader()
    writer.writerows(rows)