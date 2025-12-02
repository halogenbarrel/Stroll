"""
Pytest configuration for Selenium tests.
Supports headless mode via HEADLESS environment variable.
"""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_firefox_driver():
    """Create and return a Firefox WebDriver instance.
    Uses headless mode if HEADLESS environment variable is set.
    """
    options = Options()
    
    # Enable headless mode if HEADLESS env var is set
    if os.getenv('HEADLESS', '').lower() in ('true', '1', 'yes'):
        options.add_argument('--headless')
    
    # Additional options for headless/CI environments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    return driver

