from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
from email.mime.multipart import MIMEMultipart
import json

class GmailAPI:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, token_filename: str = 'token_gmail.json', secret_filename: str = 'secret.json'):
        """
        GmailAPI constructor to initialize the Gmail service.

        Args:
            token_filename (str): Filename of the token file.
            secret_filename (str): Filename of the client secret file.
        """
        self.current_dir = Path(__file__).resolve().parent
        self.token_path = Path(__file__).resolve().parent.parent / 'tokens' / token_filename
        self.secret_path = Path(__file__).resolve().parent.parent / 'tokens' / secret_filename
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """
        Authenticates and returns a Google Gmail service object.

        Returns:
            googleapiclient.discovery.Resource: The Google Gmail API service instance.
        Raises:
            RuntimeError: If there is an issue creating the Gmail service.
        """
        creds = self._load_credentials()

        if not creds or not creds.valid:
            creds = self._refresh_or_authorize_credentials(creds)

        try:
            return build('gmail', 'v1', credentials=creds)
        except HttpError as error:
            raise RuntimeError(f'An error occurred while creating the service: {error}')

    def _load_credentials(self) -> Credentials:
        """
        Loads credentials from the token file if it exists.

        Returns:
            Credentials: The loaded credentials.
        """
        if self.token_path.exists():
            return Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
        return None

    def _refresh_or_authorize_credentials(self, creds: Credentials) -> Credentials:
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
    
    def _create_html_content(self, ai_response: str) -> str:
        """
        Creates HTML content for the email using the AI response data.

        Args:
            ai_response (str): The AI response containing the data for the email as a JSON string.

        Returns:
            str: The HTML content of the email.
        """
        try:
            ai_response_dict = json.loads(ai_response)
        except json.JSONDecodeError:
            return "<h1>Error in generating content</h1><p>There was an error processing your daily schedule and weather update.</p>"

        try:
            with open('email_template.html', 'r') as file:
                template = file.read()
        except FileNotFoundError:
            return "<h1>Error in generating content</h1><p>There was an error processing your daily schedule and weather update.</p>"
        
        schedule_items = ""
        for hour, activity in ai_response_dict.get('plan', {}).get('hours', {}).items():
            schedule_items += f'<div class="schedule-item"><span class="time">{hour}:00</span> - {activity}</div>\n'
        
        break_items = ""
        for break_info in ai_response_dict.get('break_recommendations', []):
            break_items += f'<div class="break"><strong>{break_info["time"]}</strong> ({break_info["duration"]}): {break_info["activity"]}</div>\n'
        
        try:
            html_content = template.format(
                summary=ai_response_dict.get('summary', 'No summary available'),
                today_fact=ai_response_dict.get('today_fact', 'No fact available'),
                schedule_items=schedule_items,
                break_items=break_items
            )
        except KeyError as e:
            return "<h1>Error in generating content</h1><p>There was an error processing your daily schedule and weather update.</p>"
        
        return html_content

    def send_email(self, to: str, subject: str, ai_response: str):
        """
        Sends an HTML email using the Gmail API with data from AI response.

        Args:
            to (str): The recipient email address.
            subject (str): The subject of the email.
            ai_response (str): The AI response containing the data for the email as a JSON string.

        Returns:
            dict: The response from the Gmail API containing the message ID.

        Raises:
            RuntimeError: If the Gmail service is not available or an error occurs while sending the email.
        """
        if not self.service:
            raise RuntimeError('Gmail service is not available.')

        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject

        html_content = self._create_html_content(ai_response)
        
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        try:
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            message_response = self.service.users().messages().send(
                userId='me', 
                body={'raw': raw_message}
            ).execute()
            return message_response
        except HttpError as error:
            raise RuntimeError(f'An error occurred while sending email: {error}')