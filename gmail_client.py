"""
Gmail API client for AI Gmail Guardian.
Handles authentication, email fetching, and labeling.
"""

import os.path
import pickle
from typing import Dict, List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

import yaml
from utils.logger import get_logger
from utils.helpers import get_email_headers, extract_email_body, clean_sender_email


class GmailClient:
    """
    Gmail API client wrapper for email operations.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    TOKEN_FILE = 'token.pickle'
    CREDENTIALS_FILE = 'credentials.json'
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize Gmail client.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger()
        self.config = self._load_config(config_path)
        self.service: Optional[Resource] = None
        self.spam_label_id: Optional[str] = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                'gmail': {'max_results': 10, 'spam_label': 'SPAM_AI'}
            }
    
    def authenticate(self, credentials_file: str = None) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Args:
            credentials_file: Path to OAuth2 credentials file
            
        Returns:
            True if authentication successful
        """
        creds = None
        credentials_file = credentials_file or self.CREDENTIALS_FILE
        
        # Load existing token
        if os.path.exists(self.TOKEN_FILE):
            try:
                with open(self.TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                self.logger.error(f"Error loading token file: {e}")
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(credentials_file):
                    self.logger.error(
                        f"Credentials file {credentials_file} not found. "
                        "Please download from Google Cloud Console."
                    )
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.logger.error(f"Error during authentication flow: {e}")
                    return False
            
            # Save credentials
            try:
                with open(self.TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                self.logger.error(f"Error saving token file: {e}")
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Successfully authenticated with Gmail API")
            return True
        except Exception as e:
            self.logger.error(f"Error building Gmail service: {e}")
            return False
    
    def _get_or_create_spam_label(self) -> Optional[str]:
        """
        Get or create the SPAM_AI label.
        
        Returns:
            Label ID for spam label
        """
        try:
            # Try to find existing label
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            spam_label_name = self.config['gmail']['spam_label']
            
            for label in labels:
                if label['name'] == spam_label_name:
                    self.logger.info(f"Found existing label: {spam_label_name}")
                    return label['id']
            
            # Create new label
            label_object = {
                'name': spam_label_name,
                'messageListVisibility': 'show',
                'labelListVisibility': 'labelShow'
            }
            
            created_label = self.service.users().labels().create(
                userId='me', body=label_object
            ).execute()
            
            self.logger.info(f"Created new label: {spam_label_name}")
            return created_label['id']
            
        except HttpError as e:
            self.logger.error(f"Error managing labels: {e}")
            return None
    
    def fetch_unread_messages(self) -> List[Dict]:
        """
        Fetch unread messages from Gmail.
        
        Returns:
            List of message dictionaries
        """
        if not self.service:
            self.logger.error("Gmail service not initialized")
            return []
        
        try:
            # Get unread messages
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD'],
                maxResults=self.config['gmail']['max_results']
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                self.logger.info("No unread messages found")
                return []
            
            full_messages = []
            for message in messages:
                try:
                    msg = self.service.users().messages().get(
                        userId='me', id=message['id'], format='full'
                    ).execute()
                    full_messages.append(msg)
                except HttpError as e:
                    self.logger.error(f"Error fetching message {message['id']}: {e}")
                    continue
            
            self.logger.info(f"Fetched {len(full_messages)} unread messages")
            return full_messages
            
        except HttpError as e:
            self.logger.error(f"Error fetching messages: {e}")
            return []
    
    def get_message_details(self, message_data: Dict) -> Dict:
        """
        Extract details from message data.
        
        Args:
            message_data: Gmail message data
            
        Returns:
            Dictionary with message details
        """
        headers = get_email_headers(message_data)
        body = extract_email_body(message_data)
        
        return {
            'id': message_data['id'],
            'thread_id': message_data.get('threadId'),
            'subject': headers.get('subject', ''),
            'sender': headers.get('from', ''),
            'sender_email': clean_sender_email(headers.get('from', '')),
            'date': headers.get('date', ''),
            'body': body,
            'snippet': message_data.get('snippet', '')
        }
    
    def label_as_spam(self, message_id: str) -> bool:
        """
        Apply spam label to a message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            True if labeling successful
        """
        if not self.service:
            self.logger.error("Gmail service not initialized")
            return False
        
        try:
            # Get or create spam label
            if not self.spam_label_id:
                self.spam_label_id = self._get_or_create_spam_label()
                if not self.spam_label_id:
                    return False
            
            # Apply label
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [self.spam_label_id]}
            ).execute()
            
            self.logger.info(f"Applied spam label to message {message_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Error labeling message {message_id}: {e}")
            return False
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark message as read.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            True if marking successful
        """
        if not self.service:
            self.logger.error("Gmail service not initialized")
            return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            self.logger.debug(f"Marked message {message_id} as read")
            return True
            
        except HttpError as e:
            self.logger.error(f"Error marking message {message_id} as read: {e}")
            return False
