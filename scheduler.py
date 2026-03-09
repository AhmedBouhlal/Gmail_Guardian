"""
Scheduler module for continuous email monitoring.
"""

import time
import schedule
from typing import Callable, Optional
from threading import Thread
import signal
import sys

from utils.logger import get_logger


class EmailScheduler:
    """
    Scheduler for continuous email monitoring and processing.
    """
    
    def __init__(self, check_interval: int = 300):
        """
        Initialize scheduler.
        
        Args:
            check_interval: Interval in seconds between email checks (default: 5 minutes)
        """
        self.logger = get_logger()
        self.check_interval = check_interval
        self.running = False
        self.scheduler_thread: Optional[Thread] = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def _run_scheduler(self):
        """Run the scheduler in a continuous loop."""
        self.logger.info("Scheduler started")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)  # Wait before retrying
        
        self.logger.info("Scheduler stopped")
    
    def _check_emails_job(self, check_function: Callable):
        """
        Job function to check emails.
        
        Args:
            check_function: Function to call for checking emails
        """
        try:
            self.logger.info("Starting scheduled email check")
            check_function()
            self.logger.info("Email check completed")
        except Exception as e:
            self.logger.error(f"Error during email check: {e}")
    
    def add_email_check_job(self, check_function: Callable):
        """
        Add email checking job to scheduler.
        
        Args:
            check_function: Function to call for checking emails
        """
        job = schedule.every(self.check_interval).seconds.do(
            self._check_emails_job, check_function
        )
        self.logger.info(f"Scheduled email check every {self.check_interval} seconds")
        return job
    
    def start(self, check_function: Callable):
        """
        Start the scheduler.
        
        Args:
            check_function: Function to call for checking emails
        """
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        # Add the email checking job
        self.add_email_check_job(check_function)
        
        # Start scheduler in a separate thread
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Email scheduler started successfully")
        
        # Run initial check immediately
        try:
            self.logger.info("Running initial email check")
            check_function()
        except Exception as e:
            self.logger.error(f"Error during initial email check: {e}")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.running = False
        
        # Clear all scheduled jobs
        schedule.clear()
        
        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Scheduler stopped")
    
    def run_forever(self, check_function: Callable):
        """
        Run the scheduler forever (blocking call).
        
        Args:
            check_function: Function to call for checking emails
        """
        self.start(check_function)
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop()
    
    def get_next_run_time(self):
        """
        Get the next scheduled run time.
        
        Returns:
            Next run time as string or None
        """
        jobs = schedule.get_jobs()
        if jobs:
            return str(jobs[0].next_run)
        return None
    
    def get_job_count(self):
        """
        Get the number of scheduled jobs.
        
        Returns:
            Number of scheduled jobs
        """
        return len(schedule.get_jobs())


class SimpleScheduler:
    """
    Simple scheduler implementation without external dependencies.
    """
    
    def __init__(self, check_interval: int = 300):
        """
        Initialize simple scheduler.
        
        Args:
            check_interval: Interval in seconds between checks
        """
        self.logger = get_logger()
        self.check_interval = check_interval
        self.running = False
    
    def run_forever(self, check_function: Callable):
        """
        Run the check function continuously.
        
        Args:
            check_function: Function to call for checking emails
        """
        self.running = True
        self.logger.info(f"Starting simple scheduler with {self.check_interval}s interval")
        
        try:
            while self.running:
                try:
                    self.logger.info("Starting email check")
                    check_function()
                    self.logger.info(f"Email check completed, waiting {self.check_interval}s")
                except Exception as e:
                    self.logger.error(f"Error during email check: {e}")
                
                # Sleep in small increments to allow for faster shutdown
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.running = False
            self.logger.info("Simple scheduler stopped")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
