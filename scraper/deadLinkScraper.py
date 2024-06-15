import time
from datetime import datetime, timedelta
from ICD.KijijiAdICD import KijijiAd
from core.coreDatabase.DatabaseFactory import DatabaseFactory
from scraper.kijijiScraper import KijijiScraper
from enum import Enum, auto
from core.baseFSM import BaseFSM

class State(Enum):
    FETCH_AD = auto()
    CHECK_LINK = auto()
    UPDATE_AD = auto()
    END = auto()
    
class KijijiLinkCheckFSM(BaseFSM):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _initialize(self):
        self.States = State
        self.current_state = self.States.FETCH_AD

        self.headers = getattr(self, "headers", None)
        self.kijiji_scraper = KijijiScraper(headers=self.headers)
        
        self.db_config = getattr(self, "db_config", None)
        if not self.db_config:
            self.logger.error("No database configuration provided.")
            raise ValueError("Missing required parameter: db_config.")
        
        kijijiAdSchema = KijijiAd.get_schema()
        self.database = DatabaseFactory.create_database(**self.db_config, schema=kijijiAdSchema)
        self.database.initialize()
        self.ad = None
        self.response = None

    def FETCH_AD(self):
        self.logger.debug("Entering FETCH_AD state.")
        cutoff_time = datetime.now() - timedelta(hours=24)
        ad_list = self.database.read(
            {'process_state': 'COMPLETED', 'last_checked_date': {'$lt': cutoff_time.strftime("%Y-%m-%d %H:%M:%S")}},
            limit=1
        )
        self.ad = ad_list[0] if ad_list else None
        if self.ad:
            self.logger.info(f"Ad found: {self.ad.get('url')}")
            return self.States.CHECK_LINK
        else:
            self.logger.info("No ads found to check.")
            return self.States.END
    
    def CHECK_LINK(self):
        self.logger.debug("Entering CHECK_LINK state.")
        url = self.ad.get('url')
        self.logger.info(f"Checking link: {url}")
        self.kijiji_scraper.delay_action(1.5, 3)
        self.response = self.kijiji_scraper.fetch_page(url)
        if self.response == 404 or self.kijiji_scraper.is_link_dead(self.response):
            self.logger.warning(f"Link is dead: {url}")
            ad = self.ad.copy()
            ad['process_state'] = 'COMPLETED'
            ad['state'] = 'DEAD'
            date = time.strftime("%Y-%m-%d %H:%M:%S")
            ad['last_checked_date'] = date
            ad['removal_date'] = date
            self.database.update({'url': self.ad['url']}, ad)
            self.logger.info(f"Ad updated as DEAD: {url}")
        else:
            self.logger.info(f"Link is still active: {url}")
            date = time.strftime("%Y-%m-%d %H:%M:%S")
            ad = self.ad.copy()
            
            ad['last_checked_date'] = date
            self.database.update({'url': self.ad['url']}, ad)
            
        return self.States.FETCH_AD
    
    def END(self):
        self.logger.debug("Entering END state.")
        self.logger.info("No more ads to check.")

        return None
