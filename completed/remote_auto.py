from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Assuming SELENIUM_REMOTE_URL is set in your environment variables
selenium_remote_url = os.environ.get('SELENIUM_REMOTE_URL')

# Setting up the Selenium Remote WebDriver
driver = webdriver.Remote(
    command_executor=selenium_remote_url,
    options=webdriver.ChromeOptions()
)

try:
    driver.get("https://myaccount.uscis.gov/users/sign_up")
    
    # Wait for the email field to be loaded.
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "newAccountForm_email"))
    )
    
    # Example email. Replace with your desired value or generate dynamically.
    email = "test@example.com"
    
    # Find the email and confirmation fields and fill them
    email_field = driver.find_element(By.ID, "newAccountForm_email")
    confirm_email_field = driver.find_element(By.ID, "newAccountForm_emailConfirmation")
    
    email_field.send_keys(email)
    confirm_email_field.send_keys(email)
    
    # You can extend this script to submit the form and handle the response as needed.
    
finally:
    driver.quit()

