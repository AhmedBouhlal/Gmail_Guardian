"""
Logging utility for AI Gmail Guardian.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import yaml


def setup_logger(
    name: str = "gmail_guardian",
    config_path: str = "config.yaml",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up logger with configuration from YAML file.
    
    Args:
        name: Logger name
        config_path: Path to configuration file
        log_file: Override log file path
        
    Returns:
        Configured logger instance
    """
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/gmail_guardian.log'
            }
        }
    
    log_config = config.get('logging', {})
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_file_path = log_file or log_config.get('file', 'logs/gmail_guardian.log')
    log_dir = os.path.dirname(log_file_path)
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "gmail_guardian") -> logging.Logger:
    """
    Get logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
