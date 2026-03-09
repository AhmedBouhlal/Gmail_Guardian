"""
Main application entry point for AI Gmail Guardian.
Continuously monitors Gmail account for spam emails.
"""

import os
import sys
import yaml
from typing import Dict

from gmail_client import GmailClient
from spam_detector import SpamDetector
from scheduler import SimpleScheduler
from utils.logger import setup_logger


class GmailGuardian:
    """
    Main application class for AI Gmail Guardian.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Gmail Guardian.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = setup_logger()
        
        # Initialize components
        self.gmail_client = GmailClient(config_path)
        self.spam_detector = SpamDetector()
        self.scheduler = SimpleScheduler(
            check_interval=self.config['gmail']['check_interval']
        )
        
        self.logger.info("AI Gmail Guardian initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing configuration: {e}")
            sys.exit(1)
    
    def initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            True if initialization successful
        """
        self.logger.info("Initializing AI Gmail Guardian components...")
        
        # Authenticate with Gmail
        self.logger.info("Authenticating with Gmail API...")
        if not self.gmail_client.authenticate():
            self.logger.error("Failed to authenticate with Gmail API")
            return False
        
        # Load spam detection model
        self.logger.info("Loading spam detection model...")
        model_path = self.config['model']['path']
        vectorizer_path = self.config['model']['vectorizer']
        
        if not self.spam_detector.load_model(model_path, vectorizer_path):
            self.logger.error("Failed to load spam detection model")
            self.logger.error("Please run 'python train_model.py' first")
            return False
        
        self.logger.info("All components initialized successfully")
        return True
    
    def process_emails(self):
        """
        Process unread emails and classify spam.
        """
        try:
            # Fetch unread messages
            messages = self.gmail_client.fetch_unread_messages()
            
            if not messages:
                self.logger.info("No new emails to process")
                return
            
            self.logger.info(f"Processing {len(messages)} new emails")
            
            spam_count = 0
            processed_count = 0
            
            for message_data in messages:
                try:
                    # Extract message details
                    message = self.gmail_client.get_message_details(message_data)
                    
                    # Combine subject and body for spam detection
                    email_text = f"{message['subject']} {message['body']}"
                    
                    if not email_text.strip():
                        self.logger.debug(f"Empty email content for message {message['id']}")
                        continue
                    
                    # Check if spam
                    is_spam = self.spam_detector.is_spam(email_text)
                    
                    if is_spam:
                        self.logger.info(
                            f"SPAM DETECTED: {message['sender']} - {message['subject']}"
                        )
                        
                        # Label as spam
                        if self.gmail_client.label_as_spam(message['id']):
                            spam_count += 1
                            self.logger.info(f"Labeled message {message['id']} as spam")
                        else:
                            self.logger.error(f"Failed to label message {message['id']} as spam")
                    else:
                        self.logger.debug(
                            f"Not spam: {message['sender']} - {message['subject']}"
                        )
                    
                    # Mark as read to avoid reprocessing
                    self.gmail_client.mark_as_read(message['id'])
                    processed_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    continue
            
            self.logger.info(
                f"Email processing complete: {processed_count} processed, {spam_count} marked as spam"
            )
            
        except Exception as e:
            self.logger.error(f"Error in email processing: {e}")
    
    def start(self):
        """
        Start the email monitoring service.
        """
        self.logger.info("Starting AI Gmail Guardian...")
        
        # Initialize components
        if not self.initialize():
            self.logger.error("Failed to initialize components")
            return
        
        # Start continuous monitoring
        self.logger.info(
            f"Starting continuous email monitoring (check interval: "
            f"{self.config['gmail']['check_interval']} seconds)"
        )
        
        try:
            self.scheduler.run_forever(self.process_emails)
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            self.logger.info("AI Gmail Guardian stopped")
    
    def stop(self):
        """
        Stop the email monitoring service.
        """
        self.logger.info("Stopping AI Gmail Guardian...")
        self.scheduler.stop()


def main():
    """Main entry point."""
    print("=== AI Gmail Guardian ===")
    print("Intelligent Spam Detection for Gmail")
    print()
    
    # Check if model exists
    model_path = "models/model.pkl"
    if not os.path.exists(model_path):
        print("Error: Spam detection model not found!")
        print("Please run 'python train_model.py' first to train the model.")
        sys.exit(1)
    
    # Check if credentials exist
    credentials_path = "credentials.json"
    if not os.path.exists(credentials_path):
        print("Error: Gmail API credentials not found!")
        print("Please download credentials.json from Google Cloud Console")
        print("and place it in the project directory.")
        sys.exit(1)
    
    # Create and start guardian
    guardian = GmailGuardian()
    
    try:
        guardian.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
