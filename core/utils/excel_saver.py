import os
import time

import pandas as pd

from core.config import FILENAME_TEMPLATE, RESULTS_DIR


class ExcelSaver:
    """Класс для сохранения отзывов в Excel."""

    @staticmethod
    def save_to_excel(reviews, product_ids):
        """Сохраняет отзывы в файл Excel."""
        if not reviews:
            print("Нет отзывов для сохранения.")
            return

        os.makedirs(RESULTS_DIR, exist_ok=True)
        product_ids_str = "_".join(product_ids[:3])
        timestamp = time.strftime("%Y%m%d_%H%M")
        filename = FILENAME_TEMPLATE.format(product_ids_str, timestamp)
        filepath = os.path.join(RESULTS_DIR, filename)

        pd.DataFrame(reviews).to_excel(filepath, index=False)
        print(f"Данные сохранены в {filepath}")
