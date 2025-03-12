import time
import booking.constants as const
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Booking(webdriver.Chrome):
    def __init__(self, teardown=False):
        # Automatically install and manage the ChromeDriver
        self.teardown = teardown
        super().__init__(service=Service(ChromeDriverManager().install()))
        self.implicitly_wait(15)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def land_first_page(self):
        self.get(const.BASE_URL)

    def change_currency(self, currency=None):

        # Wait for and click the currency button (button tag below)

        # <button
        #     aria-haspopup="dialog"
        #     data-testid="header-currency-picker-trigger"
        #     aria-label="Prices in Pakistani Rupee"
        #     type="button"
        #     class="a83ed08757 c21c56c305 f38b6daa18 f671049264 fd3248769f">
        #     <span class="e4adce92df">PKR</span>
        # </button>

        

        currency_button = WebDriverWait(self, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'button[data-testid="header-currency-picker-trigger"]',
                )
            )
        )
        currency_button.click()
        print("Currency button clicked successfully!")

        # Wait for and click the selected currency

        # <button
        #     data-testid="selection-item"
        #     aria-current="false"
        #     type="button"
        #     class="a83ed08757 aee4999c52 ffc914f84a c39dd9701b ac7953442b">
        #     <div class="c624d7469d f034cf5568 dab7c5c6fa a937b09340 a3214e5942" style="--bui_stack_spaced_gap--s: 2;">
        #         <div class="dc5041d860 c72df67c95 fb60b9836d">
        #         <span class="Picker_selection-text">
        #             U.S. Dollar
        #             <div class="CurrencyPicker_currency">USD</div>
        #         </span>
        #         </div>
        #     </div>
        # </button>

        # Multiple ways of selecting the above button

        # Way 1)
        currency_button = WebDriverWait(self, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[@data-testid="selection-item" and contains(., "U.S. Dollar")]',
                )
            )
        )
        print(currency_button.get_attribute("outerHTML"))
        currency_button.click()


    def select_place_to_go(self, place_to_go):
        # Wait for and interact with the search field
        search_field = WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.ID, "ss"))
        )
        search_field.clear()
        search_field.send_keys(place_to_go)

        # Wait for and click the first result
        first_result = WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-i="0"]'))
        )
        first_result.click()
