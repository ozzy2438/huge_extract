from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.logger.info("Enter column names as comma-separated values:")
        
        columns_input = input().strip()
        self.columns = [col.strip() for col in columns_input.split(',') if col.strip()]

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
            
    def extract_product_data(self):
        """Extract product information from the page."""
        self.logger.info("\n🔍 Extracting product information...")
        
        # Wait for products to be visible
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-tile"))
        )
        
        products = self.driver.find_elements(By.CLASS_NAME, "product-tile")
        extracted_data = []
        
        for product in products:
            try:
                data = {}
                # Extract based on common attributes
                if 'book_name' in self.columns or 'title' in self.columns:
                    title_element = product.find_element(By.CLASS_NAME, "product-title")
                    title = title_element.text.strip()
                    data['book_name'] = title
                    data['title'] = title
                
                if 'author' in self.columns:
                    try:
                        author = product.find_element(By.CLASS_NAME, "author").text.strip()
                        data['author'] = author
                    except:
                        data['author'] = 'N/A'
                
                if 'price' in self.columns:
                    try:
                        price = product.find_element(By.CLASS_NAME, "price").text.strip()
                        data['price'] = price
                    except:
                        data['price'] = 'N/A'
                
                if 'published_date' in self.columns:
                    try:
                        date = product.find_element(By.CLASS_NAME, "publication-date").text.strip()
                        data['published_date'] = date
                    except:
                        data['published_date'] = 'N/A'
                
                # Add any additional requested columns
                for col in self.columns:
                    if col not in data:
                        try:
                            value = product.find_element(By.CLASS_NAME, col.replace('_', '-')).text.strip()
                            data[col] = value
                        except:
                            data[col] = 'N/A'
                
                extracted_data.append(data)
                
            except Exception as e:
                self.logger.warning(f"Error extracting product data: {str(e)}")
                continue
        
        return extracted_data

    def save_data(self, extracted_data):
        """Save extracted data to CSV and JSON."""
        if not extracted_data:
            self.logger.warning("\n⚠️ No data was extracted!")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"extracted_data_{timestamp}"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save as CSV
        df = pd.DataFrame(extracted_data)
        csv_path = f"data/{base_filename}.csv"
        df.to_csv(csv_path, index=False)
        
        # Save as JSON
        json_path = f"data/{base_filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n✅ Data saved successfully! Found {len(extracted_data)} items.")
        self.logger.info(f"📊 CSV file: {csv_path}")
        self.logger.info(f"📋 JSON file: {json_path}")
        
        # Display sample of extracted data
        self.logger.info("\n🔎 Sample of extracted data:")
        print(df.head().to_string())

    def scrape(self):
        """Main scraping method."""
        try:
            self.setup_driver()
            self.get_user_input()
            
            if not self.columns:
                self.logger.info("\n❌ No columns specified. Exiting...")
                return
            
            self.scroll_to_bottom()
            extracted_data = self.extract_product_data()
            self.save_data(extracted_data)
            
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