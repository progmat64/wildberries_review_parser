import time
import pandas as pd
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
    options.add_argument("--disable-direct-composition")
    options.add_argument("--incognito")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 55)

        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "cookies__btn")))
            cookie_btn.click()
        except Exception:
            pass

        try:
            product_name_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-page__title")))
            product_name = product_name_element.text.strip()
        except Exception:
            product_name = "Не найдено"

        try:
            reviews_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'comments__btn-all')]") ))
            driver.execute_script("arguments[0].click();", reviews_tab)
        except Exception:
            return []

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                wait.until(lambda d: d.execute_script("return document.body.scrollHeight") > last_height)
            except Exception:
                break

            last_height = driver.execute_script("return document.body.scrollHeight")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        reviews_container = soup.find("ul", class_="comments__list")
        if not reviews_container:
            return []

        reviews = []
        for review in reviews_container.select("li.comments__item"):
            reviewer = review.find("p", class_="feedback__header")
            reviewer = reviewer.get_text(strip=True) if reviewer else "Аноним"

            rating_element = review.find("span", class_="feedback__rating")
            rating = 0
            if rating_element and "stars-line" in rating_element.get("class", []):
                for cls in rating_element.get("class", []):
                    if cls.startswith("star") and cls[4:].isdigit():
                        rating = int(cls[4:])
                        break

            try:
                date_element = review.find("div", class_="feedback__date")
                review_date = date_element.text.strip() if date_element else "Не найдено"
            except Exception:
                review_date = "Не найдено"

            advantages, disadvantages, comment, purchase_state = "", "", "", ""
            text_block = review.find("p", class_="feedback__text")
            
            if text_block:
                for span in text_block.find_all("span", class_="feedback__text--item"):
                    bold_text = span.find("span", class_="feedback__text--item-bold")
                    if bold_text:
                        label = bold_text.get_text(strip=True)
                        content = span.get_text(strip=True).replace(label, "").strip()
                        if "Достоинства" in label:
                            advantages = content
                        elif "Недостатки" in label:
                            disadvantages = content
                        elif "Комментарий" in label:
                            comment = content
                    else:
                        comment = span.get_text(strip=True)

            state_span = review.find("span", class_="feedback__state--text")
            if state_span:
                purchase_state = state_span.get_text(strip=True)

            reviews.append({
                "product_id": product_id,
                "product_name": product_name,
                "reviewer": reviewer,
                "rating": rating,
                "review_date": review_date,
                "advantages": advantages,
                "disadvantages": disadvantages,
                "comment": comment,
                "purchase_state": purchase_state,
            })
        
        return reviews
    finally:
        driver.quit()

def save_to_excel(reviews, filename="wildberries_reviews_4{product_ids}.xlsx"):
    df = pd.DataFrame(reviews)
    df.to_excel(filename, index=False)
    print(f"Данные сохранены в {filename}")

if __name__ == "__main__":
    product_ids = input("Введите артикулы товаров через запятую: ").split(",")
    product_ids = [pid.strip() for pid in product_ids if pid.strip()]
    
    all_reviews = []
    for product_id in product_ids:
        reviews = get_reviews_selenium(product_id)
        all_reviews.extend(reviews)
    
    if all_reviews:
        save_to_excel(all_reviews)
    else:
        print("Отзывы не найдены.")
