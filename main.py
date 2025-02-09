from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from config import PROXY
from scrapers.c_scraper import Site1Scraper
from scrapers.l_scraper import Site2Scraper

# from scrapers.site2_scraper import Site2Scraper

# note to myself: don't check for stale elements nor page count change as you shall run this script several times a week


def web_browser(proxy=None):
    service = Service(executable_path="/usr/lib/chromium-browser/chromedriver")
    options = webdriver.ChromeOptions()

    # If a proxy is provided, set it in the options
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(service=service, options=options)
    return driver


if __name__ == "__main__":
    # Define the proxy
    proxy = PROXY

    # Create a driver for the scraper with a proxy
    driver = web_browser(proxy)
    try:
        # Run scrapers for different websites
        # site1_scraper = Site1Scraper(driver)
        # site1_scraper.scrape()

        site2_scraper = Site2Scraper(driver)
        site2_scraper.scrape()
    finally:
        driver.quit()

    # Create a driver for the scraper without a proxy
    driver = web_browser()
    try:
        # Run scrapers for different websites
        site1_scraper = Site1Scraper(driver)
        site1_scraper.scrape()

        # site2_scraper = Site2Scraper(driver)
        # site2_scraper.scrape()
    finally:
        driver.quit()
