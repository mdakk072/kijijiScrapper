from scrapper.kijijiScrapper import KijijiScraper
from core.database import Database
from enum import Enum, auto
from core.utils import Utils

class State(Enum):
    GET_PAGE = auto()
    GET_JSON_TAG = auto()
    EXTRACT_LISTINGS = auto()
    FORMAT_DATA = auto()
    ADD_DATA = auto()
    INC_PAGE = auto()
    END = auto()

class KijijiPaginationFSM:
    
    def __init__(self, **kwargs):
        self.logger = Utils.get_logger()
        state_class = State
        self.current_state = state_class.GET_PAGE

        # Load configuration from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Set default values if not provided in kwargs
        self.db_path = getattr(self, 'db_path', 'sqlite:///default.db')
        self.headers = getattr(self, 'headers',None)
        self.url_settings = getattr(self, 'url_settings', None)
        self.base_url = getattr(self, 'base_url', None)
        self.start_page = getattr(self, 'start_page', 1)
        # Setup database and scraper
        
        if not self.headers or not self.url_settings or not self.base_url:
            raise Exception("Missing required parameters.")
        self.db = Database(self.db_path)
        self.kijiji_scraper = KijijiScraper(self.headers)
        # Initializing attributes to None
        self.response = None
        self.json_script_tag = None
        self.extracted_listings = None
        self.formatted_data = None
        
    def run(self):
        self.logger.info("Starting FSM run.")
        while self.current_state != self.current_state.END:
            self.logger.debug("Current state: %s", self.current_state.name)
            self.current_state = self.fsm()
        self.logger.info("Scrapper quit and resources cleaned up.")

    def fsm(self):
        self.logger.debug("Handling state: %s", self.current_state.name)
        if self.current_state == self.current_state.GET_PAGE:
            try:
                formated_url = self.kijiji_scraper.format_url(self.base_url, self.url_settings)
                self.response = self.kijiji_scraper.fetch_pagination(formated_url,self.start_page)
                self.logger.info(f"Fetching page {self.start_page}")
                return self.current_state.GET_JSON_TAG
            except Exception as e:
                return self.current_state.END

        elif self.current_state == self.current_state.GET_JSON_TAG:
            try:
                self.json_script_tag = self.kijiji_scraper.get_json_script_tag(self.response)
                return self.current_state.EXTRACT_LISTINGS
            except Exception as e:
                return self.current_state.END

        elif self.current_state == self.current_state.EXTRACT_LISTINGS:
            self.extracted_listings = self.kijiji_scraper.get_ads_listings(self.json_script_tag)
            return self.current_state.FORMAT_DATA

        elif self.current_state == self.current_state.FORMAT_DATA:
            self.formatted_data = [self.kijiji_scraper.format_ad_data_pagination(data) for data in self.extracted_listings]
            return self.current_state.ADD_DATA

        elif self.current_state == self.current_state.ADD_DATA:
            added_data_count = sum(self.db.add_listing(data) for data in self.formatted_data)
            self.logger.info(f"Added  {added_data_count}/{len(self.formatted_data)} listings to the database.") 
            if added_data_count == 0:return self.current_state.END
            else:return self.current_state.INC_PAGE
            
        elif self.current_state == self.current_state.INC_PAGE:
            self.start_page += 1
            return self.current_state.GET_PAGE

        elif self.current_state == self.current_state.END:
            print("> Process completed. Cleaning up and shutting down.")
            self.is_running = False
        
        else:
            print("> Unknown state encountered.")
            return self.current_state.END