import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from to_delete.scraperc import test_cv_ee_pagination


def webBrowser():
    # Option 1: Specify the ChromeDriver path manually using Service
    service = Service(executable_path="/usr/lib/chromium-browser/chromedriver")

    # Set up Chrome options
    options = webdriver.ChromeOptions()

    # Initialize the WebDriver with the service
    driver = webdriver.Chrome(service=service, options=options)

    # --------------------------------------------------------------------------------------
    test_cv_ee_pagination(driver)
    # --------------------------------------------------------------------------------------

    # ждем 30 секунд
    time.sleep(30)

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    webBrowser()
