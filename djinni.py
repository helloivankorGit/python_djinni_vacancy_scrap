import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, TimeoutException
from bs4 import BeautifulSoup

# URL of the webpage with vacancies
url = "https://djinni.co/jobs/?primary_keyword=JavaScript"

# Your DJinni.com credentials
username = "xxx"
password = "xxx"

cover_letter_text = """
Hello. I am writing to express my strong interest in joining your team as a frontend developer. With nearly 7 years of experience in web development, I have honed a versatile skill set, specializing in creating exceptional online experiences.

Throughout my career, I have worked extensively with various e-commerce platforms, including Magento, Shopify, Salesforce Commerce Cloud, and WordPress. My primary focus has been on frontend development, where I've mastered technologies like HTML, CSS, jQuery, JavaScript, and Knockout.js.

However, as the dynamic field of web development evolves, so do I. I am actively expanding my skill set to include more modern technologies, such as React, Vue. I have gained real-world experience in React development, notably in the creation of an application for asset protection, encompassing NFTs and cryptocurrencies.

My commitment to continuous learning and growth drives me to explore new horizons within web development. I possess strong problem-solving and troubleshooting skills, project management capabilities, and a keen eye for best coding practices. I can seamlessly adapt to new languages and technologies and relish the opportunity to embrace the challenges of modern frontend development.

I am excited about the possibility of contributing my skills and expertise to your company and being part of its ongoing success. My commitment to professional growth and my openness to exploring areas where I may have limited experience demonstrate my dedication to staying on the cutting edge of web development.

Thank you for considering my application. I look forward to the possibility of discussing how I can contribute to your team and support your development initiatives. Please find my attached resume for your review.

Sincerely,
Ivan
"""

# List of keywords to filter out
keywords_to_filter = ["lead", "full", "node", "senior", "angular", "native", "architect"]

# Initialize the web browser (you may need to install a webdriver)
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Initialize the previous_vacancy variables 
previous_vacancy_name = ""
previous_vacancy_url = ""

# Function to log in to DJinni.com
def login_to_djinni():
    browser.get(url)
    
    # Locate the login button and click it
    login_button = browser.find_element(By.XPATH, "//a[@data-analytics-param='login_navbar_jobs']")
    login_button.click()
    
    # Locate the username and password input fields, and submit button
    username_input = browser.find_element(By.ID, "email")
    password_input = browser.find_element(By.ID, "password")
    
    # Input your credentials
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Locate the form and submit it
    login_form = browser.find_element(By.TAG_NAME, "form")
    login_form.submit()

# Call the login function to log in once
login_to_djinni()

# Function to scrape vacancies from the webpage
def scrape_vacancies():
    # Load the webpage
    browser.get(url)

    # Wait for the vacancies to load (you may need to adjust the wait time)
    time.sleep(5) 

    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find the first vacancy element
    vacancy_element = soup.find('li', class_='list-jobs__item job-list__item')
    
    # Extract the vacancy URL
    vacancy_url = vacancy_element.find('a', class_='job-list-item__link')['href']
    
    # Extract the vacancy name
    vacancy_name = vacancy_element.find('a', class_='job-list-item__link').text.strip()

    return vacancy_url, vacancy_name

# Function to open a new window with a vacancy URL
def open_new_window(vacancy_url):
    base_url = "https://djinni.co"
    full_vacancy_url = base_url + vacancy_url
    # Print the URL for debugging
    print(full_vacancy_url)

    # Get the number of open windows before opening a new one
    initial_window_count = len(browser.window_handles)

    # Open the URL in a new window
    browser.execute_script(f"window.open('{full_vacancy_url}', '_blank');")
    
    # Wait for the new window to open
    try:
        wait = WebDriverWait(browser, 10)
        wait.until(lambda driver: len(driver.window_handles) > initial_window_count)
        
        # Switch to the new window
        browser.switch_to.window(browser.window_handles[-1])

        # Check if the element with class 'js-inbox-toggle-reply-form' is present
        replyButton = None
        try:
            replyButton = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "js-inbox-toggle-reply-form")))
        except TimeoutException:
            pass

        # If the reply button is present, proceed with interactions
        if replyButton:
            replyButton.click()  # For example, you can click on the element

            # Locate the cover letter field
            textarea = browser.find_element(By.ID, "message")

            # Input cover letter
            textarea.send_keys(cover_letter_text)

            # Locate and submit button
            start_conversation_button = browser.find_element(By.ID, "job_apply")
            start_conversation_button.click()

            # Close the newly opened window after processing
            browser.close()
            
            # Switch back to the original window
            browser.switch_to.window(browser.window_handles[0])
        else:
            # The element is not present, close the window
            try:
                browser.close()
                # Switch back to the original window
                browser.switch_to.window(browser.window_handles[0])
            except NoSuchWindowException:
                pass  # Handle the NoSuchWindowException if the window is already closed
    except TimeoutException:
        # Handle the timeout exception (window didn't open properly)
        print("Timeout waiting for the new window to open.")

# Main loop to periodically check for new vacancies
while True:
    print("Checking for new vacancies...")
    
    # Get the URL and name of the first vacancy
    current_vacancy_url, current_vacancy_name = scrape_vacancies()
    
    # Check if the vacancy name contains any filtered keywords
    if current_vacancy_name:
        if any(keyword in current_vacancy_name.lower() for keyword in keywords_to_filter):
            print("Skipping a vacancy with filtered keyword:", current_vacancy_name)
        elif current_vacancy_url != previous_vacancy_url:
            print("Found a new vacancy:", current_vacancy_name)
            # Open the new vacancy in a new window
            open_new_window(current_vacancy_url)

    # Update the previous_vacancy_url
    previous_vacancy_url = current_vacancy_url
    
    # Sleep for a while before checking again 
    time.sleep(300)  # Sleep for 300 seconds (adjust as needed)
