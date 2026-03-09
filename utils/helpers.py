"""
Helper utilities for AI Gmail Guardian.
"""

import base64
import re
from typing import Dict, List, Optional
import email
from email.message import Message


def decode_base64(data: str) -> str:
    """
    Decode base64 encoded string.
    
    Args:
        data: Base64 encoded string
        
    Returns:
        Decoded string
    """
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except Exception:
        return ""


def extract_email_body(message_data: Dict) -> str:
    """
    Extract email body from Gmail message data.
    
    Args:
        message_data: Gmail message data dictionary
        
    Returns:
        Email body text
    """
    try:
        payload = message_data.get('payload', {})
        parts = payload.get('parts', [])
        
        # Handle single part messages
        if not parts:
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                return decode_base64(body_data)
        
        # Handle multipart messages
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                body_data = part.get('body', {}).get('data', '')
                if body_data:
                    return decode_base64(body_data)
        
        # Fallback to HTML if no plain text found
        for part in parts:
            if part.get('mimeType') == 'text/html':
                body_data = part.get('body', {}).get('data', '')
                if body_data:
                    html_content = decode_base64(body_data)
                    # Remove HTML tags
                    return re.sub(r'<[^>]+>', '', html_content)
        
        return ""
    
    except Exception:
        return ""


def get_email_headers(message_data: Dict) -> Dict[str, str]:
    """
    Extract email headers from Gmail message data.
    
    Args:
        message_data: Gmail message data dictionary
        
    Returns:
        Dictionary of email headers
    """
    headers = {}
    try:
        for header in message_data.get('payload', {}).get('headers', []):
            name = header.get('name', '').lower()
            value = header.get('value', '')
            headers[name] = value
        return headers
    except Exception:
        return {}


def clean_sender_email(sender: str) -> str:
    """
    Extract email address from sender string.
    
    Args:
        sender: Sender string (e.g., "John Doe <john@example.com>")
        
    Returns:
        Clean email address
    """
    # Extract email from angle brackets
    match = re.search(r'<([^>]+)>', sender)
    if match:
        return match.group(1).strip()
    
    # If no angle brackets, check if it's already an email
    if '@' in sender:
        return sender.strip()
    
    return sender


def is_valid_email(email_str: str) -> bool:
    """
    Validate email format.
    
    Args:
        email_str: Email string to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email_str))


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_message_summary(message_data: Dict) -> str:
    """
    Get a summary of the email message.
    
    Args:
        message_data: Gmail message data dictionary
        
    Returns:
        Message summary string
    """
    headers = get_email_headers(message_data)
    subject = headers.get('subject', 'No Subject')
    sender = headers.get('from', 'Unknown Sender')
    body = extract_email_body(message_data)
    
    return f"From: {sender}\nSubject: {subject}\nBody: {truncate_text(body, 200)}"
