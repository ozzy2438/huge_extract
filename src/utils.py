import time
from functools import wraps
import logging

def retry_decorator(max_retries=3, delay=1):
    """Decorator for retrying functions that might fail."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    logging.warning(
                        f'Attempt {retries} failed: {str(e)}. Retrying...'
                    )
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def validate_config(config):
    """Validate configuration settings."""
    required_fields = ['BASE_URL', 'PAGINATION_SELECTOR', 'DATA_SELECTORS']
    for field in required_fields:
        if not hasattr(config, field):
            raise ValueError(f'Missing required config field: {field}')
    
    if not isinstance(config.DATA_SELECTORS, dict):
        raise ValueError('DATA_SELECTORS must be a dictionary')

def format_data(data):
    """Format extracted data before saving."""
    if not data:
        return []

    formatted_data = []
    for item in data:
        if isinstance(item, dict):
            formatted_data.append(item)
        else:
            formatted_data.append({'value': str(item)})
    return formatted_data