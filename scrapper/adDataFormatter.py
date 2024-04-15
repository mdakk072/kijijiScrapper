from bs4 import BeautifulSoup
from core.utils import Utils

class AdDataFormatter:
    def __init__(self):
        self.logger = Utils.get_logger()

    def format_ad_data_pagination(self, ad_data):
        """
        Format advertisement data extracted from the webpage into a structured dictionary.
        """
        try:
            formatted_ad_data = {
                "id": self._get_int(ad_data, "id"),
                "title": ad_data.get("title", ""),
                "description": ad_data.get("description", ""),
                "price": self._calculate_price(ad_data),
                "attributes": self._format_attributes(ad_data),
                "images": ad_data.get("imageUrls", []),
                "url": f"https://www.kijiji.ca{ad_data.get('seoUrl', '')}",
                "activation_date": ad_data.get("activationDate", ""),
                "sorting_date": ad_data.get("sortingDate", ""),
                "_processState": "NEW",
                "_state": "ACTIVE"
            }
            self.logger.debug("Ad data formatted successfully: %s", formatted_ad_data)
            return formatted_ad_data
        except Exception as e:
            self.logger.error("Failed to format ad data: %s", str(e))
            raise

    def format_ad_data_completion(self, extracted_json, ad):
        """
        Complete the formatting of advertisement data using extracted JSON and previously fetched ad object.
        """
        try:
            self.logger.debug("Formatting data for ad ID %s...", ad.id)
            formatted_ad_data = {
                "id": ad.id,
                "title": extracted_json.get("title", ""),
                "description": self._clean_description(extracted_json),
                "price": self._calculate_price(extracted_json),
                "attributes": self._extract_attributes(extracted_json),
                "images": self._extract_images(extracted_json),
                "url": ad.url,
                "activation_date": ad.activation_date,
                "sorting_date": ad.sorting_date,
                "address": extracted_json.get("adLocation", {}).get("mapAddress", ""),
                "location": self._extract_location(extracted_json),
                "sellerName": extracted_json.get("sellerName", None),
                "_processState": "COMPLETE",
                "_state": ad._state
            }
            return formatted_ad_data
        except Exception as e:
            self.logger.error("Failed to format ad data completion: %s", str(e))
            raise

    def _calculate_price(self, data):
        """ Helper method to calculate the price from data. """
        try:
            # Attempt to retrieve the 'amount' from the data, safely falling back to 0 if not found or if None
            price_info = data.get("price", {})
            amount = price_info.get("amount", 0)
            if amount is None:
                amount = None  # Ensure amount is zero if it's None
                return amount
            amount = int(amount)  # Safely convert to integer
        except (TypeError, ValueError) as e:
            self.logger.error(f"Error converting price to integer: {e}")
            amount = None # Set to 0 if any error occurs
            return amount
        calculated_price = float("{:.2f}".format(amount / 100.0))
        return calculated_price
    def _format_attributes(self, ad_data):
        """ Extract attributes into a dictionary. """
        return {attr["name"]: (attr["values"] if len(attr['values']) > 1 else attr['values'][0])
                for attr in ad_data.get("attributes", [])}

    def _extract_images(self, json_data):
        """ Extract images if available. """
        return [item["href"] for item in json_data.get("media", []) if item["type"] == "image"]

    def _extract_location(self, json_data):
        """ Extract and format the location data. """
        return {
            "latitude": json_data.get("adLocation", {}).get("latitude", 0.0),
            "longitude": json_data.get("adLocation", {}).get("longitude", 0.0)
        }

    def _clean_description(self, json_data):
        """ Clean and format the description field. """
        description = json_data.get("description", "")
        return BeautifulSoup(description, "lxml").text.strip().replace("\n", " ")

    def _extract_attributes(self, json_data):
        """ Extract attributes from json_data. """
        return {attr['machineKey']: attr['machineValue'] for attr in json_data.get("adAttributes", [])}

    def _get_int(self, data, key):
        """ Safely get an integer value from data. """
        return int(data.get(key, 0))
