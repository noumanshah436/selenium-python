import booking.constants as const
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class Booking(webdriver.Chrome):
    def __init__(self):
        # Automatically install and manage the ChromeDriver
        self.driver = webdriver.Chrome()
        super().__init__( )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the browser when exiting the context manager
        self.quit()

    def land_first_page(self):
        self.get(const.BASE_URL)