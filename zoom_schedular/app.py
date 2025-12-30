"""
Usage: python app.py
"""
# pip install requests python-dotenv google-auth
# 1. requests: To perform HTTP requests.
# 2. python-dotenv: To manage your API credentials in a .env file.

## API reference: https://marketplace.zoom.us/user/build





####################################################################################
####################################################################################
################################### Example 1 ######################################
####################################################################################
####################################################################################


# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()
# account_id = os.getenv("ZOOM_ACCOUNT_ID")
# client_id = os.getenv("ZOOM_CLIENT_ID")
# client_secret = os.getenv("ZOOM_CLIENT_SECRET")

# print(account_id)
# print(client_id)
# print(client_secret)


# def get_zoom_token():
#     token_url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
#     auth = (client_id, client_secret)
#     response = requests.post(token_url, auth=auth)
#     print(response)
#     if response.status_code == 200:
#         token = response.json()["access_token"]
#         print(token)
#         return token
#     else:
#         print("Error getting token:", response.text)
#         return None

# # Example usage:
# if __name__ == "__main__":
#     token = get_zoom_token()
#     if token:
#         print("Access token acquired!")








from datetime import datetime, timedelta
from icalendar import Calendar, Event


# from google.oauth2 import service_account
# from googleapiclient.discovery import build


####################################################################################
####################################################################################
################################### Example 2 ######################################
####################################################################################
####################################################################################
import csv
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv


load_dotenv()









# Function to get access token
def get_zoom_token():
    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    account_id = os.getenv("ZOOM_ACCOUNT_ID")
    token_url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
    auth = (client_id, client_secret)
    response = requests.post(token_url, auth=auth)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(token)  ########################### test
        return token
    else:
        print("Error getting token:", response.text)
        return None

# Function to create a Zoom meeting
def create_zoom_meeting(token, topic, start_time, duration):
    url = "https://api.zoom.us/v2/users/me/meetings"
    payload = {
        "topic": topic,
        "type": 2,  # Type 2 means a scheduled meeting
        "start_time": start_time.isoformat(),
        "duration": duration,
        "timezone": os.getenv("TIMEZONE"),  # Adjust if necessary
        "agenda": "Meeting scheduled via server-to-server OAuth"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        meeting = response.json()
        # print(meeting) ################ test
        print(f"Meeting '{topic}' created. Join URL: {meeting.get('join_url')}")
        return meeting
    else:
        print("Error creating meeting:", response.text)
        return None

# Main function to read CSV and create meetings
def schedule_meetings(csv_file):
    token = get_zoom_token()
    if not token:
        print("Cannot proceed without a valid access token.")
        return

    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print(reader) ########################### test
        for row in reader:
            print(row) ########################### test
            # Convert CSV date and time to a datetime object
            start_datetime = datetime.strptime(f"{row['date']} {row['start_time']}", "%Y-%m-%d %H:%M")
            topic = row['topic']
            duration = int(row['duration'])

            # Create Zoom Meeting
            meeting = create_zoom_meeting(token, topic, start_datetime, duration)
            if meeting:
                zoom_link = meeting.get("join_url")


                # # Schedule on Google Calendar
                # create_google_calendar_event(topic, start_datetime, duration, zoom_link)

                # create ICO files
        create_ics_file(f'{csv_file}', f'{csv_file}.ics')




# Explanation:
# Token Acquisition:
# The script first obtains an access token using your Server-to-Server credentials.

# CSV Reading:
# It then reads your CSV file, parsing the date and time into Python’s datetime objects.

# Meeting Creation:
# For each row in the CSV, it makes a POST request to create a scheduled meeting using the Zoom API. The meeting details (like topic, start time, and duration) are sent in the payload.

















####################################################################################
####################################################################################
################################### Example 3 Google ######################################
####################################################################################
####################################################################################





# from google.oauth2 import service_account
# from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=creds)
    return service


def create_google_calendar_event(meeting_topic, start_time, duration, zoom_link):
    service = get_calendar_service()
    
    end_time = start_time + timedelta(minutes=duration)
    event = {
        "summary": meeting_topic,
        "description": f"Zoom Meeting Link: {zoom_link}",
        "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
        "reminders": {"useDefault": True},
    }

    event_result = service.events().insert(calendarId="primary", body=event).execute()
    print(event_result)
    print(f"Google Calendar Event Created: {event_result['htmlLink']}")
    return event_result
















####################################################################################
####################################################################################
################################### Example 4 ICS ######################################
####################################################################################
####################################################################################







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







if __name__ == "__main__":
    schedule_meetings('zoom_schedule.csv')

