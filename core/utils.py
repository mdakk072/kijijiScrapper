"""
utils.py

This module provides utility functions for common tasks such as file I/O,
logging, and timestamp generation. The Utils class offers various static methods
for interacting with YAML and JSON files, setting up logging, creating directories,
and generating timestamps. These utilities are designed to simplify the development
of web scraping projects and other applications that require basic file and logging
operations.

Author: mdakk072

Date: 5 May 2024
"""

import logging
import os
import yaml
import json
import xml.etree.ElementTree as ET
import configparser

class Utils:
    """
    A utility class for common operations such as file I/O, logging, and timestamp generation.

    The Utils class provides static methods for handling YAML and JSON files,
    setting up logging, creating directories, and generating timestamps. These
    utilities are designed to be reusable across different projects.

    Attributes:
        _logger (logging.Logger): The class-level logger instance used for logging.
    """
    _logger = None  # Class-level attribute to hold the logger
    

    @staticmethod
    def setup_logging(file_path='data/logs/app.log', log_level='INFO', console_logging=True, file_logging=True):
        """
        Configure and return a logger instance.

        Sets up logging for the application, outputting messages to both console and a log file.
        The logging level is determined by the `log_level` parameter. If a logger already exists,
        it returns the existing logger.

        Args:
            file_path (str): The file path where logs should be saved. Defaults to 'data/log/app.log'.
            log_level (str): The logging level (e.g., DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
            console_logging (bool): Flag to indicate whether to log to the console. Defaults to True.
            file_logging (bool): Flag to indicate whether to log to a file. Defaults to True.

        Returns:
            logging.Logger: The configured logger instance.
        """
        # Check if logger already exists to avoid multiple handlers
        if Utils._logger is not None:
            return Utils._logger

        # Create a custom logger
        Utils._logger = logging.getLogger(__name__)
        Utils._logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        log_format = '[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s:%(lineno)d] : %(message)s'
        formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%M:%S')

        # Create console handler if enabled
        if console_logging:
            c_handler = logging.StreamHandler()
            c_handler.setFormatter(formatter)
            Utils._logger.addHandler(c_handler)

        # Create file handler if enabled
        if file_logging:
            logs_folder = os.path.dirname(file_path)
            if not os.path.exists(logs_folder):
                os.makedirs(logs_folder)
            f_handler = logging.FileHandler(file_path)
            f_handler.setFormatter(formatter)
            Utils._logger.addHandler(f_handler)

        return Utils._logger
    @staticmethod
    def get_logger():
        """
        Retrieve logger instance.

        If the logger has not been set up, this method will initialize it with
        default settings and issue a warning indicating that it wasn't set up
        beforehand.

        Returns:
            logging.Logger: The logger instance for the current context.
        """
        if Utils._logger is None:
            # Logger is not set up, set it up with default settings
            Utils._logger = Utils.setup_logging()
            Utils._logger.warning("Logger was not set up. Please set it up before using it,using default settings.")
        return Utils._logger
    
    @staticmethod
    def read_yaml(file_path):
        """
        Read and parse a YAML file.

        This method reads a YAML file from the specified file path and returns its contents.
        If the file is not found or cannot be parsed, it logs an error message and returns None.

        Args:
            file_path (str): The path to the YAML file.

        Returns:
            dict or list or None: The parsed contents of the YAML file, or None if an error occurred.
        """
        try:
            # Open the file and parse its contents
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Log an error if the file is not found
            logging.error("The file was not found: %s", file_path)
            return None
        except yaml.YAMLError as exc:
            # Log an error if there is an issue parsing the file
            logging.error("Error while parsing YAML file: %s", exc)
            return None
        
    @staticmethod
    def write_yaml(data, file_path):
        """
        Write data to a YAML file.

        This method writes the provided data to a YAML file at the specified file path.
        If an error occurs during writing, it logs an error message and returns False.

        Args:
            data (dict or list): The data to be written to the YAML file.
            file_path (str): The path where the YAML file will be saved.

        Returns:
            bool: True if the data was successfully written to the YAML file, False otherwise.
        """
        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Open the file and write the data to it
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(data, file, default_flow_style=False, allow_unicode=True)
            return True
        except IOError as exc:
            # Log an error if there is an issue writing to the file
            logging.error("Error while writing to YAML file: %s", exc)
            return False
        except yaml.YAMLError as exc:
            # Log an error if there is an issue with the YAML data
            logging.error("Error while dumping data to YAML file: %s", exc)
            return False

    @staticmethod
    def read_json(file_path):
        """
        Read and parse a JSON file.

        This method reads a JSON file from the specified file path and returns its contents.
        If the file is not found or cannot be parsed, it logs an error message and returns None.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            dict or list or None: The parsed contents of the JSON file, or None if an error occurred.
        """
        try:
            # Open the file and parse its contents
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error("The file was not found: %s", file_path)
            return None
        except json.JSONDecodeError as exc:
            logging.error("Error while parsing JSON file: %s", exc)
            return None

    @staticmethod
    def write_json(data, file_path):
        """
        Write data to a JSON file.

        This method writes the provided data to a JSON file at the specified file path.
        If an error occurs during writing, it logs an error message and returns False.

        Args:
            data (dict or list): The data to be written to the JSON file.
            file_path (str): The path where the JSON file will be saved.

        Returns:
            bool: True if the data was successfully written to the JSON file, False otherwise.
        """
        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Open the file and write the data to it
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except IOError as exc:
            logging.error("Error while writing to JSON file: %s", exc)
            return False

    @staticmethod
    def read_ini(file_path):
        """
        Read and parse an INI file.

        This method reads an INI file from the specified file path and returns its contents as a dictionary.
        If the file is not found or cannot be parsed, it logs an error message and returns None.

        Args:
            file_path (str): The path to the INI file.

        Returns:
            dict or None: The parsed contents of the INI file, or None if an error occurred.
        """
        config = configparser.ConfigParser()
        try:
            # Open the file and parse its contents
            config.read(file_path, encoding='utf-8')
            return {section: dict(config.items(section)) for section in config.sections()}
        except FileNotFoundError:
            logging.error("The file was not found: %s", file_path)
            return None
        except configparser.Error as exc:
            logging.error("Error while parsing INI file: %s", exc)
            return None

    @staticmethod
    def write_ini(data, file_path):
        """
        Write data to an INI file.

        This method writes the provided data to an INI file at the specified file path.
        If an error occurs during writing, it logs an error message and returns False.

        Args:
            data (dict): The data to be written to the INI file.
            file_path (str): The path where the INI file will be saved.

        Returns:
            bool: True if the data was successfully written to the INI file, False otherwise.
        """
    
        config = configparser.ConfigParser()
        for section, values in data.items():
            config[section] = values

        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Open the file and write the data to it
            with open(file_path, 'w', encoding='utf-8') as file:
                config.write(file)
            return True
        except IOError as exc:
            logging.error("Error while writing to INI file: %s", exc)
            return False

    @staticmethod
    def read_xml(file_path):
        """
        Read and parse an XML file.

        This method reads an XML file from the specified file path and returns its contents as an ElementTree object.
        If the file is not found or cannot be parsed, it logs an error message and returns None.

        Args:
            file_path (str): The path to the XML file.

        Returns:
            ET.ElementTree or None: The parsed contents of the XML file, or None if an error occurred.
        """
        try:
            # Open the file and parse its contents
            return ET.parse(file_path)
        except FileNotFoundError:
            logging.error("The file was not found: %s", file_path)
            return None
        except ET.ParseError as exc:
            logging.error("Error while parsing XML file: %s", exc)
            return None

    @staticmethod
    def write_xml(data, file_path):
        """
        Write data to an XML file.

        This method writes the provided data to an XML file at the specified file path.
        If an error occurs during writing, it logs an error message and returns False.

        Args:
            data (ET.ElementTree): The data to be written to the XML file.
            file_path (str): The path where the XML file will be saved.

        Returns:
            bool: True if the data was successfully written to the XML file, False otherwise.
        """
        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Write the data to the file
            data.write(file_path, encoding='utf-8', xml_declaration=True)
            return True
        except IOError as exc:
            logging.error("Error while writing to XML file: %s", exc)
            return False
        except ET.ElementTree as exc:
            logging.error("Error while creating XML file: %s", exc)
            return False

    @staticmethod
    def read_file(file_path, as_lines=False, encoding='utf-8'):
        """
        Read and return the contents of a file.

        This method reads the contents of a file from the specified file path and returns 
        it either as a string or as a list of lines. If the file is not found or cannot 
        be read, it logs an error message and returns None.

        Args:
            file_path (str): The path to the file.
            as_lines (bool): Flag to indicate whether to return lines. Defaults to False.
            encoding (str): The encoding of the file. Defaults to 'utf-8'.

        Returns:
            str or list of str or None: The contents of the file, or None if an error occurred.
        """
        try:
            # Open the file and read its contents
            with open(file_path, 'r', encoding=encoding) as file:
                return file.readlines() if as_lines else file.read()
        except FileNotFoundError:
            logging.error("The file was not found: %s", file_path)
            return None
        except IOError as exc:
            logging.error("Error while reading file: %s", exc)
            return None

    @staticmethod
    def write_file(data, file_path, mode='w', encoding='utf-8'):
        """
        Write data to a file.

        This method writes the provided data to a file at the specified file path.
        The mode can be specified to determine whether to overwrite or append to the file.
        If an error occurs during writing, it logs an error message and returns False.

        Args:
            data (str): The data to be written to the file.
            file_path (str): The path where the file will be saved.
            mode (str): The mode for writing the file. Defaults to 'w' (overwrite).
            encoding (str): The encoding of the file. Defaults to 'utf-8'.

        Returns:
            bool: True if the data was successfully written to the file, False otherwise.
        """
        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Open the file and write the data to it
            with open(file_path, mode, encoding=encoding) as file:
                file.write(data)
            return True
        except IOError as exc:
            logging.error("Error while writing to file: %s", exc)
            return False
