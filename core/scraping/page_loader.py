from selenium.common.exceptions import TimeoutException
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

    def _find_reviews_button(self, driver):
        """Ищет кнопку для открытия раздела с отзывами."""
        elems = driver.find_elements(
            By.XPATH, "//a[contains(@class, 'comments__btn-all')]"
        )
        if elems:
            return elems[0]
        driver.execute_script("window.scrollBy(0, 400);")
        return False

    def open_reviews_section(self) -> bool:
        """Открывает раздел с отзывами."""
        try:
            button = self.wait.until(self._find_reviews_button)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
            self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'comments__btn-all')]")
                )
            ).click()
            return True
        except TimeoutException:
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
                last_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
            except Exception:
                break
