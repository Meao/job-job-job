import pytest
import requests
import sqlite3
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import WEBSITE_URL, STARTS_E, URL_IFR, URL_SITE, URL_NEXT, BOT_TOKEN, CHAT_ID

FILTER_OUT = [
    'senior', 'middle', 'lead', 'night', 'arendaja', 'vanemarendaja', 
    'veebiarendaja', 'testija', 'projektijuht', 'security', 'director', 
    'accountant', 'legal', 'risk', 'therapist', 'autonoomsete', 'sõidukite', 
    'seadmete', 'valdkonna', 'vanemteadur', 'küberturbe', 'projektijuht', 
    'majandustarkvara', 'kaubanduse', 'logistika', 'analüütik', 'konsultant', 
    'tooteomanik', 'it-juht', 'konsultant', 'elektrimontaažilukksepp', 
    'swedish', 'spanish', 'shifts', 'maastiku', 'tegija', 'ios', 
    'tarkvarainsener'
]
ALLOW_ONLY = [
        'analyst', 'analiste', 'аналитик', 'analise', 'аналитик/system', 'analysis', 
        'аналитика', 'аналитики', 'данных', 'аналитик(начинающий)', 'backend', 
        'backend-разработчик', 'бизнес-аналитик', 'бизнес-аналитика', 'бизнес-аналитик/аналитик', 
        'back-end', 'data', 'data-science-специалист', 'digital', 'developer', 'интерфейс', 
        'инженер-программист', 'manual', 'open', 'программист', 'искусственным', 'программированию', 
        'программирование', 'python-разработчик', 'qa', 'рекрутер', 'английском', 'исполнителей', 
        'ручной', 'разметчик', 'системы', 'системный', 'системный/бизнес', 'системный/специалист', 
        'специалист-аналитик', 'анализу', 'аналитике', 'тестировщик', 'software', 'intern', 
        'frontend', 'developpeur', 'stage', 'sw', 'visualization', 'sw/qa', 'technical', 
        'consultant', 'french', 'ux-исследователя', 'virtual'
    ]

def open_page(webBrowser, url):
    webBrowser.get(url)

def open_link_in_new_tab(webBrowser, link):
    webBrowser.execute_script("window.open(arguments[0], '_blank');", link)
    WebDriverWait(webBrowser, 10).until(
        lambda driver: len(driver.window_handles) > 1
    )
    webBrowser.switch_to.window(webBrowser.window_handles[-1])

def save_to_db(conn, cursor, name, href, expires, description=None, requirements=None):
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
    try:
        # Check if the vacancy already exists in the database
        cursor.execute("SELECT * FROM vacancies WHERE name = ? AND url = ? AND expires = ?", (name, href, expires))
        if cursor.fetchone() is None:
            # Insert the vacancy into the database
            cursor.execute('''
                INSERT INTO vacancies (name, url, expires, description, requirements)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, href, expires, description, requirements))
            conn.commit()
            print(f"Saved: {name}, {href}, {expires}")
        else:
            print(f"Already exists in DB: {name}")
    except Exception as e:
        print(f"Error saving to database: {e}")

def should_avoid_text(text):
    """
    Check if the vacancy name contains any keywords to avoid.
    Args:
        name: The name of the vacancy.
        avoid_keywords: A list of keywords to avoid.
    Returns:
        True if the name contains any avoid keywords, otherwise False.
    """
    return any(keyword in text.lower() for keyword in FILTER_OUT)

def extract_deadline(span_elements):
    for span in span_elements:
        if 'Deadline:' in span.text:
            return span.text.replace('Deadline: ', '').strip()
    return None

def extract_vacancy_data(webBrowser):
    """
    Extracts the vacancy name and deadline from the current page.
    Args:
        webBrowser: The Selenium WebDriver instance.
    Returns:
        A tuple (name, expires) if data is found, otherwise (None, None).
    """
    try:
        name = webBrowser.find_element(By.CSS_SELECTOR, 'h1').text
        names_lst = name.lower().split()
        if any(word in ALLOW_ONLY for word in names_lst):
            span_elements = webBrowser.find_elements(By.TAG_NAME, "span")
            expires = extract_deadline(span_elements)
            content_type = None
            try:
                webBrowser.find_element(By.CSS_SELECTOR, '.vacancy-details__image img')
                content_type = 'image'
                print(content_type)
            except:
                pass
            try:
                webBrowser.find_element(By.CSS_SELECTOR, '.vacancy-details__section')
                content_type = 'text'
                vacancy_description = webBrowser.find_element(By.CSS_SELECTOR, '.vacancy-details__section').text
                print(content_type)
                if should_avoid_text(vacancy_description):
                    return None, None, None
            except:
                pass
            try:
                iframe = webBrowser.find_element(By.CSS_SELECTOR, 'iframe.vacancy-content__url')
                webBrowser.switch_to.frame(iframe)  
                vacancy_description = webBrowser.find_element(By.TAG_NAME, 'body').text  # Extract text from the iframe
                content_type = 'iframe'
                webBrowser.switch_to.default_content() 
                print(content_type)
                if should_avoid_text(vacancy_description):
                    return None, None, None
            except:
                pass
            if expires:
                return name, vacancy_description, expires
        return None, None, None
    except Exception as e:
        print(f"Error extracting vacancy data: {e}")
        return None, None, None

def send_to_telegram(message):
    """
    Send a message to a Telegram bot.
    Args:
        message: The message to send.
    """
    bot_token = BOT_TOKEN
    chat_id = CHAT_ID
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, data=payload)
    print("Message sent to Telegram.")

def close_current_tab(webBrowser):
    webBrowser.close()
    webBrowser.switch_to.window(webBrowser.window_handles[0])

def go_to_next_page(webBrowser):
    try:
        next_button = webBrowser.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
        next_button.click()
        print("Clicked 'Next' button.")
        return True
    except Exception as e:
        print(f"Error clicking 'Next' button: {e}")
        return False

def get_total_results(webBrowser):
    try:
        result_text_element = webBrowser.find_element(By.XPATH, "//span[contains(@class, 'search-results-heading__value')]")
        results_text = result_text_element.text.strip()
        return int(results_text.strip(' ():')) 
    except Exception as e:
        print(f"Error getting total results count: {e}")
        return 0

def process_vacancy(conn, cursor, webBrowser, links):
    for link in links:
        try:
            title = link.text
            if should_avoid_text(title):
                print(f"Skipping vacancy due to keywords: {title}")
                continue
            href = link.get_attribute('href')
            if href and href.startswith(STARTS_E):
                open_link_in_new_tab(webBrowser, href)
                name, description, expires = extract_vacancy_data(webBrowser)
                if name and expires:
                    save_to_db(conn, cursor, name, href, expires, description)
                    send_to_telegram(f"New Vacancy: {name}\nURL: {href}\nExpires: {expires}\nDescription: {description}")
                close_current_tab(webBrowser)
        except Exception as e:
            print(f"Error processing link: {e}")

def handle_pagination(conn, cursor, webBrowser):
    while True:
        WebDriverWait(webBrowser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a'))
        )
        links = webBrowser.find_elements(By.CSS_SELECTOR, 'a')
        process_vacancy(conn, cursor, webBrowser, links)
        if not go_to_next_page(webBrowser):
            break

@pytest.mark.parametrize('page', [1])
def test_cv_ee_pagination(webBrowser):
    # to check next page 
    # open_page(webBrowser, URL_NEXT)
    # to check normal
    # open_page(webBrowser, URL_SITE)
    # to check iframe 
    open_page(webBrowser, URL_IFR)
    try:
        conn = sqlite3.connect('cv_ee.db')
        cursor = conn.cursor()
        total_results = get_total_results(webBrowser)
        if total_results:
            handle_pagination(conn, cursor, webBrowser)
        conn.close()
        print("Saved to DB")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")

        # to do:  check if text contains keywords like night shifts and others to avoid
        # to do delete useless code
        # to do other job sites
        # code author Krivtsoun