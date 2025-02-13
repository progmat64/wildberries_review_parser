from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class WebDriverManager:
    """Класс для управления WebDriver."""

    @staticmethod
    def create_webdriver():
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-direct-composition")
        options.add_argument("--incognito")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
