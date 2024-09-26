from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from models.task_model import Task
from typing import List, Optional

class GoogleTasksAPI:

    SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

    def __init__(self, token_filename: str = 'token_tasks.json', secret_filename: str = 'secret.json'):
        """
        Initializes the GoogleTasksAPI class and sets up the service.

        Args:
            token_filename (str): Filename of the token file.
            secret_filename (str): Filename of the client secret file.
        """
        self.current_dir = Path(__file__).resolve().parent
        self.token_path = Path(__file__).resolve().parent.parent / 'tokens' / token_filename
        self.secret_path = Path(__file__).resolve().parent.parent / 'tokens' / secret_filename
        self.service = self._get_tasks_service()

    def _get_tasks_service(self) -> Optional[any]:
        """
        Authenticates and returns a Google Tasks service object.

        Returns:
            googleapiclient.discovery.Resource: The Google Tasks API service instance.
        Raises:
            RuntimeError: If an error occurs while creating the service.
        """
        creds = self._load_credentials()

        if not creds or not creds.valid:
            creds = self._refresh_or_authorize_credentials(creds)

        try:
            return build('tasks', 'v1', credentials=creds)
        except HttpError as error:
            raise RuntimeError(f'An error occurred while creating the service: {error}')

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

    def get_tasks(self, list_id: str = '@default') -> List[Task]:
        """
        Retrieves tasks from a specified task list.

        Args:
            list_id (str): The task list ID to retrieve tasks from.

        Returns:
            List[Task]: A list of Task instances for the given task list.

        Raises:
            RuntimeError: If the tasks service is not available or an error occurs while retrieving tasks.
        """
        if not self.service:
            raise RuntimeError('Tasks service is not available.')

        try:
            results = self.service.tasks().list(tasklist=list_id, showCompleted=True).execute()
            items = results.get('items', [])

            return self._process_tasks(items)

        except HttpError as error:
            raise RuntimeError(f'An error occurred while retrieving tasks: {error}')

    def _process_tasks(self, items: List[dict]) -> List[Task]:
        """
        Processes the raw task data into Task instances.

        Args:
            items (List[dict]): List of raw task data from the API.

        Returns:
            List[Task]: Processed list of Task objects.
        """
        tasks = []
        for item in items:
            due = None
            if 'due' in item:
                due = datetime.fromisoformat(item['due'].replace('Z', '+00:00'))

            task = Task(
                id=item['id'],
                title=item['title'],
                notes=item.get('notes'),
                due=due,
                status=item['status']
            )
            tasks.append(task)

        return tasks
