import time
from core.coreDatabase.DatabaseFactory import DatabaseFactory
from ICD.EntityAdICD import EntityAd
from scraper.actionScraper import ActionScraper
from enum import Enum, auto
from core.utils import Utils
from core.baseFSM import BaseFSM, BaseState

class State(Enum):
    FETCH_AD = auto()
    GOTO_LINK = auto()
    extract_ad_JSON = auto()
    FORMAT_DATA = auto()
    DEAD_AD = auto()
    UPDATE_AD = auto()
    END = auto()
    
class CompletionFSM(BaseFSM):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _initialize(self):
        """
        Perform additional initialization specific to PaginationFSM.

        This method sets up the initial state, checks for required parameters,
        and initializes the  scraper.
        """
        self.States = State
        self.current_state = self.States.FETCH_AD

        # Set base default values if not provided in kwargs
        self.headers = getattr(self, "headers", None)
        self.action_scraper = ActionScraper(headers=self.headers)
        
        self.db_config = getattr(self, "db_config", None)
        if not self.db_config:
            self.logger.error("No database configuration provided.")
            raise ValueError("Missing required parameter: db_config.")
        AdSchema = EntityAd.get_schema()
        self.database = DatabaseFactory.create_database(**self.db_config, schema=AdSchema)
        self.database.initialize()
        self.ad = None
        self.response = None
        self.json_script_tag = None
        self.formatted_data = None
        self.strignify_json = True if self.db_config.get('db_type') == 'SQL' else False

    def FETCH_AD(self):
        ad_list= self.database.read({'process_state': 'NEW'},limit=1) 
        self.ad  = ad_list[0] if ad_list else None
        return self.States.GOTO_LINK if self.ad  else self.States.END
    
    def GOTO_LINK(self):
            url = self.ad.get('url')
            self.action_scraper.delay_action(1.5,3)
            self.response = self.action_scraper.fetch_page(url)
            return self.States.DEAD_AD if self.action_scraper.is_link_dead(self.response) else self.States.extract_ad_JSON
            
    def extract_ad_JSON(self):
            self.extracted_json = self.action_scraper.extract_ad_JSON(self.response)
            return self.States.FORMAT_DATA if self.extracted_json else self.States.END
            
    def FORMAT_DATA(self):
            self.formatted_ad_data = self.action_scraper.format_ad_data(self.extracted_json,stringnify_json=self.strignify_json)
            return self.current_state.UPDATE_AD
        
    def UPDATE_AD(self):
        
            ad = self.formatted_ad_data.copy()
            ad['url'] = self.ad['url']
            ad['process_state'] = 'COMPLETED'
            ad['state'] = 'ACTIVE'
            ad['last_checked_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.database.update({'url': self.ad['url']}, ad)
            
            return self.current_state.FETCH_AD
        
    def DEAD_AD(self):
            ad = self.ad.copy()
            ad['process_state'] = 'COMPLETED'
            ad['state'] = 'DEAD'
            date= time.strftime("%Y-%m-%d %H:%M:%S")
            ad['last_checked_date'] = date
            ad['removal_date'] = date
            self.database.update({'url': self.ad['url']}, ad)
            
            return self.current_state.FETCH_AD
