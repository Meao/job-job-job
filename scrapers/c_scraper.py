import sqlite3

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import STARTS_E, URL_IFR, URL_NEXT, URL_SITE
from db_save import save_to_db
from scrapers.base_scraper import BaseScraper
from tg_bot import send_to_telegram
from utils import ALLOW_ONLY, should_avoid_text


class Site1Scraper(BaseScraper):
    def extract_deadline(self, span_elements):
        for span in span_elements:
            if "Deadline:" in span.text:
                return span.text.replace("Deadline: ", "").strip()
        return None

    def extract_vacancy_data(self):
        try:
            name = self.driver.find_element(By.CSS_SELECTOR, "h1").text
            names_lst = name.lower().split()
            if any(word in ALLOW_ONLY for word in names_lst):
                span_elements = self.driver.find_elements(By.TAG_NAME, "span")
                expires = self.extract_deadline(span_elements)
                content_type = None
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR, ".vacancy-details__section"
                    )
                    content_type = "text"
                    vacancy_description = self.driver.find_element(
                        By.CSS_SELECTOR, ".vacancy-details__section"
                    ).text
                    print(content_type)
                    if should_avoid_text(vacancy_description):
                        return None, None, None
                except:
                    pass
                try:
                    iframe = self.driver.find_element(
                        By.CSS_SELECTOR, "iframe.vacancy-content__url"
                    )
                    self.driver.switch_to.frame(iframe)
                    vacancy_description = self.driver.find_element(
                        By.TAG_NAME, "body"
                    ).text  # Extract text from the iframe
                    content_type = "iframe"
                    self.driver.switch_to.default_content()
                    print(content_type)
                    if should_avoid_text(vacancy_description):
                        return None, None, None
                except:
                    pass
                try:
                    self.driver.find_element(By.CSS_SELECTOR, ".vacancy-details__image")
                    content_type = "image"
                    print(content_type)
                except:
                    pass
                if expires:
                    return name, vacancy_description, expires
            return None, None, None
        except Exception as e:
            print(f"Error extracting vacancy data: {e}")
            return None, None, None

    def go_to_next_page(self):
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR, '[aria-label="Next"]'
            )
            next_button.click()
            print("Clicked 'Next' button.")
            return True
        except Exception as e:
            print(f"Error clicking 'Next' button: {e}")
            return False

    def get_total_results(self):
        try:
            result_text_element = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'search-results-heading__value')]"
            )
            results_text = result_text_element.text.strip()
            return int(results_text.strip(" ():"))
        except Exception as e:
            print(f"Error getting total results count: {e}")
            return 0

    def process_vacancy(self, conn, cursor, links):
        for link in links:
            try:
                title = link.text
                if should_avoid_text(title):
                    print(f"Skipping vacancy due to keywords: {title}")
                    continue
                href = link.get_attribute("href")
                if href and href.startswith(STARTS_E):
                    self.open_link_in_new_tab(href)
                    name, description, expires = self.extract_vacancy_data()
                    if name and expires:
                        saved = save_to_db(
                            conn, cursor, name, href, expires, description
                        )
                        if saved:
                            send_to_telegram(
                                f"New Vacancy: {name}\nURL: {href}\nExpires: {expires}\nDescription: {description}"
                            )
                    self.close_current_tab()
            except Exception as e:
                print(f"Error processing link: {e}")

    # def handle_pagination(self, conn, cursor):
    #     while True:
    #         WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
    #         )
    #         links = self.driver.find_elements(By.CSS_SELECTOR, "a")
    #         self.process_vacancy(conn, cursor, links)
    #         if not self.go_to_next_page():
    #             break
    def handle_pagination(self, conn, cursor, total_results):
        results_per_page = 20
        total_pages = (
            total_results + results_per_page - 1
        ) // results_per_page  # Adding results_per_page - 1 ensures that any remainder from the division results in an additional page being counted.
        current_page = 1  # Start from the first page

        while current_page <= total_pages:
            print(f"Processing page {current_page} of {total_pages}...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
            )
            links = self.driver.find_elements(By.CSS_SELECTOR, "a")
            self.process_vacancy(conn, cursor, links)

            if not self.go_to_next_page():
                break

            current_page += 1  # Increment the page coun

    def scrape(self):
        # to check next page
        self.open_page(URL_NEXT)
        # to check normal
        # self.open_page(URL_SITE)
        # to check iframe
        # self.open_page(URL_IFR)
        try:
            conn = sqlite3.connect("jobs.db")
            cursor = conn.cursor()
            total_results = self.get_total_results()
            if total_results:
                self.handle_pagination(conn, cursor, total_results)
            conn.close()
            print("Saved to DB")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
