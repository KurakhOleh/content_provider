import logging
from scraper import KraftDeleScraper
from translator import ContentTranslator
from yml_generator import YmlGenerator

logging.basicConfig(level=logging.INFO)

def run_pipeline():
    logging.info("--- СТАРТ ПАЙПЛАЙНУ ---")

    scraper = KraftDeleScraper()
    translator = ContentTranslator()
    yml_gen = YmlGenerator()

    # 1. Отримуємо дані товарів прямо з Sitemap XML (швидко, без JS)
    raw_products = scraper.get_product_data_from_sitemap(max_items=5)
    logging.info(f"Знайдено посилань: {len(raw_products)}")

    # 2. Обробка кожного товару
    for raw_data in raw_products:
        logging.info(f"Переклад товару: {raw_data['sku']} - {raw_data['title_pl']}")

        # 3. Переклад контенту (PL -> UK)
        title_uk = translator.translate_text(raw_data['title_pl'])
        description_uk = translator.translate_text(raw_data['description_html_pl'])
        params_uk = translator.translate_params(raw_data['params_pl'])

        processed_data = {
            "sku": raw_data['sku'],
            "title_uk": title_uk,
            "description_uk": description_uk,
            "params_uk": params_uk,
            "images": raw_data['images']
        }

        # 4. Додаємо в YML
        yml_gen.add_product(processed_data)

    # 5. Збереження результату
    yml_gen.save_to_file("prom_feed.xml")
    logging.info("--- ЗАВЕРШЕНО! Файл prom_feed.xml успішно згенеровано ---")

if __name__ == "__main__":
    run_pipeline()
