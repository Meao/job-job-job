import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

@pytest.fixture(scope="session")
def webBrowser():
    # Option 1: Specify the ChromeDriver path manually using Service
    service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')

    # Set up Chrome options
    options = webdriver.ChromeOptions()

    # Initialize the WebDriver with the service
    driver = webdriver.Chrome(service=service, options=options)
    
    #--------------------------------------------------------------------------------------
    yield driver
    #--------------------------------------------------------------------------------------

    # ждем 30 секунд
    time.sleep(30)

    # Close the browser
    driver.quit()
