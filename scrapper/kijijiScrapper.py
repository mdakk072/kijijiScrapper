# Standard library imports
import json
import random
import re
import time
from urllib.parse import quote_plus, urlparse, urlunparse
# Third-party library imports for web scraping
from bs4 import BeautifulSoup
from lxml import etree
# Local application/library specific imports
from core.baseScrapper import BaseScraper
from core.utils import Utils
from scrapper.adDataFormatter import AdDataFormatter


class KijijiScraper(BaseScraper ):
    
    def __init__(self,headers ):
        self.logger = Utils.get_logger()
        self.logger.debug("Initializing KijijiScraper...")
        super().__init__()
        self.headers = headers
        self.logger.debug("KijijiScraper initialized.")
        
    def format_url(self, base_url, url_settings):
        """
        Format a URL based on base URL and URL settings, which include parameters like
        address, latitude, longitude, radius, and sorting preferences.

        Args:
            base_url (str): The base URL to be formatted with additional parameters.
            url_settings (dict): A dictionary containing URL parameters such as
                                address, latitude, longitude, radius, and sorting type.

        Returns:
            str: The formatted URL containing all specified parameters.
        
        Raises:
            KeyError: If a required key is missing in url_settings.
        """
        try:
            # URL encoding the address to handle special characters
            address = quote_plus(url_settings['address'])
            # Formatting the URL with parameters from url_settings
            formatted_url = base_url.format(
                page='{page}',  # Placeholder for pagination
                address=address,
                latitude=url_settings['latitude'],
                longitude=url_settings['longitude'],
                radius=url_settings['radius'],
                sort=url_settings['sort']
            )
            self.logger.debug("URL formatted successfully: %s", formatted_url)
            return formatted_url
        except KeyError as e:
            # Log the error and re-raise it with more context
            error_msg = f"Missing key {str(e)} in url_settings during URL formatting."
            self.logger.error(error_msg)
            raise KeyError(error_msg) from e

    def fetch_pagination(self, url, page_number):
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
            formatted_url = url.format(page=page_number)
            self.logger.debug("Fetching page %s...", formatted_url)
            # Perform the HTTP request using the formatted URL
            response = self.fetch_page(formatted_url, self.headers)
            # Check if the response was successful
            response.raise_for_status()
            self.logger.debug("Page %s fetched successfully.", page_number)
            with open("data/html_json/fetch_pagination.html", "w") as file:
                file.write(response.text)
            return response
        except Exception as e:
            # Log any exceptions that occur during the fetch
            self.logger.error("Failed to fetch page %s: %s", page_number, str(e))
            raise

    def get_json_script_tag(self, response):
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
                with open("data/html_json/get_json_script_tag.json", "w") as file:
                    file.write(json.dumps(json_data, indent=4,ensure_ascii=False))
                return json_data
            except json.JSONDecodeError as e:
                # Log and re-raise the exception with a more informative error message
                self.logger.error("Failed to decode JSON from script tag with ID '%s': %s", script_id, str(e))
                raise
        else:
            # Log the absence of the script tag and return None
            self.logger.warning("No script tag with ID '%s' found in the response.", script_id)
            return None

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
            with open("data/html_json/get_ads_listings.json", "w") as file:
                file.write(json.dumps(listings, indent=4,ensure_ascii=False))
            return listings
        except KeyError as e:
            # Log an error if the JSON structure is not as expected
            self.logger.error("Key error when accessing JSON data for listings: %s", str(e))
            raise
        except TypeError as e:
            # Log type errors in JSON structure access, e.g., if None is returned instead of a dict
            self.logger.error("Type error when processing JSON data for listings: %s", str(e))
            raise

    def extract_ad_info(self, response):
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
            with open("data/html_json/extract_ad_info.json", "w") as file:
                file.write(json.dumps(ad_info, indent=4,ensure_ascii=False))
            return ad_info
        except json.JSONDecodeError as e:
            self.logger.error(f"Error extracting or parsing JSON data: {e}")
            raise

    def format_ad_data_pagination(self, ad_data):
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
            formatter = AdDataFormatter()
            formatted_ad_data = formatter.format_ad_data_pagination(ad_data)
            self.logger.debug("Pagination ad data formatted successfully.")
            with open("data/html_json/format_ad_data_pagination.json", "w") as file:
                file.write(json.dumps(formatted_ad_data, indent=4,ensure_ascii=False))
            return formatted_ad_data
        except Exception as e:
            self.logger.error("Failed to format pagination ad data: %s", str(e))
            raise

    def format_ad_data_completion(self, extracted_json, ad):
        """
        Use the AdDataFormatter class to complete the formatting of ad data based on the extracted JSON.
        
        Args:
            extracted_json (dict): The JSON data extracted and pre-processed.
            ad (object): An object representing the initial ad data including identifiers and URLs.
        
        Returns:
            dict: The completely formatted advertisement data.
        
        Raises:
            Exception: Propagates exceptions from the AdDataFormatter.
        """
        try:
            formatter = AdDataFormatter()
            formatted_ad_data = formatter.format_ad_data_completion(extracted_json, ad)
            self.logger.debug("Completion ad data formatted successfully for ad ID %s.", ad.id)
            with open("data/html_json/format_ad_data_completion.json", "w") as file:
                file.write(json.dumps(formatted_ad_data, indent=4,ensure_ascii=False))
            return formatted_ad_data
        except Exception as e:
            self.logger.error("Failed to format completion ad data for ad ID %s: %s", ad.id, str(e))
            raise