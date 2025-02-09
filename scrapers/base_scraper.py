from selenium.webdriver.support.ui import WebDriverWait

from db_save import save_to_db
from tg_bot import send_to_telegram


class BaseScraper:
    def __init__(self, driver):
        self.driver = driver

    def open_page(self, url):
        self.driver.get(url)

    def open_link_in_new_tab(self, link):
        self.driver.execute_script("window.open(arguments[0], '_blank');", link)
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.window_handles) > 1
        )
        self.driver.switch_to.window(self.driver.window_handles[-1])

    # def wait_for_element(self, by, value, timeout=10):
    #     return WebDriverWait(self.driver, timeout).until(
    #         EC.presence_of_element_located((by, value))
    #     )

    def close_current_tab(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def close_browser(self):
        self.driver.quit()

    def save_to_db(
        self, conn, cursor, name, href, expires, description=None, requirements=None
    ):
        """
        Save vacancy data to the database.
        Args:
            conn: SQLite connection object.
            cursor: SQLite cursor object.
            name: Vacancy name.
            href: Vacancy URL.
            expires: Expiration date of the vacancy.
            description: Full description of the vacancy.
            requirements: Specific requirements extracted from the description.
        """
        return save_to_db(conn, cursor, name, href, expires, description, requirements)

    def send_to_telegram(self, message):
        """
        Send a message to a Telegram bot.
        Args:
            message: The message to send.
        """
        send_to_telegram(message)
