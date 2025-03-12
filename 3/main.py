from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Automatically install and manage the ChromeDriver
driver = webdriver.Chrome()

# Open the target webpage
driver.get('https://www.seleniumeasy.com/test/basic-first-form-demo.html')

# Wait for the page to load and handle the popup if it appears
try:
    no_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'at-cm-no-button'))
    )
    no_button.click()
except:
    print('No element with this class name. Skipping ....')

# Locate the input fields and enter values
sum1 = driver.find_element(By.ID, 'sum1')
sum2 = driver.find_element(By.ID, 'sum2')

sum1.send_keys(Keys.NUMPAD1, Keys.NUMPAD5)  # Enter 15 using numpad keys
sum2.send_keys('15')  # Enter 15 directly

# Locate and click the button to calculate the sum
btn = driver.find_element(By.CSS_SELECTOR, 'button[onclick="return total()"]')
btn.click()

# Wait for the result to appear and print it
result = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.ID, 'displayvalue')))
print("Result:", result.text)

# Close the browser
driver.quit()
