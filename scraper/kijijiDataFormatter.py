from core.utils import Utils
from core.baseFormatter import BaseFormatter
from ICD.KijijiAdICD import KijijiAd
import json
class KijijiDataFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()

    def format_data(self, raw_data):
        """Format raw Kijiji data into the KijijiAd structure."""
        try:
            rent_ad = KijijiAd()
            rent_ad.title=raw_data.get('title')
            rent_ad.description=raw_data.get('description', '')
            rent_ad.images=self._extract_images(raw_data)
            rent_ad.price=self._calculate_price(raw_data)
            rent_ad.url=f"{'' if 'www.kijiji.ca'  in raw_data.get('seoUrl', '') else 'https://www.kijiji.ca' }{raw_data.get('seoUrl', '')}"
            rent_ad.process_state='NEW'
            rent_ad.state='ACTIVE'
            rent_ad.location = {
                'longitude': raw_data.get('adLocation', {}).get('longitude'),
                'latitude': raw_data.get('adLocation', {}).get('latitude')
            }
            rent_ad.address=self.get_json_value(raw_data, ['location.address', 'adLocation.mapAddress'])
            rent_ad.posted_date=str(self.parse_date(raw_data.get('sortingDate', ''),"%Y-%m-%dT%H:%M:%SZ"))
            rent_ad.attributes=self._extract_attributes(raw_data)
            rent_ad.seller_name=raw_data.get('sellerName', '')
            return rent_ad
        except Exception as e:
            self.logger.error(f"Error formatting data: {e}")
            return None
        
    def _calculate_price(self, data):
        """ Helper method to calculate the price from data. """
        try:
            # Attempt to retrieve the 'amount' from the data, safely falling back to 0 if not found or if None
            price_info = data.get("price", {})
            amount = price_info.get("amount", 0)
            if amount is None:
                amount = None  # Ensure amount is zero if it's None
                return amount
            amount = float(amount)  # Safely convert to integer
        except (TypeError, ValueError) as e:
            self.logger.error(f"Error converting price to integer: {e}")
            amount = None # Set to 0 if any error occurs
            return amount
        calculated_price = float("{:.2f}".format(amount / 100.0))
        return calculated_price
    
    def _extract_attributes(self, data):
        """
        Extract attributes into a dictionary based on the available data.
        
        Args:
            data (dict): The data containing attributes.
            
        Returns:
            dict: A dictionary of extracted attributes.
        """
        attributes = data.get("attributes", [])
        if attributes:
            return {attr["name"]: (attr["values"] if len(attr['values']) > 1 else attr['values'][0])
                for attr in attributes}
            
        else:
            return {attr['machineKey']: attr['machineValue'] for attr in data.get("adAttributes", [])}

    def _extract_images(self, data):
        """ Extract images if available. """
        images=data.get("imageUrls", [])
        if not images:
            images = [item["href"] for item in data.get("media", []) if item["type"] == "image"]
        return  images
