"""
Text preprocessing utilities for spam detection.
"""

import re
import string
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and preprocess text for spam detection.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def remove_stopwords(text: str, stopwords: List[str] = None) -> str:
    """
    Remove stopwords from text.
    
    Args:
        text: Input text
        stopwords: List of stopwords to remove
        
    Returns:
        Text with stopwords removed
    """
    if not text:
        return ""
    
    if stopwords is None:
        # Basic English stopwords
        stopwords = [
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
            'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
            'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
            'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
            'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
            'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
            'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above',
            'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        ]
    
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    
    return ' '.join(filtered_words)


def extract_features(text: str) -> dict:
    """
    Extract basic features from text for analysis.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary of extracted features
    """
    if not text:
        return {
            'length': 0,
            'word_count': 0,
            'uppercase_ratio': 0.0,
            'digit_count': 0,
            'special_char_count': 0,
            'url_count': 0,
            'email_count': 0
        }
    
    # Basic text statistics
    length = len(text)
    word_count = len(text.split())
    
    # Uppercase ratio
    uppercase_chars = sum(1 for c in text if c.isupper())
    uppercase_ratio = uppercase_chars / length if length > 0 else 0
    
    # Digit count
    digit_count = sum(1 for c in text if c.isdigit())
    
    # Special character count
    special_chars = string.punctuation
    special_char_count = sum(1 for c in text if c in special_chars)
    
    # URL count
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\,])|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    url_count = len(re.findall(url_pattern, text))
    
    # Email count
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_count = len(re.findall(email_pattern, text))
    
    return {
        'length': length,
        'word_count': word_count,
        'uppercase_ratio': uppercase_ratio,
        'digit_count': digit_count,
        'special_char_count': special_char_count,
        'url_count': url_count,
        'email_count': email_count
    }


def preprocess_email(subject: str, body: str) -> str:
    """
    Preprocess email subject and body for spam detection.
    
    Args:
        subject: Email subject
        body: Email body
        
    Returns:
        Preprocessed text
    """
    # Combine subject and body
    combined_text = f"{subject} {body}"
    
    # Clean the text
    cleaned_text = clean_text(combined_text)
    
    # Remove stopwords
    final_text = remove_stopwords(cleaned_text)
    
    return final_text
