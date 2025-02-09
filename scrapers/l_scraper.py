import sqlite3
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import STARTS_E, URL_IFR, URL_L_SITE, URL_NEXT, URL_SITE
from db_save import save_to_db
from scrapers.base_scraper import BaseScraper
from tg_bot import send_to_telegram
from utils import ALLOW_ONLY, should_avoid_text


class Site2Scraper(BaseScraper):
    def open_vacancy(self):
        # ждем 30 секунд
        time.sleep(3000)

    def scrape(self):
        self.open_page(URL_L_SITE)
        try:
            conn = sqlite3.connect("jobs.db")
            cursor = conn.cursor()
            self.open_vacancy()
            conn.close()
            print("Saved to DB")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
