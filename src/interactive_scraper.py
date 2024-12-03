from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import logging
import os
import json
from datetime import datetime

class InteractiveScraper:
    def __init__(self):
        self.setup_logging()
        self.data = []
        self.driver = None
        self.url = None
        self.columns = []
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        """Initialize and configure the Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(30)

    def get_user_input(self):
        """Get URL and column names from user."""
        self.url = input("\n🌐 Enter the URL to scrape: ").strip()
        
        self.logger.info("\n⏳ Loading page...")
        self.driver.get(self.url)
        
        input("\n✨ Page is loaded! Press Enter when you're ready to select data to extract...")
        
        self.logger.info("\n📝 What information would you like to extract?")
        self.logger.info("Enter column names one by one (press Enter twice when done):")
        
        while True:
            column = input().strip()
            if not column:
                if self.columns:
                    break
                continue
            self.columns.append(column)

    def scroll_to_bottom(self):
        """Automatically scroll to the bottom of the page."""
        self.logger.info("\n🔄 Scrolling through the page to load all content...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(2)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Break if no more content loads
            if new_height == last_height:
                break
            last_height = new_height

    def extract_page_data(self):
        """Extract all visible text data from the page."""
        self.logger.info("\n🔍 Analyzing page content...")
        
        # Get all elements with visible text
        elements = self.driver.find_elements(By.XPATH, "//*[not(self::script) and not(self::style)]/text()[normalize-space()]/..")
        
        # Extract text content
        text_data = []
        for element in elements:
            try:
                text = element.text.strip()
                if text and len(text.split()) <= 20:  # Avoid long paragraphs
                    text_data.append(text)
            except:
                continue
                
        return list(set(text_data))  # Remove duplicates

    def organize_data(self, text_data):
        """Organize extracted text into columns based on user input."""
        self.logger.info("\n🎯 Matching extracted data with your requested columns...")
        
        organized_data = {col: [] for col in self.columns}
        remaining_data = text_data.copy()
        
        # Try to match data to columns
        for col in self.columns:
            col_lower = col.lower()
            matched_data = []
            
            for text in remaining_data[:]:
                if any(keyword in text.lower() for keyword in col_lower.split()):
                    matched_data.append(text)
                    remaining_data.remove(text)
            
            organized_data[col] = matched_data
        
        return organized_data

    def save_data(self, organized_data):
        """Save extracted data to CSV and JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"extracted_data_{timestamp}"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save as CSV
        df = pd.DataFrame(organized_data)
        csv_path = f"data/{base_filename}.csv"
        df.to_csv(csv_path, index=False)
        
        # Save as JSON
        json_path = f"data/{base_filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(organized_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n✅ Data saved successfully!")
        self.logger.info(f"📊 CSV file: {csv_path}")
        self.logger.info(f"📋 JSON file: {json_path}")

    def scrape(self):
        """Main scraping method."""
        try:
            self.setup_driver()
            self.get_user_input()
            
            if not self.columns:
                self.logger.info("\n❌ No columns specified. Exiting...")
                return
            
            self.scroll_to_bottom()
            text_data = self.extract_page_data()
            
            if not text_data:
                self.logger.info("\n❌ No data found on the page. Exiting...")
                return
            
            organized_data = self.organize_data(text_data)
            self.save_data(organized_data)
            
        except Exception as e:
            self.logger.error(f"\n❌ Error: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

def main():
    scraper = InteractiveScraper()
    scraper.scrape()

if __name__ == "__main__":
    main()