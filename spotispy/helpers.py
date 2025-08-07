import logging
import os
from datetime import datetime, timedelta


def get_last_hour_timestamp():
    """Get timestamp for one hour ago (for Spotify API)"""
    current_time = datetime.now()
    previous_hour = current_time.replace(
        minute=0, second=0, microsecond=0) - timedelta(hours=0)
    return int(previous_hour.timestamp() * 1000)


def get_yesterday_timestamp():
    """Get timestamp for 24 hours ago"""
    current_time = datetime.now()
    yesterday = current_time - timedelta(days=1)
    return int(yesterday.timestamp() * 1000)


def get_date_string(days_ago=0):
    """Get ISO date string for N days ago"""
    target_date = datetime.now() - timedelta(days=days_ago)
    return target_date.strftime('%Y-%m-%d')


def setup_logger(log_name='music_tracker', log_level=logging.INFO):
    """
    Set up logging to both file and console
    
    Args:
        log_name: Name for the logger
        log_level: Logging level (default: INFO)
        
    Returns:
        Logger instance
    """
    # Find the project root directory (where logs/ folder should be)
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    logs_dir = os.path.join(project_root, 'logs')

    # Create logs directory if it doesn't exist
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create log file with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(logs_dir, f"{log_name}_{current_date}.log")

    logger = logging.getLogger(log_name)

    # Only set up handlers if they don't already exist
    if not logger.handlers:
        logger.setLevel(log_level)

        # File handler - logs to file
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Console handler - logs to terminal
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Global logger instance that can be imported
_logger = None

def get_logger():
    """Get the global logger instance"""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def format_time_duration(seconds):
    """
    Format seconds into human-readable duration
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted string like "2h 15m" or "45m 30s"
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if secs == 0:
            return f"{minutes}m"
        else:
            return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {minutes}m"


def validate_environment_vars():
    """
    Check that all required environment variables are set
    
    Returns:
        Tuple: (is_valid, missing_vars)
    """
    required_vars = [
        'SPOTIFY_CLIENT_ID',
        'SPOTIFY_CLIENT_SECRET', 
        'SPOTIPY_REDIRECT_URI',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SLACK_BOT_TOKEN'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars


def is_weekend():
    """Check if today is Saturday or Sunday"""
    today = datetime.now().weekday()
    return today >= 5  # Saturday = 5, Sunday = 6


def is_sunday():
    """Check if today is Sunday (for weekly summaries)"""
    return datetime.now().weekday() == 6


def safe_int(value, default=0):
    """Safely convert value to int with fallback"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert value to float with fallback"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def chunks(lst, n):
    """Yield successive n-sized chunks from list"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_config_value(key, default=None):
    """
    Get configuration value from environment with fallback
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    return os.getenv(key, default)


if __name__ == "__main__":
    # Test helper functions
    logger = get_logger()
    logger.info("Testing helper functions...")
    
    # Test timestamp functions
    hour_ago = get_last_hour_timestamp()
    yesterday = get_yesterday_timestamp()
    today_str = get_date_string()
    
    logger.info("Hour ago timestamp: %s", hour_ago)
    logger.info("Yesterday timestamp: %s", yesterday) 
    logger.info("Today date string: %s", today_str)
    
    # Test duration formatting
    test_durations = [45, 125, 3675]
    for duration in test_durations:
        formatted = format_time_duration(duration)
        logger.info("%s seconds = %s", duration, formatted)
    
    # Test environment validation
    is_valid, missing = validate_environment_vars()
    logger.info("Environment valid: %s", is_valid)
    if missing:
        logger.warning("Missing variables: %s", missing)
    
    # Test day checks
    logger.info("Is weekend: %s", is_weekend())
    logger.info("Is Sunday: %s", is_sunday())