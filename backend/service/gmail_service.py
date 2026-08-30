import os
import base64

from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "credentials.json"
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "token.json"
)


def get_gmail_service():

    creds = None

    # Existing OAuth token
    if os.path.exists(TOKEN_FILE):

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Refresh expired token
    if creds and creds.expired and creds.refresh_token:

        creds.refresh(Request())

    # First-time OAuth login
    if not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES
        )

        creds = flow.run_local_server(
            port=0
        )

        # Save token for future requests
        with open(TOKEN_FILE, "w") as token:

            token.write(
                creds.to_json()
            )

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


def send_email(
    to_email: str,
    subject: str,
    body: str
):

    service = get_gmail_service()

    message = MIMEText(body)

    message["to"] = to_email
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    message_body = {
        "raw": raw_message
    }

    sent_message = service.users().messages().send(
        userId="me",
        body=message_body
    ).execute()

    return sent_message