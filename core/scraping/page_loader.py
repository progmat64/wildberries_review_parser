from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import WAIT_TIMEOUT


class PageLoader:
    """Класс для загрузки страниц и обработки навигации."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_TIMEOUT)

    def load_page(self, url):
        """Загружает указанную страницу."""
        self.driver.get(url)

    def accept_cookies(self):
        """Принимает файлы cookie, если появляется запрос."""
        try:
            button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "cookies__btn"))
            )
            button.click()
        except Exception:
            pass

    def open_reviews_section(self):
        """Открывает раздел отзывов."""
        try:
            button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'comments__btn-all')]")
                )
            )
            self.driver.execute_script("arguments[0].click();", button)
            return True
        except Exception:
            return False

    def scroll_to_load_reviews(self):
        """Прокручивает страницу для загрузки всех отзывов."""
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            try:
                self.wait.until(
                    lambda d: d.execute_script(
                        "return document.body.scrollHeight"
                    )
                    > last_height
                )
            except Exception:
                break
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
