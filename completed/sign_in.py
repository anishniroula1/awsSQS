import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to the login page
driver.get("https://myaccount.uscis.gov/")

# Find the email and password input fields
email_field = driver.find_element(
    By.ID, "user_email"
)  # You might need to update the element identifier
password_field = driver.find_element(
    By.ID, "user_password"
)  # You might need to update the element identifier

# Enter your email and password (use environment variables or a secure method to handle credentials)
email_field.send_keys("test@gmail.com")
password_field.send_keys("testthis")

# Find and click the sign-in button
sign_in_button = driver.find_element(
    By.ID, "sign_in"
)  # You might need to update the element identifier
sign_in_button.click()

time.sleep(5)
# driver.get("https://myaccount.uscis.gov/users/two_factor_authentication")
WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located(
        (
            By.XPATH,
            "//*[contains(text(), 'Please enter your verification code to continue.')]",
        )
    )
)
# Now, find the input box with ID `code` and enter the value 10
verification_code_input = driver.find_element(By.ID, "code")
print(verification_code_input.get_attribute)
verification_code_input.send_keys("10")
very_button_click = driver.find_element(By.ID, "two_factor_submit")
very_button_click.click()
time.sleep(20)
# Add your automation tasks here

# Don't forget to close the driver after your automation tasks are done
driver.close()
