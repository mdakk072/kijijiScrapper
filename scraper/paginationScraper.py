"""
This module defines the KijijiPaginationFSM class, which implements a finite state machine (FSM) 
to handle pagination and data extraction from Kijiji listings. The FSM transitions between states 
defined as methods within the class, allowing for flexible and dynamic state management.

Classes:
    - State: An enumeration of possible states for the KijijiPaginationFSM.
    - KijijiPaginationFSM: A class that implements the FSM for Kijiji pagination and data extraction.

Usage:
    To use this FSM, instantiate the KijijiPaginationFSM class with the necessary configuration options.
    The FSM will handle fetching pages, extracting listings, formatting data, and storing the data 
    in a database.

Example:
    ```python
    fsm = KijijiPaginationFSM(headers=my_headers, url_settings=my_url_settings, base_url=my_base_url)
    fsm.run()
    ```

Dependencies:
    - scraper.kijijiScraper: Module containing the KijijiScraper class for interacting with Kijiji.
    - core.utils: Module containing utility functions and classes.
    - core.baseFSM: Module containing the BaseFSM class for creating finite state machines.
    - enum: Standard library module for creating enumerations.
    - typing: Standard library module for type hints.
"""

from typing import Type
from scraper.kijijiScraper import KijijiScraper
from enum import Enum, auto
from core.utils import Utils
from core.baseFSM import BaseFSM
from core.coreDatabase.DatabaseFactory import DatabaseFactory
from ICD.KijijiAdICD import KijijiAd
class State(Enum):
    GET_PAGE = auto()
    EXTRACT_LISTINGS = auto()
    FORMAT_DATA = auto()
    ADD_DATA = auto()
    INC_PAGE = auto()
    END = auto()

class KijijiPaginationFSM(BaseFSM):
    """
    KijijiPaginationFSM implements a finite state machine to handle pagination and data extraction
    from Kijiji listings.

    This class provides methods for fetching pages, extracting listings, formatting data,
    and transitioning through different states until all required pages are processed.

    Attributes:
        headers (dict): Headers for HTTP requests.
        url_settings (dict): URL settings for the scraper.
        base_url (str): Base URL for the Kijiji site.
        start_page (int): Starting page number for pagination.
        kijiji_scraper (KijijiScraper): An instance of the KijijiScraper class.
        response (str): Response from the HTTP request.
        json_script_tag (str): Extracted JSON script tag from the response.
        extracted_listings (list): List of extracted listings.
        formatted_data (list): List of formatted listings data.
    """

    def __init__(self, **kwargs):
        """
        Initialize the KijijiPaginationFSM with configuration options.

        Args:
            **kwargs: Arbitrary keyword arguments representing configuration options.
        """
        super().__init__(**kwargs)

    def _initialize(self):
        """
        Perform additional initialization specific to KijijiPaginationFSM.

        This method sets up the initial state, checks for required parameters,
        and initializes the Kijiji scraper.
        """
        self.States = State
        self.current_state = State.GET_PAGE

        # Set base default values if not provided in kwargs
        self.headers = getattr(self, "headers", None)
        self.url_settings = getattr(self, "url_settings", None)
        self.base_url = getattr(self, "base_url", None)
        self.start_page = getattr(self, "start_page", 1)
        self.db_config = getattr(self, "db_config", None)
        self.max_zero_added = getattr(self, "max_zero_added", 1)
        # Setup database and scraper
        if not self.url_settings or not self.base_url:
            self.logger.error("Missing required parameters: url_settings and base_url.")
            raise ValueError("Missing required parameters: url_settings and base_url.")
        
        if not self.db_config:
            self.logger.error("No database configuration provided.")
            raise ValueError("Missing required parameter: db_config.")

        self.kijiji_scraper = KijijiScraper(headers=self.headers)
        kijijiAdSchema = KijijiAd.get_schema()
        self.database = DatabaseFactory.create_database(**self.db_config, schema=kijijiAdSchema)
        self.database.initialize()
        self.response = None
        self.json_script_tag = None
        self.extracted_listings = None
        self.formatted_data = None
        self.zero_added = 0 
        self.strignify_json = True if self.db_config.get('db_type') == 'SQL' else False

    def GET_PAGE(self) -> Type[State]:
        """
        Fetch a page from the Kijiji site and transition to the EXTRACT_LISTINGS state.

        This method formats the URL, fetches the page, and handles any exceptions that occur
        during this process. If an error occurs, it logs the error and transitions to the END state.

        Returns:
            State: The next state of the FSM, EXTRACT_LISTINGS if successful, otherwise END.
        """
        try:
            formatted_url: str = self.kijiji_scraper.format_url(
                self.base_url, {**self.url_settings, "start_page": self.start_page}
            )
            self.response = self.kijiji_scraper.fetch_page(
                formatted_url
            )
            self.logger.info(f"Fetching page {self.start_page}")
            return self.States.EXTRACT_LISTINGS
        except Exception as e:
            self.logger.error(f"Error fetching page {self.start_page}: {e}")
            return self.States.END

    def EXTRACT_LISTINGS(self) -> Type[State]:
        """
        Extract listings from the fetched page and transition to the FORMAT_DATA state.

        This method extracts the JSON script tag and listings from the response.
        If an error occurs, it logs the error and transitions to the END state.

        Returns:
            State: The next state of the FSM, FORMAT_DATA if successful, otherwise END.
        """
        try:
            self.json_script_tag = self.kijiji_scraper.get_ad_listing_JSON(
                self.response
            )
            self.extracted_listings = self.kijiji_scraper.get_ads_listings(
                self.json_script_tag
            )
            return self.States.FORMAT_DATA
        except Exception as e:
            self.logger.error(f"Error extracting listings: {e}")
            return self.States.END

    def FORMAT_DATA(self) -> Type[State]:
        """
        Format the extracted listings data and transition to the ADD_DATA state.

        This method formats the extracted listings data for further processing.
        If an error occurs, it logs the error and transitions to the END state.

        Returns:
            State: The next state of the FSM, ADD_DATA if successful, otherwise END.
        """
        try:
            self.formatted_data = [
                self.kijiji_scraper.format_ad_data(data,self.strignify_json)
                for data in self.extracted_listings
            ]
            Utils.write_json(self.formatted_data, "data/html_json/formatted_data_lisitng.json")
            return self.States.ADD_DATA
        except Exception as e:
            self.logger.error(f"Error formatting data: {e}")
            return self.States.END

    def ADD_DATA(self) -> Type[State]:
        """
        Add the formatted data to the database and transition to the INC_PAGE state.

        This method adds the formatted data to the database.
        If an error occurs, it logs the error and transitions to the END state.

        Returns:
            State: The next state of the FSM, INC_PAGE if successful, otherwise END.
        """
        try:
            total_ads = len(self.formatted_data)
            added_ads = 0
            for data in self.formatted_data:
                added_ads +=1 if self.database.create(data) else 0
            self.logger.info(f"Added {added_ads} / {total_ads} ads to the database.")
            if added_ads == 0:
                self.zero_added += 1
                if self.zero_added > self.max_zero_added:
                    self.logger.info(f"max zero added reached : {self.zero_added} , exiting")
                    return self.States.END
            return self.States.INC_PAGE
        except Exception as e:
            self.logger.error(f"Error adding data to the database: {e}")
            return self.States.END

    def INC_PAGE(self) -> Type[State]:
        """
        Increment the page number and transition to the GET_PAGE state to fetch the next page.

        This method increments the current page number for pagination.
        If an error occurs, it logs the error and transitions to the END state.

        Returns:
            State: The next state of the FSM, GET_PAGE if successful, otherwise END.
        """
        try:
            self.start_page += 1
            return self.States.GET_PAGE
        except Exception as e:
            self.logger.error(f"Error incrementing page number: {e}")
            return self.States.END
