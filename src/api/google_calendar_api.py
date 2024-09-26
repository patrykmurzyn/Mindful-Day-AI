from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from models.calendar_event_model import CalendarEvent
from typing import List, Optional

class GoogleCalendarAPI:

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self, token_filename: str = 'token_calendar.json', secret_filename: str = 'secret.json'):
        """
        GoogleCalendarAPI constructor to initialize the Calendar service.

        Args:
            token_filename (str): Filename of the token file.
            secret_filename (str): Filename of the client secret file.
        """
        self.current_dir = Path(__file__).resolve().parent
        self.token_path = self.current_dir.parent / 'tokens' / token_filename
        self.secret_path = self.current_dir.parent / 'tokens' / secret_filename
        self.service = self._get_calendar_service()

    def _get_calendar_service(self) -> Optional[any]:
        """
        Authenticates and returns a Google Calendar service object.

        Returns:
            googleapiclient.discovery.Resource: The Google Calendar API service instance.
        Raises:
            RuntimeError: If there is an issue creating the Calendar service.
        """
        creds = self._load_credentials()

        if not creds or not creds.valid:
            creds = self._refresh_or_authorize_credentials(creds)

        try:
            return build('calendar', 'v3', credentials=creds)
        except HttpError as error:
            raise RuntimeError(f'Error while creating the Calendar service: {error}')

    def _load_credentials(self) -> Optional[Credentials]:
        """
        Loads credentials from the token file if it exists.

        Returns:
            Credentials: The loaded credentials, or None if the file doesn't exist.
        """
        if self.token_path.exists():
            return Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
        return None

    def _refresh_or_authorize_credentials(self, creds: Optional[Credentials]) -> Credentials:
        """
        Refreshes or authorizes credentials if they are expired or not found.

        Args:
            creds (Credentials): The current credentials.

        Returns:
            Credentials: The refreshed or newly authorized credentials.
        """
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(self.secret_path), self.SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with self.token_path.open('w') as token_file:
            token_file.write(creds.to_json())

        return creds

    def get_events_for_day(self, date: datetime) -> List[CalendarEvent]:
        """
        Retrieves events for a specific day from the user's primary calendar.

        Args:
            date (datetime): The date for which to retrieve events.

        Returns:
            List[CalendarEvent]: A list of CalendarEvent instances for the given day.

        Raises:
            RuntimeError: If the Calendar service is not available or an error occurs while retrieving events.
        """
        if not self.service:
            raise RuntimeError('Calendar service is not available.')

        start_of_day, end_of_day = self._get_day_time_range(date)

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return self._process_events(events_result.get('items', []))

        except HttpError as error:
            raise RuntimeError(f'Error while retrieving events: {error}')

    def _get_day_time_range(self, date: datetime) -> (str, str):
        """
        Returns the start and end time range for the given day in ISO format.

        Args:
            date (datetime): The date for which to generate the time range.

        Returns:
            Tuple[str, str]: Start and end times of the day in ISO 8601 format.
        """
        start_of_day = datetime.combine(date, datetime.min.time()).isoformat() + 'Z'
        end_of_day = (datetime.combine(date, datetime.max.time()) - timedelta(microseconds=1)).isoformat() + 'Z'
        return start_of_day, end_of_day

    def _process_events(self, events: List[dict]) -> List[CalendarEvent]:
        """
        Processes the raw events from the API response into CalendarEvent instances.

        Args:
            events (List[dict]): List of raw event data from the API.

        Returns:
            List[CalendarEvent]: Processed list of CalendarEvent objects.
        """
        calendar_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))

            calendar_event = CalendarEvent(
                summary=event['summary'],
                start_time=start_time,
                end_time=end_time,
                description=event.get('description')
            )
            calendar_events.append(calendar_event)

        return calendar_events
