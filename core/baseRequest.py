"""
BaseRequest Module

Description:
    This module defines the `BaseRequest` class, which provides a foundation for making HTTP requests
    and handling web scraping tasks. It includes functionalities such as retries, session management,
    timeout handling, and user-agent rotation to facilitate robust web scraping activities.

    The class is designed to be extended for specific web scraping needs, allowing for customizable
    request headers, proxy support, and automated request delays to mimic human interaction and avoid
    blocking by web servers.

Classes:
    BaseRequest: A base class for building web scrapers with customizable HTTP session configurations.

Imported Modules:
    requests: For making HTTP requests.
    logging: For logging activities.
    random: For generating random numbers.
    time: For adding delays.
    itertools.cycle: For cycling through proxies and user agents.
    core.utils: For utility functions including logging setup.

Usage Example:
    from core.baseRequest import BaseRequest

    base_request = BaseRequest(base_url='https://example.com', retries=3, timeout=5.0)
    
    # Send a GET request
    response = base_request.send_request('GET', '/api/data')
    print(response.json())

    # Introduce a random delay
    base_request.delay_action()

    # Close the session
    base_request.close()

Author:
    mdakk072

Date:
    11 May 2024
"""

import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib.parse import quote_plus
from typing import Iterator, Optional, Dict, Any, List
import random
import time
from itertools import cycle
from core.utils import Utils

class BaseRequest:
    """
    A base class for making HTTP requests and parsing HTML content, designed to support 
    web scraping activities with robust features like retries, timeouts, and request customizations.

    This class provides reusable methods for common HTTP-based web scraping tasks
    and serves as a parent class for specific scraper implementations.

    Attributes:
        logger (logging.Logger): The logger for logging messages.
        session (requests.Session): The HTTP session for making requests.
        default_headers (Dict[str, str]): Default headers for requests.
        timeout (float): The timeout for HTTP requests.
        headers (Dict[str, str]): Custom headers for requests, with defaults provided.
    """

    def __init__(self, base_url: Optional[str] = None, retries: int = 3, backoff_factor: float = 0.3,
                 timeout: float = 5.0, headers: Optional[Dict[str, str]] = None, proxies: Optional[List[str]] = None,
                 user_agents: Optional[List[str]] = None):
        """
        Initialize the base request class with optional configurations for HTTP requests.

        Args:
            base_url (Optional[str]): The base URL for all requests.
            retries (int): The number of retries for failed requests.
            backoff_factor (float): The backoff factor to apply between retry attempts.
            timeout (float): The timeout for HTTP requests in seconds.
            headers (Optional[Dict[str, str]]): Custom headers for requests.
            proxies (Optional[List[str]]): A list of proxy servers (e.g., ['http://proxy1', 'https://proxy2']).
            user_agents (Optional[List[str]]): A list of user agents to rotate with each request.
        """
        self.logger: logging.Logger = Utils.get_logger()
        self.base_url: str = base_url if base_url is not None else ""
        self.retries: int = retries
        self.backoff_factor: float = backoff_factor
        self.timeout: float = timeout
        self.proxies: Optional[Iterator[str]] = cycle(proxies) if proxies else None
        self.user_agents: Optional[Iterator[str]] = cycle(user_agents) if user_agents else None
        self.session: requests.Session = requests.Session()
        retries_obj: Retry = Retry(total=retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504])
        adapter: HTTPAdapter = HTTPAdapter(max_retries=retries_obj)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.default_headers: Dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.google.com/",
            "DNT": "1"
        }
        self.headers: Dict[str, str] = headers  if headers is not None else self.default_headers
        
        self.num_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        
    def format_url(self, base_url: str, url_settings: Dict[str, Any]) -> str:
        """
        Format a URL based on base URL and URL settings, automatically mapping and encoding the parameters.

        Args:
            base_url (str): The base URL to be formatted with additional parameters.
            url_settings (dict): A dictionary containing URL parameters.

        Returns:
            str: The formatted URL containing all specified parameters.
        
        Raises:
            KeyError: If a required key is missing in url_settings.
        """
        try:
            # URL encoding the parameters
            encoded_settings = {k: quote_plus(str(v)) for k, v in url_settings.items()}
            # Formatting the URL with parameters from url_settings
            formatted_url = base_url.format(**encoded_settings)
            self.logger.debug("URL formatted successfully: %s", formatted_url)
            return formatted_url
        except KeyError as e:
            # Log the error and re-raise it with more context
            error_msg = f"Missing key {str(e)} in url_settings during URL formatting."
            self.logger.error(error_msg)
            raise KeyError(error_msg) from e

    def send_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Send an HTTP request using the specified method to the specified endpoint.

        Args:
            method (str): The HTTP method to use (e.g., 'GET', 'POST').
            endpoint (str): The endpoint path to append to the base URL.
            **kwargs: Additional keyword arguments to pass to the requests method (e.g., params, json).

        Returns:
            requests.Response: The response object from the HTTP request.

        Raises:
            requests.RequestException: An error occurred during the request.
        """
        url: str = self.base_url + endpoint
        headers: Dict[str, str] = kwargs.pop('headers') if 'headers' in kwargs else self.headers
        if self.user_agents:
            headers['User-Agent'] = next(self.user_agents)
        if self.proxies:
            kwargs['proxies'] = {'http': next(self.proxies), 'https': next(self.proxies)}
            
        self.num_requests += 1
        try:
            response: requests.Response = self.session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            self.successful_requests += 1
            return response
        except requests.RequestException as e:
            self.failed_requests += 1
            self.logger.error(f"Error during {method} request to {url}: {e}")
            raise

    def delay_action(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """
        Introduce a random delay to mimic human interaction and manage request rate.

        Args:
            min_delay (float): The minimum delay in seconds before making a request.
            max_delay (float): The maximum delay in seconds before making a request.
        """
        delay: float = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        self.logger.debug(f"Action delayed for {delay} seconds.")

    def close(self):
        """
        Close the HTTP session and release any resources.
        """
        self.session.close()
        self.logger.info("Session closed.")
