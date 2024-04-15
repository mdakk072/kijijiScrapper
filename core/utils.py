import logging
import os

import yaml

class Utils:
    _logger = None  # Class-level attribute to hold the logger
    
    @staticmethod
    def setup_logging(file_path='data/log/app.log'):
        # Extract the directory part from the file_path
        logs_folder = os.path.dirname(file_path)

        # Check if the directory exists, create if not
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

        # Check if logger already exists to avoid multiple handlers
        if Utils._logger is not None:
            return Utils._logger

        # Create a custom logger
        Utils._logger = logging.getLogger(__name__)
        Utils._logger.setLevel(logging.DEBUG)  # Set the logging level

        # Create handlers
        c_handler = logging.StreamHandler()  # Console handler
        f_handler = logging.FileHandler(file_path)  # File handler

        # Create formatters and add it to handlers
        log_format = '[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s:%(lineno)d] : %(message)s'
        formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%M:%S')
        c_handler.setFormatter(formatter)
        f_handler.setFormatter(formatter)

        # Add handlers to the logger
        Utils._logger.addHandler(c_handler)
        Utils._logger.addHandler(f_handler)
        
        return Utils._logger
    @staticmethod
    def get_logger():
        """Method to retrieve the current logger."""
        if Utils._logger is None:
            Utils._logger = Utils.setup_logging()
            Utils._logger.warning("Logger was not set up. Please set it up before using it.")
        return Utils._logger
    
    @staticmethod
    def read_yaml(file_path):
        # Read a YAML file and return the contents
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logging.error("The file was not found: %s", file_path)
            return None
        except yaml.YAMLError as exc:
            logging.error("Error while parsing YAML file: %s", exc)
            return None