import logging
import os
from datetime import datetime

def setup_logger(log_name='music_tracker', log_level=logging.INFO):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    logs_dir = os.path.join(repo_root, 'logs')

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(logs_dir, f"{log_name}_{current_date}.log")

    logger = logging.getLogger(log_name)

    if not logger.handlers:
        logger.setLevel(log_level)

        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Create a default app-wide logger instance that can be imported directly
app_logger = setup_logger()
