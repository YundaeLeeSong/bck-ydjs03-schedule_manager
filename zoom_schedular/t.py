


# pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv

# 1. requests: To perform HTTP requests.
# 2. python-dotenv: To manage your API credentials in a .env file.




## API reference: https://console.cloud.google.com/
# 1. Create a new project (or select an existing one).
# Enable Google Calendar API: `APIs & Services > Library`
# Search for Google Calendar API and enable it.
# Set Up OAuth 2.0 Credentials: `APIs & Services > Credentials > Create Credentials > OAuth Client ID`.
# Choose "Desktop App" or "Web Application" (if you want web-based authorization).






# Create a Service Account:

# Navigate to APIs & Services > Credentials.

# Click Create Credentials > Service Account.

# Give it a name (e.g., google-calendar-service).

# Click Create and Continue.

# Grant the Service Account Access:

# Assign the role: Editor or Calendar Administrator.

# Generate a JSON Key File:

# After creating the service account, go to Keys > Add Key > JSON.

# Download the JSON file (e.g., service_account.json).

# Move JSON File to Your Project Folder:

# Place it in your Python project directory.

# Update your Python script to point to this file.




# Click Create and download the credentials.json file.






from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta



SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        "service_account2.json", scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=creds)
    return service



def create_google_calendar_event(service, meeting_topic, start_time, duration, zoom_link):
    end_time = start_time + timedelta(minutes=duration)
    event = {
        "summary": meeting_topic,
        "description": f"Zoom Meeting Link: {zoom_link}",
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC"  # Adjust if needed
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC"
        },
        "reminders": {
            "useDefault": True,
        },
    }
    event_result = service.events().insert(calendarId="primary", body=event).execute()
    print("Google Calendar Event Created:")
    print("Event link:", event_result.get("htmlLink"))
    return event_result

# Example usage:
if __name__ == "__main__":
    service = get_calendar_service()
    # Example event details:
    meeting_topic = "Sample Meeting"
    # Schedule start_time as an example:
    start_time = datetime(2025, 4, 4, 9, 0)
    duration = 60  # in minutes
    zoom_link = "https://us05web.zoom.us/j/82528473964?pwd=example"
    create_google_calendar_event(service, meeting_topic, start_time, duration, zoom_link)













# ####################################################################################
# ####################################################################################
# ################################### Example 1 ######################################
# ####################################################################################
# ####################################################################################

# from google.oauth2 import service_account
# from googleapiclient.discovery import build

# SCOPES = ["https://www.googleapis.com/auth/calendar"]

# def get_calendar_service():
#     creds = service_account.Credentials.from_service_account_file(
#         "credentials.json", scopes=SCOPES
#     )
#     service = build("calendar", "v3", credentials=creds)
#     return service


# def create_google_calendar_event(meeting_topic, start_time, duration, zoom_link):
#     service = get_calendar_service()
    
#     end_time = start_time + timedelta(minutes=duration)
#     event = {
#         "summary": meeting_topic,
#         "description": f"Zoom Meeting Link: {zoom_link}",
#         "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
#         "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
#         "reminders": {"useDefault": True},
#     }

#     event_result = service.events().insert(calendarId="primary", body=event).execute()
#     print(f"Google Calendar Event Created: {event_result['htmlLink']}")
#     return event_result






# ####################################################################################
# ####################################################################################
# ################################### Example 2 ######################################
# ####################################################################################
# ####################################################################################



# def schedule_meetings(csv_file):
#     token = get_zoom_token()
#     if not token:
#         print("Cannot proceed without a valid access token.")
#         return

#     with open(csv_file, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             start_datetime = datetime.strptime(f"{row['date']} {row['start_time']}", "%Y-%m-%d %H:%M")
#             topic = row['topic']
#             duration = int(row['duration'])

#             # Create Zoom Meeting
#             meeting = create_zoom_meeting(token, topic, start_datetime, duration)
#             if meeting:
#                 zoom_link = meeting.get("join_url")

#                 # Schedule on Google Calendar
#                 create_google_calendar_event(topic, start_datetime, duration, zoom_link)
