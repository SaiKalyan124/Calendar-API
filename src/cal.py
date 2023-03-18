from __future__ import print_function
import pytz
import os.path
import json
from datetime import datetime, time,timedelta
from dateutil import tz
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
class UserInput(BaseModel):
    inputValue: str
    pickedDate: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'Desktop.json', SCOPES)
        creds = flow.run_local_server(port=0)


service = build('calendar', 'v3', credentials=creds)



@app.post("/user/")
def create_user(user_input: UserInput):
    input_value = user_input.inputValue
    picked_date = user_input.pickedDate
    utc_date = datetime.fromisoformat(picked_date).replace(tzinfo=tz.tzutc())

    # Convert the UTC datetime to the local time zone
    local_date = utc_date.astimezone(tz.tzlocal())

    # Format the local datetime as a string in the same format as datetime.now()
    local_date_str = local_date.strftime('%Y-%m-%d %H:%M:%S.%f')
    local_date_obj = datetime.strptime(local_date_str, '%Y-%m-%d %H:%M:%S.%f').date()
    
    availble_time_slots=find_available_time_slots(get_calendar('primary',service),get_calendar(input_value,service),local_date_obj)
    print(availble_time_slots)
    

    return [{"start_time": slot["start_time"], "end_time": slot["end_time"]} for slot in availble_time_slots]



def get_calendar(calendar_id, service):


    pacific_tz = pytz.timezone('US/Pacific')
    # Define the date range for the events you want to retrieve
    now = datetime.now(pacific_tz)
    start_date = now
    start_time = datetime.combine(start_date, time(hour=9))
    end_time = datetime.combine(start_date, time(hour=17)) 
    time_min = start_time.astimezone(pacific_tz).isoformat()
    time_max = end_time.astimezone(pacific_tz).isoformat()

    # Retrieve events from Google Calendar API
    events_result = service.events().list(calendarId=calendar_id, timeMin=time_min,
                                        timeMax=time_max, maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    # print(events)

    event_dict = {}
    for event in events:
        start_time = datetime.fromisoformat(event['start']['dateTime']).astimezone(pacific_tz)
        end_time = datetime.fromisoformat(event['end']['dateTime']).astimezone(pacific_tz)
        event_date = start_time.date()
        event_start_time = start_time.time()
        event_end_time=end_time.time()
        # event_duration = (end_time - start_time).total_seconds() // 60  # duration in minutes
        
        if event_date not in event_dict:
            event_dict[event_date] = []
            
        event_dict[event_date].append({'start_time': event_start_time, 'end_time': event_end_time})

    return event_dict

def find_available_time_slots(dict1, dict2, current_date):
    # Set the start and end times for the day
    print(current_date)
    start_time = datetime.combine(current_date, time(hour=9))
    end_time = datetime.combine(current_date, time(hour=17))
    
    # Create a list of all 30-minute time slots for the day
    time_slots = []
    current_time = start_time
    while current_time < end_time:
        time_slots.append(current_time.time())
        current_time += timedelta(minutes=30)
    
    # Get calendar1 schedule
    start_end_times_calendar_1 = {}
    for date, slots in dict1.items():
        start_end_times_calendar_1[date] = []
        for slot in slots:
            start_end_times_calendar_1[date].append({'start_time': slot['start_time'], 'end_time': slot['end_time']})

    # Get calendar2 schedule
    start_end_times_calendar_2 = {}
    for date, slots in dict2.items():
        start_end_times_calendar_2[date] = []
        for slot in slots:
            start_end_times_calendar_2[date].append({'start_time': slot['start_time'], 'end_time': slot['end_time']})

   
    # Find available time slots
    busy_slots = []
    for schedule in [start_end_times_calendar_1, start_end_times_calendar_2]:
        for date, slots in schedule.items():
            for slot in slots:
                start_time = datetime.combine(date, slot['start_time'])
                end_time = datetime.combine(date, slot['end_time'])
                busy_slots.append((start_time, end_time))

    available_slots = []
    for i in range(len(time_slots)-1):
        gap_start = datetime.combine(current_date, time_slots[i])
        gap_end = datetime.combine(current_date, time_slots[i+1])
        is_busy = False
        for busy_start, busy_end in busy_slots:
            if busy_start <= gap_start < busy_end or busy_start < gap_end <= busy_end:
                is_busy = True
                break
        if not is_busy:
            if gap_end - gap_start >= timedelta(minutes=30):
                available_slots.append({'start_time': gap_start.time(), 'end_time': gap_end.time()})
    print("calendar1:",start_end_times_calendar_1)
    print("calendar2:",start_end_times_calendar_2)
    return available_slots




def main():
    get_calendar('primary',service)
    get_calendar('pavan.badam12@gmail.com',service)
    print(find_available_time_slots(get_calendar('primary',service),get_calendar('pavan.badam12@gmail.com',service),datetime.now()))


if __name__ == '__main__':
    main()





    

# def getEventDetails(events):

#     formatted_events = []
#     for event in events:
#         start_time = event['start'].get('dateTime')
#         start_date=event['start'].get('date')
#         summary = event.get('summary', '')
#         attendees = []
#         for attendee in event.get('attendees', []):
#             attendee_email = attendee.get('email', '')
#             attendee_status = attendee.get('responseStatus', '')
#             attendees.append({'email': attendee_email, 'status': attendee_status})
#         formatted_events.append({'start_time': start_time, 'summary': summary, 'attendees': attendees})

#     # Return the formatted events as a JSON string
#     return json.dumps(formatted_events)

# def modify_event(service,event_id, start_time_str=None, summary=None, description=None, location=None, end_time_str=None, attendees=None):
#     # Build the event object with the updated fields
#     event = {}
#     if start_time_str:
#         start_time = datetime.fromisoformat(start_time_str)
#         event['start'] = {
#             'dateTime': start_time_str,
#             'timeZone': 'UTC',
#         }
#     if summary:
#         event['summary'] = summary
#     if description:
#         event['description'] = description
#     if location:
#         event['location'] = location
#     if end_time_str:
#         end_time = datetime.fromisoformat(end_time_str)
#         event['end'] = {
#             'dateTime': end_time_str,
#             'timeZone': 'UTC',
#         }
#     if attendees:
#         att_list=[]
#         for att in attendees:
#             att_list.append({'email':att})
#         event['attendees'] = att_list

#     # Call the API to update the event
#     try:
#         event = service.events().patch(calendarId='primary', eventId=event_id, body=event).execute()
#         return event
#     except HttpError as error:
#         print(f"An error occurred: {error}")
