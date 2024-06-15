import argparse
import time
from ICD.ConfigICD import ConfigICD
from ICD.monitoringICD import MonitoringICD
from core.utils import Utils
from core.baseMain import BaseMain
from scraper.completionScraper import KijijiCompletionFSM
from scraper.paginationScraper import KijijiPaginationFSM
from scraper.deadLinkScraper import KijijiLinkCheckFSM

from datetime import datetime
from core.ipc import IPC
class Main(BaseMain):
    """
    Main class for running the Kijiji Scraper.
    
    Inherits from BaseMain and handles the initialization, configuration parsing,
    and execution of the pagination and completion scrapers.
    """

    def __init__(self):
        """
        Initializes the Main class by parsing the configuration and setting up the logger.
        """
        self.publish_address = None
        self.id = None
        self.config = ConfigICD()
        if not self.parse_config():
            raise Exception("Failed to parse configuration.")
        self.init_logger(self.config.log_path, self.config.log_level, self.config.log_console, self.config.log_file)
        self.logger.info("======================================== Kijiji Scraper ========================================")
        self.logger.info(f"Starting {self.config.name} v{self.config.version}")
        self.monitoring = MonitoringICD(config=self.config.to_dict(),id=self.id)
        self.ipc = IPC()    if self.publish_address else None
        if self.ipc:
            self.ipc.init_publisher(self.publish_address)
    
    def read_args(self):
        """
        Parse command line arguments.

        Returns:
            argparse.Namespace: The parsed command line arguments.
        """
        parser = argparse.ArgumentParser(description='Run the scrapping tool with optional configuration.')
        parser.add_argument('-c', '--config', default='config.yaml', type=str,
                            help='Specify the configuration file. Default is "config.yaml".')
        parser.add_argument('-i', '--id', default=None, type=str,
                            help='Specify the unique ID for the scraper. Default is None.')
        parser.add_argument('-p', '--publish_address', default=None, type=str,
                            help='Specify the publish address. Default is None.')
        return parser.parse_args()

    
    def parse_config(self):
        """
        Read the configuration parameters from the configuration file.

        Returns:
            bool: True if the configuration was successfully read, False otherwise.
        """
        args = self.read_args()
        config_file = args.config
        self.publish_address = args.publish_address
        self.id = args.id
        config_dict = Utils.read_yaml(config_file) or {}
        if not self.config.parse(config_dict):
            raise Exception("Failed to parse configuration.")
        return True

    def update_monitoring(self,scraper_info):
        """
        Update the monitoring instance with the current status of the scraper.
        """
        # Assuming self.monitoring.start_time is a string in ISO format
        start_time = datetime.fromisoformat(self.monitoring.start_time)
        current_time = datetime.now()
        
        # Update last_updated to the current time
        self.monitoring.last_updated = current_time.isoformat()
        
        # Calculate the duration and update it
        duration = current_time - start_time
        self.monitoring.duration = str(duration)
        self.monitoring.status = scraper_info.get('scraper_name', 'UNKNOWN')
        self.monitoring.state = scraper_info.get('scraper').current_state.name
        scraper = scraper_info.get('scraper')
        self.monitoring.num_requests = scraper.kijiji_scraper.num_requests
        self.monitoring.successful_requests = scraper.kijiji_scraper.successful_requests 
        self.monitoring.failed_requests = scraper.kijiji_scraper.failed_requests
        
        # Calculate and update requests_per_minute
        duration_minutes = duration.total_seconds() / 60
        if duration_minutes > 0:
            self.monitoring.requests_per_minute = round(scraper.kijiji_scraper.num_requests / duration_minutes, 2)

    def run(self):
        """
        Execute the main logic of the scraper, running pagination and/or completion scrapers
        based on the configuration.
        """
        # Flags to track completion status of each scraper
        done_pagination, done_completion ,done_deadlinkCheck= False, False , False

        # Initialize the pagination scraper if configured to do so
        pagination_scraper = self._initialize_pagination_scraper() if self.config.do_pagination else None
        # Initialize the completion scraper if configured to do so
        completion_scraper = self._initialize_completion_scraper() if self.config.do_completion else None

        dead_link_scraper = self._initialize_dead_link_scraper() if self.config.do_dead_link else None

        # List of scrapers with their associated done status and start flag
        scrapers = [
            {'scraper': pagination_scraper, 'done': done_pagination, 'start': False,"scraper_name": "pagination"},
            {'scraper': completion_scraper, 'done': done_completion, 'start': False,"scraper_name": "completion"},
            {'scraper': dead_link_scraper, 'done': done_deadlinkCheck, 'start': False,"scraper_name": "dead_link_check"}
        ]

        # Loop until all scrapers have completed their tasks
        while not all(scraper['done'] or scraper['scraper'] is None for scraper in scrapers):
            for scraper_info in scrapers:
                scraper = scraper_info['scraper']
                # If the scraper exists and hasn't started yet
                if scraper and not scraper_info['start']:
                    # Mark the scraper as started
                    scraper_info['start'] = True
                    # Run the scraper in a step-by-step mode until it completes
                    
                    
                    while not scraper_info['done']:
                        time.sleep(0.3)
                        scraper_info['done'] = scraper.run(continuous=False)
                        self.update_monitoring(scraper_info)
                        Utils.write_json(self.monitoring.to_dict(),f"data/html_json/scraper_monitoring.json")
                        if self.ipc :
                            self.ipc.publish(self.monitoring.to_json())
                        
                        
                        
                elif scraper is None:
                    # Mark as done if scraper is None to prevent infinite loop
                    scraper_info['done'] = True


    def _initialize_pagination_scraper(self):
        """
        Initialize and return the pagination scraper based on the configuration.
        """
        return KijijiPaginationFSM(
            url_settings=self.config.pagination.url_settings,
            base_url=self.config.pagination.base_url,
            start_page=self.config.pagination.start_page,
            db_config=self._get_db_config(),
            max_zero_added=self.config.pagination.max_zero_added
        )

    def _initialize_completion_scraper(self):
        """
        Initialize and return the completion scraper based on the configuration.
        """
        return KijijiCompletionFSM(
            db_config=self._get_db_config()
        )
        
    def _initialize_dead_link_scraper(self):
        """
        Initialize and return the dead link scraper based on the configuration.
        """
        return KijijiLinkCheckFSM(
            db_config=self._get_db_config()
        )
    def _get_db_config(self):
        """
        Return the database configuration dictionary.
        """
        return {
            'db_type': self.config.db_type,
            'connection_info': self.config.connection_info,
            'db_name': self.config.db_name,
            'table_name': self.config.table_name,
        }
    

if __name__ == "__main__":
    main = Main()
    try:
        main.run()
    except KeyboardInterrupt:
        main.logger.info("Exiting...")
        if main.ipc:
            main.ipc.close()
