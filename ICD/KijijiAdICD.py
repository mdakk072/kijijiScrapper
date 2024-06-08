import json
from typing import Dict, List, Optional

class KijijiAd:
    def __init__(self, 
                 title: Optional[str] = None, 
                 price: Optional[float] = None, 
                 location: Optional[Dict] = None, 
                 description: Optional[str] = None, 
                 posted_date: Optional[str] = None,
                 attributes: Optional[Dict] = None,
                 images: Optional[List[str]] = None,
                 url: Optional[str] = None,
                 sorting_date: Optional[str] = None,
                 process_state: Optional[str] = None,
                 state: Optional[str] = None,
                 address: Optional[str] = None,
                 seller_name: Optional[str] = None,
                 removal_date: Optional[str] = None,
                 last_checked_date: Optional[str] = None):
        self.title = title # The title or headline of the rental ad.
        self.price = price # The rental price of the property.
        self.location = location # The general location or address of the property.
        self.description = description # A detailed description of the property.
        self.posted_date = posted_date # The date when the ad was posted.
        self.attributes = attributes or {} # Additional attributes of the property, stored as key-value pairs.
        self.images = images or [] # A list of URLs pointing to images of the property.
        self.url = url # The URL of the rental ad.
        self.process_state = process_state # The current state of the ad in the processing pipeline.
        self.state = state # The current state of the ad.
        self.address = address # The specific address of the property.
        self.seller_name = seller_name # The name of the seller or landlord.
        self.removal_date = removal_date # The date when the ad was removed.
        self.last_checked_date = last_checked_date # The date when the ad was last checked.
        
    def to_dict(self,stringnify_json=False):
        obj_dict = self.__dict__.copy()
        if stringnify_json:
            obj_dict["attributes"] = json.dumps(obj_dict["attributes"])
            obj_dict["images"] = json.dumps(obj_dict["images"])
            obj_dict["location"] = json.dumps(obj_dict["location"])
        """Convert the instance to a dictionary and return a copy."""
        return obj_dict
    
    def to_json(self, indent=1,ensure_ascii=False):
        """Convert the instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent,ensure_ascii=ensure_ascii)
    
    @staticmethod
    def metadata():
        """Provide metadata for the KijijiAd fields."""
        return {
            "title": {
                "type": "string",
                "label": "Title",
                "description": "The title or headline of the ad."
            },
            "price": {
                "type": "float",
                "label": "Price",
                "description": "The price of the item or service."
            },
            "location": {
                "type": "string",
                "label": "Location",
                "description": "The general location or address where the item or service is available."
            },
            "description": {
                "type": "string",
                "label": "Description",
                "description": "A detailed description of the item or service."
            },
            "posted_date": {
                "type": "date",
                "label": "Posted Date",
                "description": "The date when the ad was posted."
            },
            "attributes": {
                "type": "dict",
                "label": "Attributes",
                "description": "Additional attributes of the item or service, stored as key-value pairs."
            },
            "images": {
                "type": "list",
                "label": "Images",
                "description": "A list of URLs pointing to images of the item or service."
            },
            "url": {
                "type": "string",
                "label": "URL",
                "description": "The URL of the ad."
            },
            "process_state": {
                "type": "string",
                "label": "Process State",
                "description": "The current state of the ad in the processing pipeline."
            },
            "state": {
                "type": "string",
                "label": "State",
                "description": "The current state of the ad."
            },
            "address": {
                "type": "string",
                "label": "Address",
                "description": "The specific address where the item or service is available."
            },
            "seller_name": {
                "type": "string",
                "label": "Seller Name",
                "description": "The name of the seller or provider."
            },
            "removal_date": {
                "type": "date",
                "label": "Removal Date",
                "description": "The date when the ad was removed."
            },
            "last_checked_date": {
                "type": "date",
                "label": "Last Checked Date",
                "description": "The date when the ad was last checked."
            }
        }
    
    @staticmethod
    def get_schema():
        """Return a dictionary representing the table schema with attributes."""
        return {
            "title": {"type": "TEXT"},
            "price": {"type": "REAL"},
            "location": {"type": "TEXT"},  # JSON stored as text
            "description": {"type": "TEXT"},
            "posted_date": {"type": "TEXT"},
            "attributes": {"type": "TEXT"},  # JSON stored as text
            "images": {"type": "TEXT"},  # JSON stored as text
            "url": {"type": "TEXT", "unique": True},  # URL should be unique
            "process_state": {"type": "TEXT"},
            "state": {"type": "TEXT"},
            "address": {"type": "TEXT"},
            "seller_name": {"type": "TEXT"},
            "removal_date": {"type": "TEXT"},
            "last_checked_date": {"type": "TEXT"}
        }
