import unittest
from unittest.mock import MagicMock, patch
from src.scraper import WebScraper
from src.config import Config

class TestWebScraper(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.scraper = WebScraper(self.config)

    def tearDown(self):
        if self.scraper.driver:
            self.scraper.driver.quit()

    @patch('selenium.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome):
        self.scraper.setup_driver()
        self.assertIsNotNone(self.scraper.driver)

    def test_extract_element_data(self):
        mock_element = MagicMock()
        mock_element.text = 'Test Data'
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_element
        
        self.scraper.driver = mock_driver
        result = self.scraper.extract_element_data('.test-selector')
        
        self.assertEqual(result, 'Test Data')

    def test_has_next_page(self):
        mock_element = MagicMock()
        mock_element.is_enabled.return_value = True
        mock_element.get_attribute.return_value = ''
        
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_element
        
        self.scraper.driver = mock_driver
        self.assertTrue(self.scraper.has_next_page())