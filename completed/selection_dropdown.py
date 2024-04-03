import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize the WebDriver. The example uses Chrome.
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open the page
driver.get("https://www.uscis.gov/tools/find-a-civil-surgeon")

try:
    # Wait for the Select2 container to be clickable.
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "select2-edit-gender-container"))
    )

    # Click the Select2 box to open the dropdown.
    select2_container = driver.find_element(By.ID, "select2-edit-gender-container")
    select2_container.click()

    # Wait for the dropdown options to be visible. Adjust the selector as needed.
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "select2-results__option"))
    )

    # This assumes "Female" is a visible text option in the dropdown. Adjust as necessary.
    female_option = driver.find_element(By.XPATH, "//li[contains(text(), 'Female')]")
    female_option.click()
    time.sleep(10)

    # Add any additional actions here, like submitting the form

finally:
    # Uncomment the next line if you want to see the result before closing.
    # input("Press Enter to close...")
    driver.quit()
