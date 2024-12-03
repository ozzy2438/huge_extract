from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

    def go_to_next_page(self):
        """Navigate to the next page if available."""
        try:
            # First try to find the next button by class
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label='Next']") or \
                          self.driver.find_elements(By.CSS_SELECTOR, ".pagination .next") or \
                          self.driver.find_elements(By.CSS_SELECTOR, "[rel='next']") or \
                          self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]") or \
                          self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]") or \
                          self.driver.find_elements(By.CSS_SELECTOR, ".next-page")
            
            if next_buttons:
                next_button = next_buttons[0]
                if next_button.is_displayed() and next_button.is_enabled():
                    self.driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)  # Wait for page to load
                    return True
            return False
        except Exception as e:
            self.logger.warning(f"Could not navigate to next page: {str(e)}")
            return False

    def extract_product_data(self):
        """Extract product information from all pages."""
        all_products = []
        page_num = 1
        
        while True:
            self.logger.info(f"\n📖 Processing page {page_num}...")
            
            # Wait for products to be visible
            try:
                product_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-tile, .product-item, .product-card"))
                )
            except:
                self.logger.warning("No products found on this page")
                break

            # Extract data from each product
            for product in product_elements:
                try:
                    data = {}
                    # Title/Book Name
                    if 'book_name' in self.columns or 'title' in self.columns:
                        title_element = product.find_element(By.CSS_SELECTOR, ".product-title, h3, .title")
                        title = title_element.text.strip()
                        data['book_name'] = title
                        data['title'] = title
                    
                    # Author
                    if 'author' in self.columns:
                        try:
                            author = product.find_element(By.CSS_SELECTOR, ".author, .product-author").text.strip()
                            data['author'] = author.replace('by ', '')
                        except:
                            data['author'] = 'N/A'
                    
                    # Price
                    if 'price' in self.columns:
                        try:
                            price = product.find_element(By.CSS_SELECTOR, ".price, .product-price").text.strip()
                            data['price'] = price
                        except:
                            data['price'] = 'N/A'
                    
                    # Published Date
                    if 'published_date' in self.columns:
                        try:
                            date = product.find_element(By.CSS_SELECTOR, ".publication-date, .release-date").text.strip()
                            data['published_date'] = date
                        except:
                            data['published_date'] = 'N/A'
                    
                    all_products.append(data)
                    
                except Exception as e:
                    self.logger.warning(f"Error extracting product data: {str(e)}")
                    continue
            
            # Try to go to next page
            if not self.go_to_next_page():
                break
                
            page_num += 1
            time.sleep(2)  # Wait between pages
        
        self.logger.info(f"\n✅ Finished processing {page_num} pages")
        return all_products

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
        
        self.logger.info(f"\n✅ Data saved successfully! Found {len(extracted_data)} items")
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