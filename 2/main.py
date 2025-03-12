from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Automatically install and manage the ChromeDriver
driver = webdriver.Chrome()

# Open the target webpage
driver.get(
    "https://www.seleniumeasy.com/test/jquery-download-progress-bar-demo.html")

# Wait for the download button to be present and click it
download_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'downloadButton'))
)

download_button.click()

# Wait for the progress label to show 'Complete!'
WebDriverWait(driver, 30).until(
    EC.text_to_be_present_in_element(
        (By.CLASS_NAME, 'progress-label'),  # Element filtration
        'Complete!'  # The expected text
    )
)

# Close the browser
driver.quit()
