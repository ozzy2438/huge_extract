from scraper import WebScraper
from config import Config
import logging

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        # Initialize scraper
        scraper = WebScraper(Config())
        
        # Start scraping
        logger.info('Starting web scraping process...')
        success = scraper.scrape()
        
        if success:
            logger.info('Scraping completed successfully')
        else:
            logger.warning('Scraping completed with some issues')
            
    except Exception as e:
        logger.error(f'Scraping failed: {str(e)}')
        raise

if __name__ == '__main__':
    main()