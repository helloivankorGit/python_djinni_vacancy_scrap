import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, TimeoutException

# Constants and Environment Variables
VACANCY_KEYWORD = "JavaScript"
URL = "https://djinni.co/jobs/?primary_keyword=" + VACANCY_KEYWORD
DJINNI_USERNAME = "your_djinni_username"
DJINNI_PASSWORD = "your_djinni_password"
COVER_LETTER_TEXT = "your_cover_letter_text"
# avoid vacancies with those words in them
KEYWORDS_TO_FILTER = ["lead", "full", "node", "senior", "angular", "native", "architect"]
HEADLESS_MODE = True  # Set to False if you want to see the browser

# Initialize WebDriver with Headless Option
options = webdriver.ChromeOptions()
options.headless = HEADLESS_MODE
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def login_to_djinni():
    # Function to log in to the website
    browser.get(URL)
    try:
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@data-analytics-param='login_navbar_jobs']"))).click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(DJINNI_USERNAME)
        browser.find_element(By.ID, "password").send_keys(DJINNI_PASSWORD + Keys.RETURN)
    except (NoSuchElementException, TimeoutException):
        print("Error during login process.")
        return False
    return True

def scrape_vacancies():
    # Function to scrape vacancies from the webpage
    browser.get(URL)
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "list-jobs__item")))
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        vacancy_element = soup.find('li', class_='list-jobs__item job-list__item')
        vacancy_url = vacancy_element.find('a', class_='job-list-item__link')['href']
        vacancy_name = vacancy_element.find('a', class_='job-list-item__link').text.strip()
        return vacancy_url, vacancy_name
    except (NoSuchElementException, TimeoutException):
        print("Error during vacancy scraping.")
        return None, None

def apply_to_vacancy(vacancy_url):
    # Function to apply to a single vacancy
    base_url = "https://djinni.co"
    full_vacancy_url = base_url + vacancy_url
    print("Applying to:", full_vacancy_url)

    browser.execute_script(f"window.open('{full_vacancy_url}', '_blank');")
    browser.switch_to.window(browser.window_handles[-1])
    
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "js-inbox-toggle-reply-form"))).click()
        browser.find_element(By.ID, "message").send_keys(COVER_LETTER_TEXT)
        browser.find_element(By.ID, "job_apply").click()
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
    except (NoSuchElementException, TimeoutException, NoSuchWindowException):
        print("Error during job application process.")
        browser.switch_to.window(browser.window_handles[0])

def main_loop():
    # Main loop to periodically check for new vacancies
    if not login_to_djinni():
        return
    previous_vacancy_url = ""
    while True:
        current_vacancy_url, current_vacancy_name = scrape_vacancies()
        if current_vacancy_name and current_vacancy_url != previous_vacancy_url:
            if any(keyword in current_vacancy_name.lower() for keyword in KEYWORDS_TO_FILTER):
                print("Filtered vacancy:", current_vacancy_name)
            else:
                apply_to_vacancy(current_vacancy_url)
                previous_vacancy_url = current_vacancy_url
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main_loop()
