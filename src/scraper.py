from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from retrying import retry
import pandas as pd
import logging
import os
from config import Config

class WebScraper:
    def __init__(self, config=None):
        self.config = config or Config()
        self.setup_logging()
        self.data = []
        self.driver = None

    def setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format=self.config.LOG_FORMAT
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        """Initialize and configure the Chrome WebDriver."""
        chrome_options = Options()
        if self.config.HEADLESS:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
        self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)

    @retry(stop_max_attempt_number=Config.MAX_RETRIES, wait_fixed=Config.RETRY_DELAY * 1000)
    def navigate_to_page(self, url):
        """Navigate to a given URL with retry logic."""
        try:
            self.driver.get(url)
            return True
        except TimeoutException as e:
            self.logger.error(f'Failed to load page: {url}. Error: {str(e)}')
            raise

    def extract_element_data(self, selector, element=None):
        """Extract data from an element using a CSS selector."""
        try:
            target = element or self.driver
            element = target.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            self.logger.warning(f'Element not found with selector: {selector}')
            return None

    def has_next_page(self):
        """Check if there is a next page available."""
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR, self.config.PAGINATION_SELECTOR
            )
            return next_button.is_enabled() and 'disabled' not in next_button.get_attribute('class')
        except NoSuchElementException:
            return False

    def extract_page_data(self):
        """Extract data from the current page."""
        items = []
        try:
            for selector, data_selector in self.config.DATA_SELECTORS.items():
                value = self.extract_element_data(data_selector)
                if value:
                    items.append({selector: value})
            return items
        except Exception as e:
            self.logger.error(f'Error extracting page data: {str(e)}')
            return []

    def scrape(self):
        """Main scraping method."""
        try:
            self.setup_driver()
            self.navigate_to_page(self.config.BASE_URL)

            while True:
                page_data = self.extract_page_data()
                self.data.extend(page_data)
                self.logger.info(f'Extracted {len(page_data)} items from current page')

                if not self.has_next_page():
                    break

                self.navigate_to_page(self.get_next_page_url())

            return self.save_data()

        except Exception as e:
            self.logger.error(f'Scraping failed: {str(e)}')
            raise
        finally:
            if self.driver:
                self.driver.quit()

    def save_data(self):
        """Save extracted data to CSV."""
        if not self.data:
            self.logger.warning('No data to save')
            return False

        try:
            df = pd.DataFrame(self.data)
            os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
            output_path = os.path.join(
                self.config.OUTPUT_DIR,
                self.config.DEFAULT_FILENAME
            )
            df.to_csv(output_path, index=False)
            self.logger.info(f'Data saved successfully to {output_path}')
            return True
        except Exception as e:
            self.logger.error(f'Error saving data: {str(e)}')
            return False

    def get_next_page_url(self):
        """Get the URL for the next page."""
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR, self.config.PAGINATION_SELECTOR
            )
            return next_button.get_attribute('href')
        except NoSuchElementException:
            return None