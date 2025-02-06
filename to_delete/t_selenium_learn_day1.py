from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# from webdriver_manager.chrome import ChromeDriverManager  # optional, automatically downloads ChromeDriver
from config import WEBSITE_URL, STARTS_R, URL_SITE, URL_NEXT, URL_1_23

import time
# Option 1: Specify the ChromeDriver path manually using Service
service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')

# Option 2: Alternatively, use webdriver_manager to automatically download the correct version of ChromeDriver
# service = Service(ChromeDriverManager().install())

# Set up Chrome options
options = webdriver.ChromeOptions()

# Initialize the WebDriver with the service
driver = webdriver.Chrome(service=service, options=options)

# Open a website
driver.get(URL_1_23)
# driver.get('https://www.google.com/search?q=test&oq=test+&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQABiABDIHCAIQABiABDIGCAMQRRg8MgYIBBBFGEEyBggFEEUYQTIGCAYQRRhBMgYIBxBFGDzSAQgxOTIxajBqN6gCALACAA&sourceid=chrome&ie=UTF-8')
# time.sleep(5)
#--------------------------------------------------------------------------------------
# Подождать немного для загрузки страницы (если нужно, используйте WebDriverWait)
driver.implicitly_wait(3)

# Находим все элементы с результатами поиска
results = driver.find_elements(By.CSS_SELECTOR, 'a')

# Выводим ссылки на страницы
for result in results:
    href = result.get_attribute('href')
    # Убедимся, что ссылка не пустая и начинается с 
    if href and href.startswith(STARTS_R):
        print(href)


# Находим кнопку с aria-label="Фильтры" и нажимаем на неё
filter_button = driver.find_element(By.XPATH, '//button[@aria-label="Фильтры"]')
filter_button.click()
print(str(time.time()) + ' click filter_button')
# Находим кнопку с текстом "Отмена" и нажимаем на неё
cancel_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn--type-secondary") and contains(@class, "btn--width-full")]'))
)
# cancel_button.click()
# print(str(time.time()) + ' click cancel_button')

# Step 1: Wait for the "Remove" button to be clickable
remove_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Remove Информационные технологии (208)"]'))
)

time.sleep(3)

# Step 2: Click on the "Remove" button to delete the option
remove_button.click()

time.sleep(3)

# Step 1: Wait for the button with text starting with 'Показать' to be clickable
show_results_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//button[starts-with(span, "Показать")]'))
)

# Step 2: Click the button to apply the filter
show_results_button.click()
print("Clicked show results button")
#--------------------------------------------------------------------------------------

# ждем 5 минут
time.sleep(300)

# Print the title of the page
print(driver.title)

# Close the browser
driver.quit()
