import time
from scrapper.kijijiScrapper import KijijiScraper
from core.database import Database
from enum import Enum, auto
from core.utils import Utils

class State(Enum):
    FETCH_AD = auto()
    GOTO_LINK = auto()
    EXTRACT_AD_INFO = auto()
    FORMAT_DATA = auto()
    UPDATE_AD = auto()
    END = auto()
class KijijiCompletionFSM:
    
    def __init__(self, **kwargs):
        self.logger = Utils.get_logger()
        state_class = State
        self.current_state = state_class.FETCH_AD

        # Load configuration from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Set default values if not provided in kwargs
        self.db_path = getattr(self, 'db_path', 'sqlite:///default.db')
        self.headers = getattr(self, 'headers',None)
        # Setup database and scraper
        if not self.headers :
            raise Exception("Missing required parameters.")
        self.db = Database(self.db_path)
        self.kijiji_scraper = KijijiScraper(self.headers)
        # Initializing attributes to None
        self.ad = None
        self.response = None
        self.extracted_json = None
        self.formatted_ad_data = None

    def run(self):
        self.logger.info("Starting FSM run.")
        while self.current_state != self.current_state.END:
            self.logger.debug("Current state: %s", self.current_state.name)
            self.current_state = self.fsm()
        self.logger.info("Scrapper quit and resources cleaned up.")

    def fsm(self):
        self.logger.debug("Handling state: %s", self.current_state.name)
        if self.current_state == self.current_state.FETCH_AD:
            self.ad = self.db.fetch_random_new_ad()
            if self.ad:return self.current_state.GOTO_LINK
            else:return self.current_state.END
        elif self.current_state == self.current_state.GOTO_LINK:
            url = self.ad.url
            self.kijiji_scraper.delay_action(1,4)
            self.response = self.kijiji_scraper.fetch_page(url, self.headers)
            if self.response.status_code == 200:return self.current_state.EXTRACT_AD_INFO
            else :return self.current_state.END
        elif self.current_state == self.current_state.EXTRACT_AD_INFO:
            self.extracted_json = self.kijiji_scraper.extract_ad_info(self.response)
            if self.extracted_json:return self.current_state.FORMAT_DATA
            else:return self.current_state.FETCH_AD
        elif self.current_state == self.current_state.FORMAT_DATA:
            self.formatted_ad_data = self.kijiji_scraper.format_ad_data_completion(self.extracted_json, self.ad)
            return self.current_state.UPDATE_AD
        elif self.current_state == self.current_state.UPDATE_AD:
            self.db.update_listing(self.formatted_ad_data['id'], self.formatted_ad_data)
            return self.current_state.FETCH_AD
        else:
            return self.current_state.END