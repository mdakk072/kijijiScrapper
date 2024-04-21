import requests
from bs4 import BeautifulSoup
from core.utils import Utils
import time
import random

class BaseScraper:
    def __init__(self):
        self.logger = Utils.get_logger()
        if not self.logger:
            raise Exception("Logger not initialized")
        self.logger.debug("BaseScraper initialized.")
        headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "max-age=0",
                    "Referer": "https://www.google.com/",
                    "DNT": "1"}


    def fetch_page(self, url, headers):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            self.logger.debug("Page fetched successfully: %s", url)
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to fetch page %s: %s", url, str(e))
            raise

    def parse_html(self, html_content, parser_type='lxml'):
        try:
            soup = BeautifulSoup(html_content, parser_type)
            self.logger.debug("HTML parsed successfully.")
            return soup
        except Exception as e:
            self.logger.error("Failed to parse HTML: %s", str(e))
            raise

    def delay_action(self, min_delay=0.5, max_delay=1.5):
        delay = random.uniform(min_delay, max_delay)  # Random delay to mimic human interaction
        time.sleep(delay)
        self.logger.debug("Action delayed for %s seconds.", delay)

