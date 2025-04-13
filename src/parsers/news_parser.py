import time
import random
import re
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class NewsParser:
    def __init__(self, source_config):
        """
        Initialize with a news source configuration.
        """
        self.source_config = source_config
        self.driver = None

    def initialize_driver(self):
        """Initialize Selenium WebDriver."""
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

    def parse_date(self, date_text, date_format):
        """Parse date string to datetime object using the provided format."""
        try:
            if date_format:
                return datetime.strptime(date_text.strip(), date_format)

            # For special cases in Russian
            if "сегодня" in date_text.lower():
                today = datetime.now()
                time_part = re.search(r'в\s+(\d+):(\d+)', date_text)
                if time_part:
                    hours, minutes = map(int, time_part.groups())
                    return datetime(today.year, today.month, today.day, hours, minutes)
                return today

            elif "вчера" in date_text.lower():
                yesterday = datetime.now() - timedelta(days=1)
                time_part = re.search(r'в\s+(\d+):(\d+)', date_text)
                if time_part:
                    hours, minutes = map(int, time_part.groups())
                    return datetime(yesterday.year, yesterday.month, yesterday.day, hours, minutes)
                return yesterday

            # Default case - check for relative time
            if "час" in date_text.lower():
                hours = int(re.search(r'\d+', date_text).group())
                return datetime.now() - timedelta(hours=hours)
            elif "день" in date_text.lower() or "дня" in date_text.lower() or "дней" in date_text.lower():
                days = int(re.search(r'\d+', date_text).group())
                return datetime.now() - timedelta(days=days)
            elif "минут" in date_text.lower():
                minutes = int(re.search(r'\d+', date_text).group())
                return datetime.now() - timedelta(minutes=minutes)

            # Try common Russian date formats
            for fmt in ["%d.%m.%Y", "%d.%m.%Y %H:%M", "%d %B %Y", "%d %B %Y %H:%M"]:
                try:
                    return datetime.strptime(date_text.strip(), fmt)
                except ValueError:
                    continue

            # Return current date as fallback
            print(f"Could not parse date: {date_text}")
            return datetime.now()
        except Exception as e:
            print(f"Error parsing date '{date_text}': {e}")
            return datetime.now()

    def extract_article_data(self, article_url, source_config):
        """Extract data from a single article page."""
        if source_config.get('js_rendered', False):
            soup = self.get_soup_from_selenium(article_url)
        else:
            response = requests.get(article_url)
            soup = BeautifulSoup(response.text, 'html.parser')

        if not soup:
            return None

        try:
            title_element = soup.select_one(source_config['title_selector'])
            title = title_element.get_text().strip() if title_element else "No title found"
            if title == "No title found":
                return None

            date_element = soup.select_one(source_config['date_selector'])
            date_text = date_element.get_text().strip() if date_element else ""
            date = self.parse_date(date_text, source_config.get('date_format', '')) if date_text else None

            def extract_content(soup, selector):
                content_elements = soup.select(selector)
                if content_elements:
                    txt = ' '.join([p.get_text().strip() for p in content_elements])
                    txt = txt.replace('\xa0', ' ')
                    return txt
                return "No content found"

            content = extract_content(soup, source_config['content_selector'])

            return {
                'title': title,
                'date': date,
                'content': content,
                'url': article_url,
                'source_name': source_config['source_name']
            }
        except Exception as e:
            print(f"Error parsing article {article_url}: {e}")
            return None

    def extract_article_url(self, element, base_url):
        """Extract article URL from an element with better fallback handling."""
        try:
            # First try to find an anchor tag
            link_element = element.find('a')
            if link_element and link_element.get('href'):
                return urljoin(base_url, link_element.get('href'))

            # Try to get href from the element itself
            if element.get('href'):
                return urljoin(base_url, element.get('href'))

            # Look for any element with href attribute
            hrefs = element.select('[href]')
            if hrefs:
                return urljoin(base_url, hrefs[0].get('href'))

            # If element is already an 'a' tag
            if element.name == 'a' and element.get('href'):
                return urljoin(base_url, element.get('href'))

            return None
        except Exception as e:
            print(f"Error extracting article URL: {e}")
            return None

    def handle_pagination(self, source_config, soup, base_url, current_url, page_count):
        """
        Handle pagination with more flexible approach.
        Returns:
            tuple: (new_current_url, new_page_count, should_continue, need_reload)
        """
        # Case 1: No pagination configured - scroll down for more content
        if not source_config.get('has_pagination', False):
            if source_config.get('js_rendered', False) and self.driver:
                try:
                    # Scroll down to load more content
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(10)  # Wait for content to load

                    # Check if new content was loaded
                    new_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    if len(new_soup.select(source_config['entries_selector'])) > len(soup.select(source_config['entries_selector'])):
                        return current_url, page_count, True, True
                    else:
                        return current_url, page_count, False, True
                except Exception as e:
                    print(f"Error scrolling for more content: {e}")
                    return current_url, page_count, False, True
            else:
                # No pagination and not JS rendered - can't get more content
                return current_url, page_count, False, True

        # Case 2: Check if direct pagination URL is specified
        if source_config.get('pagination_direct_url', False):
            pattern = source_config.get('pagination_direct_url', '?page={}')
            if '{}' in pattern:
                next_url = f"{base_url}/{pattern.format(page_count + 1)}"
            else:
                next_url = f"{base_url}/{pattern}"
            page_count += 1
            return next_url, page_count, True, True

        # Case 3: Standard pagination handling based on selectors
        if source_config.get('js_rendered', False) and self.driver:
            try:
                # Try to find "Load More" button if that's the pagination type
                if source_config.get('pagination_type') == 'load_more' and 'pagination_selector' in source_config:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(5)
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, source_config['pagination_selector'])
                        ActionChains(self.driver).scroll_to_element(element).perform()
                        time.sleep(3)
                        self.driver.execute_script("window.scrollBy(0, 150);")
                        time.sleep(3)
                        
                        next_page_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, source_config['pagination_selector']))
                        )
                        if next_page_element:
                            next_page_element.click()
                            time.sleep(5)  # Wait for content to load
                            return current_url, page_count, True, False
                    except Exception as e:
                        print(f"Error clicking load more button: {e}")
                        return current_url, page_count, False, False

                # Try to find numbered pagination
                if 'pagination_selector' in source_config:
                    try:
                        next_page_elements = self.driver.find_elements(By.CSS_SELECTOR, source_config['pagination_selector'])
                        for element in next_page_elements:
                            href = element.get_attribute('href')
                            if href and (str(page_count + 1) in href or "next" in element.text.lower()):
                                next_url = href
                                page_count += 1
                                return next_url, page_count, True, True
                    except NoSuchElementException:
                        pass

                # Try URL pattern fallbacks
                if "?page=" in current_url:
                    base_part = current_url.split('?page=')[0]
                    next_url = f"{base_part}?page={page_count + 1}"
                elif "/page/" in current_url:
                    base_part = current_url.split('/page/')[0]
                    next_url = f"{base_part}/page/{page_count + 1}"
                else:
                    # Add appropriate pagination suffix based on common patterns
                    if "?" in current_url:
                        next_url = f"{current_url}&page={page_count + 1}"
                    else:
                        next_url = f"{current_url}?page={page_count + 1}"

                page_count += 1
                return next_url, page_count, True, True

            except Exception as e:
                print(f"Error handling JS pagination: {e}")
                return current_url, page_count, False, True
        else:
            # Handle non-JS rendered pagination
            if 'pagination_selector' in source_config:
                next_page_element = soup.select_one(source_config['pagination_selector'])
                if next_page_element and next_page_element.get('href'):
                    next_url = urljoin(base_url, next_page_element.get('href'))
                    page_count += 1
                    return next_url, page_count, True, True

                # Try to find next page by pattern
                pagination_elements = soup.select(source_config['pagination_selector'])
                for element in pagination_elements:
                    if str(page_count + 1) in element.text or (element.get('href') and str(page_count + 1) in element.get('href')):
                        next_url = urljoin(base_url, element.get('href'))
                        page_count += 1
                        return next_url, page_count, True, True

        # No pagination options worked
        return current_url, page_count, False, True

    def parse_source(self):
        """Parse a single news source according to its configuration."""
        source_config = self.source_config
        if 'base_url' in source_config:
            base_url = source_config['base_url']
        else:
            base_url = source_config['url']
        current_url = source_config['url']
        articles_data = []
        cutoff_date = datetime.now() - timedelta(days=2)
        page_count = 1
        max_attempts = 5  # Maximum pagination attempts
        entry_elements = []
        need_reload = True
        
        try:
            while len(articles_data) < 30 and page_count <= max_attempts:
                print(f"Processing page {page_count} from {source_config['source_name']}")

                if source_config.get('js_rendered', False):
                    soup = self.get_soup_from_selenium(current_url, need_reload)
                else:
                    response = requests.get(current_url)
                    soup = BeautifulSoup(response.text, 'html.parser')

                if not soup:
                    break
                
                if source_config['has_pagination']:
                    entry_elements = []
                entry_elements.extend(soup.select(source_config['entries_selector']))
                print(f"Found {len(entry_elements)} entries")
                
                if not source_config['has_pagination'] and len(entry_elements) < 30:
                    # If no entries but JS rendered, try scrolling
                    if source_config.get('js_rendered', False) and self.driver:
                        try:
                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(3)
                            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                            entry_elements.extend(soup.select(source_config['entries_selector']))
                            if not entry_elements:
                                break
                        except Exception as e:
                            print(f"Error during scroll attempt: {e}")
                            break
                    else:
                        break

                # Process articles on the current page
                continue_parsing = True
                if source_config['has_pagination'] or len(entry_elements) >= 1:
                    for element in entry_elements:
                        # Extract link to full article with improved extraction
                        article_url = self.extract_article_url(element, base_url)
                        if not article_url:
                            continue

                        # Delay between requests to avoid overloading the server
                        time.sleep(random.uniform(1, 3))
                        article_data = self.extract_article_data(article_url, source_config)
                        if article_data and article_data['date'] and article_data['title'] not in [dt['title'] for dt in articles_data]:
                            if article_data['date'] < cutoff_date:
                                continue_parsing = False
                                break

                            articles_data.append(article_data)
                            print(f"Article added: {article_data['title'][:30]}...")

                            if len(articles_data) >= 30:
                                break

                    # Check if we should stop due to date cutoff or article limit
                    if not continue_parsing or len(articles_data) >= 30:
                        break

                # Handle pagination with the updated flexible approach
                current_url, page_count, should_continue, need_reload = self.handle_pagination(
                    source_config, soup, base_url, current_url, page_count)
                if not should_continue:
                    break
        finally:
            # Clean up the driver
            if self.driver:
                self.driver.quit()
                
        return articles_data

