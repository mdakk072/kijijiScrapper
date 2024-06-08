"""
BaseDriver Module

This module provides a robust web scraping class `BaseDriver` using Selenium WebDriver.
The `BaseDriver` class includes methods to initialize, control, and interact with a web browser,
as well as utilities for handling cookies, navigating to URLs, and interacting with web elements.

Classes:
    BaseDriver: A class that encapsulates the functionality required to perform web scraping
                using Selenium WebDriver.

Usage Example:
    from core.baseDriver import BaseDriver

    driver_path = 'path/to/your/webdriver'
    base_driver = BaseDriver(driver_path=driver_path, headless=True)
    base_driver.init_driver()
    
    # Navigate to a URL
    base_driver.navigate_to('https://www.example.com')

    # Find an element
    element = base_driver.find_element('//div[@id="example"]')
    
    # Input text into an element
    base_driver.input_text(element, 'Sample Text')

    # Click an element
    base_driver.click_element(element)

    # Save page source to a file
    base_driver.save_page('page_source.html')

    # Save and load cookies
    base_driver.save_cookies()
    base_driver.load_cookies()

    # Execute JavaScript
    base_driver.execute_script('console.log("Hello, world!");')

    # Clear browser storage
    base_driver.clear_driver_storage()

    # Close the driver
    base_driver.close_driver()

Dependencies:
    - selenium
    - core.utils (for logging utility)

This module requires a WebDriver executable (e.g., geckodriver for Firefox, chromedriver for Chrome) 
to be installed and specified in the driver_path.

Author: mdakk072
"""
import logging
import json
import os
import random
import time

from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException

from core.utils import Utils

class BaseDriver:
    """
    A robust web scraping class using Selenium WebDriver.

    Attributes:
        driver_path (str): Path to the WebDriver executable.
        headless (bool): Whether to run the browser in headless mode.
        driver (Optional[webdriver.Firefox]): The Selenium WebDriver instance.
        options (webdriver.FirefoxOptions): Browser options for customization.
    """

    def __init__(self, driver_path: str, headless: bool = True):
        """
        Initializes the BaseDriver with the given parameters.

        Args:
            driver_path (str): Path to the WebDriver executable.
            headless (bool): Whether to run the browser in headless mode.
        """
        self.logger = Utils.get_logger()
        if not self.logger:
            raise Exception("Logger not initialized")
        self.logger.debug("BaseDriver initialized with driver path: %s, headless: %s", driver_path, headless)

        self.driver_path: str = driver_path
        self.headless = headless
        self.driver: Optional[webdriver.Firefox] = None

        self.options = FirefoxOptions()
        self.options.headless = headless
        self.options.add_argument("start-maximized")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")

        self.options.set_preference("browser.cache.disk.enable", False)
        self.options.set_preference("browser.cache.memory.enable", False)
        self.options.set_preference("browser.cache.offline.enable", False)
        self.options.set_preference("network.http.use-cache", False)

    def init_driver(self):
        """
        Initializes the WebDriver instance with specified options.
        """
        if self.headless:
            os.environ['MOZ_HEADLESS'] = '1'
        else:
            os.environ.pop('MOZ_HEADLESS', None)

        service = FirefoxService(executable_path=self.driver_path)
        try:
            self.driver = webdriver.Firefox(service=service, options=self.options)
            self.driver.implicitly_wait(5)
            self.logger.info("WebDriver initialized successfully.")
        except WebDriverException as e:
            self.logger.error("Failed to initialize WebDriver: %s", str(e))
            raise

    def restart_driver(self):
        """
        Restarts the WebDriver instance.
        """
        if self.driver:
            self.driver.quit()
            self.logger.debug("WebDriver quit successfully.")
        self.init_driver()

    def close_driver(self):
        """
        Closes the browser and quits the driver.
        """
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed and driver quit.")

    def navigate_to(self, url: str):
        """
        Navigates to the specified URL.

        Args:
            url (str): The URL to navigate to.
        """
        try:
            if self.driver:
                self.driver.get(url)
                self.logger.info("Navigated to URL: %s", url)
        except WebDriverException as e:
            self.logger.error("Failed to navigate to URL %s: %s", url, str(e))
            raise

    def find_element(self, locator: str, by: By = By.XPATH) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        Finds an element on the web page by specified locator.

        Args:
            locator (str): The locator of the web element to find.
            by (By): The strategy to use for locating elements (default By.XPATH).

        Returns:
            Optional[webdriver.remote.webelement.WebElement]: The web element if found, else None.
        """
        try:
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by, locator)))
            self.logger.info(f"Element found: {locator}")
            return element
        except Exception as e:
            self.logger.error(f"Error finding element: {e}")
            return None

    def input_text(self, element, text: str):
        """
        Inputs text into a specified web element with a delay to mimic human typing.

        Args:
            element: The web element to input text into.
            text (str): The text to input.
        """
        try:
            for char in text:
                delay = random.uniform(0.1, 0.3)  # Adjust the range as needed for realism
                time.sleep(delay)
                element.send_keys(char)
            self.logger.debug("Text input successful into element.")
        except NoSuchElementException as e:
            self.logger.error("Failed to input text: Element not found. %s", str(e))
            raise
        except WebDriverException as e:
            self.logger.error("Error during text input: %s", str(e))
            raise

    def click_element(self, element):
        """
        Clicks on a specified web element with a delay to mimic human reaction time.

        Args:
            element: The web element to click.
        """
        try:
            delay = random.uniform(0.5, 1.5)  # Random delay to mimic human reaction time
            time.sleep(delay)
            element.click()
            self.logger.debug("Clicked element successfully.")
        except NoSuchElementException as e:
            self.logger.error("Failed to click: Element not found. %s", str(e))
            raise
        except WebDriverException as e:
            self.logger.error("Error during click on element: %s", str(e))
            raise

    def clear_driver_storage(self):
        """
        Clears local and session storage in the browser.
        """
        if self.driver:
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            self.logger.debug("Local and session storage cleared.")

    def save_cookies(self):
        """
        Saves browser cookies to a file.
        """
        if self.driver:
            self.cookies = self.driver.get_cookies()
            with open("cookies.json", "w") as f:
                f.write(json.dumps(self.cookies, indent=4))
            self.logger.debug("Cookies saved to file.")

    def load_cookies(self, cookies=None):
        """
        Loads browser cookies from a file or the provided cookies.

        Args:
            cookies (Optional[List[dict]]): The cookies to load. If not provided, uses cookies from the instance.
        """
        if self.driver:
            if not cookies:
                cookies = self.cookies
            if not cookies:
                self.logger.error("No cookies provided to load.")
                return
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.logger.debug("Cookies loaded from file.")

    def save_page(self, file_path: str):
        """
        Saves the current page source to a file.

        Args:
            file_path (str): The path of the file to save the page source to.
        """
        if self.driver:
            with open(file_path, "w") as f:
                f.write(self.driver.page_source)
            self.logger.debug("Page source saved to file.")

    def execute_script(self, script: str, *args):
        """
        Executes JavaScript on the current page.

        Args:
            script (str): The JavaScript to execute.
            args: Arguments to pass to the JavaScript.
        """
        if self.driver:
            return self.driver.execute_script(script, *args)
        else:
            self.logger.error("Driver not initialized.")
            return None

    # Additional methods for managing cookies, proxies, user agents, etc., can be added here.

