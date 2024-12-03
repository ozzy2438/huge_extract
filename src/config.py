# Configuration settings for the scraper

class Config:
    # Browser settings
    HEADLESS = True
    IMPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 30

    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    # Output settings
    OUTPUT_DIR = 'data'
    DEFAULT_FILENAME = 'extracted_data.csv'

    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Scraping settings
    BASE_URL = 'https://example.com'  # Replace with target website
    PAGINATION_SELECTOR = '.pagination .next'  # Replace with actual selector
    DATA_SELECTORS = {  # Replace with actual selectors
        'title': '.item-title',
        'price': '.item-price',
        'description': '.item-description'
    }