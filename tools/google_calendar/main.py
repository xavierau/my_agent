#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line sample for the Calendar API.
Command-line application that retrieves the list of the user's calendars."""
import os
import sys
from datetime import datetime, timedelta
from typing import List

from googleapiclient.errors import HttpError
from oauth2client import client
from googleapiclient import sample_tools


def search_events(query, timeMin, timeMax):
    service = get_service()

    try:
        page_token = None
        while True:

            fetched_events = []

            config = {}

            if timeMin:
                config['timeMin'] = timeMin
            if timeMax:
                config['timeMax'] = timeMax
            if query:
                config['q'] = query

            events = service.events().list(calendarId='primary',
                                           pageToken=page_token,
                                           timeMax=timeMax,
                                           timeMin=timeMin).execute()
            for event in events['items']:
                print(event)
                fetched_events.append(_convert_event(event))
            page_event_token = events.get('nextPageToken')
            if not page_event_token:
                break

        return fetched_events

    except client.AccessTokenRefreshError:
        print(
            "The credentials have been revoked or expired, please re-run"
            "the application to re-authorize."
        )


def get_service():
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        [os.path.dirname(os.path.abspath(__file__))],
        "calendar",
        "v3",
        __doc__,
        __file__,
        scope=[
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events"
        ],
    )
    return service


def _convert_event(event: dict) -> dict:
    return {
        "id": event.get("id", None),
        "summary": event.get("summary", None),
        "start": event.get("start", None),
        "end": event.get("end", None),
        "location": event.get("location", None),
        "attendees": event.get("attendees", None),
        "status": event.get("status", None),
        "htmlLink": event.get("htmlLink", None),
    }


def create_event(summary: str, location: str = None, description: str = None, start: str = None, end: str = None):
    event = {
        'summary': summary,
        'location': location or "",
        'description': description or "",
    }
    if start:
        event['start'] = {'dateTime': start}
    if end:
        event['end'] = {'dateTime': end}

    event = get_service().events().insert(calendarId='primary', body=event).execute()
    return _convert_event(event)


def update_event(event_id: str, summary: str = None, location: str = None, description: str = None, start: str = None,
                 end: str = None):
    # First retrieve the event from the API.
    event = get_service().events().get(calendarId='primary', eventId=event_id).execute()

    if summary:
        event['summary'] = summary
    if location:
        event['location'] = location
    if description:
        event['description'] = description
    if start:
        event['start'] = {'dateTime': start}
    if end:
        event['end'] = {'dateTime': end}

    updated_event = get_service().events().update(calendarId='primary', eventId=event['id'], body=event).execute()

    return _convert_event(updated_event)


def delete_events(event_ids: List[str]):
    for event_id in event_ids:
        get_service().events().delete(calendarId='primary', eventId=event_id).execute()

    return True
