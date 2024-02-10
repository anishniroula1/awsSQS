import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# pip3 install --upgrade webdriver_manager
# pip3 install selenium

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open the sign-up page
driver.get("https://myaccount.uscis.gov/users/sign_up")

# Locate the email input field and enter an email address
email_input = driver.find_element(By.ID, "user_email")
email_input.send_keys("test@example.com")

# Locate the email confirmation input field and enter the same email address
email_confirm_input = driver.find_element(By.ID, "user_email_confirmation")
email_confirm_input.send_keys("test@example.com")
# Add any other actions you need, like submitting the form
submit_button = driver.find_element(By.ID, "sign_up")
submit_button.click()

# Close the browser window
driver.close()
