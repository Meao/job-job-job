import pytest
import sqlite3
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import WEBSITE_URL, STARTS_R, URL_SITE, URL_NEXT, URL_7_21, URL_7_84

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

def test_cv_ee(webBrowser):
    # Open a website
    webBrowser.get(URL_7_21)

    # could use WebDriverWait
    webBrowser.implicitly_wait(3)

    # find links
    results = webBrowser.find_elements(By.CSS_SELECTOR, 'a')

    i = 0
    # open links
    for result in results:
        href = result.get_attribute('href')
        # starts with 
        if href and href.startswith(STARTS_R):
            # print(href)
            i+=1
            # webBrowser.get(href)  # Открываем ссылку
            
            # # open link JavaScript
            # webBrowser.execute_script(f"window.open('{href}', '_blank');")

            # time.sleep(2)  # wait load
            
        # stop 
        # if i == 3:  # after 10
            # break


    # find with aria-label="Фильтры" and press
    filter_button = webBrowser.find_element(By.XPATH, '//button[@aria-label="Фильтры"]')
    filter_button.click()
    print(str(time.time()) + ' click filter_button')
    # find cancel button
    cancel_button = WebDriverWait(webBrowser, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn--type-secondary") and contains(@class, "btn--width-full")]'))
    )
    # cancel_button.click()
    # print(str(time.time()) + ' click cancel_button')

    # Step 1: Wait for the "Remove" button to be clickable
    remove_button = WebDriverWait(webBrowser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Remove Информационные технологии (208)"]'))
    )

    time.sleep(3)

    # Step 2: Click on the "Remove" button to delete the option
    remove_button.click()

    time.sleep(3)

    # Step 1: Wait for the button with text starting with 'Показать' to be clickable
    show_results_button = WebDriverWait(webBrowser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[starts-with(span, "Показать")]'))
    )

    # Step 2: Click the button to apply the filter
    show_results_button.click()
    # print("Clicked show results button")

def test_cv_ee_pytest(webBrowser):
    # Open a website
    webBrowser.get(URL_7_84)

    # wait page load
    WebDriverWait(webBrowser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a')))

    # find elem
    results = webBrowser.find_elements(By.CSS_SELECTOR, 'a')

    try:
        conn = sqlite3.connect('cv_ee.db')
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    # Store the main window handle
    main_window_handle = webBrowser.current_window_handle  
    # onnly 20 links
    for result in results:
        href = result.get_attribute('href')
        # check page starts with
        if href and href.startswith(STARTS_R):
            # print(href)
            # open link new page with JavaScript
            webBrowser.execute_script(f"window.open('{href}', '_blank');")
  
            # wait page load
            time.sleep(2)
             # Switch to the newly opened tab
            new_window_handle = [handle for handle in webBrowser.window_handles if handle != main_window_handle][0]
            webBrowser.switch_to.window(new_window_handle)
            
            # find on page text of name in h1, expires in span after text Deadline: 
             # Extract the vacancy name (usually in <h1>)
            name = webBrowser.find_element(By.CSS_SELECTOR, 'h1').text
            # text preprocessing for filtering
            names_lst = name.lower().split()
            # text cleaning
            if not any(word in names_lst for word in FILTER_OUT):
                # print(name)
                    
                # Extract the expiration date (look for span after 'Deadline:')
                expires_element = webBrowser.find_element(By.XPATH, "//span[contains(text(), 'Deadline:')]")
                # Extract only the date (remove the "Deadline: " part)
                expires = expires_element.text.replace('Deadline: ', '').strip()
                # print(expires)
                # check the values of name, url, expires are not in db
                try:
                    cursor.execute("SELECT * FROM vacancies WHERE name = ? AND url = ? AND expires = ?", (name, href, expires))
                    result_from_db = cursor.fetchone()
                    
                    if result_from_db is None:
                        # Insert the new vacancy into the database if it does not exist
                        cursor.execute('''
                        INSERT INTO vacancies (name, url, expires) 
                        VALUES (?, ?, ?)
                        ''', (name, href, expires))
                        conn.commit()
                        print(f"Saved: {name}, {href}, {expires}")
                    else:
                        print(f"Already exists in DB: {name}")
                except Exception as e:
                    print(f"Error processing {name}: {e}")
            # close the opened tab to return to results page
            # After processing the current vacancy, close the current tab
            webBrowser.close()

            # Switch back to the main tab
            webBrowser.switch_to.window(main_window_handle)
            # # wait for page to load
            # time.sleep(2)  
    
    # Close the database connection
    conn.close()
    print("saved to db")


