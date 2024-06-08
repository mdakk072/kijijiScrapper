import abc
import argparse
from core.utils import Utils

class BaseMain(abc.ABC):
    def __init__(self):
        self.logger = None
        self.config = None
        

    def init_logger(self, log_path: str = "data/log/app_log.log", log_level: str = "INFO", log_console: bool = False, log_file: bool = True):
        """
        Initialize the logger based on the configuration.

        Args:
            log_path (str): Path to the log file.
            log_level (str): The logging level (e.g., DEBUG, INFO, WARNING, ERROR).
        """
        self.logger = Utils.setup_logging(log_path, log_level, log_console, log_file)

    @abc.abstractmethod
    def run(self):
        """
        Abstract run method to be implemented by child classes.
        """
        pass
    
    @abc.abstractmethod
    def parse_config(self, config_path: str):
        """
        Abstract method to parse the configuration file.

        Args:
            config_path (str): Path to the configuration file.
        """
        pass

    @abc.abstractmethod
    def read_args(self):
        """
        Abstract method to parse the command line arguments.

        Returns:
            argparse.Namespace: The parsed command line arguments.
        """
        pass
