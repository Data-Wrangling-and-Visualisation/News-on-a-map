from abc import ABC, abstractmethod
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests

class BaseParser(ABC):
    """Base class for all parsers"""
    
    def __init__(self):
        self.driver = None
        
    def initialize_driver(self):
        """Initialize Selenium WebDriver with recommended options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    
    def get_soup_from_selenium(self, url, need_reload=True, wait_time=15):
        """Get BeautifulSoup object from URL using Selenium for JavaScript rendering."""
        if self.driver is None:
            self.driver = self.initialize_driver()

        try:
            if need_reload:
                self.driver.get(url)
                # Wait for the page to load completely
                time.sleep(wait_time)

            # Get the page source after JavaScript execution
            page_source = self.driver.page_source
            return BeautifulSoup(page_source, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url} with Selenium: {e}")
            return None
            
    def get_soup_from_requests(self, url):
        """Get BeautifulSoup object from URL using requests"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url} with requests: {e}")
            return None
            
    def __del__(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
    
    @abstractmethod
    def parse(self):
        """Parse method to be implemented by subclasses"""
        pass