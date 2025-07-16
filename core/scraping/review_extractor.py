from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import WAIT_TIMEOUT_GET_PRODUCT


class ReviewExtractor:
    """Класс для извлечения отзывов из загруженной страницы."""

    @staticmethod
    def get_product_name(driver):
        """Извлекает название продукта с ожиданием появления элемента."""
        try:
            wait = WebDriverWait(driver, WAIT_TIMEOUT_GET_PRODUCT)
            element = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "product-page__title")
                )
            )
            return element.text.strip()
        except Exception:
            return "Не найдено"

    @staticmethod
    def extract_reviews(driver, product_id, product_name):
        """Извлекает отзывы о товаре."""
        soup = BeautifulSoup(driver.page_source, "html.parser")
        reviews_section = soup.find("ul", class_="comments__list")
        if not reviews_section:
            return []

        reviews = []
        for review in reviews_section.select("li.comments__item"):
            reviewer = review.find("p", class_="feedback__header")
            reviewer = reviewer.get_text(strip=True) if reviewer else "Аноним"

            rating_element = review.find("span", class_="feedback__rating")
            rating = next(
                (
                    int(cls[4:])
                    for cls in rating_element.get("class", [])
                    if cls.startswith("star") and cls[4:].isdigit()
                ),
                0,
            )

            date_element = review.find("div", class_="feedback__date")
            review_date = (
                date_element.text.strip() if date_element else "Не найдено"
            )

            advantages, disadvantages, comment = "", "", ""
            for span in review.find_all("span", class_="feedback__text--item"):
                bold_text = span.find(
                    "span", class_="feedback__text--item-bold"
                )
                if bold_text:
                    label = bold_text.get_text(strip=True)
                    content = (
                        span.get_text(strip=True).replace(label, "").strip()
                    )
                    if "Достоинства" in label:
                        advantages = content
                    elif "Недостатки" in label:
                        disadvantages = content
                    elif "Комментарий" in label:
                        comment = content
                else:
                    comment = span.get_text(strip=True)

            purchase_state = review.find(
                "span", class_="feedback__state--text"
            )
            purchase_state = (
                purchase_state.get_text(strip=True) if purchase_state else ""
            )

            reviews.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "reviewer": reviewer,
                    "rating": rating,
                    "review_date": review_date,
                    "advantages": advantages,
                    "disadvantages": disadvantages,
                    "comment": comment,
                    "purchase_state": purchase_state,
                }
            )

        return reviews
