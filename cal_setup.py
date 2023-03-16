from __future__ import print_function

from datetime import datetime,timedelta
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Edge cases to be taken care of:

# Creating:

# What happens if the start or end time is in the past?
# What happens if the start time is after the end time?
# What happens if the user doesn't have permission to create an event on the specified calendar?
# What happens if the event already exists (i.e., same start and end time, summary, attendees, etc.)?
# Updating:

# What happens if the event to be updated doesn't exist?
# What happens if the user doesn't have permission to update the event?
# What happens if the updated start or end time is in the past?
# What happens if the updated start time is after the end time?
# What happens if the update creates a conflict with another event?
# Deleting:

# What happens if the event to be deleted doesn't exist?
# What happens if the user doesn't have permission to delete the event?
# What happens if the event has already been deleted?




# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
def getEventDetails(events):

    formatted_events = []
    for event in events:
        start_time = event['start'].get('dateTime')
        start_date=event['start'].get('date')
        summary = event.get('summary', '')
        attendees = []
        for attendee in event.get('attendees', []):
            attendee_email = attendee.get('email', '')
            attendee_status = attendee.get('responseStatus', '')
            attendees.append({'email': attendee_email, 'status': attendee_status})
        formatted_events.append({'start_time': start_time, 'summary': summary, 'attendees': attendees})

    # Return the formatted events as a JSON string
    return json.dumps(formatted_events)

def modify_event(service,event_id, start_time_str=None, summary=None, description=None, location=None, end_time_str=None, attendees=None):
    # Build the event object with the updated fields
    event = {}
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        event['start'] = {
            'dateTime': start_time_str,
            'timeZone': 'UTC',
        }
    if summary:
        event['summary'] = summary
    if description:
        event['description'] = description
    if location:
        event['location'] = location
    if end_time_str:
        end_time = datetime.fromisoformat(end_time_str)
        event['end'] = {
            'dateTime': end_time_str,
            'timeZone': 'UTC',
        }
    if attendees:
        att_list=[]
        for att in attendees:
            att_list.append({'email':att})
        event['attendees'] = att_list

    # Call the API to update the event
    try:
        event = service.events().patch(calendarId='primary', eventId=event_id, body=event).execute()
        return event
    except HttpError as error:
        print(f"An error occurred: {error}")
    


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Desktop.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # with open('token.json', 'w') as token:
        #     token.write(creds.to_json())



    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow()
        start_time = now
        end_time = now + timedelta(days=7) # get meetings for the next 7 days

        # Get the events from the calendar
        events_result = service.events().list(calendarId='primary', timeMin=start_time.isoformat()+'Z',
                                            timeMax=end_time.isoformat()+'Z', maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        print(getEventDetails(events))

        #modify event
        # event_id = events[0]['id'] 
        # attendees=['kalyan@thenirvanaapp.com','pavan.badam12@gmail.com']
        # summary='Updating Test Title Check'
        # start_time_str=None         
        # description=None
        # location=None
        # end_time_str=None
        # modify_event(service,event_id,summary ,attendees )
        
    except HttpError as error:
        print('An error occurred: %s' % error)


        


if __name__ == '__main__':
    main()
