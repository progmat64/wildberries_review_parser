from core.config import BASE_URL
from core.scraping.page_loader import PageLoader
from core.scraping.review_extractor import ReviewExtractor
from core.utils.excel_saver import ExcelSaver
from core.utils.webdriver import WebDriverManager

if __name__ == "__main__":
    product_ids = input("Введите артикулы товаров через запятую: ").split(",")
    product_ids = [pid.strip() for pid in product_ids if pid.strip()]

    all_reviews = []
    for pid in product_ids:
        driver = WebDriverManager.create_webdriver()
        page_loader = PageLoader(driver)
        page_loader.load_page(f"{BASE_URL}{pid}/detail.aspx")
        page_loader.accept_cookies()
        product_name = ReviewExtractor.get_product_name(driver)

        if page_loader.open_reviews_section():
            page_loader.scroll_to_load_reviews()
            all_reviews.extend(
                ReviewExtractor.extract_reviews(driver, pid, product_name)
            )
        driver.quit()

    ExcelSaver.save_to_excel(all_reviews, product_ids)
