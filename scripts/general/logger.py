import logging
import os
from datetime import datetime

def setup_logger(log_name='music_tracker', log_level=logging.INFO):
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create a timestamped log filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(logs_dir, f"{log_name}_{current_date}.log")
    
    # Create and configure logger
    logger = logging.getLogger(log_name)
    
    # Only add handlers if none exist (prevents duplicate handlers)
    if not logger.handlers:
        logger.setLevel(log_level)
        
        # File handler for writing to log file
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Console handler for printing to console
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add both handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Create a default app-wide logger instance that can be imported directly
app_logger = setup_logger()
