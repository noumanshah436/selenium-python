import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import traceback
from faker import Faker

fake = Faker()


MAX_USER_FORM_SUBMISSIONS = 5
MAX_USER_FORM_CREATION = 5


class QForRiceSubmitFormForUser:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def setup_driver(self):
        try:
            options = webdriver.ChromeOptions()
            # Headless mode settings
            options.add_argument("--headless=new")  # new headless mode for Chrome
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")  # Required for headless on Windows
            options.add_argument("--window-size=1920,1080")  # Set window size
            options.add_argument("--start-maximized")
            options.add_argument(
                "--disable-blink-features=AutomationControlled"
            )  # Hide automation
            options.add_argument("--disable-extensions")

            # Add user agent to look more like a real browser
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
            print("Browser setup successful in headless mode")
        except Exception as e:
            print(f"Error setting up browser: {str(e)}")
            raise

    def login(self, email: str, password: str):
        try:
            self.driver.get("https://dev.qforrice.com/signin")
            print("Navigating to login page")

            # Wait for login form and enter credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            password_field = self.driver.find_element(By.NAME, "password")

            email_field.send_keys(email)
            password_field.send_keys(password)

            self.driver.implicitly_wait(10)

            # Find and click login button
            login_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            )

            # Remove 'disabled' attribute and 'Mui-disabled' class (for testing purposes)
            self.driver.execute_script(
                """
                arguments[0].removeAttribute('disabled');
                arguments[0].classList.remove('Mui-disabled');
            """,
                login_button,
            )

            # Click the button (JS click to avoid overlay)
            self.driver.execute_script("arguments[0].click();", login_button)
            self.driver.implicitly_wait(10)

            login_button.click()

            print("Login successful")

        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise

    def logout(self):
        print("logging out user...")
        try:
            # Wait for the <header> element
            header = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "header"))
            )

            self.driver.implicitly_wait(10)

            # Find any <button> element inside header node that has both type="button" and aria-label="Open settings" attributes.
            button_in_header = header.find_elements(
                By.XPATH, './/button[@type="button" and @aria-label="Open settings"]'
            )

            if button_in_header:
                print("Settings Button found. Clicking it...")
                settings_button = button_in_header[0]
                settings_button.click()
            else:
                print("Settings Button not found inside header. Can't able to logout")
                raise Exception(
                    "Settings Button not found inside header. Can't able to logout"
                )

            time.sleep(1)

            # Wait for the dropdown menu with "Log Out"
            logout_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//li[contains(@class, "MuiMenuItem-root")]//p[text()="Log Out"]',
                    )
                )
            )
            print("Clicking logout button..")
            logout_option.click()
            print("Logout clicked successfully.")

            time.sleep(1)

        except Exception as e:
            print(f"Error while clicking log out button: {e}")

    def select_first_form(self):
        try:
            print("Selecting form...")

            # Find the first grid item
            grid_item = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="simple-tabpanel-0"]/div/p/div/div[2]/div/div/div[1]',
                    )
                )
            )
            grid_item.click()

            self.driver.implicitly_wait(5)

        except Exception as e:
            print(f"Form selection Failed: {str(e)}")
            raise

    def complete_form_and_submit(self, tried=1):
        if tried > 3:
            return

        try:
            print("Completing form with dummy data...")
            # Wait for the grid to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "MuiGrid-container"))
            )

            time.sleep(3)

            # Get all inputs and textareas
            form_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "input, textarea"
            )

            for element in form_elements:
                tag_name = element.tag_name

                try:
                    if tag_name == "textarea":
                        # Handle textareas
                        element.clear()
                        element.send_keys(fake.sentence(nb_words=50))

                    elif tag_name == "input":
                        input_type = (
                            element.get_attribute("type")
                            if tag_name == "input"
                            else None
                        )
                        if input_type == "text":
                            # Handle text inputs
                            element.clear()
                            element.send_keys(fake.catch_phrase())

                        elif input_type == "radio" or input_type == "checkbox":
                            # Click if not already selected
                            if not element.is_selected():
                                self.driver.execute_script(
                                    "arguments[0].click();", element
                                )
                        else:
                            print(f"Skipping input with type: {input_type}")

                    else:
                        print(f"Skipping unknown tag: {tag_name}")

                    time.sleep(1)

                except Exception:
                    # print(f"Error processing element: {e}")
                    continue

            self.driver.implicitly_wait(20)

            submit_buttons = self.driver.find_elements(
                By.XPATH, '//button[@type="button" and contains(., "Submit")]'
            )

            if submit_buttons:
                submit_buttons[0].click()

                # Wait for and click the "Submit feedback" button
                submit_feedback_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[@type='button' and contains(., 'Submit feedback')]",
                        )
                    )
                )
                submit_feedback_button.click()
                print("Submitted form successfully.")
                time.sleep(2)

                return

            # If no Submit, check for "Next"
            next_buttons = self.driver.find_elements(
                By.XPATH, '//button[@type="button" and contains(., "Next")]'
            )

            if next_buttons:
                print("Submit button not found. Found Next button, clicking it...")
                next_buttons[0].click()
                time.sleep(2)
                self.complete_form_and_submit(tried=tried + 1)
            else:
                raise Exception("Neither Submit nor Next button found.")

        except Exception as e:
            print(f"Form submission error: {str(e)}")
            raise

    def process_form_submission(self):
        # Go to `Survey Taker Dashboard`
        self.driver.get("https://dev.qforrice.com/survey/taker/dashboard")
        self.driver.implicitly_wait(2)

        for _ in range(MAX_USER_FORM_SUBMISSIONS):
            try:
                self.select_first_form()
                self.complete_form_and_submit()

                self.driver.implicitly_wait(10)
            except Exception:
                print("Form submission failed. Proceeding to the next form.")
                self.driver.get("https://dev.qforrice.com/survey/taker/dashboard")
                # time.sleep(2)
                self.driver.implicitly_wait(10)
                continue

    def create_new_form(self):
        # Assuming we are on `Survey Maker Dashboard` page
        try:
            print("Creating new Survey Form")
            # click on `Create New Survey` button
            dashboard_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//button[@type="button" and contains(., "Create New Survey")]',
                    )
                )
            )
            dashboard_button.click()

            # Fill requested_survey input field
            requested_survey_input = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.NAME, "requested_survey"))
            )
            requested_survey_input.clear()
            requested_survey_input.send_keys("5")

            # fill in the form title
            form_title_textarea = self.driver.find_element(
                By.XPATH, '//textarea[contains(@placeholder, "form title")]'
            )
            form_title_textarea.clear()
            form_title_textarea.send_keys(fake.catch_phrase())

            # fill in the form description
            form_desc_textarea = self.driver.find_element(
                By.XPATH,
                '//textarea[contains(@placeholder, "introduction to survey takers")]',
            )
            form_desc_textarea.clear()
            form_desc_textarea.send_keys(fake.paragraph(nb_sentences=3))

            # fill in the Question
            # question_input = self.driver.find_element(
            #     By.XPATH, '//input[@placeholder="Enter Question"]'
            # )
            # question_input.clear()
            # question_input.send_keys(fake.sentence(nb_words=6).rstrip(".") + "?")

            time.sleep(1)
            # add another question
            add_question_button = self.driver.find_element(
                By.XPATH, '//span[@aria-label="Add Question"]'
            )
            add_question_button.click()

            self.driver.implicitly_wait(20)

            # Wait for all draggable sections
            draggable_blocks = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[@draggable="true"]')
                )
            )

            for idx, block in enumerate(draggable_blocks):
                # Get all input fields inside this block
                inputs = block.find_elements(
                    By.XPATH, './/input[@type="text" and @placeholder="Enter Question"]'
                )

                for i, input_field in enumerate(inputs):
                    try:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView(true);", input_field
                        )
                        input_field.clear()
                        input_field.send_keys(
                            fake.sentence(nb_words=6).rstrip(".") + "?"
                        )
                    except Exception as e:
                        print(
                            f"Failed to interact with input {i+1} in block {idx+1}: {e}"
                        )
                time.sleep(0.5)

            # Wait until the dropdown is clickable and then click it
            dropdown = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//div[@role="combobox" and @id="demo-simple-select2" and contains(@class, "MuiSelect-select")]',
                    )
                )
            )
            dropdown.click()

            # Wait for the list items in the dropdown menu to become visible
            options = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        '//div[contains(@class,"MuiPopover-paper")]//ul[contains(@class,"MuiMenu-list")]//li[@role="option" and contains(@class,"MuiMenuItem-root")]',
                    )
                )
            )
            random_choice = random.choice(options)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", random_choice
            )
            random_choice.click()

            # click on next button
            next_button = self.driver.find_element(
                By.XPATH, '//button[@type="button" and contains(., "Next")]'
            )
            next_button.click()

            # it's showing preview of the form, click next button again
            preview_next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@type="button" and contains(., "Next")]')
                )
            )
            preview_next_button.click()

            # Select q-for-rice wallet checkbox
            checkbox_wrapper = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//input[@name="QforRice Wallet"]/parent::span')
                )
            )
            checkbox_wrapper.click()

            # click on publish survey button
            publish_survey_button = self.driver.find_element(
                By.XPATH, '//button[@type="button" and contains(., "Publish Survey")]'
            )
            publish_survey_button.click()
            time.sleep(2)

            # try:
            #     print("Checking if insufficient Balance toast appears")
            #     WebDriverWait(self.driver, 2).until(
            #         EC.presence_of_element_located(
            #             (
            #                 By.XPATH,
            #                 '//div[contains(@class, "Toastify__toast-body")]//div[contains(text(), "Your balance is insufficient")]',
            #             )
            #         )
            #     )
            #     raise Exception("Balance error: Your balance is insufficient.")
            # except TimeoutException:
            #     print(f"line 502")
            #     pass  # No toast appeared, continue normally

            print("Created New survey form successfully. Redirecting to the Dashboard")

            self.driver.get("https://dev.qforrice.com/survey/maker/dashboard")
            self.driver.implicitly_wait(1)

        except Exception as e:
            print(f"Form creation error: {str(e)}")
            raise

    def process_form_creation(self):
        # Go to `Survey Maker Dashboard`
        dashboard_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@role='button' and .//span[text()='Survey Maker Dashboard']]",
                )
            )
        )
        dashboard_button.click()

        for _ in range(MAX_USER_FORM_CREATION):
            try:
                self.create_new_form()
                self.driver.implicitly_wait(10)

            except Exception:
                print("Form Creation failed. Try creating new form.")
                self.driver.get("https://dev.qforrice.com/survey/maker/dashboard")
                # time.sleep(2)
                self.driver.implicitly_wait(20)
                continue

    def process_user_forms(self):
        try:
            self.setup_driver()
            self.login(self.email, self.password)

            # Creating forms
            self.process_form_creation()

            time.sleep(2)

            # Submitting forms
            self.process_form_submission()

            self.logout()

            time.sleep(1)

        except TimeoutException as e:
            print(
                f"Timeout while processing forms for user with email {self.email}: {str(e)}"
            )
        except Exception as e:
            print(f"Fatal error occurred: {str(e)}\n{traceback.format_exc()}")
        finally:
            try:
                self.driver.quit()
                print("Browser closed successfully")
            except:  # noqa: E722
                print("Could not close browser properly")


def run_for_user(email: str, password: str):
    try:
        updater = QForRiceSubmitFormForUser(email, password)
        updater.process_user_forms()
    except Exception as e:
        print(f"User: {email} | Error: {str(e)}\n{traceback.format_exc()}")


def main():

    users = [
        {"email": "user1@gmail.com", "password": "12345"},
        {"email": "user2@gmail.com", "password": "12345"},
        {"email": "user3@gmail.com", "password": "12345"},
        {"email": "user4@gmail.com", "password": "12345"},
        {"email": "user5@gmail.com", "password": "12345"},
        # {"email": "user6@gmail.com", "password": "12345"},
        # {"email": "user7@gmail.com", "password": "12345"},
        # {"email": "user8@gmail.com", "password": "12345"},
        # {"email": "user9@gmail.com", "password": "12345"},
        # {"email": "user10@gmail.com", "password": "12345"},
        # {"email": "user11@gmail.com", "password": "12345"},
        # {"email": "user12@gmail.com", "password": "12345"},
        # {"email": "user13@gmail.com", "password": "12345"},
        # {"email": "user14@gmail.com", "password": "12345"},
        # {"email": "user15@gmail.com", "password": "12345"},
        # {"email": "user16@gmail.com", "password": "12345"},
        # {"email": "user17@gmail.com", "password": "12345"},
        # {"email": "user18@gmail.com", "password": "12345"},
        # {"email": "user19@gmail.com", "password": "12345"},
        # {"email": "user20@gmail.com", "password": "12345"},
    ]

    threads = []

    for user in users:
        t = threading.Thread(
            target=run_for_user, args=(user["email"], user["password"])
        )
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("All user processes completed.")


if __name__ == "__main__":
    main()
