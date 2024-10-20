from core.utils import Utils
from core.baseFormatter import BaseFormatter
from ICD.EntityAdICD import EntityAd
import json
from datetime import datetime, timezone
class DataFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()

    def format_data(self, raw_data):
        """Format raw data into the EntityAd structure."""
        try:
            rent_ad = EntityAd()
            rent_ad.title=raw_data.get('subject')
            rent_ad.description=raw_data.get('description', '')
            rent_ad.images=self._extract_images(raw_data)
            rent_ad.price=self._calculate_price(raw_data)
            rent_ad.url=raw_data.get('href') or raw_data.get('friendlyUrl',{}).get('url')
            rent_ad.process_state='NEW'
            rent_ad.state='ACTIVE'
            rent_ad.location = raw_data.get('location', "").split(",")[0].strip() if type(raw_data.get('location')) == str else raw_data.get('location', {}).get('city', {}).get('name', "")
            rent_ad.address=raw_data.get('location', "").split(",")[1].strip() if type(raw_data.get('location')) == str else raw_data.get('location', {}).get('area', {}).get('name', "")
            #TODO : ADApt the date to the correct format FROM TIME SPENT TO ACTUAL DATE
            rent_ad.posted_date = f"{raw_data.get('date', '')} | {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}" if raw_data.get('date') else raw_data.get('listTime')
            rent_ad.attributes=self._extract_attributes(raw_data)
            rent_ad.seller_name=raw_data.get('seller', {}).get('name', "")
            return rent_ad
        except Exception as e:
            self.logger.error(f"Error formatting data: {e}")
            return None
        
    def _calculate_price(self, data):
        """ Helper method to calculate the price from data. """
        try:
            # Attempt to retrieve the 'amount' from the data, safely falling back to 0 if not found or if None
            price_info = data.get("price", {})
            amount = price_info.get("value", 0)
            if amount is None:
                amount = None  # Ensure amount is zero if it's None
                return amount
            amount = float(amount)  # Safely convert to integer
        except (TypeError, ValueError) as e:
            self.logger.error(f"Error converting price to integer: {e}")
            amount = None # Set to 0 if any error occurs
            return amount
        calculated_price = float("{:.2f}".format(amount))
        return calculated_price
    
    def _extract_attributes(self, data):
        """
        Extract attributes into a dictionary based on the available data.
        
        Args:
            data (dict): The data containing attributes.
            
        Returns:
            dict: A dictionary of extracted attributes.
        """
        attributes = data.get("params", {})
        if attributes:
            extracted_attributes = {}
            for key, values in attributes.items():
                for attribute in values:
                    attr_key = attribute.get('key')
                    attr_value = attribute.get('value')
                    if attr_key and attr_value:
                        extracted_attributes[attr_key] = attr_value
            if 'phone' in data:
                extracted_attributes['phone'] = data['phone']
            return extracted_attributes
        else:
            return {attr['machineKey']: attr['machineValue'] for attr in data.get("adAttributes", [])}

    def _extract_images(self, data):
        """ Extract images if available. """
        images = data.get("images", [])
        
        # Check if images is a list of strings
        if images and all(isinstance(image, str) for image in images):
            return images
        
        # If images is a list of dicts, extract URLs from the specified JSON path
        if images and all(isinstance(image, dict) for image in images):
            images = [image.get("paths", {}).get("standard", "") for image in images if "paths" in image and "standard" in image["paths"]]
            return images
        
        return images
