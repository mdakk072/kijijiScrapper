# Standard library imports
import json
import random
import re
import time
from urllib.parse import quote_plus, urlparse, urlunparse
# Third-party library imports for web scraping
from bs4 import BeautifulSoup
# Local application/library specific imports
from core.baseRequest import BaseRequest
from core.utils import Utils
from scraper.kijijiDataFormatter import KijijiDataFormatter


class KijijiScraper(BaseRequest ):
    
    def __init__(self,**kwargs ):
        self.logger = Utils.get_logger()
        self.logger.debug("Initializing KijijiScraper...")
        super().__init__()
        self.headers = kwargs.get('headers') or self.headers
        self.logger.debug("KijijiScraper initialized.")

    def fetch_page(self, url):
        """
        Fetch a specific page by applying pagination to a base URL. This method assumes the URL
        contains a placeholder for the page number which will be formatted into the URL.

        Args:
            url (str): The base URL containing a placeholder for the page number.
            page_number (int): The page number to fetch.

        Returns:
            requests.Response: The response object from the fetched URL.

        Raises:
            Exception: Raises an exception if there is an issue fetching the page.
        """
        try:
            # Format the URL with the specified page number
            self.logger.debug("Fetching page %s...", url)
            # Perform the HTTP request using the formatted URL
            response= self.send_request('GET',url)
            Utils.write_file(response.text,"data/html_json/last_fetch_page.html")
            return response
        except Exception as e:
            # Log any exceptions that occur during the fetch
            self.logger.error("Failed to fetch page %s: %s", url, str(e))
            raise

    def get_ad_listing_JSON(self, response):
        """
        Extract JSON data from a script tag identified by a specific ID in the HTML response.

        Args:
            response (requests.Response): The HTTP response object from which to extract the JSON.

        Returns:
            dict: A dictionary containing the parsed JSON data if found, or None if not found.

        Raises:
            json.JSONDecodeError: If the JSON data in the script tag is not properly formatted.
        """
        soup = BeautifulSoup(response.content, 'lxml')
        script_id = '__NEXT_DATA__'
        script_tag = soup.find('script', {'id': script_id})
        if script_tag:
            try:
                # Attempt to parse the JSON data from the script tag
                json_data = json.loads(script_tag.string)
                self.logger.debug("Successfully extracted JSON data from script tag with ID '%s'.", script_id)
                Utils.write_json(json_data,"data/html_json/get_ad_listing_JSON.json")
                return json_data

            except json.JSONDecodeError as e:
                # Log and re-raise the exception with a more informative error message
                self.logger.error("Failed to decode JSON from script tag with ID '%s': %s", script_id, str(e))
                raise
        else:
            # Log the absence of the script tag and return None
            self.logger.warning("No script tag with ID '%s' found in the response.", script_id)
            return None

    def extract_ad_JSON(self, response):
        """
        Extract advertisement information from a script tag within an HTML response. This method
        looks for a specific script tag containing 'window.__data' and attempts to parse the JSON
        data contained within to extract specific ad information.

        Args:
            response (requests.Response): The HTTP response object containing the HTML content.

        Returns:
            dict or None: The extracted ad information as a dictionary if successful, None otherwise.

        Raises:
            json.JSONDecodeError: If JSON parsing fails.
            RuntimeError: If the regex fails to match or if the expected script tag is not found.
        """
        # Parsing the response content with BeautifulSoup
        soup = BeautifulSoup(response.content, "lxml")
        script_tag = soup.find("script", string=lambda text: text and "window.__data" in text)

        if not script_tag:
            self.logger.error("Script tag containing 'window.__data' not found.")
            raise RuntimeError("Script tag containing 'window.__data' not found.")

        data_text = script_tag.string
        try:
            # Attempt to extract JSON string using regex
            pattern = re.compile(r"window\.__data\s*=\s*(.*?);", re.DOTALL)
            match = pattern.search(data_text)
            if not match:
                self.logger.error("Regex match failed to find the JSON data.")
                raise RuntimeError("Regex match failed to find the JSON data.")

            # If regex fails to work correctly, use the replacement method
            json_str = data_text.replace("window.__data=", "").strip()[:-1]
            # Load JSON string into Python dictionary
            data = json.loads(json_str)
            ad_info = data.get("config", {}).get("VIP", {})
            with open("data/html_json/extract_ad_JSON.json", "w") as file:
                file.write(json.dumps(ad_info, indent=4,ensure_ascii=False))
            return ad_info
        except json.JSONDecodeError as e:
            self.logger.error(f"Error extracting or parsing JSON data: {e}")
            raise

    def get_ads_listings(self, json_data):
        """
        Extract listings from the JSON data based on a specific structure expected in the Apollo state.
        This method specifically looks for keys containing 'ListingV2' to gather listing information.

        Args:
            json_data (dict): The JSON data from which to extract listing information.

        Returns:
            list: A list of values extracted from the Apollo state where the keys contain 'ListingV2'.

        Raises:
            KeyError: If the expected keys are not found in the JSON structure.
        """
        try:
            # Navigate through the nested JSON structure to find the Apollo state
            apollo_state = json_data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})

            # Extracting listings from the Apollo state
            listings = [value for key, value in apollo_state.items() if 'ListingV2' in key]
            
            self.logger.debug("Extracted %d listings from the Apollo state.", len(listings))
            Utils.write_json(listings,"data/html_json/get_ads_listings.json")

            return listings
        except KeyError as e:
            # Log an error if the JSON structure is not as expected
            self.logger.error("Key error when accessing JSON data for listings: %s", str(e))
            raise
        except TypeError as e:
            # Log type errors in JSON structure access, e.g., if None is returned instead of a dict
            self.logger.error("Type error when processing JSON data for listings: %s", str(e))
            raise

    def is_link_dead(self, response):
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        dead_flags = ('page non trouvée', 'page not found', 'annonce non disponible','this page no longer exists',"listing was so awesome that it's already gone")

        # Get all text from the page
        page_text = soup.get_text().lower().strip()  # Extracts all text and processes it

        # Check if any of the specific text is in the page text
        return any(dead_flag in page_text for dead_flag in dead_flags)
    
    def format_ad_data(self, ad_data,stringnify_json=False):
        """
        Use the AdDataFormatter class to format ad data from pagination.
        
        Args:
            ad_data (dict): The raw advertisement data to be formatted.
        
        Returns:
            dict: The formatted advertisement data.
        
        Raises:
            Exception: Propagates exceptions from the AdDataFormatter.
        """
        try:
            formatter = KijijiDataFormatter()
            formatted_ad_data =  formatter.format_data(ad_data)
            self.logger.debug(f"Ad data formatted successfully : {formatted_ad_data.url}")
            Utils.write_json(formatted_ad_data.to_dict(),"data/html_json/format_ad_data.json")
            return formatted_ad_data.to_dict(stringnify_json )
        except Exception as e:
            self.logger.error("Failed to format pagination ad data: %s", str(e))
            raise
