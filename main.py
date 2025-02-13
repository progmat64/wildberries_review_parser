import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_reviews_selenium(product_id):
    url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)

        # Принимаем куки
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "cookies__btn")))
            cookie_btn.click()
        except Exception as e:
            print("Не удалось принять куки:", e)

        # Переходим на вкладку с отзывами
        try:
            reviews_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'comments__btn-all')]"))
            )
            driver.execute_script("arguments[0].click();", reviews_tab)
            print("Переход на страницу отзывов выполнен")
        except Exception as e:
            print("Не удалось перейти на страницу отзывов:", e)
            return []

        # Ждем загрузки отзывов
        time.sleep(3)

        # Пролистываем страницу 3 раза для подгрузки отзывов
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(6)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Получаем обновленный HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Ищем контейнер с отзывами
        reviews_container = soup.find("ul", class_="comments__list")
        if not reviews_container:
            print("Контейнер с отзывами не найден")
            return []

        reviews = []
        # Парсим каждый отзыв
        for review in reviews_container.select("li.comments__item"):

            # Извлекаем имя автора
            reviewer = (
                review.find("p", class_="feedback__header").get_text(strip=True)
                if review.find("p", class_="feedback__header")
                else "Аноним"
            )

            # Извлекаем оценку
            rating_element = review.find("span", class_="feedback__rating")
            rating = 0
            if rating_element and "stars-line" in rating_element.get("class", []):
                for cls in rating_element.get("class", []):
                    if cls.startswith("star") and cls[4:].isdigit():  # Проверяем, что после "star" идет число
                        rating = int(cls[4:])
                        break

            # Извлекаем текст отзыва
            review_text = ""
            text_block = review.find("p", class_="feedback__text")

            if text_block:
                # Обрабатываем основной текст
                main_text = text_block.find("span", class_="feedback__text--item")
                if main_text:
                    review_text += main_text.get_text(strip=True)

            reviews.append(
                {
                    "reviewer": reviewer,
                    "rating": rating,
                    "review_text": review_text.strip(),
                }
            )

        return reviews

    finally:
        driver.quit()


if __name__ == "__main__":
    product_id = "155404700"  # Тестовый товар с отзывами
    reviews = get_reviews_selenium(product_id)

    if reviews:
        print(f"Найдено отзывов: {len(reviews)}")
        for i, review in enumerate(reviews, 1):
            print(f"Отзыв #{i}:")
            print(f"Автор: {review['reviewer']}")
            print(f"Оценка: {review['rating']}/5")
            print(f"Текст: {review['review_text']}")
            print("-" * 50)
    else:
        print("Отзывы не найдены.")
