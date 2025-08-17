import os
import pickle
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Use this scope to read and write calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_with_oauth():
    """Authenticate and create a Google Calendar service using OAuth 2.0."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def add_event(service, summary, location=None, description=None, start_time=None, end_time=None, attendees=None, reminders=None):
    """Function to add an event with provided details."""
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,  
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [{'email': attendee} for attendee in attendees] if attendees else [],
        'reminders': reminders if reminders else {
            'useDefault': True,
        },
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event_result.get("htmlLink")}')
    return event_result.get("id")  

def delete_event(service, event_id):
    """Function to delete an event by its event ID."""
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f'Event with ID {event_id} has been deleted.')
    except Exception as e:
        print(f'An error occurred: {e}')

def list_events(service):
    """List the next 10 events from the user's calendar."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'  
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f'{start} - {event["summary"]} - {event["id"]}')

