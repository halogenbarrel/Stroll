"""
Pytest configuration for Selenium tests.
Supports headless mode via HEADLESS environment variable.
Supports multiple browsers via --browser command line argument (default: chrome).
"""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService


def pytest_addoption(parser):
    """Add command line option for browser selection."""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox"],
        help="Browser to use for tests (default: chrome)"
    )


@pytest.fixture(scope="function")
def browser(request):
    """Fixture to get the browser name from command line."""
    return request.config.getoption("--browser")


@pytest.fixture(scope="function")
def driver(browser):
    """Create and return a WebDriver instance based on browser selection.
    Uses headless mode if HEADLESS environment variable is set.
    """
    headless = os.getenv('HEADLESS', '').lower() in ('true', '1', 'yes')
    
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)
    else:  # firefox
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Firefox(options=options)
    
    yield driver
    driver.quit()


def get_browser_name_from_config():
    """Get browser name from command line arguments or environment variable."""
    import sys
    
    # Check command line arguments for --browser
    browser = None
    if '--browser' in sys.argv:
        idx = sys.argv.index('--browser')
        if idx + 1 < len(sys.argv):
            browser = sys.argv[idx + 1].lower()
    elif any('--browser=firefox' in arg for arg in sys.argv):
        browser = 'firefox'
    elif any('--browser=chrome' in arg for arg in sys.argv):
        browser = 'chrome'
    
    # Fallback to environment variable or default
    if browser is None:
        browser = os.getenv('SELENIUM_BROWSER', 'chrome').lower()
    
    return browser


def get_driver(browser_name=None):
    """Helper function to create a driver instance.
    Used by tests that don't use the fixture.
    If browser_name is None, gets it from pytest config or env var.
    """
    if browser_name is None:
        browser_name = get_browser_name_from_config()
    
    headless = os.getenv('HEADLESS', '').lower() in ('true', '1', 'yes')
    
    if browser_name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        return webdriver.Chrome(options=options)
    else:  # firefox
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Firefox(options=options)

